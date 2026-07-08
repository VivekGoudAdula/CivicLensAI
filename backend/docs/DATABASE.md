# CivicLens AI — Firestore Database Documentation

## Overview

CivicLens AI uses Google Cloud Firestore as its primary operational database for civic intelligence in Indian parliamentary constituencies. The schema supports citizen complaints, AI-driven clustering, departmental recommendations, and analytics dashboards.

**Constituency context (seed data):** Amethi, Uttar Pradesh

---

## Entity Relationship Model

```
┌─────────────┐       1:N        ┌──────────────┐
│   Village   │─────────────────▶│  Complaint   │
└─────────────┘                  └──────┬───────┘
       │                                │
       │                                │ N:1
       │                                ▼
       │                         ┌──────────────┐
       │                         │   Cluster    │
       │                         └──────┬───────┘
       │                                │
       │                                │ N:M
       │                                ▼
       │      N:M               ┌──────────────────┐
       └───────────────────────▶│ Recommendation   │
                                └────────┬─────────┘
                                         │
                                         │ N:1
                                         ▼
                                ┌──────────────────┐
                                │   Department     │
                                └──────────────────┘

┌──────────────┐     derived from      ┌──────────────┐
│  Complaint   │──────────────────────▶│  Analytics   │
│ Recommendation│─────────────────────▶│              │
└──────────────┘                       └──────────────┘
```

### Relationship Summary

| Parent | Child | Cardinality | Link Fields |
|--------|-------|-------------|-------------|
| Village | Complaint | 1:N | `complaints.village_id`, `complaints.village_ref` |
| Cluster | Complaint | 1:N | `complaints.cluster_id`, `complaints.cluster_ref` |
| Cluster | Recommendation | N:M | `recommendations.cluster_ids`, `clusters.recommendation_ids` |
| Department | Recommendation | 1:N | `recommendations.department_id`, `recommendations.department_ref` |
| Village | Cluster | N:M | `clusters.village_ids` |
| Village | Recommendation | N:M | `recommendations.village_ids` |
| Complaints + Recommendations | Analytics | derived | `analytics.metrics`, `analytics.source_*_count` |

---

## Collections

### 1. `villages`

Administrative units within a parliamentary constituency.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | auto | Document ID |
| `name` | string | yes | Village name |
| `constituency` | string | yes | Parliamentary constituency |
| `district` | string | yes | District name |
| `state` | string | yes | State name |
| `block` | string | no | Tehsil/block |
| `pin_code` | string | no | 6-digit PIN code |
| `population` | integer | no | Estimated population |
| `geo` | object | no | `{ latitude, longitude, address }` |
| `is_active` | boolean | yes | Active flag |
| `complaint_count` | integer | yes | Denormalized total complaints |
| `open_complaint_count` | integer | yes | Denormalized open complaints |
| `metadata` | object | yes | Audit metadata |

---

### 2. `departments`

Government departments responsible for civic service delivery.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | auto | Document ID |
| `name` | string | yes | Department full name |
| `code` | string | yes | Unique code (e.g. `PWD`) |
| `category` | enum | yes | `infrastructure`, `health`, `water`, etc. |
| `description` | string | no | Department mandate |
| `head_name` | string | no | Department head |
| `contact_email` | string | no | Official email |
| `contact_phone` | string | no | Contact number |
| `constituency` | string | no | Jurisdiction |
| `is_active` | boolean | yes | Active flag |
| `assigned_recommendation_count` | integer | yes | Denormalized count |
| `active_recommendation_count` | integer | yes | Denormalized active count |
| `metadata` | object | yes | Audit metadata |

---

### 3. `complaints`

Citizen-submitted civic grievances.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | auto | Document ID |
| `title` | string | yes | Complaint headline |
| `description` | string | yes | Full complaint text |
| `category` | enum | yes | `roads`, `water`, `health`, etc. |
| `priority` | enum | yes | `low`, `medium`, `high`, `critical` |
| `status` | enum | yes | Lifecycle status |
| `village_id` | string | yes | Denormalized village ID |
| `village_ref` | string | yes | `villages/{id}` path |
| `village_name` | string | yes | Denormalized village name |
| `constituency` | string | yes | Constituency |
| `district` | string | yes | District |
| `state` | string | yes | State |
| `citizen_name` | string | no | Complainant name |
| `citizen_phone` | string | no | Complainant phone |
| `citizen_email` | string | no | Complainant email |
| `location` | object | no | Geo coordinates |
| `attachments` | array | no | File attachments |
| `cluster_id` | string | no | Linked cluster ID |
| `cluster_ref` | string | no | `clusters/{id}` path |
| `ai_analysis` | object | no | AI sentiment, keywords, summary |
| `submitted_at` | timestamp | yes | Submission time |
| `resolved_at` | timestamp | no | Resolution time |
| `metadata` | object | yes | Audit metadata |

**AI fields (`ai_analysis`):**

| Field | Type | Description |
|-------|------|-------------|
| `sentiment` | enum | `positive`, `neutral`, `negative`, `mixed` |
| `urgency_score` | float | 0.0–1.0 urgency score |
| `keywords` | array | Searchable keywords |
| `summary` | string | AI-generated summary |
| `language` | string | Detected language code |
| `processed_at` | timestamp | AI processing time |
| `model_version` | string | Gemini model version |

---

### 4. `clusters`

AI-grouped complaint clusters representing systemic issues.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | auto | Document ID |
| `title` | string | yes | Cluster title |
| `description` | string | yes | Cluster description |
| `theme` | string | yes | Thematic label |
| `category` | enum | yes | Primary category |
| `status` | enum | yes | `open`, `analyzing`, `recommended`, etc. |
| `complaint_ids` | array | yes | Linked complaint IDs |
| `complaint_refs` | array | yes | `complaints/{id}` paths |
| `complaint_count` | integer | yes | Count of linked complaints |
| `village_ids` | array | yes | Affected village IDs |
| `constituency` | string | yes | Constituency |
| `district` | string | yes | District |
| `state` | string | yes | State |
| `ai_insights` | object | no | AI cluster analysis |
| `recommendation_ids` | array | no | Linked recommendation IDs |
| `metadata` | object | yes | Audit metadata |

**AI fields (`ai_insights`):**

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Cluster summary |
| `root_causes` | array | Identified root causes |
| `affected_population_estimate` | integer | Estimated affected population |
| `priority_score` | float | 0.0–1.0 priority |
| `key_themes` | array | Thematic tags |
| `generated_at` | timestamp | Generation time |
| `model_version` | string | Model version |

---

### 5. `recommendations`

Actionable recommendations assigned to government departments.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | auto | Document ID |
| `title` | string | yes | Recommendation title |
| `description` | string | yes | Full recommendation |
| `status` | enum | yes | Workflow status |
| `priority` | enum | yes | `low`, `medium`, `high`, `urgent` |
| `cluster_ids` | array | yes | Source cluster IDs |
| `cluster_refs` | array | yes | `clusters/{id}` paths |
| `department_id` | string | yes | Assigned department ID |
| `department_ref` | string | yes | `departments/{id}` path |
| `department_name` | string | yes | Denormalized name |
| `department_code` | string | yes | Denormalized code |
| `village_ids` | array | yes | Affected villages |
| `constituency` | string | yes | Constituency |
| `district` | string | yes | District |
| `state` | string | yes | State |
| `estimated_budget_inr` | float | no | Budget estimate (INR) |
| `estimated_timeline_days` | integer | no | Timeline in days |
| `ai_recommendation` | object | no | AI-generated action plan |
| `assigned_official` | string | no | Responsible official |
| `due_date` | timestamp | no | Target completion date |
| `completed_at` | timestamp | no | Actual completion date |
| `metadata` | object | yes | Audit metadata |

---

### 6. `analytics`

Pre-computed analytics snapshots for dashboards.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | auto | Document ID |
| `report_type` | enum | yes | Report category |
| `period_start` | timestamp | yes | Reporting period start |
| `period_end` | timestamp | yes | Reporting period end |
| `constituency` | string | yes | Constituency scope |
| `district` | string | no | District scope |
| `state` | string | no | State scope |
| `department_id` | string | no | Department scope |
| `village_id` | string | no | Village scope |
| `metrics` | object | yes | Aggregated metrics payload |
| `generated_at` | timestamp | yes | Report generation time |
| `source_complaint_count` | integer | yes | Source data count |
| `source_recommendation_count` | integer | yes | Source data count |
| `metadata` | object | yes | Audit metadata |

---

## Query Strategy

### Dashboard Queries

| Use Case | Collection | Filters | Sort |
|----------|------------|---------|------|
| Constituency complaint feed | `complaints` | `constituency`, `status` | `submitted_at DESC` |
| Village complaint list | `complaints` | `village_id`, `status` | `submitted_at DESC` |
| Priority triage | `complaints` | `constituency`, `priority` | `submitted_at DESC` |
| Open clusters | `clusters` | `constituency`, `status` | `complaint_count DESC` |
| Department workload | `recommendations` | `department_id`, `status` | `due_date ASC` |
| Latest snapshot | `analytics` | `constituency`, `report_type` | `generated_at DESC` |

### Search Patterns

- **Prefix search:** `name`, `title`, `theme` fields using `>=` / `<` range queries
- **Keyword search:** `complaints.ai_analysis.keywords` via `array_contains`
- **Array membership:** `village_ids`, `cluster_ids`, `complaint_ids` via `array_contains`
- **Date ranges:** `submitted_at`, `period_start`, `period_end`, `due_date`

### Denormalization Strategy

Firestore document references are stored as both:
1. **Reference paths** (`village_ref`, `cluster_ref`, `department_ref`) for integrity
2. **Denormalized IDs and names** for efficient single-collection queries

Counters (`complaint_count`, `assigned_recommendation_count`) are maintained on parent documents and updated by application services in Phase 3.

---

## Index Strategy

Composite indexes are defined in `firestore.indexes.json`. Deploy with:

```bash
firebase deploy --only firestore:indexes
```

### Index Categories

1. **Filtering + sorting** — constituency/status/date combinations
2. **Array contains + filter** — village/cluster membership queries
3. **Department workload** — department_id + status + due_date
4. **Analytics time-series** — constituency + report_type + generated_at

---

## Repository Layer

| Repository | Module | Methods |
|------------|--------|---------|
| `VillageRepository` | `app.repositories.village_repository` | CRUD, list, search, count |
| `DepartmentRepository` | `app.repositories.department_repository` | CRUD, list, search, `get_by_code` |
| `ComplaintRepository` | `app.repositories.complaint_repository` | CRUD, list, search, `list_by_village` |
| `ClusterRepository` | `app.repositories.cluster_repository` | CRUD, list, search, `list_by_complaint` |
| `RecommendationRepository` | `app.repositories.recommendation_repository` | CRUD, list, search, `list_by_department` |
| `AnalyticsRepository` | `app.repositories.analytics_repository` | CRUD, list, search, `get_latest_constituency_snapshot` |

All repositories extend `BaseRepository` with cursor-based pagination via `PaginationParams`.

---

## Firestore Utilities

| Module | Purpose |
|--------|---------|
| `app.db.collections` | Collection names and reference helpers |
| `app.db.converters` | Pydantic ↔ Firestore conversion |
| `app.db.timestamps` | Server timestamp helpers |
| `app.db.transactions` | Transaction and batch write wrappers |
| `app.db.pagination` | Pagination models |

---

## Seeding

```bash
cd backend
.\.venv\Scripts\python scripts\seed_database.py --clear
```

**Seed data includes:**
- 6 villages in Amethi constituency
- 7 government departments
- 10 citizen complaints with AI analysis
- 3 complaint clusters
- 5 departmental recommendations
- 2 analytics reports

---

## Phase 3 Readiness

The database layer is complete and ready for API endpoint implementation:

- Pydantic models: `app.models.domain.*`
- Repository DI: `app.api.repository_deps`
- Enums: `app.models.enums.common`
- No schema changes required for Phase 3 business logic

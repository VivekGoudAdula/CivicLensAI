# CivicLens AI — Phase 9: MP Dashboard Architecture

## Overview

Phase 9 delivers the **MP Command Center** — a government decision-intelligence dashboard for Members of Parliament and constituency administrators. It aggregates live data from Phases 1–8 (complaints, AI analysis, vision, clustering, priority engine) into a unified, real-time command center comparable to enterprise cloud consoles.

**Route prefix:** `/dashboard`  
**API prefix:** `/api/v1/analytics`

---

## Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MP Command Center (React)                        │
├─────────────────────────────────────────────────────────────────────────┤
│  DashboardLayout                                                         │
│  ├── DashboardSidebar (navigation)                                       │
│  ├── DashboardFiltersBar (global filters context)                          │
│  ├── Firestore Realtime Indicator + useFirestoreRealtime()               │
│  └── Outlet → Page components                                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Data Layer                                                              │
│  ├── TanStack Query (REST cache + invalidation)                          │
│  ├── dashboardApi → /analytics/dashboard | /activities | /overview       │
│  ├── complaintsApi, clustersApi, priorityApi (detail drawers)            │
│  └── Firebase onSnapshot → invalidate dashboard queries on change        │
├─────────────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)                                                       │
│  └── AnalyticsPortalService                                              │
│      ├── ComplaintRepository (up to 500 docs)                            │
│      ├── ClusterRepository (up to 500 docs)                              │
│      └── PriorityPortalService (top priorities + recommendations)        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
features/dashboard/
├── layout/
│   ├── DashboardLayout.tsx          # Shell: sidebar, filters, realtime, outlet
│   ├── DashboardSidebar.tsx         # MP-specific navigation
│   └── dashboard-navigation.ts      # Nav item definitions
├── context/
│   └── dashboard-filters-context.tsx
├── hooks/
│   ├── use-dashboard.ts             # React Query hooks
│   └── use-firestore-realtime.ts    # Firestore listeners
├── components/
│   ├── kpi/dashboard-kpi-grid.tsx
│   ├── filters/dashboard-filters-bar.tsx
│   ├── charts/dashboard-charts-grid.tsx
│   ├── priority/ai-priority-section.tsx
│   ├── complaints/dashboard-complaints-table.tsx
│   ├── clusters/cluster-cards-grid.tsx
│   ├── activity/activity-timeline.tsx
│   ├── insights/ai-insights-panel.tsx
│   ├── summary/
│   │   ├── complaint-heat-summary.tsx
│   │   └── summary-panels.tsx
│   └── drawers/
│       ├── dashboard-drawer.tsx
│       ├── complaint-detail-drawer.tsx
│       ├── cluster-detail-drawer.tsx
│       ├── priority-detail-drawer.tsx
│       ├── ai-analysis-drawer.tsx
│       └── image-analysis-drawer.tsx
└── pages/
    ├── DashboardHomePage.tsx
    ├── DashboardComplaintsPage.tsx
    ├── DashboardComplaintDetailPage.tsx
    ├── DashboardPriorityPage.tsx
    ├── DashboardClustersPage.tsx
    ├── DashboardAnalyticsPage.tsx
    └── DashboardActivitiesPage.tsx
```

---

## Page Hierarchy

| Route | Page | Purpose |
|-------|------|---------|
| `/dashboard` | Command Center Home | KPIs, AI priorities, heat map, recent items, insights, charts |
| `/dashboard/complaints` | Complaints Registry | Enterprise table with search, sort, pagination, filters |
| `/dashboard/complaints/:id` | Complaint Details | Full AI + vision intelligence for a single complaint |
| `/dashboard/priority` | Priority Center | AI-ranked clusters, leaderboard, recommendations |
| `/dashboard/clusters` | Cluster Intelligence | Cluster cards with quick-view drawers |
| `/dashboard/analytics` | Analytics Overview | Full chart suite + KPIs + AI insights |
| `/dashboard/activities` | Activity Timeline | Chronological constituency events |

---

## State Management Flow

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│ Global Filters   │────▶│ Client-side filter  │────▶│ Table / lists    │
│ (React Context)  │     │ on complaints page  │     │ on dashboard     │
└──────────────────┘     └─────────────────────┘     └──────────────────┘

┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│ TanStack Query   │◀────│ REST APIs           │◀────│ FastAPI services │
│ dashboard keys   │     │ /analytics/*        │     │ aggregation      │
└────────┬─────────┘     └─────────────────────┘     └──────────────────┘
         │
         │ invalidateQueries(["dashboard", "complaints", "clusters", "priority"])
         ▼
┌──────────────────┐
│ Firestore        │
│ onSnapshot       │
│ complaints       │
│ clusters         │
└──────────────────┘

┌──────────────────┐
│ Drawer state     │  Local useState per page (complaintId, clusterId, priority)
└──────────────────┘
```

**Query keys:**
- `["dashboard", "home"]`
- `["dashboard", "activities", limit]`
- `["dashboard", "analytics"]`

---

## Firestore Query Strategy

### Backend (aggregation)
- `ComplaintRepository.list(limit=500, order_by=submitted_at desc)`
- `ClusterRepository.list(limit=500, order_by=complaint_count desc)`
- No new Firestore indexes required for dashboard API

### Frontend (realtime)
- `onSnapshot(query(collection(db, "complaints"), limit(1)))`
- `onSnapshot(query(collection(db, "clusters"), limit(1)))`
- On any document change → `invalidateQueries` for dashboard, complaints, clusters, priority
- Emulator: `VITE_FIREBASE_USE_EMULATOR=true` + `VITE_FIREBASE_EMULATOR_PORT=8085`
- Production: set `VITE_FIREBASE_*` credentials; listeners attach automatically

---

## Performance Optimization Strategy

| Technique | Implementation |
|-----------|----------------|
| Code splitting | All dashboard pages lazy-loaded via `React.lazy` in `routes.tsx` |
| React Query cache | `staleTime: 30s` (home/activities), `60s` (analytics) |
| Memoization | `DashboardChartsGrid` wrapped in `memo()` |
| Pagination | Complaints table: server fetch 100 + client DataTable pagination |
| Backend cap | Aggregation limited to 500 complaints / 500 clusters |
| Realtime debounce | Firestore listeners invalidate cache (React Query dedupes refetches) |
| Skeletons | KPI, table, card skeletons on all pages |
| Empty / error states | Dedicated components per section |

---

## Responsive Layout Diagram

```
Desktop (≥1280px)
┌────────┬────────────────────────────────────────────────────┐
│ Sidebar│ Header: back link · Live indicator                  │
│ 256px  ├────────────────────────────────────────────────────┤
│        │ Global filters (8-column grid)                      │
│        ├────────────────────────────────────────────────────┤
│        │ KPI grid (5 columns)                                │
│        │ ┌──────────────────────┬─────────────────────────┐│
│        │ │ AI Priority (2/3)    │ AI Insights (1/3)       ││
│        │ └──────────────────────┴─────────────────────────┘│
│        │ Charts · Tables · Cluster cards                     │
└────────┴────────────────────────────────────────────────────┘

Tablet (768–1279px)
- Sidebar hidden; hamburger opens Sheet drawer
- KPI grid: 3 columns
- Charts: 2 columns

Mobile (<768px)
- Single column layout
- Filters stack vertically
- Tables horizontal scroll
- Drawers full-width
```

---

## API Endpoints

| Method | Path | Response |
|--------|------|----------|
| GET | `/api/v1/analytics/dashboard` | `DashboardHomeResponse` |
| GET | `/api/v1/analytics/activities?limit=100` | `DashboardActivitiesResponse` |
| GET | `/api/v1/analytics/overview` | `DashboardAnalyticsResponse` |

---

## Activity Event Types

| Type | Source |
|------|--------|
| `complaint_submitted` | `complaint.submitted_at` |
| `ai_analysis_completed` | `complaint.analysis_completed_at` |
| `image_analysis_completed` | `complaint.vision_completed_at` |
| `cluster_created` | `cluster.metadata.created_at` |
| `cluster_updated` | `cluster.metadata.updated_at` |
| `priority_updated` | `cluster.priority_updated_at` |

---

## Environment Variables

### Frontend (`frontend/.env`)
```
VITE_FIREBASE_PROJECT_ID=civiclens-ai-dev
VITE_FIREBASE_USE_EMULATOR=true
VITE_FIREBASE_EMULATOR_HOST=127.0.0.1
VITE_FIREBASE_EMULATOR_PORT=8085
```

### Backend
No new variables. Uses existing Firestore connection via `firebase-admin`.

---

## Running Phase 9

```powershell
# Terminal 1 — Firestore emulator
cd backend
npx firebase-tools emulators:start --only firestore --project civiclens-ai-dev

# Terminal 2 — API
cd backend
.\.venv\Scripts\python run.py

# Terminal 3 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173/dashboard**

---

## Ready for Phase 10

Phase 9 provides:
- ✅ Unified analytics API
- ✅ MP Command Center UI at `/dashboard`
- ✅ Real-time Firestore listeners
- ✅ KPI cards, charts, filters, drawers, activity timeline
- ✅ Integration with priority engine (Phase 8) and clustering (Phase 7)

Phase 10 can extend with: role-based MP access, constituency switching, export/PDF reports, push notifications, and departmental assignment workflows.

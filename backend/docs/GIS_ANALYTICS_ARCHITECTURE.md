# CivicLens AI — Phase 10 & 11: GIS + Analytics Intelligence Architecture

## Overview

Phases 10 and 11 transform CivicLens AI into a full **Government Decision Intelligence Platform** with:

- **Phase 10:** Interactive constituency GIS map at `/map`
- **Phase 11:** Constituency analytics intelligence at `/analytics`

Both modules extend Phases 1–9 without modifying existing pipelines.

---

## GIS Architecture (Phase 10)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MapPage (/map)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  MapFiltersPanel · MapControls · MapLegend                               │
│  ConstituencyMap (React Leaflet)                                         │
│    ├── OpenStreetMap TileLayer                                           │
│    ├── HeatmapLayer (leaflet.heat)                                       │
│    ├── ComplaintMarkers (leaflet.markercluster)                          │
│    └── ClusterMarkers                                                    │
│  MapPinDrawer · MapClusterDrawer                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  useGisMap() → GET /api/v1/gis/map                                       │
│  useGisRealtime() → Firestore onSnapshot → invalidate gis + analytics    │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  GisPortalService                                                        │
│    ComplaintRepository.list(500) → filter location != null               │
│    ClusterRepository.list(500) → filter coordinates != null              │
│    heat_weight from priority × severity × AI confidence                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Pin Color Strategy

| Condition | Color |
|-----------|-------|
| Resolved / Closed | Blue `#3b82f6` |
| Critical priority | Red `#ef4444` |
| High | Orange `#f97316` |
| Medium | Yellow `#eab308` |
| Low | Green `#22c55e` |

Color modes: `priority` (default), `severity`, `department` (hash-based palette).

### API

| Method | Path | Response |
|--------|------|----------|
| GET | `/api/v1/gis/map` | `GisMapResponse` |

---

## Analytics Architecture (Phase 11)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AnalyticsPage (/analytics)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  AnalyticsFiltersBar · AnalyticsExportToolbar                            │
│  AnalyticsKPIGrid (10 KPIs)                                              │
│  PredictiveAnalyticsPanel (7 AI-ready cards)                             │
│  AnalyticsChartsGrid (14 Recharts visualizations)                        │
├─────────────────────────────────────────────────────────────────────────┤
│  useAnalyticsIntelligence() → GET /api/v1/analytics/intelligence          │
│  Export: CSV · JSON · Print · PNG (html-to-image)                        │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AnalyticsIntelligenceService                                            │
│    Aggregates complaints + clusters from Firestore                       │
│    Builds 14 chart datasets + KPIs + predictive heuristics               │
│    export_rows for CSV download                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 14 Charts

1. Complaint Trend (Daily)
2. Complaint Trend (Weekly)
3. Complaint Trend (Monthly)
4. Complaint Categories
5. Department Distribution
6. Village Comparison
7. Priority Distribution
8. Severity Distribution
9. Cluster Size Distribution
10. Resolution Status
11. Top Villages
12. Top Departments
13. Complaint Timeline (cumulative)
14. AI Confidence Distribution

### Predictive Analytics Cards

Designed with `PredictiveAnalyticsCard` schema for future ML plug-in:

| Card | Heuristic Source |
|------|------------------|
| Trending Category | Category frequency counter |
| Fastest Growing Cluster | Max `complaint_count` |
| Highest Risk Village | Village complaint density |
| Department Workload | Department assignment counter |
| Predicted Growth | 7-day vs prior 7-day trend |
| Resolution Load | Open case count |
| Most Critical Area | AI priority risk clusters |

**Future AI integration:** Replace `AnalyticsIntelligenceService._build_predictive()` with a `PredictionEngine` interface; keep `PredictiveAnalytics` response shape unchanged.

---

## Firestore Query Strategy

| Service | Query | Limit |
|---------|-------|-------|
| GIS | `complaints` ordered by `submitted_at` DESC | 500 |
| GIS | `clusters` ordered by `complaint_count` DESC | 500 |
| Analytics | Same as GIS | 500 |
| Realtime | `onSnapshot(complaints, limit 1)` | 1 |
| Realtime | `onSnapshot(clusters, limit 1)` | 1 |

Client-side filtering applied for map/analytics filter bars (no extra Firestore indexes).

Geo filtering: only complaints with `location.latitude/longitude` and clusters with `coordinates` are mapped.

---

## Component Hierarchy

### GIS (`frontend/src/features/gis/`)

```
gis/
├── pages/MapPage.tsx
├── components/
│   ├── constituency-map.tsx
│   ├── heatmap-layer.tsx
│   ├── map-markers.tsx
│   ├── map-controls.tsx
│   ├── map-legend.tsx
│   ├── map-filters-panel.tsx
│   └── map-pin-drawer.tsx
├── hooks/use-gis-map.ts, use-gis-realtime.ts
├── lib/gis-api.ts, gis-filters.ts, map-utils.ts, leaflet-setup.ts
└── types/gis.ts
```

### Analytics (`frontend/src/features/analytics-intelligence/`)

```
analytics-intelligence/
├── pages/AnalyticsPage.tsx
├── components/
│   ├── analytics-kpi-grid.tsx
│   ├── analytics-charts-grid.tsx
│   ├── predictive-analytics-panel.tsx
│   ├── analytics-filters-bar.tsx
│   └── analytics-export-toolbar.tsx
├── hooks/use-analytics-intelligence.ts
├── lib/analytics-api.ts, export-utils.ts
└── types/analytics.ts
```

---

## State Management Flow

```
Firestore change
    → useGisRealtime() invalidateQueries
        → ["gis", "map"]
        → ["analytics-intelligence"]
        → ["dashboard"]

MapPage local state:
  filters, layers, selected pin/cluster, resetToken

AnalyticsPage local state:
  filters, dashboardRef for PNG export

Server state:
  TanStack Query with staleTime 30s (GIS) / 60s (analytics)
```

---

## Performance Optimization

| Technique | Implementation |
|-----------|----------------|
| Code splitting | Lazy routes for `/map` and `/analytics` |
| Backend cap | 500 documents per aggregation query |
| Memoization | `ConstituencyMap`, `AnalyticsChartsGrid` wrapped in `memo` |
| Marker clustering | `leaflet.markercluster` for complaint density |
| Heatmap | `leaflet.heat` with weighted points |
| Query cache | TanStack Query staleTime + Firestore invalidation |
| Leaflet icons | Vite-compatible default icon fix in `leaflet-setup.ts` |

---

## Future AI Prediction Integration

```python
# Pluggable prediction interface (future Phase 12+)
class PredictionEngine(Protocol):
    def predict(self, context: AnalyticsContext) -> PredictiveAnalytics: ...

# Current: HeuristicPredictionEngine in analytics_intelligence_service.py
# Future: GeminiPredictionEngine or ML model without API contract changes
```

Frontend `PredictiveAnalyticsCard.model_version` distinguishes heuristic vs future models.

---

## Routes

| Path | Module |
|------|--------|
| `/map` | Phase 10 GIS |
| `/analytics` | Phase 11 Analytics |
| `/dashboard/analytics` | Phase 9 MP dashboard charts (unchanged) |

---

## Running

```powershell
cd backend
npx firebase-tools emulators:start --only firestore --project civiclens-ai-dev
.\.venv\Scripts\python run.py

cd frontend
npm run dev
```

Open:
- http://localhost:5173/map
- http://localhost:5173/analytics

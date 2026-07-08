# CivicLens AI — Phase 5 AI Architecture

## Overview

Phase 5 adds an automatic Gemini 2.5 Flash analysis pipeline that enriches citizen complaints with structured civic intelligence immediately after submission.

## Architecture Diagram

```mermaid
flowchart TB
    subgraph Frontend
        Submit[Submit Complaint Page]
        Details[Complaint Details Page]
        Panel[AI Insights Panel]
    end

    subgraph API
        POST_CREATE[POST /api/v1/complaints]
        POST_ANALYZE[POST /api/v1/complaints/{id}/analyze]
        GET_DETAIL[GET /api/v1/complaints/{id}]
    end

    subgraph ServiceLayer
        CS[ComplaintService]
        AIS[ComplaintAIService]
        PB[PromptBuilder]
        RP[ResponseParser]
    end

    subgraph Gemini
        GM[Gemini 2.5 Flash]
    end

    subgraph Firestore
        FC[(complaints collection)]
    end

    Submit --> POST_CREATE --> CS
    CS --> FC
    CS --> AIS
    AIS --> PB
    PB --> GM
    GM --> RP
    RP --> AIS
    AIS --> FC
    GET_DETAIL --> Details --> Panel
    POST_ANALYZE --> CS --> AIS
    Details --> POST_ANALYZE
```

## Request / Response Flow

### 1. Complaint submission with auto-analysis

```
Citizen → POST /complaints
  → ComplaintService.create()
    → ComplaintRepository.create()        [status=pending, analysis_status=pending]
    → ComplaintAIService.analyze_if_needed()
      → mark analysis_status=processing
      → build prompt + multimodal parts (text, image, audio)
      → Gemini generate_content (JSON mode, retries up to 3)
      → parse + validate GeminiComplaintAnalysisOutput
      → map to ComplaintAIAnalysis
      → update complaint [ai_analysis, priority, status=under_review, analysis_status=completed]
  → ComplaintDetailResponse (includes ai_analysis)
```

### 2. Manual retry

```
UI Retry → POST /complaints/{id}/analyze?force=true
  → ComplaintService.analyze_complaint()
  → ComplaintAIService.analyze_complaint(force=True)
  → same pipeline, skips cache when force=true
```

### 3. Failure handling

```
Gemini/validation error
  → analysis_status=failed
  → analysis_error_message stored
  → original complaint preserved
  → UI shows failed state + Retry button
```

## Prompt Template (v1.0.0)

**System role:** Expert Government Civic Intelligence Officer analyzing citizen grievances for MP constituencies in India.

**Inputs:** title, description, user category, location, landmark, constituency context, optional image, optional audio.

**Rules:** strict JSON only, lowercase urgency/severity/priority, confidence 0–1, transcribe audio to `voice_transcript`, translate non-English to `translated_english`.

See `backend/app/services/ai/prompt_builder.py`.

## JSON Schema

Validated by `GeminiComplaintAnalysisOutput` in `backend/app/models/schemas/ai_complaint_analysis.py`:

| Field | Type |
|-------|------|
| category, sub_category | string |
| responsible_department | string |
| urgency, severity, priority_level | string |
| summary, detailed_explanation | string |
| keywords, tags | string[] |
| affected_infrastructure | string |
| affected_citizens_estimate | string \| null |
| government_scheme | string \| null |
| suggested_immediate_action, suggested_long_term_action | string |
| required_department, required_team | string |
| confidence_score, duplicate_possibility | float 0–1 |
| reasoning | string |
| language_detected | string |
| translated_english, voice_transcript | string \| null |
| sentiment | string |

## Firestore Document After Enrichment

```json
{
  "title": "...",
  "description": "...",
  "status": "under_review",
  "priority": "high",
  "analysis_status": "completed",
  "analysis_started_at": "2026-07-06T10:00:00Z",
  "analysis_completed_at": "2026-07-06T10:00:02Z",
  "analysis_model_name": "gemini-2.5-flash",
  "analysis_processing_time_ms": 1840,
  "analysis_prompt_version": "1.0.0",
  "analysis_retry_count": 1,
  "analysis_error_message": null,
  "ai_analysis": {
    "category": "Roads",
    "sub_category": "Potholes",
    "responsible_department": "Public Works Department",
    "urgency": "high",
    "severity": "high",
    "priority_level": "high",
    "summary": "...",
    "detailed_explanation": "...",
    "keywords": ["pothole", "road damage"],
    "confidence_score": 0.91,
    "duplicate_possibility": 0.12,
    "tags": ["infrastructure", "roads"],
    "language_detected": "hi",
    "translated_english": "...",
    "voice_transcript": "...",
    "sentiment": "negative",
    "urgency_score": 0.82,
    "processed_at": "2026-07-06T10:00:02Z",
    "model_version": "gemini-2.5-flash",
    "prompt_version": "1.0.0"
  }
}
```

## Future Phase Integration (no refactor required)

| Future Phase | Extension Point |
|--------------|-----------------|
| **Image intelligence** | `ComplaintAIService._build_content_parts()` already sends images; add dedicated vision pass or enrich prompt |
| **Duplicate detection** | `duplicate_possibility` field + `ai_analysis.keywords` indexed in Firestore; Phase 6 compares against existing complaints |
| **Clustering** | `cluster_id` field exists; cluster service reads `ai_analysis.keywords`, `tags`, `category` |
| **Priority scoring** | `urgency_score`, `priority_level` already mapped to `ComplaintPriority`; analytics aggregates scores |
| **Recommendations** | `RecommendationAIContent` model exists; recommendation service consumes complaint `ai_analysis` |
| **Background jobs** | `ComplaintAIService.analyze_complaint()` is isolated; swap sync call for queue worker without API changes |
| **Speech-to-text** | `voice_transcript` populated by Gemini today; dedicated STT service can pre-fill before analysis |

## Key Files

| Layer | Path |
|-------|------|
| AI service | `backend/app/services/ai/complaint_ai_service.py` |
| Prompt | `backend/app/services/ai/prompt_builder.py` |
| Parser | `backend/app/services/ai/response_parser.py` |
| Schema | `backend/app/models/schemas/ai_complaint_analysis.py` |
| Domain | `backend/app/models/domain/complaint.py` |
| API | `backend/app/api/v1/endpoints/complaints.py` |
| UI panel | `frontend/src/components/complaints/complaint-ai-insights-panel.tsx` |

## Configuration

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MAX_RETRIES=3
GEMINI_PROMPT_VERSION=1.0.0
AI_ANALYSIS_ENABLED=true
```

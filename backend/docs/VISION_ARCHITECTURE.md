# CivicLens AI — Phase 6: Image Intelligence Architecture

## Overview

Phase 6 adds a dedicated **Gemini Vision** pipeline that analyzes citizen-uploaded complaint photographs independently from Phase 5 text/multimodal AI analysis. Results are stored in Firestore as `image_analysis` and displayed in the **Image Intelligence** section on the Complaint Details page.

---

## Architecture Diagram

```mermaid
flowchart TB
    subgraph CitizenPortal["Citizen Portal (React)"]
        Submit[Submit Complaint + Image]
        Details[Complaint Details Page]
        ImagePanel[Image Intelligence Panel]
    end

    subgraph API["FastAPI"]
        CreateEP[POST /complaints]
        AnalyzeImageEP[POST /complaints/{id}/analyze-image]
        ComplaintSvc[ComplaintService]
    end

    subgraph VisionPipeline["Vision Pipeline"]
        VisionSvc[ImageVisionService]
        ImgProc[ImageProcessor]
        Prompt[VisionPromptBuilder]
        Parser[VisionResponseParser]
        Validator[GeminiImageAnalysisOutput Schema]
    end

    subgraph External["Google Cloud"]
        Gemini[Gemini 2.5 Flash Vision]
        Firestore[(Firestore)]
    end

    Submit --> CreateEP --> ComplaintSvc
    ComplaintSvc -->|save complaint| Firestore
    ComplaintSvc -->|if image present| VisionSvc
    AnalyzeImageEP --> ComplaintSvc --> VisionSvc

    VisionSvc --> ImgProc
    ImgProc -->|compressed base64| VisionSvc
    VisionSvc --> Prompt
    VisionSvc --> Gemini
    Gemini -->|strict JSON| Parser
    Parser --> Validator
    Validator -->|ComplaintImageAnalysis| Firestore

    Firestore --> Details --> ImagePanel
    ImagePanel -->|retry| AnalyzeImageEP
```

---

## Request / Response Flow

### Automatic flow (complaint creation)

```
1. Citizen submits complaint with image (JPG/PNG/WEBP)
2. ComplaintService.create() persists complaint to Firestore
   - image_analysis_status = "pending" (when image present)
3. Phase 5: ComplaintAIService.analyze_if_needed() (text/multimodal)
4. Phase 6: ImageVisionService.analyze_if_needed() (vision-only)
   a. Skip if image_analysis already completed
   b. Mark image_analysis_status = "processing"
   c. ImageProcessor.compress_image_base64()
   d. Build vision prompt + send image to Gemini
   e. Parse JSON → validate schema → retry up to GEMINI_MAX_RETRIES
   f. Persist image_analysis + metadata on success
   g. Mark image_analysis_status = "failed" on error (complaint preserved)
5. API returns ComplaintDetailResponse with image intelligence fields
```

### Manual retry flow

```
POST /api/v1/complaints/{id}/analyze-image?force=false

Response:
{
  "success": true,
  "message": "Image analysis completed",
  "complaint": { ... ComplaintDetailResponse ... }
}
```

---

## Prompt Template

**Role:** Expert Government Infrastructure Inspection Officer

**Location:** `backend/app/services/vision/vision_prompt_builder.py`

**Version:** `VISION_PROMPT_VERSION=1.0.0`

Key instructions:
- Analyze only visible evidence in the photograph
- Classify `primary_issue` from 16 supported civic types or `Unknown`
- Return strict JSON only (no markdown)
- Lower confidence when image is ambiguous
- Never hallucinate off-frame conditions

---

## JSON Schema

**Pydantic model:** `GeminiImageAnalysisOutput`  
**File:** `backend/app/models/schemas/ai_image_analysis.py`

```json
{
  "primary_issue": "Pothole | Broken Road | ... | Unknown",
  "secondary_issue": "string | null",
  "description": "string (10-3000 chars)",
  "severity": "Low | Medium | High | Critical",
  "confidence_score": 0.0,
  "visible_damage": "string",
  "estimated_area_affected": "string",
  "safety_risk": "string",
  "suggested_department": "string",
  "suggested_immediate_action": "string",
  "suggested_long_term_action": "string",
  "possible_public_impact": "string",
  "duplicate_indicators": ["string"],
  "detected_objects": ["string"],
  "environmental_risk": "string",
  "road_safety_risk": "string",
  "human_presence": false,
  "vehicles_present": false,
  "requires_urgent_attention": false,
  "reasoning": "string (10-3000 chars)"
}
```

**Validation:** Pydantic v2 strict validation + issue type normalization + JSON fence stripping + up to 3 retries with error feedback.

---

## Firestore Document Structure

Complaint document fields added in Phase 6:

```json
{
  "image_analysis": {
    "primary_issue": "Pothole",
    "secondary_issue": "Broken Road",
    "description": "...",
    "severity": "High",
    "confidence_score": 0.87,
    "visible_damage": "...",
    "estimated_area_affected": "...",
    "safety_risk": "...",
    "suggested_department": "Public Works Department",
    "suggested_immediate_action": "...",
    "suggested_long_term_action": "...",
    "possible_public_impact": "...",
    "duplicate_indicators": ["..."],
    "detected_objects": ["pothole", "asphalt"],
    "environmental_risk": "...",
    "road_safety_risk": "...",
    "human_presence": false,
    "vehicles_present": false,
    "requires_urgent_attention": true,
    "reasoning": "...",
    "processed_at": "2026-07-06T10:30:00Z",
    "model_version": "gemini-2.5-flash",
    "prompt_version": "1.0.0"
  },
  "image_analysis_status": "completed",
  "vision_model": "gemini-2.5-flash",
  "vision_processing_time_ms": 1842,
  "vision_completed_at": "2026-07-06T10:30:02Z",
  "vision_started_at": "2026-07-06T10:30:00Z",
  "vision_prompt_version": "1.0.0",
  "vision_error_message": null,
  "vision_retry_count": 1
}
```

**Status values:** `pending` | `processing` | `completed` | `failed` (reuses `AnalysisStatus` enum)

---

## Module Map

| Module | Path | Responsibility |
|--------|------|----------------|
| Image Processor | `services/vision/image_processor.py` | Format validation, resize, compress |
| Prompt Builder | `services/vision/vision_prompt_builder.py` | Production vision prompt |
| Response Parser | `services/vision/vision_response_parser.py` | JSON extract, validate, map |
| Vision Service | `services/vision/image_vision_service.py` | Orchestration, retry, Firestore |
| Schema | `models/schemas/ai_image_analysis.py` | Strict output contract |
| Domain | `models/domain/complaint.py` | `ComplaintImageAnalysis` model |
| API | `api/v1/endpoints/complaints.py` | `POST .../analyze-image` |
| UI | `complaint-image-intelligence-panel.tsx` | Image Intelligence display |

---

## Configuration

```env
VISION_ANALYSIS_ENABLED=true
VISION_PROMPT_VERSION=1.0.0
VISION_MAX_IMAGE_DIMENSION=1600
VISION_JPEG_QUALITY=85
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MAX_RETRIES=3
```

---

## Future Phase Integration (No Refactoring Required)

### Phase 7+ Duplicate Detection
- `image_analysis.duplicate_indicators` and `detected_objects` provide visual fingerprint signals
- `primary_issue` + `estimated_area_affected` can be compared with geospatial proximity
- Vision pipeline is independent; duplicate service reads `image_analysis` as input features

### Clustering
- Clustering jobs can aggregate by `primary_issue`, `detected_objects`, and location
- `image_analysis.confidence_score` weights cluster membership confidence
- No changes to vision service — clustering reads persisted `image_analysis`

### Priority Scoring
- `requires_urgent_attention`, `severity`, `road_safety_risk`, and `safety_risk` are ready-made scoring inputs
- Phase 5 `ai_analysis` and Phase 6 `image_analysis` can be fused in a future `PriorityScoringService`
- Both pipelines write to separate fields; fusion layer composes without modifying either pipeline

### Design principle
Each intelligence module writes to its own Firestore sub-document (`ai_analysis`, `image_analysis`). Downstream phases consume these as read-only features, enabling additive evolution without architectural changes.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid image format | `image_analysis_status=failed`, error message stored |
| Gemini invalid JSON | Retry up to 3x, then failed |
| Vision disabled | Skipped on create; API returns 400 on manual trigger |
| No image on complaint | Skipped silently / API 400 |
| Already analyzed | Skipped unless `force=true` |
| Complaint always preserved | Never deleted on vision failure |

---

## Supported Image Formats

- JPEG / JPG
- PNG
- WEBP

Images are compressed/resized before Gemini API call to reduce latency and token cost.

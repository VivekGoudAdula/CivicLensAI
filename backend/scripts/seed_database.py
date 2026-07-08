#!/usr/bin/env python3
"""Seed Firestore with realistic Indian constituency civic data for CivicLens AI."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings
from app.db.collections import CollectionNames
from app.models.domain.analytics import AnalyticsCreate, AnalyticsMetrics, VillageComplaintMetric
from app.models.domain.category import CategoryCreate
from app.models.domain.cluster import ClusterAIInsights, ClusterCreate, ClusterUpdate
from app.models.domain.complaint import ComplaintAIAnalysis, ComplaintCreate, ComplaintUpdate
from app.models.domain.department import DepartmentCreate
from app.models.domain.recommendation import RecommendationAIContent, RecommendationCreate
from app.models.domain.village import VillageCreate
from app.models.enums.common import (
    AnalysisStatus,
    AnalyticsReportType,
    ClusterStatus,
    ComplaintCategory,
    ComplaintPriority,
    ComplaintStatus,
    DepartmentCategory,
    RecommendationPriority,
    SentimentLabel,
)
from app.models.schemas.common import DocumentMetadataCreate, GeoLocation
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.village_repository import VillageRepository
from app.services.firebase import get_firestore_client, initialize_firebase, shutdown_firebase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger("seed_database")

CONSTITUENCY = "Amethi"
DISTRICT = "Amethi"
STATE = "Uttar Pradesh"
SEED_ACTOR = "civiclens-seed"


def clear_collection(db, collection_name: CollectionNames) -> int:
    """Delete all documents in a collection."""
    collection = db.collection(collection_name.value)
    deleted = 0
    for snapshot in collection.stream():
        snapshot.reference.delete()
        deleted += 1
    return deleted


CATEGORY_SEED_DATA: list[tuple[str, str, int, str]] = [
    ("Roads", "roads", 1, "Road damage, potholes, and street infrastructure"),
    ("Water", "water", 2, "Water supply, quality, and pipeline issues"),
    ("Garbage", "garbage", 3, "Waste collection and dumping complaints"),
    ("Street Lights", "street_lights", 4, "Non-functional or missing street lighting"),
    ("Drainage", "drainage", 5, "Blocked drains and waterlogging"),
    ("Healthcare", "healthcare", 6, "Public health facilities and services"),
    ("Education", "education", 7, "Schools, anganwadis, and education services"),
    ("Public Transport", "public_transport", 8, "Bus stops, routes, and transport access"),
    ("Environment", "environment", 9, "Pollution, trees, and environmental concerns"),
    ("Other", "other", 10, "Other civic issues not listed above"),
]


def seed_categories(repo: CategoryRepository) -> dict[str, str]:
    """Seed complaint categories and return slug-to-id mapping."""
    slug_to_id: dict[str, str] = {}
    for name, slug, display_order, description in CATEGORY_SEED_DATA:
        doc_id = f"category_{slug}"
        existing = repo.get_by_id(doc_id)
        if existing:
            slug_to_id[slug] = existing.id
            continue
        created = repo.create(
            CategoryCreate(
                name=name,
                slug=slug,
                description=description,
                display_order=display_order,
                is_active=True,
                metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
            ),
            document_id=doc_id,
        )
        slug_to_id[slug] = created.id
    logger.info("Seeded %d categories", len(slug_to_id))
    return slug_to_id


def seed_villages(repo: VillageRepository) -> dict[str, str]:
    """Seed village documents and return name-to-id mapping."""
    villages = [
        VillageCreate(
            name="Jagdishpur",
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            block="Jagdishpur",
            pin_code="227809",
            population=12450,
            geo=GeoLocation(latitude=26.4672, longitude=81.5234, address="Jagdishpur, Amethi"),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        VillageCreate(
            name="Bhadar",
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            block="Tiloi",
            pin_code="229309",
            population=8320,
            geo=GeoLocation(latitude=26.3128, longitude=81.6412, address="Bhadar, Amethi"),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        VillageCreate(
            name="Semari",
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            block="Musafirkhana",
            pin_code="227813",
            population=6780,
            geo=GeoLocation(latitude=26.3891, longitude=81.4987, address="Semari, Amethi"),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        VillageCreate(
            name="Musafirkhana",
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            block="Musafirkhana",
            pin_code="227813",
            population=15620,
            geo=GeoLocation(latitude=26.3745, longitude=81.5123, address="Musafirkhana, Amethi"),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        VillageCreate(
            name="Singhpur",
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            block="Gauriganj",
            pin_code="227409",
            population=9450,
            geo=GeoLocation(latitude=26.2012, longitude=81.6891, address="Singhpur, Amethi"),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        VillageCreate(
            name="Tiloi",
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            block="Tiloi",
            pin_code="229309",
            population=11230,
            geo=GeoLocation(latitude=26.2987, longitude=81.6234, address="Tiloi, Amethi"),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
    ]

    ids: dict[str, str] = {}
    document_ids = [
        "village_jagdishpur",
        "village_bhadar",
        "village_semari",
        "village_musafirkhana",
        "village_singhpur",
        "village_tiloi",
    ]
    for village, doc_id in zip(villages, document_ids, strict=True):
        created = repo.create(village, document_id=doc_id)
        ids[village.name] = created.id
        logger.info("Seeded village: %s (%s)", village.name, created.id)
    return ids


def seed_departments(repo: DepartmentRepository) -> dict[str, str]:
    """Seed department documents and return code-to-id mapping."""
    departments = [
        DepartmentCreate(
            name="Public Works Department",
            code="PWD",
            category=DepartmentCategory.INFRASTRUCTURE,
            description="Responsible for roads, bridges, and rural infrastructure in Amethi constituency.",
            head_name="Shri Rajesh Kumar Yadav",
            contact_email="pwd.amethi@up.gov.in",
            contact_phone="+919415678901",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        DepartmentCreate(
            name="Jal Nigam (Water Board)",
            code="JAL_NIGAM",
            category=DepartmentCategory.WATER,
            description="Manages drinking water supply and pipeline infrastructure.",
            head_name="Smt. Priya Sharma",
            contact_email="jal.amethi@up.gov.in",
            contact_phone="+919876543210",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        DepartmentCreate(
            name="District Health Department",
            code="HEALTH",
            category=DepartmentCategory.HEALTH,
            description="Oversees PHCs, sub-centres, and rural health programmes.",
            head_name="Dr. Anil Verma",
            contact_email="health.amethi@up.gov.in",
            contact_phone="+919012345678",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        DepartmentCreate(
            name="Basic Education Department",
            code="EDUCATION",
            category=DepartmentCategory.EDUCATION,
            description="Manages government schools and education infrastructure.",
            head_name="Shri Mohan Tiwari",
            contact_email="education.amethi@up.gov.in",
            contact_phone="+919532167890",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        DepartmentCreate(
            name="Municipal Sanitation Board",
            code="SANITATION",
            category=DepartmentCategory.SANITATION,
            description="Handles waste management, drainage, and Swachh Bharat initiatives.",
            head_name="Shri Sunil Pandey",
            contact_email="sanitation.amethi@up.gov.in",
            contact_phone="+919718263540",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        DepartmentCreate(
            name="Electricity Distribution Division",
            code="ELECTRICITY",
            category=DepartmentCategory.ELECTRICITY,
            description="UP Power Corporation Ltd. division for Amethi rural electrification.",
            head_name="Shri Vikram Singh",
            contact_email="electricity.amethi@up.gov.in",
            contact_phone="+919005432187",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
        DepartmentCreate(
            name="Rural Development Authority",
            code="RURAL_DEV",
            category=DepartmentCategory.RURAL_DEVELOPMENT,
            description="Coordinates MNREGA, housing schemes, and village development projects.",
            head_name="Smt. Kavita Mishra",
            contact_email="ruraldev.amethi@up.gov.in",
            contact_phone="+919831245670",
            constituency=CONSTITUENCY,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        ),
    ]

    ids: dict[str, str] = {}
    document_ids = [
        "dept_pwd",
        "dept_jal_nigam",
        "dept_health",
        "dept_education",
        "dept_sanitation",
        "dept_electricity",
        "dept_rural_dev",
    ]
    for department, doc_id in zip(departments, document_ids, strict=True):
        created = repo.create(department, document_id=doc_id)
        ids[department.code] = created.id
        logger.info("Seeded department: %s (%s)", department.name, created.id)
    return ids


def seed_complaints(
    repo: ComplaintRepository,
    village_ids: dict[str, str],
) -> list[str]:
    """Seed complaint documents."""
    now = datetime.now(UTC)
    complaints_data = [
        {
            "id": "complaint_road_jagdishpur",
            "title": "Main road to Jagdishpur market is damaged",
            "description": (
                "The connecting road from NH-330 to Jagdishpur haat has large potholes "
                "and broken patches for over 6 months. Farmers cannot transport produce "
                "and school buses are frequently stuck during monsoon."
            ),
            "category": ComplaintCategory.ROADS,
            "priority": ComplaintPriority.HIGH,
            "village": "Jagdishpur",
            "citizen_name": "Ram Prasad Maurya",
            "citizen_phone": "+919415670012",
            "keywords": ["road", "pothole", "jagdishpur", "infrastructure"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.82,
            "days_ago": 45,
        },
        {
            "id": "complaint_road_bhadar",
            "title": "Unmetalled village road in Bhadar needs repair",
            "description": (
                "Bhadar to Tiloi link road has no blacktop and becomes unusable after rain. "
                "Multiple accidents reported near the primary school crossing."
            ),
            "category": ComplaintCategory.ROADS,
            "priority": ComplaintPriority.HIGH,
            "village": "Bhadar",
            "citizen_name": "Sunita Devi",
            "citizen_phone": "+919876540321",
            "keywords": ["road", "bhadar", "tiloi", "accident"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.78,
            "days_ago": 38,
        },
        {
            "id": "complaint_water_semari",
            "title": "No drinking water supply in Semari ward 3",
            "description": (
                "Hand pumps in Semari ward 3 have run dry. Pipeline from overhead tank "
                "was promised under Jal Jeevan Mission but work has not started."
            ),
            "category": ComplaintCategory.WATER,
            "priority": ComplaintPriority.CRITICAL,
            "village": "Semari",
            "citizen_name": "Ashok Kumar",
            "citizen_phone": "+919012340987",
            "keywords": ["water", "handpump", "jal jeevan", "semari"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.91,
            "days_ago": 22,
        },
        {
            "id": "complaint_water_musafirkhana",
            "title": "Contaminated tap water in Musafirkhana bazaar",
            "description": (
                "Residents report foul smell and discoloration in municipal tap water near "
                "the main bazaar. Several children fell ill last week."
            ),
            "category": ComplaintCategory.WATER,
            "priority": ComplaintPriority.CRITICAL,
            "village": "Musafirkhana",
            "citizen_name": "Fatima Begum",
            "citizen_phone": "+919718260011",
            "keywords": ["water", "contamination", "musafirkhana", "health"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.95,
            "days_ago": 8,
        },
        {
            "id": "complaint_health_singhpur",
            "title": "PHC Singhpur lacks doctors and medicines",
            "description": (
                "Primary Health Centre at Singhpur has only one nurse on duty. Essential "
                "medicines for fever and diabetes are out of stock for 3 weeks."
            ),
            "category": ComplaintCategory.HEALTH,
            "priority": ComplaintPriority.HIGH,
            "village": "Singhpur",
            "citizen_name": "Dr. Ramesh Patel",
            "citizen_phone": "+919532160045",
            "keywords": ["phc", "medicine", "singhpur", "doctor"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.85,
            "days_ago": 30,
        },
        {
            "id": "complaint_education_tiloi",
            "title": "Tiloi primary school building is unsafe",
            "description": (
                "Roof of Government Primary School Tiloi leaks during rain. Classroom "
                "ceiling plaster has fallen in two rooms. 180 students at risk."
            ),
            "category": ComplaintCategory.EDUCATION,
            "priority": ComplaintPriority.HIGH,
            "village": "Tiloi",
            "citizen_name": "Geeta Singh",
            "citizen_phone": "+919831240099",
            "keywords": ["school", "building", "tiloi", "education"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.80,
            "days_ago": 25,
        },
        {
            "id": "complaint_sanitation_jagdishpur",
            "title": "Open garbage dumping near Jagdishpur pond",
            "description": (
                "Municipal waste is being dumped near the community pond causing mosquito "
                "breeding and foul odour. No door-to-door collection in the ward."
            ),
            "category": ComplaintCategory.SANITATION,
            "priority": ComplaintPriority.MEDIUM,
            "village": "Jagdishpur",
            "citizen_name": "Munna Lal",
            "citizen_phone": "+919005431122",
            "keywords": ["garbage", "sanitation", "jagdishpur", "pond"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.65,
            "days_ago": 18,
        },
        {
            "id": "complaint_electricity_bhadar",
            "title": "Frequent power cuts in Bhadar during peak hours",
            "description": (
                "Bhadar village experiences 8-10 hour daily power cuts affecting irrigation "
                "pumps and students preparing for board exams."
            ),
            "category": ComplaintCategory.ELECTRICITY,
            "priority": ComplaintPriority.MEDIUM,
            "village": "Bhadar",
            "citizen_name": "Vijay Yadav",
            "citizen_phone": "+919415678234",
            "keywords": ["electricity", "power cut", "bhadar", "irrigation"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.70,
            "days_ago": 12,
        },
        {
            "id": "complaint_corruption_musafirkhana",
            "title": "MNREGA wage delay and middleman exploitation",
            "description": (
                "Workers in Musafirkhana report MNREGA wages delayed by 4 months. Local "
                "contractor demands commission for job card entries."
            ),
            "category": ComplaintCategory.CORRUPTION,
            "priority": ComplaintPriority.HIGH,
            "village": "Musafirkhana",
            "citizen_name": "Phoolchand",
            "citizen_phone": "+919876541200",
            "keywords": ["mnrega", "corruption", "wage", "musafirkhana"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.88,
            "days_ago": 40,
        },
        {
            "id": "complaint_employment_semari",
            "title": "Youth employment centre closed in Semari",
            "description": (
                "Rozgar Sewa Kendra in Semari has been closed for 2 months with no notice. "
                "Unemployed youth cannot access skill training programmes."
            ),
            "category": ComplaintCategory.EMPLOYMENT,
            "priority": ComplaintPriority.MEDIUM,
            "village": "Semari",
            "citizen_name": "Ajay Pratap",
            "citizen_phone": "+919012345011",
            "keywords": ["employment", "rozgar", "semari", "youth"],
            "sentiment": SentimentLabel.NEGATIVE,
            "urgency": 0.55,
            "days_ago": 55,
        },
    ]

    complaint_ids: list[str] = []
    for item in complaints_data:
        village_name = item["village"]
        village_id = village_ids[village_name]
        submitted_at = now - timedelta(days=item["days_ago"])
        complaint = ComplaintCreate(
            title=item["title"],
            description=item["description"],
            category=item["category"],
            priority=item["priority"],
            village_id=village_id,
            village_name=village_name,
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            citizen_name=item["citizen_name"],
            citizen_phone=item["citizen_phone"],
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        )
        created = repo.create(complaint, document_id=item["id"])
        repo.update(
            created.id,
            ComplaintUpdate(
                ai_analysis=ComplaintAIAnalysis(
                    category=item.get("category", "roads"),
                    sub_category=item.get("sub_category", "surface damage"),
                    responsible_department="Public Works Department",
                    urgency="high" if item["urgency"] >= 0.7 else "medium",
                    severity="high" if item["urgency"] >= 0.8 else "medium",
                    priority_level="high" if item["urgency"] >= 0.7 else "medium",
                    summary=f"AI summary: {item['title']}",
                    detailed_explanation=item["description"],
                    keywords=item["keywords"],
                    affected_infrastructure="Local road network",
                    suggested_immediate_action="Dispatch inspection team",
                    suggested_long_term_action="Plan permanent repair works",
                    required_department="Public Works Department",
                    required_team="Road maintenance unit",
                    confidence_score=0.85,
                    reasoning="Seeded demo analysis for hackathon dataset.",
                    duplicate_possibility=0.1,
                    tags=item["keywords"][:3],
                    language_detected="hi",
                    sentiment=item["sentiment"],
                    urgency_score=item["urgency"],
                    language="hi",
                    processed_at=submitted_at + timedelta(hours=2),
                ),
                analysis_status=AnalysisStatus.COMPLETED,
                analysis_model_name="gemini-2.5-flash",
                analysis_prompt_version="1.0.0",
                analysis_processing_time_ms=1200,
                updated_by=SEED_ACTOR,
            ),
        )
        complaint_ids.append(created.id)
        logger.info("Seeded complaint: %s", created.id)

    return complaint_ids


def seed_clusters(
    repo: ClusterRepository,
    complaint_ids: dict[str, list[str]],
    village_ids: dict[str, str],
) -> dict[str, str]:
    """Seed cluster documents."""
    now = datetime.now(UTC)
    clusters_spec = [
        {
            "id": "cluster_rural_roads",
            "title": "Rural Road Infrastructure Failure — Jagdishpur & Bhadar",
            "description": (
                "Cluster of road-related complaints across Jagdishpur and Bhadar blocks "
                "indicating systemic neglect of rural connectivity infrastructure."
            ),
            "theme": "Rural road connectivity",
            "category": ComplaintCategory.ROADS,
            "complaint_ids": complaint_ids["roads"],
            "village_ids": [village_ids["Jagdishpur"], village_ids["Bhadar"]],
        },
        {
            "id": "cluster_water_crisis",
            "title": "Drinking Water Crisis — Semari & Musafirkhana",
            "description": (
                "Water supply and quality complaints indicating urgent need for Jal Jeevan "
                "Mission acceleration and water quality testing in Amethi rural blocks."
            ),
            "theme": "Drinking water access and quality",
            "category": ComplaintCategory.WATER,
            "complaint_ids": complaint_ids["water"],
            "village_ids": [village_ids["Semari"], village_ids["Musafirkhana"]],
        },
        {
            "id": "cluster_public_services",
            "title": "Public Service Delivery Gaps — Health, Education & Sanitation",
            "description": (
                "Cross-sector cluster covering healthcare, education infrastructure, and "
                "sanitation failures affecting quality of life in Amethi villages."
            ),
            "theme": "Public service delivery",
            "category": ComplaintCategory.HEALTH,
            "complaint_ids": complaint_ids["services"],
            "village_ids": [
                village_ids["Singhpur"],
                village_ids["Tiloi"],
                village_ids["Jagdishpur"],
            ],
        },
    ]

    cluster_ids: dict[str, str] = {}
    for spec in clusters_spec:
        cluster = ClusterCreate(
            title=spec["title"],
            description=spec["description"],
            theme=spec["theme"],
            category=spec["category"],
            complaint_ids=spec["complaint_ids"],
            village_ids=spec["village_ids"],
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        )
        created = repo.create(cluster, document_id=spec["id"])
        repo.update(
            created.id,
            ClusterUpdate(
                ai_insights=ClusterAIInsights(
                    summary=spec["description"][:500],
                    root_causes=[
                        "Underfunded rural infrastructure budgets",
                        "Delayed contractor payments",
                        "Lack of citizen feedback loops",
                    ],
                    affected_population_estimate=35000,
                    priority_score=0.87,
                    key_themes=[spec["theme"], CONSTITUENCY, "rural development"],
                    generated_at=now,
                ),
                status=ClusterStatus.ANALYZING,
                updated_by=SEED_ACTOR,
            ),
        )
        cluster_ids[spec["id"]] = created.id
        logger.info("Seeded cluster: %s", created.id)

    return cluster_ids


def seed_recommendations(
    repo: RecommendationRepository,
    cluster_ids: dict[str, str],
    department_ids: dict[str, str],
    village_ids: dict[str, str],
) -> list[str]:
    """Seed recommendation documents."""
    now = datetime.now(UTC)
    recommendations_spec = [
        {
            "id": "rec_road_repair_pwd",
            "title": "Emergency resurfacing of Jagdishpur-Bhadar rural roads",
            "description": (
                "Approve immediate resurfacing of 12 km rural road network connecting "
                "Jagdishpur haat and Bhadar-Tiloi link under PWD emergency fund."
            ),
            "priority": RecommendationPriority.URGENT,
            "cluster_id": cluster_ids["cluster_rural_roads"],
            "department_code": "PWD",
            "department_name": "Public Works Department",
            "village_ids": [village_ids["Jagdishpur"], village_ids["Bhadar"]],
            "budget": 2450000.0,
            "timeline": 45,
            "official": "Executive Engineer, PWD Amethi",
        },
        {
            "id": "rec_jal_jeevan_semari",
            "title": "Accelerate Jal Jeevan Mission pipeline for Semari",
            "description": (
                "Fast-track overhead tank and pipeline installation for Semari ward 3 with "
                "weekly progress reporting to constituency office."
            ),
            "priority": RecommendationPriority.URGENT,
            "cluster_id": cluster_ids["cluster_water_crisis"],
            "department_code": "JAL_NIGAM",
            "department_name": "Jal Nigam (Water Board)",
            "village_ids": [village_ids["Semari"], village_ids["Musafirkhana"]],
            "budget": 1800000.0,
            "timeline": 60,
            "official": "Superintending Engineer, Jal Nigam",
        },
        {
            "id": "rec_water_quality",
            "title": "Water quality audit and tank cleaning — Musafirkhana",
            "description": (
                "Conduct immediate water quality testing, clean overhead tanks, and install "
                "chlorination units in Musafirkhana bazaar area."
            ),
            "priority": RecommendationPriority.HIGH,
            "cluster_id": cluster_ids["cluster_water_crisis"],
            "department_code": "HEALTH",
            "department_name": "District Health Department",
            "village_ids": [village_ids["Musafirkhana"]],
            "budget": 350000.0,
            "timeline": 14,
            "official": "CMO, Amethi District",
        },
        {
            "id": "rec_phc_singhpur",
            "title": "Staff augmentation and medicine stock at PHC Singhpur",
            "description": (
                "Deploy one additional doctor and ensure essential medicine stock at PHC "
                "Singhpur with fortnightly supply chain monitoring."
            ),
            "priority": RecommendationPriority.HIGH,
            "cluster_id": cluster_ids["cluster_public_services"],
            "department_code": "HEALTH",
            "department_name": "District Health Department",
            "village_ids": [village_ids["Singhpur"]],
            "budget": 520000.0,
            "timeline": 21,
            "official": "District Medical Officer",
        },
        {
            "id": "rec_school_tiloi",
            "title": "Urgent school building repair — GPS Tiloi",
            "description": (
                "Structural assessment and roof repair of Government Primary School Tiloi "
                "before monsoon season with temporary classroom arrangement."
            ),
            "priority": RecommendationPriority.HIGH,
            "cluster_id": cluster_ids["cluster_public_services"],
            "department_code": "EDUCATION",
            "department_name": "Basic Education Department",
            "village_ids": [village_ids["Tiloi"]],
            "budget": 890000.0,
            "timeline": 30,
            "official": "BSA, Amethi",
        },
    ]

    recommendation_ids: list[str] = []
    for spec in recommendations_spec:
        dept_code = spec["department_code"]
        recommendation = RecommendationCreate(
            title=spec["title"],
            description=spec["description"],
            priority=spec["priority"],
            cluster_ids=[spec["cluster_id"]],
            department_id=department_ids[dept_code],
            department_name=spec["department_name"],
            department_code=dept_code,
            village_ids=spec["village_ids"],
            constituency=CONSTITUENCY,
            district=DISTRICT,
            state=STATE,
            estimated_budget_inr=spec["budget"],
            estimated_timeline_days=spec["timeline"],
            assigned_official=spec["official"],
            due_date=now + timedelta(days=spec["timeline"]),
            ai_recommendation=RecommendationAIContent(
                rationale=(
                    f"AI analysis supports immediate action based on cluster severity "
                    f"and citizen impact in {CONSTITUENCY} constituency."
                ),
                action_items=[
                    "Conduct site inspection within 72 hours",
                    "Allocate budget from constituency development fund",
                    "Publish progress dashboard for citizens",
                    "Set up weekly review with department head",
                ],
                expected_impact="Improved service delivery for 15,000+ affected residents",
                risk_assessment="Moderate — contractor availability during monsoon season",
                confidence_score=0.89,
                generated_at=now,
            ),
            metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
        )
        created = repo.create(recommendation, document_id=spec["id"])
        recommendation_ids.append(created.id)
        logger.info("Seeded recommendation: %s", created.id)

    return recommendation_ids


def seed_analytics(repo: AnalyticsRepository, department_ids: dict[str, str]) -> list[str]:
    """Seed analytics documents."""
    now = datetime.now(UTC)
    period_start = now - timedelta(days=90)
    period_end = now

    constituency_metrics = AnalyticsMetrics(
        total_complaints=10,
        resolved_complaints=0,
        pending_complaints=10,
        rejected_complaints=0,
        average_resolution_days=0.0,
        complaints_by_category={
            "roads": 2,
            "water": 2,
            "health": 1,
            "education": 1,
            "sanitation": 1,
            "electricity": 1,
            "corruption": 1,
            "employment": 1,
        },
        complaints_by_status={
            "submitted": 10,
        },
        complaints_by_priority={
            "critical": 2,
            "high": 5,
            "medium": 3,
        },
        top_villages=[
            VillageComplaintMetric(village_id="village_jagdishpur", village_name="Jagdishpur", count=2),
            VillageComplaintMetric(village_id="village_bhadar", village_name="Bhadar", count=2),
            VillageComplaintMetric(village_id="village_semari", village_name="Semari", count=2),
            VillageComplaintMetric(village_id="village_musafirkhana", village_name="Musafirkhana", count=2),
            VillageComplaintMetric(village_id="village_singhpur", village_name="Singhpur", count=1),
            VillageComplaintMetric(village_id="village_tiloi", village_name="Tiloi", count=1),
        ],
        cluster_count=3,
        open_cluster_count=3,
        recommendation_count=5,
        active_recommendation_count=5,
        ai_sentiment_distribution={
            "negative": 10,
            "neutral": 0,
            "positive": 0,
        },
        department_workload={
            department_ids["PWD"]: 1,
            department_ids["JAL_NIGAM"]: 1,
            department_ids["HEALTH"]: 2,
            department_ids["EDUCATION"]: 1,
        },
    )

    constituency_report = AnalyticsCreate(
        report_type=AnalyticsReportType.CONSTITUENCY_SNAPSHOT,
        period_start=period_start,
        period_end=period_end,
        constituency=CONSTITUENCY,
        district=DISTRICT,
        state=STATE,
        metrics=constituency_metrics,
        source_complaint_count=10,
        source_recommendation_count=5,
        metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
    )
    created_snapshot = repo.create(
        constituency_report,
        document_id="analytics_constituency_snapshot_q1",
    )
    logger.info("Seeded analytics: %s", created_snapshot.id)

    dept_metrics = AnalyticsMetrics(
        total_complaints=2,
        resolved_complaints=0,
        pending_complaints=2,
        complaints_by_category={"water": 2},
        complaints_by_status={"submitted": 2},
        complaints_by_priority={"critical": 2},
        recommendation_count=2,
        active_recommendation_count=2,
        department_workload={department_ids["JAL_NIGAM"]: 2},
    )
    dept_report = AnalyticsCreate(
        report_type=AnalyticsReportType.DEPARTMENT_PERFORMANCE,
        period_start=period_start,
        period_end=period_end,
        constituency=CONSTITUENCY,
        district=DISTRICT,
        state=STATE,
        department_id=department_ids["JAL_NIGAM"],
        metrics=dept_metrics,
        source_complaint_count=2,
        source_recommendation_count=2,
        metadata=DocumentMetadataCreate(created_by=SEED_ACTOR, updated_by=SEED_ACTOR),
    )
    created_dept = repo.create(dept_report, document_id="analytics_jal_nigam_performance")
    logger.info("Seeded analytics: %s", created_dept.id)

    return [created_snapshot.id, created_dept.id]


def link_complaints_to_clusters(
    complaint_repo: ComplaintRepository,
    cluster_mapping: dict[str, list[str]],
) -> None:
    """Assign cluster references to complaints."""
    for cluster_id, complaint_id_list in cluster_mapping.items():
        for complaint_id in complaint_id_list:
            complaint_repo.update(
                complaint_id,
                ComplaintUpdate(
                    cluster_id=cluster_id,
                    status=ComplaintStatus.CLUSTERED,
                    updated_by=SEED_ACTOR,
                ),
            )


def update_village_counts(
    village_repo: VillageRepository,
    village_complaint_counts: dict[str, tuple[int, int]],
) -> None:
    """Update denormalized complaint counts on villages."""
    for village_name, (total, open_count) in village_complaint_counts.items():
        village_id = f"village_{village_name.lower()}"
        doc_ref = village_repo.collection.document(village_id)
        doc_ref.update(
            {
                "complaint_count": total,
                "open_complaint_count": open_count,
            }
        )


def update_department_counts(
    department_repo: DepartmentRepository,
    counts: dict[str, tuple[int, int]],
) -> None:
    """Update denormalized recommendation counts on departments."""
    for dept_id, (assigned, active) in counts.items():
        doc_ref = department_repo.collection.document(dept_id)
        doc_ref.update(
            {
                "assigned_recommendation_count": assigned,
                "active_recommendation_count": active,
            }
        )


def update_cluster_recommendations(
    cluster_repo: ClusterRepository,
    cluster_recommendations: dict[str, list[str]],
) -> None:
    """Link recommendations to clusters."""
    for cluster_id, recommendation_id_list in cluster_recommendations.items():
        doc_ref = cluster_repo.collection.document(cluster_id)
        doc_ref.update({"recommendation_ids": recommendation_id_list})


def run_seed(*, clear: bool = False) -> None:
    """Execute the full database seeding pipeline."""
    settings = get_settings()
    db = initialize_firebase(settings)

    if clear:
        logger.info("Clearing existing seed collections...")
        for collection in CollectionNames:
            deleted = clear_collection(db, collection)
            logger.info("Cleared %s: %d documents", collection.value, deleted)

    village_repo = VillageRepository(db)
    department_repo = DepartmentRepository(db)
    category_repo = CategoryRepository(db)
    complaint_repo = ComplaintRepository(db)
    cluster_repo = ClusterRepository(db)
    recommendation_repo = RecommendationRepository(db)
    analytics_repo = AnalyticsRepository(db)

    village_ids = seed_villages(village_repo)
    department_ids = seed_departments(department_repo)
    category_ids = seed_categories(category_repo)

    complaint_ids_list = seed_complaints(complaint_repo, village_ids)

    roads_complaints = ["complaint_road_jagdishpur", "complaint_road_bhadar"]
    water_complaints = ["complaint_water_semari", "complaint_water_musafirkhana"]
    services_complaints = [
        "complaint_health_singhpur",
        "complaint_education_tiloi",
        "complaint_sanitation_jagdishpur",
    ]
    complaint_groups = {
        "roads": roads_complaints,
        "water": water_complaints,
        "services": services_complaints,
    }

    cluster_ids = seed_clusters(cluster_repo, complaint_groups, village_ids)

    link_complaints_to_clusters(
        complaint_repo,
        {
            cluster_ids["cluster_rural_roads"]: roads_complaints,
            cluster_ids["cluster_water_crisis"]: water_complaints,
            cluster_ids["cluster_public_services"]: services_complaints,
        },
    )

    recommendation_ids = seed_recommendations(
        recommendation_repo,
        cluster_ids,
        department_ids,
        village_ids,
    )

    update_cluster_recommendations(
        cluster_repo,
        {
            cluster_ids["cluster_rural_roads"]: ["rec_road_repair_pwd"],
            cluster_ids["cluster_water_crisis"]: ["rec_jal_jeevan_semari", "rec_water_quality"],
            cluster_ids["cluster_public_services"]: ["rec_phc_singhpur", "rec_school_tiloi"],
        },
    )

    seed_analytics(analytics_repo, department_ids)

    village_counts = {
        "Jagdishpur": (2, 2),
        "Bhadar": (2, 2),
        "Semari": (2, 2),
        "Musafirkhana": (2, 2),
        "Singhpur": (1, 1),
        "Tiloi": (1, 1),
    }
    update_village_counts(village_repo, village_counts)

    dept_counts = {
        department_ids["PWD"]: (1, 1),
        department_ids["JAL_NIGAM"]: (1, 1),
        department_ids["HEALTH"]: (2, 2),
        department_ids["EDUCATION"]: (1, 1),
    }
    update_department_counts(department_repo, dept_counts)

    logger.info("Seed completed successfully.")
    logger.info("Villages: %d", len(village_ids))
    logger.info("Departments: %d", len(department_ids))
    logger.info("Categories: %d", len(category_ids))
    logger.info("Complaints: %d", len(complaint_ids_list))
    logger.info("Clusters: %d", len(cluster_ids))
    logger.info("Recommendations: %d", len(recommendation_ids))

    shutdown_firebase()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed CivicLens AI Firestore database")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all seed collections before inserting data",
    )
    args = parser.parse_args()
    run_seed(clear=args.clear)


if __name__ == "__main__":
    main()

<div align="center">

# CivicLens AI

### AI-Powered Constituency Intelligence Platform for Members of Parliament

Transforming scattered citizen complaints into explainable, AI-driven governance decisions using Google AI.

Built for **Google Cloud – Build with AI: Code for Communities 2026**

---

![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![Firebase](https://img.shields.io/badge/Firebase-Enabled-FFCA28?style=for-the-badge&logo=firebase)
![Google Gemini](https://img.shields.io/badge/Google-Gemini-blue?style=for-the-badge&logo=google)
![Google Maps](https://img.shields.io/badge/Google-Maps-4285F4?style=for-the-badge&logo=googlemaps)
![Firestore](https://img.shields.io/badge/Firestore-NoSQL-orange?style=for-the-badge)

</div>

---

# Problem Statement

Members of Parliament receive hundreds of development requests every day through:

- Public meetings
- WhatsApp
- Social media
- Phone calls
- Grievance portals
- Paper applications

These complaints are:

- Unstructured
- Frequently duplicated
- Difficult to prioritize
- Distributed across multiple platforms
- Impossible to analyze manually at scale

As a result, there is no intelligent system capable of answering questions like:

- Which issue affects the largest number of citizens?
- Which department should respond?
- Which complaints are duplicates?
- What should the MP prioritize today?

---

# Solution

CivicLens AI is an AI-powered Constituency Decision Intelligence Platform.

Instead of simply storing complaints, the platform automatically:

- Understands complaints using Google Gemini
- Analyzes uploaded images
- Detects duplicate complaints
- Creates intelligent complaint clusters
- Calculates AI priority scores
- Generates actionable recommendations
- Visualizes hotspots on GIS maps
- Provides real-time constituency analytics
- Helps MPs make data-driven development decisions

---

# Key Features

## Citizen Portal

- No login required
- Submit civic complaints
- GPS location picker
- Image upload
- Voice recording
- Anonymous reporting
- Complaint tracking

---

## AI Complaint Intelligence

Powered by Google Gemini

Automatically extracts:

- Category
- Department
- Summary
- Keywords
- Severity
- Urgency
- Suggested Action
- Confidence Score

---

## AI Image Intelligence

Gemini Vision analyzes uploaded images.

Detects:

- Potholes
- Garbage
- Water leakage
- Broken streetlights
- Encroachment
- Pollution
- Infrastructure damage

Returns:

- Description
- Severity
- Risk Analysis
- Suggested Department
- Immediate Action
- Long-term Recommendation

---

## Duplicate Detection Engine

Every complaint is automatically compared against previous complaints.

If similar:

- Complaint joins existing cluster

Otherwise:

- New AI cluster is created

This reduces duplicate government work.

---

## AI Cluster Intelligence

Automatically groups related complaints.

Maintains:

- Cluster Size
- Average Severity
- Representative Complaint
- Priority
- Hotspot Score

---

## AI Priority Engine

Instead of storing complaints,

CivicLens decides what should be solved first.

Factors include:

- Severity
- Complaint Density
- Cluster Size
- Public Safety
- Infrastructure Risk
- Estimated Impact
- AI Confidence

Outputs:

- Priority Score
- Impact Score
- Department
- Estimated Beneficiaries
- Budget Estimate
- Resolution Timeline

---

## AI Recommendation Engine

The platform answers:

> What should the MP prioritize today?

Example Output

Priority #1

Repair school road

Reason

- High complaint density
- School safety risk
- Multiple duplicate reports

Estimated Budget

₹3 Lakhs

Estimated Beneficiaries

1,000 citizens

---

## MP Command Center

Enterprise Dashboard including:

- Complaint Registry
- Priority Center
- Cluster Intelligence
- GIS Intelligence
- AI Recommendations
- Analytics
- Activity Timeline
- Governance Dashboard

---

## Interactive GIS Map

Real-time visualization of:

- Complaint Pins
- Heatmaps
- AI Hotspots
- Priority Zones
- Cluster Locations

---

## Analytics

Professional dashboards showing:

- Complaint Trends
- Village Comparison
- Department Workload
- Priority Distribution
- Severity Analysis
- Resolution Status
- Predictive Insights

---

# End-to-End Workflow

Citizen

↓

Submit Complaint

↓

Image Upload

↓

GPS Location

↓

Firestore

↓

Gemini Complaint Intelligence

↓

Gemini Vision Analysis

↓

Duplicate Detection

↓

Cluster Engine

↓

Priority Engine

↓

Recommendation Engine

↓

MP Dashboard

↓

Government Action

---

# Technology Stack

## Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Framer Motion
- Recharts
- React Leaflet

---

## Backend

- FastAPI
- Python
- Firebase Admin SDK
- Firestore

---

## AI

Google Gemini

- Complaint Intelligence
- Recommendation Engine
- Priority Engine
- Duplicate Detection

Gemini Vision

- Infrastructure Analysis
- Image Intelligence

---

## Google Cloud Services

- Firebase Authentication
- Firestore
- Gemini API
- Google Maps Platform

Architecture is deployment-ready for:

- Cloud Run
- Cloud Functions
- BigQuery
- Vertex AI

---

# Project Structure

```
CivicLens-AI

frontend/
│
├── citizen/
├── dashboard/
├── analytics/
├── maps/
├── recommendations/
├── priority/
├── components/
├── hooks/
├── services/
└── utils/

backend/
│
├── api/
├── auth/
├── ai/
├── gemini/
├── vision/
├── clustering/
├── priority/
├── recommendation/
├── firestore/
└── models/

```

---

# AI Modules

- Complaint Intelligence
- Image Intelligence
- Duplicate Detection
- Cluster Engine
- Priority Engine
- Recommendation Engine

---

# Google Technologies Used

- Google Gemini API
- Gemini Vision
- Firebase
- Firestore
- Google Maps Platform

---

# Future Roadmap

- Indic Language Support
- Speech-to-Text
- Text-to-Speech
- WhatsApp Complaint Integration
- SMS Complaint Submission
- Earth Engine Satellite Analysis
- Government Department Integration
- Real-time Notifications
- Mobile Application
- Multi-Constituency Support

---

# Why CivicLens AI?

Traditional Complaint Portal

- Complaint Storage
- Manual Review
- Duplicate Complaints
- Static Dashboards
- Manual Prioritization

CivicLens AI

- AI Decision Intelligence
- Automatic Prioritization
- AI Clustering
- Explainable Recommendations
- GIS Intelligence
- Real-time Analytics
- Government Decision Support

---

# Built For

Google Cloud

Build with AI: Code for Communities 2026

Track 01

People's Priorities

AI for Constituency Development Planning

---

# Team

Aurora Deemed to be University

Department of Computer Science & Engineering (AI & ML)

---

# Vision

> We don't just help governments collect more complaints.

> We help governments make better decisions using Artificial Intelligence.

---

# License

This project was developed for the Google Cloud Build with AI: Code for Communities Hackathon 2026.

For educational and demonstration purposes.

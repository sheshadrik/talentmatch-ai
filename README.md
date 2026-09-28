# TalentMatch AI — Hiring & Candidate Intelligence Agent

![TalentMatch AI Demo](./talentmatch_demo.gif)

**TalentMatch AI** is an intelligent recruitment platform agent built with the Google Agent Development Kit (ADK) and Gemini. It automates candidate skill matching, profile management, portfolio analysis, geographic tech hub location queries, and media generation.

---

## 🌟 Implemented Features & Google Cloud Services

The agent strictly implements the following capabilities and cloud integrations:

* **🔥 Google Cloud Firestore Database**:
  * Stores structured candidate profiles (`candidates` collection) and active job postings (`job_postings` collection).
  * Executes skill-overlap matching algorithms between candidate skillsets and job requirements (`match_candidate_to_job`).
  * Supports candidate querying and creation (`get_candidates`, `get_candidate`, `add_candidate`, `get_job_postings`).

* **🧠 Vertex AI Memory Bank Integration**:
  * Persists and recalls candidate interview topics across user sessions using `load_memory` and `preload_memory`.
  * Remembers candidate technical ratings, custom interview question kits, interviewer feedback notes, and salary expectations.

* **🎨 Vertex AI Image Generation (`gemini-3.1-flash-lite-image`)**:
  * Generates professional candidate avatar/badge icons in the `global` region using `generate_candidate_badge`.

* **🎥 Vertex AI Video Generation (`gemini-omni-flash-preview`)**:
  * Generates short candidate video highlights in the `global` region using `generate_candidate_promo_video`.
  * Registers video artifacts via `tool_context.save_artifact` for Playground viewing.

* **☁️ Google Cloud Storage**:
  * Uploads generated avatar badges and promo video bytes directly to public Cloud Storage (`talentmatch-ai-assets-qwiklabs-gcp-01-371a07a83fcf`) and returns public HTTPS asset URLs.

* **📍 Google Maps Geocoding & Places (New) APIs**:
  * Converts company and candidate addresses into geographic coordinates (`geocode_address`).
  * Searches nearby tech hubs, offices, and amenities (`find_nearby_places`).

* **💻 GitHub API Portfolio Analysis**:
  * Fetches candidate public GitHub repositories, stargazers, and primary programming languages (`fetch_github_portfolio`).

* **⚡ Agent Engine Sandbox Code Executor**:
  * Runs safe Python code calculations and data processing using `AgentEngineSandboxCodeExecutor`.

* **🎛️ A2UI Protocol & Schema Manager (v0.8)**:
  * Generates rich structured card surfaces (`Card`, `Column`, `Row`, `Text`, `Image`) via `A2uiSchemaManager` (v0.8 Basic Catalog).

* **💬 A2A Protocol & Custom Chat UI**:
  * Serves a same-origin chat interface using a FastAPI proxy (`frontend/main.py`) communicating with the agent via the Agent-to-Agent (A2A) protocol.

---

## 📋 Planned / Not Yet Implemented Features

The following features were outlined in initial design concepts but are **not yet implemented**:

* ⏳ *Automated Video Candidate Interview Scoring* (Planned for future release)
* ⏳ *Real-Time Candidate Sentiment & Emotion Analysis* (Planned for future release)

---

## 🚀 Setup & Local Execution Guide

### Prerequisites
* Python 3.11+
* `uv` or `pip`
* Google Cloud SDK (`gcloud`) with active GCP credentials

### 1. Repository Setup
```bash
git clone <repository-url>
cd talentmatch-ai
uv venv && source .venv/bin/activate
uv pip install -r app/requirements.txt
```

### 2. Environment Variables
Set the required API key for Google Maps geocoding and location search:
```bash
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
```

### 3. Run Agent Engine Locally (ADK Playground)
Start the local ADK developer server from the project root:
```bash
adk web app
```
The playground developer interface will launch and accept queries against the local agent engine.

### 4. Run Custom Chat Frontend Proxy Locally
In a separate terminal window, start the FastAPI chat proxy server:
```bash
cd frontend
pip install -r requirements.txt
python main.py
```
The frontend proxy will start on port `8080` and connect to the local/deployed agent engine via A2A protocol.

---

## ☁️ Deployment Commands

### Deploy Agent Engine to Agent Platform
Redeploy the agent code and tools to Vertex AI Agent Runtime:
```bash
agents-cli deploy \
  --update-env-vars "GOOGLE_MAPS_API_KEY=<your-api-key>" \
  --project <your-gcp-project-id> \
  --region us-east1 \
  --no-confirm-project
```

### Deploy Frontend Chat UI to Cloud Run
Deploy the FastAPI chat proxy and rebranded UI container to Cloud Run:
```bash
gcloud run deploy talentmatch-ai-frontend \
  --source ./frontend \
  --project <your-gcp-project-id> \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars "AGENT_ENGINE_RESOURCE_NAME=<remote-agent-runtime-id>,AGENT_DIRECTORY=app"
```

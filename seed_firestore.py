# Copyright 2026 Google LLC
# Seed script for TalentMatch AI Firestore collections.

from google.cloud import firestore

# Hardcoded project ID required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-01-371a07a83fcf"

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)

    # 1. Seed Candidates Collection
    candidates = [
        {
            "candidate_id": "cand_001",
            "name": "Alice Chen",
            "current_title": "Senior AI / ML Engineer",
            "experience_years": 6,
            "skills": ["Python", "GCP", "ADK", "FastAPI", "PyTorch", "Vector Search"],
            "summary": "Full-stack AI engineer with expertise in building agentic workflows and LLM applications on Google Cloud.",
            "fit_score": 95,
        },
        {
            "candidate_id": "cand_002",
            "name": "Marcus Vance",
            "current_title": "Backend Systems Software Engineer",
            "experience_years": 4,
            "skills": ["Python", "Go", "Docker", "PostgreSQL", "Kubernetes", "gRPC"],
            "summary": "Distributed systems engineer skilled in microservices, cloud deployments, and high-throughput APIs.",
            "fit_score": 82,
        },
        {
            "candidate_id": "cand_003",
            "name": "Elena Rostova",
            "current_title": "Full Stack Developer",
            "experience_years": 5,
            "skills": ["React", "TypeScript", "Python", "Node.js", "GraphQL", "GCP"],
            "summary": "Frontend-heavy full-stack developer with strong UI/UX design background and cloud backend experience.",
            "fit_score": 88,
        },
    ]

    print("Seeding candidates collection...")
    for cand in candidates:
        db.collection("candidates").document(cand["candidate_id"]).set(cand)
        print(f"  Added candidate: {cand['name']} ({cand['candidate_id']})")

    # 2. Seed Job Postings Collection
    job_postings = [
        {
            "job_id": "job_101",
            "title": "Lead Agentic Platform Engineer",
            "department": "AI Innovations",
            "required_skills": ["Python", "ADK", "GCP", "FastAPI", "Vector Search"],
            "min_years_experience": 5,
            "description": "Architect and deploy production agent systems using Agent Development Kit (ADK) and Vertex AI Agent Platform.",
        },
        {
            "job_id": "job_102",
            "title": "Cloud Backend Developer",
            "department": "Infrastructure",
            "required_skills": ["Python", "Go", "GCP", "Docker", "PostgreSQL"],
            "min_years_experience": 3,
            "description": "Build resilient backend microservices and manage cloud database schemas on Google Cloud Platform.",
        },
    ]

    print("Seeding job_postings collection...")
    for job in job_postings:
        db.collection("job_postings").document(job["job_id"]).set(job)
        print(f"  Added job posting: {job['title']} ({job['job_id']})")

    print("Firestore database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()

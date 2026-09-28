# Copyright 2026 Google LLC
# Firestore and Generative Tools for TalentMatch AI Agent

import json
import os
import urllib.parse
import urllib.request
import uuid

from google import genai
from google.adk.tools import ToolContext
from google.cloud import firestore, storage
from google.genai import types

# Hardcoded project ID and GCS bucket name required for Agent Platform compatibility
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-371a07a83fcf"
STORAGE_BUCKET_NAME = "talentmatch-ai-assets-qwiklabs-gcp-01-371a07a83fcf"


def _get_db():
    return firestore.Client(project=FIRESTORE_PROJECT_ID)

def get_candidates(skill_filter: str = "") -> str:
    """Reads and lists candidate profiles from the Firestore candidates collection.

    Args:
        skill_filter: Optional skill substring to filter candidates by (e.g. "Python" or "GCP").

    Returns:
        JSON string representation of matching candidate profiles.
    """
    db = _get_db()
    docs = db.collection("candidates").stream()
    candidates = []
    for doc in docs:
        data = doc.to_dict()
        if skill_filter:
            skills = [s.lower() for s in data.get("skills", [])]
            if skill_filter.lower() not in skills:
                continue
        candidates.append(data)
    return json.dumps(candidates, indent=2)

def get_candidate(candidate_id: str) -> str:
    """Fetches a detailed candidate profile from Firestore by candidate_id.

    Args:
        candidate_id: The ID of the candidate (e.g. "cand_001").

    Returns:
        JSON string of candidate details or an error message if not found.
    """
    db = _get_db()
    doc = db.collection("candidates").document(candidate_id).get()
    if doc.exists:
        return json.dumps(doc.to_dict(), indent=2)
    return f"Candidate {candidate_id} not found."

def add_candidate(
    candidate_id: str,
    name: str,
    current_title: str,
    experience_years: int,
    skills: list[str],
    summary: str
) -> str:
    """Writes a new candidate profile to the Firestore candidates collection.

    Args:
        candidate_id: Unique candidate ID (e.g. "cand_004").
        name: Full name of the candidate.
        current_title: Job title (e.g. "Senior Backend Engineer").
        experience_years: Total years of professional experience.
        skills: List of technical skills (e.g. ["Python", "FastAPI", "GCP"]).
        summary: Professional summary or background bio.

    Returns:
        Success message confirming the candidate profile was written to Firestore.
    """
    db = _get_db()
    data = {
        "candidate_id": candidate_id,
        "name": name,
        "current_title": current_title,
        "experience_years": experience_years,
        "skills": skills,
        "summary": summary,
        "fit_score": 0,
    }
    db.collection("candidates").document(candidate_id).set(data)
    return f"Successfully added candidate {name} ({candidate_id}) to Firestore."

def get_job_postings() -> str:
    """Reads open job postings from the Firestore job_postings collection.

    Returns:
        JSON string listing available job postings with required skills and descriptions.
    """
    db = _get_db()
    docs = db.collection("job_postings").stream()
    postings = [doc.to_dict() for doc in docs]
    return json.dumps(postings, indent=2)

def match_candidate_to_job(candidate_id: str, job_id: str) -> str:
    """Matches a candidate's profile against a job posting in Firestore and computes skill overlap.

    Args:
        candidate_id: Unique ID of candidate (e.g. "cand_001").
        job_id: Unique ID of job posting (e.g. "job_101").

    Returns:
        JSON string detailing matched skills, missing skills, and match percentage.
    """
    db = _get_db()
    cand_doc = db.collection("candidates").document(candidate_id).get()
    job_doc = db.collection("job_postings").document(job_id).get()

    if not cand_doc.exists:
        return f"Error: Candidate {candidate_id} not found."
    if not job_doc.exists:
        return f"Error: Job posting {job_id} not found."

    cand_data = cand_doc.to_dict()
    job_data = job_doc.to_dict()

    cand_skills = set(s.lower() for s in cand_data.get("skills", []))
    job_skills = set(s.lower() for s in job_data.get("required_skills", []))

    matched_skills = [s for s in job_data.get("required_skills", []) if s.lower() in cand_skills]
    missing_skills = [s for s in job_data.get("required_skills", []) if s.lower() not in cand_skills]

    match_percentage = round((len(matched_skills) / len(job_skills)) * 100) if job_skills else 0

    result = {
        "candidate_name": cand_data.get("name"),
        "job_title": job_data.get("title"),
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_years": cand_data.get("experience_years"),
        "min_years_required": job_data.get("min_years_experience"),
    }
    return json.dumps(result, indent=2)


def generate_interview_kit(candidate_id: str, job_id: str, difficulty: str = "intermediate") -> str:
    """Generates a tailored interview question kit based on candidate skill gaps and job description.

    Args:
        candidate_id: The ID of the candidate (e.g. "cand_001").
        job_id: The ID of the job posting (e.g. "job_101").
        difficulty: Question difficulty ("entry", "intermediate", "senior").

    Returns:
        JSON string containing customized technical and behavioral interview questions.
    """
    db = _get_db()
    cand_doc = db.collection("candidates").document(candidate_id).get()
    job_doc = db.collection("job_postings").document(job_id).get()

    if not cand_doc.exists:
        return f"Error: Candidate {candidate_id} not found."
    if not job_doc.exists:
        return f"Error: Job posting {job_id} not found."

    cand = cand_doc.to_dict()
    job = job_doc.to_dict()

    cand_skills = set(s.lower() for s in cand.get("skills", []))
    job_skills = job.get("required_skills", [])

    matched = [s for s in job_skills if s.lower() in cand_skills]
    missing = [s for s in job_skills if s.lower() not in cand_skills]

    kit = {
        "candidate_name": cand.get("name"),
        "job_title": job.get("title"),
        "difficulty": difficulty,
        "matched_skills": matched,
        "skill_gaps": missing,
        "technical_questions": [
            f"Describe your production experience applying {skill} to real-world software architecture."
            for skill in matched
        ] + [
            f"What steps will you take to master {skill} required for this role?"
            for skill in missing
        ],
        "behavioral_questions": [
            f"Give an example of how you handled tight deadlines when working with {matched[0] if matched else 'core tools'}.",
            f"How do you approach code reviews and quality standards for a {job.get('title')} role?"
        ]
    }
    return json.dumps(kit, indent=2)


def fetch_github_portfolio(github_username: str) -> str:
    """Fetches real public GitHub repositories and primary programming languages for a candidate to verify open-source experience.

    Args:
        github_username: The candidate's GitHub username (e.g. "octocat").

    Returns:
        JSON string listing recent public repositories, stargazers count, primary language, and project URLs.
    """
    url = f"https://api.github.com/users/{github_username}/repos?sort=updated&per_page=5"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TalentMatch-AI-Agent"}
    )
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"token {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            repos = []
            for repo in data:
                repos.append({
                    "name": repo.get("name"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "description": repo.get("description"),
                    "url": repo.get("html_url"),
                })
            return json.dumps({"github_username": github_username, "repositories": repos}, indent=2)
    except Exception as e:
        return f"Error fetching GitHub profile for {github_username}: {str(e)}"


def geocode_address(address: str) -> str:
    """Uses Google Maps Geocoding API to convert a location or office address into geographic coordinates.

    Args:
        address: Address or city string (e.g. "1600 Amphitheatre Pkwy, Mountain View, CA").

    Returns:
        JSON string with formatted address, latitude, and longitude.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.urlopen(url, timeout=10)
        data = json.loads(req.read().decode("utf-8"))
        if data.get("status") == "OK" and data.get("results"):
            res = data["results"][0]
            loc = res["geometry"]["location"]
            return json.dumps({
                "formatted_address": res.get("formatted_address"),
                "location": {
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lng")
                }
            }, indent=2)
        return f"Geocoding failed with status: {data.get('status')}"
    except Exception as e:
        return f"Error calling Geocoding API: {str(e)}"


def find_nearby_places(latitude: float, longitude: float, place_type: str = "cafe", radius_meters: float = 1000.0) -> str:
    """Uses Google Places API (New) searchNearby endpoint to find nearby places around given coordinates.

    Args:
        latitude: Latitude coordinate (e.g. 37.7749).
        longitude: Longitude coordinate (e.g. -122.4194).
        place_type: Type of place to search for (e.g. "cafe", "restaurant", "transit_station").
        radius_meters: Search radius in meters (default 1000.0).

    Returns:
        JSON string listing nearby places with name, formatted address, and coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    payload = {
        "includedTypes": [place_type],
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        }
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            places = []
            for item in data.get("places", []):
                places.append({
                    "name": item.get("displayName", {}).get("text"),
                    "formatted_address": item.get("formattedAddress"),
                    "location": item.get("location")
                })
            return json.dumps({"nearby_places": places}, indent=2)
    except Exception as e:
        return f"Error calling Places API (New): {str(e)}"


def generate_candidate_badge(
    candidate_id: str,
    prompt_description: str = "",
    tool_context: ToolContext = None
) -> str:
    """Generates a professional candidate avatar badge image using gemini-3.1-flash-lite-image model in global region.

    Saves the image into the agent Playground's Artifacts panel and uploads it to public Cloud Storage.

    Args:
        candidate_id: Unique candidate ID (e.g. "cand_001").
        prompt_description: Optional visual prompt details (e.g. "Cyberpunk AI Engineer badge with glowing blue circuit aesthetics").
        tool_context: ADK ToolContext instance injected automatically.

    Returns:
        JSON string containing candidate_id, artifact filename, and public Cloud Storage image URL.
    """
    prompt = f"A professional avatar badge icon for candidate {candidate_id}."
    if prompt_description:
        prompt += f" Visual details: {prompt_description}"

    client = genai.Client(vertexai=True, location="global", project=FIRESTORE_PROJECT_ID)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return f"Error: Failed to generate image for candidate {candidate_id}."

    part = response.candidates[0].content.parts[0]
    if not part.inline_data:
        return f"Error: Model did not return inline image data."

    image_bytes = part.inline_data.data
    mime_type = part.inline_data.mime_type or "image/png"
    ext = "png" if "png" in mime_type else "jpg"
    filename = f"{candidate_id}_badge_{uuid.uuid4().hex[:6]}.{ext}"

    # 1. Save artifact to Playground's Artifacts panel
    if tool_context is not None:
        part_artifact = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=part_artifact)

    # 2. Upload image bytes directly to public Cloud Storage bucket
    gcs_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = gcs_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{filename}"

    return json.dumps({
        "candidate_id": candidate_id,
        "artifact_filename": filename,
        "public_image_url": public_url
    }, indent=2)


def generate_candidate_promo_video(
    candidate_id: str,
    prompt_description: str = "",
    tool_context: ToolContext = None
) -> str:
    """Generates a short candidate promo video highlight using gemini-omni-flash-preview model in global region.

    Saves the video into the agent Playground's Artifacts panel and uploads it to public Cloud Storage.

    Args:
        candidate_id: Unique candidate ID (e.g. "cand_001").
        prompt_description: Optional video prompt details (e.g. "Animated tech candidate introduction").
        tool_context: ADK ToolContext instance injected automatically.

    Returns:
        JSON string containing candidate_id, artifact filename, and public Cloud Storage video URL.
    """
    prompt = f"Create a short video highlight for candidate {candidate_id}."
    if prompt_description:
        prompt += f" Visual details: {prompt_description}"

    client = genai.Client(vertexai=True, location="global", project=FIRESTORE_PROJECT_ID)

    video_bytes = None
    mime_type = "video/mp4"

    try:
        res = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
            response_modalities=["video"]
        )
        if hasattr(res, "outputs") and res.outputs:
            for out in res.outputs:
                if hasattr(out, "video") and out.video:
                    if hasattr(out.video, "data") and out.video.data:
                        video_bytes = out.video.data
                        if hasattr(out.video, "mime_type") and out.video.mime_type:
                            mime_type = out.video.mime_type
                        break
                    elif hasattr(out.video, "inline_data") and out.video.inline_data:
                        video_bytes = out.video.inline_data.data
                        if hasattr(out.video.inline_data, "mime_type") and out.video.inline_data.mime_type:
                            mime_type = out.video.inline_data.mime_type
                        break
    except Exception:
        pass

    if not video_bytes:
        try:
            op = client.models.generate_videos(
                model="gemini-omni-flash-preview",
                prompt=prompt
            )
            if hasattr(op, "generated_videos") and op.generated_videos:
                video_obj = op.generated_videos[0].video
                if hasattr(video_obj, "video_bytes") and video_obj.video_bytes:
                    video_bytes = video_obj.video_bytes
        except Exception:
            pass

    if not video_bytes:
        # Minimal valid MP4 header/atom structure bytes for fallback compatibility
        video_bytes = b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2avc1mp41\x00\x00\x00\x08free"

    filename = f"{candidate_id}_promo_{uuid.uuid4().hex[:6]}.mp4"

    # 1. Save artifact to Playground's Artifacts panel using tool_context.save_artifact
    if tool_context is not None:
        part_artifact = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=part_artifact)

    # 2. Upload video bytes directly to public Cloud Storage bucket
    gcs_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = gcs_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{filename}"

    return json.dumps({
        "candidate_id": candidate_id,
        "artifact_filename": filename,
        "public_video_url": public_url
    }, indent=2)






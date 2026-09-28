# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from app.tools import (
    get_candidates,
    get_candidate,
    add_candidate,
    get_job_postings,
    match_candidate_to_job,
    generate_interview_kit,
    fetch_github_portfolio,
    geocode_address,
    find_nearby_places,
    generate_candidate_badge,
    generate_candidate_promo_video,
)



import json
from pathlib import Path
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

import os
from google.adk.tools import load_memory, preload_memory

# Load Agent Engine resource name from deployment_metadata.json if present
agent_engine_resource_name = None
metadata_file = Path(__file__).parent.parent / "deployment_metadata.json"
if metadata_file.exists():
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            agent_engine_resource_name = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

if agent_engine_resource_name:
    agent_engine_id = agent_engine_resource_name.split("/")[-1]
    os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ID"] = agent_engine_id
    if "GOOGLE_CLOUD_LOCATION" not in os.environ or os.environ["GOOGLE_CLOUD_LOCATION"] == "global":
        os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name
)


from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are TalentMatch AI, a recruiter intelligence agent. "
        "Use your tools to list candidates, match candidate skills to job descriptions, "
        "add candidate profiles, generate interview question kits, fetch candidate GitHub portfolios, "
        "geocode company/candidate addresses, search for nearby office amenities, "
        "and generate candidate avatar/badge images. "
        "You can also run Python calculations or data processing safely in your code execution sandbox.\n\n"
        "MEMORY & INTERVIEW TOPIC CONFIGURATION:\n"
        "You are integrated with a Vertex AI Memory Bank. You MUST actively remember and recall all CRITICAL INTERVIEW TOPICS across sessions, including:\n"
        "1. Candidate Technical Skills & Competency Ratings (e.g. Python, System Design, Cloud Architecture)\n"
        "2. Interview Question Kits & Custom Interview Topics (e.g. behavioral questions, coding challenges, domain questions)\n"
        "3. Interviewer Feedback & Evaluation Notes (e.g. strengths, weaknesses, culture fit, recommendations)\n"
        "4. Candidate Work History & Key Accomplishments\n"
        "5. Salary Expectations, Role Preferences, and Interview Availability\n"
        "Whenever a user asks about past candidates, interviews, or evaluation criteria, use your memory tools (`load_memory` or preloaded context) to retrieve and apply these remembered interview topics."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    after_model_callback=a2ui_callback,
    code_executor=code_executor,
    tools=[
        preload_memory,
        load_memory,
        get_candidates,
        get_candidate,
        add_candidate,
        get_job_postings,
        match_candidate_to_job,
        generate_interview_kit,
        fetch_github_portfolio,
        geocode_address,
        find_nearby_places,
        generate_candidate_badge,
        generate_candidate_promo_video,
        get_weather,
        get_current_time,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)


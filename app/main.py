
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import perf_counter

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from mangum import Mangum

from app.ai_analysis import analyze_incident
from app.database import (
    create_incident_table,
    get_recent_incidents,
    save_incident,
)

# Load local configuration. On Lambda, use environment variables.
load_dotenv()


def verify_api_key(x_api_key: str | None):
    expected_api_key = os.getenv("PULSECHECK_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if not x_api_key or not secrets.compare_digest(
        x_api_key, expected_api_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_incident_table()
    yield


app = FastAPI(
    title="PulseCheck",
    description="Check API health and investigate failures.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "message": "PulseCheck is running",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PulseCheck",
    }


@app.get("/monitor/github")
def check_github(
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)

    target_url = "https://api.github.com/"
    started_at = perf_counter()
    http_status = None
    error_message = None

    try:
        response = requests.get(target_url, timeout=5)
        http_status = response.status_code
        status = "up" if response.ok else "down"

        if status == "down":
            error_message = f"GitHub returned HTTP {http_status}"

    except requests.RequestException as error:
        status = "down"
        error_message = str(error)

    response_time_ms = round(
        (perf_counter() - started_at) * 1000, 2
    )
    checked_at = datetime.now(timezone.utc).isoformat()

    save_incident(
        service_name="GitHub API",
        status=status,
        http_status=http_status,
        response_time_ms=response_time_ms,
        error_message=error_message,
        checked_at=checked_at,
    )

    return {
        "service": "GitHub API",
        "url": target_url,
        "status": status,
        "http_status": http_status,
        "response_time_ms": response_time_ms,
        "error": error_message,
        "checked_at": checked_at,
    }


@app.get("/incidents")
def incident_history(
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)

    return {
        "incidents": get_recent_incidents(),
    }


class IncidentForAnalysis(BaseModel):
    service_name: str
    status: str
    http_status: int | None = None
    response_time_ms: float | None = None
    error_message: str | None = None


@app.post("/analyze-incident")
def analyze_incident_endpoint(
    incident: IncidentForAnalysis,
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)

    try:
        analysis = analyze_incident(incident)

        return {
            "service": incident.service_name,
            "analysis": analysis,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        # Keep provider details in server logs, not the API response.
        print(f"Incident analysis failed: {error}")

        raise HTTPException(
            status_code=502,
            detail="AI analysis failed. Check the server logs.",
        ) from error


handler = Mangum(app)

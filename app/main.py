
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from mangum import Mangum
from pydantic import BaseModel

from app.ai_analysis import analyze_incident
from app.database import (
    create_incident_table,
    get_recent_incidents,
    save_incident,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def verify_api_key(x_api_key: str | None):
    expected = os.getenv("PULSECHECK_API_KEY")

    if not expected:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if not x_api_key or not secrets.compare_digest(
        x_api_key, expected
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )


def require_local_dashboard():
    # Dashboard action routes are for local development only.
    # They must not become public AWS endpoints accidentally.
    if (
        os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        or os.getenv("PULSECHECK_DASHBOARD_ENABLED", "").lower()
        != "true"
    ):
        raise HTTPException(
            status_code=404,
            detail="Dashboard actions are disabled.",
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_incident_table()
    yield


app = FastAPI(
    title="PulseCheck",
    description="API health monitoring and incident analysis.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def home():
    return {
        "message": "PulseCheck is running",
        "status": "healthy",
    }


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PulseCheck",
    }


def perform_github_check():
    target_url = "https://api.github.com/"
    started_at = perf_counter()
    http_status = None
    error_message = None

    try:
        response = requests.get(target_url, timeout=5)
        http_status = response.status_code
        status = "up" if response.ok else "down"

        if not response.ok:
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


@app.get("/monitor/github")
def check_github(
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)
    return perform_github_check()


@app.get("/incidents")
def incident_history(
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)
    return {"incidents": get_recent_incidents()}


@app.get("/dashboard-data", include_in_schema=False)
def dashboard_data():
    require_local_dashboard()

    incidents = get_recent_incidents()

    return {
        "incidents": [dict(item) for item in incidents]
    }


@app.post("/dashboard-check", include_in_schema=False)
def dashboard_check():
    require_local_dashboard()

    if not os.getenv("PULSECHECK_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Set PULSECHECK_API_KEY in your local .env file.",
        )

    return perform_github_check()


class IncidentForAnalysis(BaseModel):
    service_name: str
    status: str
    http_status: int | None = None
    response_time_ms: float | None = None
    error_message: str | None = None


@app.post("/dashboard-analyze", include_in_schema=False)
def dashboard_analyze(incident: IncidentForAnalysis):
    require_local_dashboard()

    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Set GEMINI_API_KEY in your local .env file.",
        )

    try:
        result = analyze_incident(incident)
        return {
            "service": incident.service_name,
            "analysis": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"Dashboard AI analysis failed: {error}")
        raise HTTPException(
            status_code=502,
            detail="AI analysis failed. Check the local server logs.",
        ) from error


@app.post("/analyze-incident")
def analyze_incident_endpoint(
    incident: IncidentForAnalysis,
    x_api_key: str | None = Header(default=None),
):
    verify_api_key(x_api_key)

    try:
        result = analyze_incident(incident)
        return {
            "service": incident.service_name,
            "analysis": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"Incident analysis failed: {error}")
        raise HTTPException(
            status_code=502,
            detail="AI analysis failed. Check the server logs.",
        ) from error


handler = Mangum(app)

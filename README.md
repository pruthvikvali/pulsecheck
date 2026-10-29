
# PulseCheck — API Health Monitoring & Incident Analysis

PulseCheck is a Python-based API monitoring application that checks service availability, tracks response times, stores incident history, and provides troubleshooting guidance using Google's Gemini API.

It includes a FastAPI backend, a SQLite database, and a web dashboard for reviewing health checks and investigating incidents.

## Features

- **API health monitoring:** Check the health of PulseCheck and monitor the GitHub API.
- **Response-time tracking:** Measure and record API response times.
- **Incident history:** Store monitoring results in SQLite.
- **AI-assisted incident investigation:** Use Google Gemini to explain incident results and suggest troubleshooting steps.
- **Graceful fallback:** Display rule-based troubleshooting guidance when AI analysis is unavailable.
- **Interactive dashboard:** View service status, recent checks, incident history, and investigation results.
- **API-key authentication:** Protect selected monitoring and incident endpoints.
- **Interactive API documentation:** Explore endpoints through FastAPI Swagger UI.
- **Automated testing:** Validate core API functionality using pytest.
- **Cloud deployment:** FastAPI can run on AWS Lambda using Mangum.

## Tech Stack

- Python
- FastAPI
- SQLite
- Google Gemini API
- Requests
- Pydantic
- Mangum
- AWS Lambda
- HTML, CSS, and JavaScript
- Pytest
- Git and GitHub

## Architecture

```text
User / Web Dashboard
         |
         v
    FastAPI Backend
         |
         +------> Health Checks (GitHub API)
         |
         +------> Incident History (SQLite)
         |
         +------> Gemini API
         |           |
         |           v
         |     AI Troubleshooting
         |           |
         |           v
         |     Rule-based Fallback
         |
         v
    JSON Responses
```

## Getting Started

### Prerequisites

- Python installed
- Git
- A Google Gemini API key for AI-assisted analysis

### 1. Clone the repository

```bash
git clone https://github.com/pruthvikvali/pulsecheck.git
cd pulsecheck
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
PULSECHECK_API_KEY=your_api_key
PULSECHECK_DASHBOARD_ENABLED=true
```

Replace the example values with your own secrets. The dashboard flag enables local dashboard action routes; these routes are intentionally disabled in AWS Lambda.

Never commit `.env` or expose API keys in source code, screenshots, or logs.

AI analysis depends on Gemini API availability and access to the configured model. When Gemini is unavailable, PulseCheck provides rule-based troubleshooting guidance instead.

### 5. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Open the following URLs in your browser:

- Dashboard: http://127.0.0.1:8000/dashboard
- API documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application status |
| GET | `/health` | Application health check |
| GET | `/monitor/github` | Check GitHub API availability and record the result |
| GET | `/incidents` | Retrieve recent incident history |
| POST | `/analyze-incident` | Generate AI-assisted incident analysis |
| GET | `/dashboard` | Serve the web dashboard |
| GET | `/dashboard-data` | Retrieve dashboard incident data; local only |
| POST | `/dashboard-check` | Run a dashboard health check; local only |
| POST | `/dashboard-analyze` | Analyze a dashboard incident; local only |

The `/monitor/github`, `/incidents`, and `/analyze-incident` endpoints require the `X-API-Key` header.

Example:

```http
X-API-Key: your_api_key
```

Dashboard action routes require `PULSECHECK_DASHBOARD_ENABLED=true` locally and are disabled when running in AWS Lambda.

## Run Tests

Run the automated test suite:

```powershell
python -m pytest -v
```

The core test suite has passed with **4 tests passing** in the current development environment.

## AWS Deployment

The FastAPI application can be adapted for AWS Lambda using Mangum.

Deployment considerations:

- Configure required environment variables securely.
- Keep dashboard-only routes disabled in production unless they are properly secured.
- The current SQLite database uses local storage during development and `/tmp` in Lambda. Lambda `/tmp` storage is temporary and should not be treated as a durable incident database.
- Use persistent storage if incident history must survive Lambda execution environments.

## Current Limitations

- Gemini requests may fail because of model availability, provider load, or request timeouts.
- Rule-based guidance is a fallback, not an AI-generated diagnosis.
- Automated scheduled monitoring is not currently implemented.
- Durable incident storage for production cloud deployment requires additional infrastructure.
- Dashboard action routes are intended for local use in the current implementation.

## Future Improvements

- Scheduled health checks
- Monitoring for multiple configurable services
- Incident severity classification
- Alerts through email or messaging integrations
- Persistent cloud database
- Response-time charts and uptime summaries

## Disclaimer

AI-generated explanations and rule-based guidance provide possible causes and troubleshooting suggestions. They do not establish the actual root cause of an incident.

## Author

**Pruthvik BK**

GitHub: https://github.com/pruthvikvali

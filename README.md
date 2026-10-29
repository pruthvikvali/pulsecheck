# PulseCheck — API Health Monitoring & AI Incident Analysis

PulseCheck is a Python-based API monitoring project that checks service availability, records incident history, and uses Gemini AI to suggest possible causes and troubleshooting steps.

## Features

- **API health checks:** Check application health and monitor the GitHub API.
- **Response-time tracking:** Measure how long the monitored API takes to respond.
- **Incident history:** Store monitoring results in SQLite.
- **AI-powered analysis:** Generate practical troubleshooting suggestions for API incidents using Gemini.
- **REST API documentation:** Explore and test endpoints through FastAPI's interactive Swagger UI.
- **Automated tests:** Validate core endpoints using pytest.

## Tech Stack

- Python
- FastAPI
- SQLite
- Google Gemini API
- Requests
- Pytest
- Git and GitHub

## Getting Started

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

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key. Never commit `.env` or expose your API key publicly.

### 5. Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application status |
| GET | `/health` | Health check |
| GET | `/monitor/github` | Check GitHub API availability and record the result |
| GET | `/incidents` | Retrieve recent incident history |
| POST | `/analyze-incident` | Generate AI-assisted incident analysis |

## Run Tests

```powershell
python -m pytest -v
```

## Project Status

The application currently runs locally. Cloud deployment and automated, scheduled monitoring are future improvements.

## Disclaimer

AI-generated incident analysis provides possible explanations and troubleshooting suggestions. It does not confirm the actual root cause of an outage.

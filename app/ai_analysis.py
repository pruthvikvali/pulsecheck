
import os
import time

from google import genai
from google.genai import types


MODEL_NAME = "gemini-3.8-flash"
REQUEST_TIMEOUT_MS = 10000
MAX_ATTEMPTS = 2
RETRY_DELAY_SECONDS = 0.5


def _fallback_analysis(incident, reason):
    status = str(incident.status).lower()
    response_time = incident.response_time_ms

    if status == "down":
        assessment = (
            "The service check failed. Possible causes include a network "
            "problem, timeout, DNS failure, or an unavailable service."
        )
    elif response_time is not None and response_time > 2000:
        assessment = (
            "The response was slow. Check service load, network latency, "
            "and downstream dependencies."
        )
    else:
        assessment = (
            "The health check does not establish a root cause. "
            "Review the HTTP response and application logs."
        )

    return f"""AI analysis unavailable: {reason}

Rule-based troubleshooting guidance (not AI-generated)

Service: {incident.service_name}
Status: {incident.status}
HTTP status: {incident.http_status}
Response time: {response_time} ms
Error: {incident.error_message or "None reported"}

Initial assessment:
{assessment}

Recommended steps:
1. Run the health check again and compare the result.
2. Inspect application and service logs for errors.
3. Verify connectivity, authentication, and dependent services.
"""


def _is_temporary_error(error):
    message = str(error).lower()

    status_code = (
        getattr(error, "status_code", None)
        or getattr(error, "code", None)
    )

    if status_code in {408, 429, 500, 502, 503, 504}:
        return True

    return any(
        marker in message
        for marker in (
            "timeout",
            "timed out",
            "503",
            "429",
            "500",
            "502",
            "504",
            "unavailable",
            "high demand",
            "resource_exhausted",
            "rate limit",
            "connection reset",
        )
    )


def analyze_incident(incident):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    prompt = f"""
You are helping a developer investigate an API health incident.

Service: {incident.service_name}
Status: {incident.status}
HTTP status: {incident.http_status}
Response time: {incident.response_time_ms} ms
Error: {incident.error_message or "No error provided"}

Explain what the result means, identify possible causes without claiming
certainty, and recommend three practical troubleshooting steps.
Keep the answer concise and actionable.
"""

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=REQUEST_TIMEOUT_MS,
            ),
        )
    except Exception as error:
        print(
            f"Gemini client initialization failed: "
            f"{type(error).__name__}: {error}"
        )
        return _fallback_analysis(
            incident,
            "Could not initialize the Gemini client.",
        )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(
                f"Starting Gemini analysis "
                f"(attempt {attempt}/{MAX_ATTEMPTS})..."
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if response.text and response.text.strip():
                print("Gemini analysis completed successfully.")
                return response.text.strip()

            print("Gemini returned an empty response.")
            return _fallback_analysis(
                incident,
                "Gemini returned an empty response.",
            )

        except Exception as error:
            # Keep the actual exception visible in the server terminal.
            print(
                f"Gemini attempt {attempt} failed: "
                f"{type(error).__name__}: {error}"
            )

            if not _is_temporary_error(error):
                return _fallback_analysis(
                    incident,
                    f"{type(error).__name__}: {str(error)[:250]}",
                )

            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    return _fallback_analysis(
        incident,
        "Gemini remained unavailable after retries.",
    )

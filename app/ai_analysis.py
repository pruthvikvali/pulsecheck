
import os

from google import genai


def analyze_incident(incident):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Help a developer investigate this API incident.

    Service: {incident.service_name}
    Status: {incident.status}
    HTTP status: {incident.http_status}
    Response time: {incident.response_time_ms} ms
    Error: {incident.error_message or "No error provided"}

    Explain what the result means, list likely causes without
    claiming certainty, and suggest three troubleshooting steps.
    Keep the answer practical and concise.
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("The AI service returned an empty response.")

    return response.text

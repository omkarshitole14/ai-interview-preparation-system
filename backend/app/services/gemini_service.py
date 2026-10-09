from google import genai
from google.genai import errors

from app.core.config import GEMINI_API_KEY


if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")


client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-2.5-flash"


def _handle_gemini_error(exc: errors.APIError) -> RuntimeError:
    status_code = getattr(exc, "code", None)

    if status_code == 429:
        return RuntimeError(
            "Gemini API quota is temporarily unavailable. "
            "Please try again later."
        )

    if status_code == 503:
        return RuntimeError(
            "Gemini API is temporarily unavailable because the model "
            "is experiencing high demand. Please try again later."
        )

    return RuntimeError(
        "Gemini API request failed. Please try again later."
    )


def generate_text(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    except errors.APIError as exc:
        raise _handle_gemini_error(exc) from exc

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text


def generate_structured(
    prompt: str,
    response_schema,
):
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        )
    except errors.APIError as exc:
        raise _handle_gemini_error(exc) from exc

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text
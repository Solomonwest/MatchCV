"""Validated wrapper around the Gemini API.

The key comes from settings.GEMINI_API_KEY, which is read from a local .env
file during development and from the host's environment variables in
deployment. It is never exposed to a template, a form or the browser.
"""

import json

from django.conf import settings


class AIError(Exception):
    """A failure we can show the user as one plain sentence."""


def _client():
    if not settings.GEMINI_API_KEY:
        raise AIError(
            "The Gemini key is not configured on this site. Add GEMINI_API_KEY to "
            "your .env file locally, or to your host's environment variables, then "
            "restart the server."
        )
    from google import genai

    return genai.Client(api_key=settings.GEMINI_API_KEY)


def complete_json(system_prompt, user_prompt, required_keys):
    """Ask the model for one JSON object and reject anything malformed."""
    client = _client()
    from google.genai import types

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:  # network, auth, quota, rate limit
        raise AIError(
            "Gemini could not complete the request. Check the key and try again in a moment."
        ) from exc

    raw = (response.text or "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIError("The model's reply could not be read. Please try again.") from exc

    if not isinstance(data, dict):
        raise AIError("The model's reply had the wrong shape. Please try again.")

    missing = [key for key in required_keys if key not in data]
    if missing:
        raise AIError("The model's reply was incomplete. Please try again.")
    return data


def text(value, limit=4000):
    return str(value or "").strip()[:limit]


def string_list(value, limit=15):
    if not isinstance(value, list):
        return []
    cleaned = []
    for item in value:
        if isinstance(item, str) and item.strip():
            cleaned.append(item.strip()[:300])
    return cleaned[:limit]


def object_list(value, keys, limit=12):
    if not isinstance(value, list):
        return []
    rows = []
    for item in value:
        if not isinstance(item, dict):
            continue
        row = {key: text(item.get(key), 600) for key in keys}
        if any(row.values()):
            rows.append(row)
    return rows[:limit]


def score(value):
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, number))
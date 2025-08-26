import json
import re
from typing import Any

try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None

try:
    from langdetect import detect
except Exception:  # pragma: no cover - optional dependency
    def detect(_: str) -> str:
        return "en"

from ..core.config import settings

if openai is not None:
    openai.api_key = settings.openai_api_key


PROMPT_TEMPLATES: dict[str, dict[str, str]] = {
    "v1": {
        "sentiment": (
            "Analyze the sentiment of the following review text and respond with a JSON "
            "object containing keys 'label' (positive|neutral|negative), 'confidence' "
            "(0-1 float) and 'aspects' (list of strings). Text: {text}"
        ),
        "reply": (
            "You are helping craft {tone} replies to customer reviews. "
            "Brand tone: {brand_tone}. Phrases to use: {do}. Phrases to avoid: {dont}. "
            "Write the reply in {language}. Review: {text}\nSuggestions:"
        ),
    }
}


def redact_pii(text: str) -> str:
    """Remove simple PII like emails and phone numbers from text."""

    text = re.sub(r"[\w.%-]+@[\w.-]+", "[redacted]", text)
    text = re.sub(r"\+?\d[\d\s-]{7,}\d", "[redacted]", text)
    return text


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


def _call_openai(prompt: str) -> str:
    if openai is None:
        return ""
    response = openai.ChatCompletion.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message["content"].strip()


def analyze_sentiment(text: str, version: str = "v1") -> dict[str, Any]:
    prompt = PROMPT_TEMPLATES[version]["sentiment"].format(text=redact_pii(text))
    raw = _call_openai(prompt)
    try:
        return json.loads(raw)
    except Exception:
        return {"label": "neutral", "confidence": 0.0, "aspects": []}


def suggest_replies(
    text: str,
    tone: str = "friendly",
    language: str | None = None,
    brand_voice: dict[str, Any] | None = None,
    version: str = "v1",
) -> list[str]:
    if brand_voice is None:
        brand_voice = {}
    language = language or detect_language(text)
    prompt = PROMPT_TEMPLATES[version]["reply"].format(
        tone=tone,
        brand_tone=brand_voice.get("tone", ""),
        do=", ".join(brand_voice.get("do", [])),
        dont=", ".join(brand_voice.get("dont", [])),
        language=language,
        text=redact_pii(text),
    )
    raw = _call_openai(prompt)
    return [s.strip() for s in raw.split("\n") if s.strip()]


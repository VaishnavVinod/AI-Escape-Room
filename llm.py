"""Optional Gemini adapter; deterministic local narration is always available."""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()


def gemini_available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def generate(prompt: str, fallback: str, history: list[dict[str, str]] | None = None) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return fallback
    try:
        from google import genai
        client = genai.Client(api_key=key)
        context = "\n".join(f"{m['role']}: {m['content']}" for m in (history or [])[-12:])
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=f"{context}\n\n{prompt}" if context else prompt,
        )
        answer = (response.text or "").strip()
        return answer or fallback
    except Exception:
        return fallback

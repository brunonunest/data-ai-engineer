"""
=== SHARED CONFIGURATION ===
The foundation of every training mission.

This module handles:
- Loading your API key from a .env file (so it never leaks into code)
- Defining the base URL and endpoint for the OpenAI Chat Completions API
- Building the HTTP headers every request needs

Why a separate config module?
In production, you never hardcode secrets. Even in a learning exercise,
building this habit early saves you from accidentally committing keys.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level up from this file)
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

# --- API Key ---
# The OpenAI API uses Bearer token authentication.
# Every request must include an "Authorization: Bearer <key>" header.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not found.\n"
        "Copy .env.example to .env and add your key:\n"
        "  cp .env.example .env\n"
        "Then edit .env and paste your actual API key."
    )

# --- Endpoint ---
# The Chat Completions endpoint is the core of OpenAI's conversational API.
# All messages (system, user, assistant, tool) go through this single URL.
BASE_URL = "https://api.openai.com/v1"
CHAT_URL = f"{BASE_URL}/chat/completions"

# --- Model ---
# gpt-4o-mini: cheapest model that reliably supports tool calling.
# Swap to "gpt-4o" if you want stronger reasoning (at higher cost).
MODEL = "gpt-4o-mini"


def get_headers() -> dict:
    """
    Build the HTTP headers for an OpenAI API request.

    - Authorization: Bearer token authentication. The API checks this
      to identify your account and bill usage.
    - Content-Type: Tells the server we're sending JSON in the request body.
    """
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

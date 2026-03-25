"""
============================================================
  TRAINING MISSION 1: THE PADAWAN'S FIRST SWING
============================================================

  "Do. Or do not. There is no try." - Yoda

  OBJECTIVE:
  Send a single message to the OpenAI Chat Completions API
  using raw HTTP (httpx). No SDK. No magic. Just you, the
  protocol, and the Force.

  WHAT YOU'LL LEARN:
  - The anatomy of a Chat Completions request (URL, headers, body)
  - The message format: roles (system, user, assistant)
  - How to read the raw JSON response
  - Bearer token authentication
  - HTTP status codes that matter (200, 401, 429, 500)

============================================================
"""

import json
import httpx
from .config import CHAT_URL, MODEL, get_headers


def mission_1():
    print("=" * 60)
    print("  MISSION 1: THE PADAWAN'S FIRST SWING")
    print("  Sending your first raw API request...")
    print("=" * 60)
    print()

    # -----------------------------------------------------------------
    # STEP 1: Build the request payload
    # -----------------------------------------------------------------
    # The Chat Completions API expects a JSON body with:
    #   - "model": which LLM to use
    #   - "messages": an array of message objects, each with:
    #       - "role": one of "system", "user", or "assistant"
    #       - "content": the text of the message
    #
    # The "system" message sets the LLM's persona/behavior.
    # The "user" message is what you're asking.
    # The "assistant" role is for the LLM's previous replies (multi-turn).

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a wise Jedi Master who speaks with calm authority. "
                    "Answer questions about the galaxy, the Force, and the ways of the Jedi."
                ),
            },
            {
                "role": "user",
                "content": "What can you tell me about the Force?",
            },
        ],
    }

    print("[PAYLOAD] Sending to:", CHAT_URL)
    print("[PAYLOAD] Model:", MODEL)
    print("[PAYLOAD] Messages:")
    for msg in payload["messages"]:
        print(f"  [{msg['role'].upper()}] {msg['content'][:80]}...")
    print()

    # -----------------------------------------------------------------
    # STEP 2: Make the HTTP request
    # -----------------------------------------------------------------
    # This is what the OpenAI SDK does under the hood. We're doing it manually.
    #
    # httpx.post() sends an HTTP POST request with:
    #   - URL: the Chat Completions endpoint
    #   - headers: Authorization (Bearer token) + Content-Type (JSON)
    #   - json: automatically serializes our dict to JSON and sets the body
    #   - timeout: how long to wait before giving up (LLM calls can be slow)

    print("[HTTP] Sending POST request...")
    response = httpx.post(
        CHAT_URL,
        headers=get_headers(),
        json=payload,
        timeout=30.0,
    )

    # -----------------------------------------------------------------
    # STEP 3: Check for errors
    # -----------------------------------------------------------------
    # raise_for_status() throws an exception if the HTTP status code
    # indicates an error:
    #   - 401: Bad API key (check your .env)
    #   - 429: Rate limit exceeded (slow down or upgrade your plan)
    #   - 500: OpenAI server error (retry later)
    #   - 200: Success!

    print(f"[HTTP] Status Code: {response.status_code}")
    response.raise_for_status()
    print("[HTTP] Request successful!")
    print()

    # -----------------------------------------------------------------
    # STEP 4: Parse and inspect the raw response
    # -----------------------------------------------------------------
    # The response is JSON. Let's look at the FULL structure first,
    # because understanding this shape is the whole point of this mission.
    #
    # Key fields in the response:
    #   - choices[0].message.role -> "assistant"
    #   - choices[0].message.content -> the actual text response
    #   - choices[0].finish_reason -> "stop" means the model finished normally
    #   - usage.prompt_tokens -> tokens in your input
    #   - usage.completion_tokens -> tokens in the output
    #   - usage.total_tokens -> the bill (prompt + completion)

    data = response.json()

    print("[RAW RESPONSE] Full JSON from the API:")
    print("-" * 60)
    print(json.dumps(data, indent=2))
    print("-" * 60)
    print()

    # -----------------------------------------------------------------
    # STEP 5: Extract the assistant's message
    # -----------------------------------------------------------------
    # In production, this is the part you actually care about.
    # But knowing the full response structure helps you debug when
    # things go wrong (and they will).

    assistant_message = data["choices"][0]["message"]["content"]
    finish_reason = data["choices"][0]["finish_reason"]
    usage = data["usage"]

    print("[RESULT] The Jedi Master speaks:")
    print()
    print(assistant_message)
    print()
    print(f"[META] Finish reason: {finish_reason}")
    print(f"[META] Tokens used: {usage['prompt_tokens']} prompt + {usage['completion_tokens']} completion = {usage['total_tokens']} total")
    print()
    print("=" * 60)
    print("  MISSION 1 COMPLETE!")
    print("  You've made your first raw API call. The Force is with you.")
    print("  Next: Mission 2 - Constructing Your Lightsaber (tool calling)")
    print("=" * 60)


if __name__ == "__main__":
    mission_1()

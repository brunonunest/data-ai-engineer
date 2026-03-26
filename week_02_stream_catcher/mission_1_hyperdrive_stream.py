"""
============================================================
  TRAINING MISSION 1: THE HYPERDRIVE STREAM
============================================================

  "Punch it, Chewie!" - Han Solo

  OBJECTIVE:
  Make a STREAMING request to the Chat Completions API and
  parse raw Server-Sent Events (SSE) as they arrive. This is
  the difference between "wait 5 seconds then see everything"
  and "watch tokens appear as the model thinks."

  WHAT YOU'LL LEARN:
  - The "stream": True flag and how it changes the response
  - SSE wire format: "data: {...}" lines separated by blank lines
  - The "chat.completion.chunk" object vs "chat.completion"
  - The "delta" field (incremental content) vs "message" (full content)
  - The "data: [DONE]" sentinel that marks the end of the stream
  - How to parse and print tokens in real-time

  HOW STREAMING DIFFERS FROM NON-STREAMING:
  Non-streaming (Week 1):
    - Single JSON response after model finishes generating
    - response.json() gives you the complete message
    - choices[0].message.content = "The Force is..."

  Streaming (this mission):
    - Response body is a stream of SSE lines
    - Each line is a separate JSON chunk with a FRAGMENT of the response
    - choices[0].delta.content = "The" (one token at a time)
    - You must iterate and concatenate to build the full response

============================================================
"""

import json
import httpx
from .config import CHAT_URL, MODEL, get_headers


def mission_1():
    print("=" * 60)
    print("  MISSION 1: THE HYPERDRIVE STREAM")
    print("  Engaging the streaming hyperdrive...")
    print("=" * 60)
    print()

    # -----------------------------------------------------------------
    # STEP 1: Build the payload (same as Week 1, but with stream=True)
    # -----------------------------------------------------------------
    # The only difference from a non-streaming request is one field:
    #   "stream": True
    #
    # This tells the API to send the response as Server-Sent Events (SSE)
    # instead of a single JSON blob. The model starts sending tokens
    # immediately as it generates them.

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
        "stream": True,  # <-- THIS IS THE KEY CHANGE
    }

    print("[PAYLOAD] Model:", MODEL)
    print("[PAYLOAD] stream: True")
    print()

    # -----------------------------------------------------------------
    # STEP 2: Make a STREAMING HTTP request
    # -----------------------------------------------------------------
    # Instead of httpx.post() (which waits for the full response),
    # we use client.stream() which gives us an open connection we can
    # iterate over line by line.
    #
    # Think of it like this:
    #   httpx.post()    = "Call me when the ship has landed"
    #   client.stream() = "Give me the intercom so I can hear every update"
    #
    # The "with" block keeps the connection open while we read.

    print("[PHASE 1] Raw SSE lines from the API")
    print("-" * 60)
    print("(Showing the first 5 raw lines so you can see the SSE format)")
    print()

    raw_lines_shown = 0
    full_content = ""

    with httpx.Client() as client:
        with client.stream(
            "POST",
            CHAT_URL,
            headers=get_headers(),
            json=payload,
            timeout=30.0,
        ) as response:
            response.raise_for_status()

            # ---------------------------------------------------------
            # STEP 3: Iterate over SSE lines
            # ---------------------------------------------------------
            # The response body looks like this:
            #
            #   data: {"id":"chatcmpl-...","choices":[{"delta":{"role":"assistant"},...}]}
            #
            #   data: {"id":"chatcmpl-...","choices":[{"delta":{"content":"The"},...}]}
            #
            #   data: {"id":"chatcmpl-...","choices":[{"delta":{"content":" Force"},...}]}
            #
            #   data: [DONE]
            #
            # Key observations:
            # - Each event starts with "data: " prefix
            # - Blank lines separate events (we skip these)
            # - The payload is JSON, EXCEPT for the final "data: [DONE]"
            # - "delta" contains only the NEW content for this chunk

            for line in response.iter_lines():
                # Skip empty lines (SSE uses blank lines as event separators)
                if not line:
                    continue

                # Show first few raw lines for educational purposes
                if raw_lines_shown < 5:
                    print(f"  RAW: {line}")
                    raw_lines_shown += 1
                    if raw_lines_shown == 5:
                        print("  ... (remaining lines parsed silently)")
                        print()

                # -------------------------------------------------
                # STEP 4: Parse each SSE line
                # -------------------------------------------------
                # The "data: [DONE]" line is a sentinel, NOT valid JSON.
                # You MUST filter it out before trying json.loads().
                # This is a common gotcha that crashes beginners' code.

                if not line.startswith("data: "):
                    continue

                data_str = line[len("data: "):]  # Strip the "data: " prefix

                if data_str == "[DONE]":
                    # Stream is complete. The model has finished generating.
                    break

                # Parse the JSON chunk
                chunk = json.loads(data_str)

                # -------------------------------------------------
                # STEP 5: Extract the delta content
                # -------------------------------------------------
                # In streaming mode, the response object type changes:
                #   Non-streaming: "chat.completion"     -> message.content
                #   Streaming:     "chat.completion.chunk" -> delta.content
                #
                # "delta" means "what's new in this chunk."
                #
                # The FIRST chunk usually has delta.role = "assistant"
                # but no content. Subsequent chunks have delta.content
                # with one or a few tokens each.

                delta = chunk["choices"][0]["delta"]
                finish_reason = chunk["choices"][0].get("finish_reason")

                content = delta.get("content", "")
                if content:
                    full_content += content

    # -----------------------------------------------------------------
    # STEP 6: Show the assembled result
    # -----------------------------------------------------------------
    print()
    print("-" * 60)
    print()
    print("[PHASE 2] Streaming output (tokens as they arrive)")
    print("-" * 60)

    # Now let's do it again, but this time print tokens live.
    # This is what a real chat UI does -- show each token immediately.

    print()
    print("[STREAM] ", end="", flush=True)

    with httpx.Client() as client:
        with client.stream(
            "POST",
            CHAT_URL,
            headers=get_headers(),
            json=payload,
            timeout=30.0,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue

                data_str = line[len("data: "):]
                if data_str == "[DONE]":
                    break

                chunk = json.loads(data_str)
                delta = chunk["choices"][0]["delta"]
                content = delta.get("content", "")

                if content:
                    # Print each token immediately, no newline, flush the buffer
                    # This creates the "typing" effect you see in ChatGPT
                    print(content, end="", flush=True)

    print()  # Final newline after the stream
    print()

    # -----------------------------------------------------------------
    # STEP 7: Explain what just happened
    # -----------------------------------------------------------------
    print("=" * 60)
    print("  WHAT JUST HAPPENED:")
    print("=" * 60)
    print()
    print("  Phase 1: We showed the raw SSE lines from the API.")
    print("  Each line is a JSON chunk with a small piece of the response.")
    print()
    print("  Phase 2: We printed tokens as they arrived.")
    print("  Instead of waiting for the full response, you saw each token")
    print("  appear in real-time -- just like ChatGPT's typing effect.")
    print()
    print("  KEY DIFFERENCES from non-streaming (Week 1):")
    print("    - Response type: 'chat.completion.chunk' (not 'chat.completion')")
    print("    - Field name: 'delta' (not 'message')")
    print("    - Content: one token per chunk (not the full text)")
    print("    - End signal: 'data: [DONE]' (not just a JSON response)")
    print()
    print("=" * 60)
    print("  MISSION 1 COMPLETE!")
    print("  You've tapped into the hyperdrive stream.")
    print("  Next: Mission 2 - The Relay Station (FastAPI + SSE to browser)")
    print("=" * 60)


if __name__ == "__main__":
    mission_1()

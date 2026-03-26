"""
============================================================
  TRAINING MISSION 2: THE RELAY STATION
============================================================

  "Stay on target..." - Gold Five

  OBJECTIVE:
  Build a FastAPI server that acts as a relay station between
  the browser and the OpenAI API. The server receives a user
  message, streams the LLM response from OpenAI, and re-emits
  each token to the browser as Server-Sent Events (SSE).

  WHAT YOU'LL LEARN:
  - FastAPI basics: routes, request handling, StreamingResponse
  - Async httpx: why you need AsyncClient inside a server
  - SSE wire format: "data: <payload>\n\n" (double newline!)
  - How to build an async generator that yields SSE events
  - Browser-side stream consumption with fetch() + ReadableStream
  - Why EventSource (GET-only) doesn't work for POST endpoints

  THE BIG PICTURE:
  This is exactly what ChatGPT's backend does:
    Browser -> Your Server -> OpenAI API
                 (relay)
  Your server receives the stream from OpenAI and re-emits it
  to the browser. The browser shows tokens as they arrive.

============================================================
"""

import json
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse

from .config import CHAT_URL, MODEL, get_headers


# -----------------------------------------------------------------
# STEP 1: Create the FastAPI app
# -----------------------------------------------------------------
# FastAPI is built on Starlette (ASGI framework).
# ASGI = Asynchronous Server Gateway Interface -- it supports async/await
# and long-lived connections like SSE and WebSockets.
#
# For streaming, we need async because:
# - The connection to OpenAI is open while tokens generate (could be seconds)
# - The connection to the browser is open while we relay tokens
# - We can't block the entire server on one request

app = FastAPI(title="The Relay Station", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "static"


# -----------------------------------------------------------------
# STEP 2: Serve the browser client
# -----------------------------------------------------------------
# A simple HTML page that connects to our streaming endpoint.
# We serve it from the same origin to avoid CORS issues.

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


# -----------------------------------------------------------------
# STEP 3: The streaming chat endpoint
# -----------------------------------------------------------------
# This is the core of the relay station.
#
# Flow:
#   1. Browser sends POST with {"message": "..."}
#   2. Server opens a streaming connection to OpenAI
#   3. For each token from OpenAI, server emits an SSE event to browser
#   4. Browser reads each event and appends the token to the page
#
# We return a StreamingResponse with an async generator.
# StreamingResponse keeps the HTTP connection open and sends data
# as our generator yields it.

@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    if not user_message:
        return {"error": "No message provided"}

    # Build the OpenAI payload -- same as Mission 1 but inside a server
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
                "content": user_message,
            },
        ],
        "stream": True,
    }

    async def event_generator():
        """
        Async generator that:
        1. Opens a streaming connection to OpenAI
        2. Parses each SSE chunk from OpenAI
        3. Re-emits it as an SSE event to the browser

        SSE wire format requires:
          "data: <payload>\n\n"
        The double newline (\n\n) is CRITICAL -- it tells the browser
        "this event is complete." A single \n is just a line break
        within the same event.
        """
        # ---------------------------------------------------------
        # ASYNC httpx: Why AsyncClient?
        # ---------------------------------------------------------
        # Inside a FastAPI endpoint (which runs in an async event loop),
        # you MUST use async HTTP calls. Sync httpx.Client() would block
        # the entire event loop, freezing ALL requests -- not just this one.
        #
        # httpx.AsyncClient is the async equivalent:
        #   sync:  httpx.Client().stream("POST", ...)
        #   async: httpx.AsyncClient().stream("POST", ...)
        #
        # Same API, but uses await and async for under the hood.

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                CHAT_URL,
                headers=get_headers(),
                json=payload,
                timeout=60.0,
            ) as response:
                # -------------------------------------------------
                # Iterate over SSE lines from OpenAI
                # -------------------------------------------------
                # aiter_lines() is the async version of iter_lines().
                # Each line is one SSE data line from the OpenAI stream.

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[len("data: "):]

                    if data_str == "[DONE]":
                        # Signal the browser that the stream is complete
                        yield "data: [DONE]\n\n"
                        return

                    # Parse the chunk from OpenAI
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0]["delta"]
                    content = delta.get("content", "")

                    if content:
                        # -----------------------------------------
                        # Re-emit as SSE to the browser
                        # -----------------------------------------
                        # We wrap the content in our own JSON envelope.
                        # The browser will parse this to extract the token.
                        #
                        # Format: "data: {"content": "The"}\n\n"
                        #
                        # Why JSON and not raw text? Because SSE data
                        # fields can't contain newlines easily. JSON
                        # encoding handles escaping for us.

                        event = json.dumps({"content": content})
                        yield f"data: {event}\n\n"

    # Return a StreamingResponse with our async generator
    # media_type="text/event-stream" tells the browser this is SSE
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            # Prevent buffering/caching that would delay events
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# -----------------------------------------------------------------
# STEP 4: Run the server
# -----------------------------------------------------------------
# When you run: python -m week_02_stream_catcher.mission_2_relay_station
# This starts uvicorn (the ASGI server) which serves our FastAPI app.
#
# Visit http://localhost:8000 to see the browser client.

def mission_2():
    print("=" * 60)
    print("  MISSION 2: THE RELAY STATION")
    print("  Starting the relay station server...")
    print("=" * 60)
    print()
    print("  Open your browser to: http://localhost:8000")
    print("  Type a message and watch tokens stream in real-time!")
    print()
    print("  Press Ctrl+C to shut down the relay station.")
    print("=" * 60)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    mission_2()

"""
============================================================
  TRAINING MISSION 3: THE KYBER CRYSTAL ASSEMBLY
============================================================

  "The crystal is the heart of the blade." - Jedi proverb

  OBJECTIVE:
  Handle streaming tool calls -- the hardest part of the
  streaming protocol. When stream=True and the model decides
  to call tools, the function arguments arrive as PARTIAL
  JSON FRAGMENTS across multiple chunks. You must accumulate
  them, detect completion, execute tools, and continue the
  conversation loop -- all while streaming SSE to the browser.

  THIS IS AN INTERVIEW-LEVEL CHALLENGE.
  If you understand this, you understand what every AI
  framework hides from you.

  WHAT YOU'LL LEARN:
  - How OpenAI streams tool calls (delta.tool_calls fragments)
  - The accumulation dict pattern (keyed by tool_call index)
  - Why arguments come as broken JSON strings you can't parse yet
  - How multiple tool calls interleave by index in the same stream
  - Reconstructing the full assistant message for conversation history
  - The complete streaming tool-use loop with SSE output

  HOW STREAMING TOOL CALLS DIFFER FROM NON-STREAMING:

  Non-streaming (Week 1 Mission 3):
    - tool_calls is a complete array in the response
    - arguments is a complete JSON string you can parse immediately
    - One response = all tool calls at once

  Streaming (this mission):
    - tool_calls arrive as FRAGMENTS across many chunks
    - First chunk: index, id, name, start of arguments ("")
    - Next chunks: index + argument fragment ("{\"na")
    - Next chunks: index + argument fragment ("me\":")
    - ...until finish_reason == "tool_calls"
    - Multiple tools interleave by index in the same stream
    - You must ACCUMULATE fragments before you can json.loads()

============================================================
"""

import json
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse

from .config import CHAT_URL, MODEL, get_headers
from .sw_tools import TOOLS, execute_tool_call


# Maximum rounds of tool calling before we bail out.
# Same safety valve as Week 1 Mission 3, but now in a streaming context.
MAX_ROUNDS = 5

app = FastAPI(title="The Kyber Crystal Assembly", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    if not user_message:
        return {"error": "No message provided"}

    # Build the conversation messages (same pattern as Week 1 Mission 3)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a droid assistant with access to galactic databases. "
                "Use your tools to look up accurate information before answering. "
                "Do not guess -- always use tools when relevant data is available."
            ),
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    async def event_generator():
        """
        The full streaming tool-use loop, emitting SSE events to the browser.

        This generator handles TWO types of streaming responses:
        1. TEXT streaming: delta.content tokens -> emit to browser immediately
        2. TOOL CALL streaming: delta.tool_calls fragments -> accumulate silently,
           execute when complete, then loop for another streaming request
        """
        nonlocal messages

        for round_num in range(1, MAX_ROUNDS + 1):

            # ---------------------------------------------------------
            # Build the streaming request payload
            # ---------------------------------------------------------
            # Same as non-streaming, but with "stream": True.
            # We include "tools" so the model can decide to call them.
            payload = {
                "model": MODEL,
                "messages": messages,
                "tools": TOOLS,
                "stream": True,
            }

            # Track what we accumulate from this streaming response
            accumulated_content = ""
            tool_calls_accumulator = {}
            finish_reason = None

            # ---------------------------------------------------------
            # Open the streaming connection to OpenAI
            # ---------------------------------------------------------
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    CHAT_URL,
                    headers=get_headers(),
                    json=payload,
                    timeout=60.0,
                ) as response:
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue

                        data_str = line[len("data: "):]
                        if data_str == "[DONE]":
                            break

                        chunk = json.loads(data_str)
                        choice = chunk["choices"][0]
                        delta = choice["delta"]
                        finish_reason = choice.get("finish_reason")

                        # -----------------------------------------
                        # CASE 1: Text content (normal streaming)
                        # -----------------------------------------
                        # Same as Mission 2 -- just yield the token
                        # to the browser immediately.
                        content = delta.get("content", "")
                        if content:
                            accumulated_content += content
                            event = json.dumps({"content": content})
                            yield f"data: {event}\n\n"

                        # -----------------------------------------
                        # CASE 2: Tool call fragments
                        # -----------------------------------------
                        # THIS IS THE HARD PART.
                        #
                        # When the model decides to call tools while
                        # streaming, the chunks look like this:
                        #
                        # Chunk 1 (first fragment for tool index 0):
                        #   delta.tool_calls = [{
                        #     "index": 0,
                        #     "id": "call_abc123",
                        #     "type": "function",
                        #     "function": {
                        #       "name": "get_planet_info",
                        #       "arguments": ""
                        #     }
                        #   }]
                        #
                        # Chunk 2 (argument fragment for index 0):
                        #   delta.tool_calls = [{
                        #     "index": 0,
                        #     "function": {"arguments": "{\"na"}
                        #   }]
                        #
                        # Chunk 3:
                        #   delta.tool_calls = [{
                        #     "index": 0,
                        #     "function": {"arguments": "me\":"}
                        #   }]
                        #
                        # ...and so on until finish_reason == "tool_calls"
                        #
                        # KEY OBSERVATIONS:
                        # 1. The "id" and "name" only appear in the FIRST
                        #    chunk for each tool call index
                        # 2. Subsequent chunks only have "index" and
                        #    "function.arguments" (a small string fragment)
                        # 3. The arguments are BROKEN JSON -- you CANNOT
                        #    parse them until all fragments are concatenated
                        # 4. Multiple tool calls interleave by index:
                        #    index 0 fragments, index 1 fragments, etc.
                        # 5. There is NO per-tool completion signal --
                        #    finish_reason == "tool_calls" means ALL are done

                        if "tool_calls" in delta:
                            for tc_delta in delta["tool_calls"]:
                                idx = tc_delta["index"]

                                if idx not in tool_calls_accumulator:
                                    # ---------------------------------
                                    # First chunk for this tool index
                                    # ---------------------------------
                                    # Contains id, type, name, and the
                                    # START of arguments (often "").
                                    tool_calls_accumulator[idx] = {
                                        "id": tc_delta["id"],
                                        "type": tc_delta.get("type", "function"),
                                        "function": {
                                            "name": tc_delta["function"]["name"],
                                            "arguments": tc_delta["function"].get("arguments", ""),
                                        },
                                    }
                                else:
                                    # ---------------------------------
                                    # Subsequent chunk -- concatenate
                                    # ---------------------------------
                                    # Only has index + argument fragment.
                                    # We APPEND to the existing string.
                                    tool_calls_accumulator[idx]["function"]["arguments"] += (
                                        tc_delta["function"]["arguments"]
                                    )

            # ---------------------------------------------------------
            # Process the completed streaming response
            # ---------------------------------------------------------

            # CASE A: Model finished with text (no tool calls)
            if finish_reason == "stop":
                # Append assistant message to history (for completeness)
                messages.append({
                    "role": "assistant",
                    "content": accumulated_content,
                })
                # Signal the browser that the stream is done
                yield "data: [DONE]\n\n"
                return

            # CASE B: Model wants to call tools
            if finish_reason == "tool_calls" and tool_calls_accumulator:
                # -------------------------------------------------
                # CRITICAL: Reconstruct the full assistant message
                # -------------------------------------------------
                # The non-streaming API gives you the complete message.
                # With streaming, YOU must rebuild it from accumulated
                # fragments. This message MUST go into the conversation
                # history (just like Week 1 Mission 3) BEFORE adding
                # tool results, or the next API call will fail with 400.
                #
                # The format must match exactly what the non-streaming
                # API would have returned:
                #   {
                #     "role": "assistant",
                #     "content": null,
                #     "tool_calls": [
                #       {"id": "...", "type": "function", "function": {"name": "...", "arguments": "..."}}
                #     ]
                #   }

                tool_calls_list = [
                    tool_calls_accumulator[idx]
                    for idx in sorted(tool_calls_accumulator.keys())
                ]

                assistant_msg = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls_list,
                }
                messages.append(assistant_msg)

                # -------------------------------------------------
                # Execute each tool and append results
                # -------------------------------------------------
                # Same pattern as Week 1 Mission 3, but we also
                # emit status events to the browser so it's not
                # sitting in silence during tool execution.

                for tc in tool_calls_list:
                    fn_name = tc["function"]["name"]
                    fn_args = json.loads(tc["function"]["arguments"])
                    call_id = tc["id"]

                    # Tell the browser what's happening
                    status = json.dumps({
                        "status": f"[Tool] Executing {fn_name}({json.dumps(fn_args)})..."
                    })
                    yield f"data: {status}\n\n"

                    # Execute the mock tool
                    result = execute_tool_call(fn_name, fn_args)

                    # Append the tool result to conversation history
                    # (same protocol as Week 1 Mission 3)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": result,
                    })

                # Loop continues -- next iteration sends updated
                # messages back to the API for the next response
                # (which might be text or more tool calls)
                continue

            # CASE C: Unexpected finish_reason or empty accumulator
            # with tool_calls finish -- bail out
            error = json.dumps({
                "status": f"[Warning] Unexpected finish_reason: {finish_reason}"
            })
            yield f"data: {error}\n\n"
            yield "data: [DONE]\n\n"
            return

        # If we exhaust MAX_ROUNDS
        warning = json.dumps({
            "status": f"[Warning] Reached maximum rounds ({MAX_ROUNDS}). Stopping."
        })
        yield f"data: {warning}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# -----------------------------------------------------------------
# Terminal mode: also run the full loop in the terminal
# -----------------------------------------------------------------
# When run directly, this does the streaming tool loop in the
# terminal (like Mission 1) AND starts the server (like Mission 2).

def mission_3():
    print("=" * 60)
    print("  MISSION 3: THE KYBER CRYSTAL ASSEMBLY")
    print("  Streaming tool calls -- the ultimate test...")
    print("=" * 60)
    print()
    print("  The server is starting with tool-calling support.")
    print("  Open your browser to: http://localhost:8000")
    print()
    print("  Try these prompts to test different paths:")
    print("    - 'Hello there!' (text only, no tools)")
    print("    - 'What planet is Luke Skywalker from?' (single tool)")
    print("    - 'Compare the Millennium Falcon with an X-Wing and")
    print("       tell me about the planet Hoth' (multiple tools)")
    print()
    print("  Watch the status events as tools execute!")
    print("  Press Ctrl+C to shut down.")
    print("=" * 60)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    mission_3()

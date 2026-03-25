"""
============================================================
  TRAINING MISSION 3: CLOSING THE HOLOCRON LOOP
============================================================

  "The circle is now complete." - Darth Vader

  OBJECTIVE:
  Build the FULL tool-use cycle:
    1. Send user message + tool definitions
    2. LLM returns tool_call(s)
    3. Execute the mock tools locally
    4. Send the results back to the LLM
    5. LLM produces the final answer (or calls more tools)

  This is the most important pattern in AI engineering.
  Every agent framework (LangChain, CrewAI, etc.) is just
  a wrapper around this loop. If you understand this,
  you understand them all.

  WHAT YOU'LL LEARN:
  - The complete tool-use protocol flow
  - Why you MUST append the assistant message (with tool_calls) to history
  - How tool_call_id links results to their calls
  - Handling multiple tool calls in a single response
  - The while loop pattern with finish_reason checking
  - Safety valves to prevent infinite loops

============================================================
"""

import json
import httpx
from .config import CHAT_URL, MODEL, get_headers
from .sw_tools import TOOLS, execute_tool_call

# Maximum rounds of tool calling before we bail out.
# Safety valve -- in production, runaway loops are expensive and dangerous.
MAX_ROUNDS = 5


def mission_3():
    print("=" * 60)
    print("  MISSION 3: CLOSING THE HOLOCRON LOOP")
    print("  The complete tool-use cycle begins...")
    print("=" * 60)
    print()

    # -----------------------------------------------------------------
    # STEP 1: Set up the conversation
    # -----------------------------------------------------------------
    # This prompt is designed to trigger MULTIPLE tool calls.
    # Comparing two ships requires two get_starship_specs calls,
    # and asking about planets may trigger get_planet_info calls.
    # The model should chain these together.

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
            "content": (
                "Compare the Millennium Falcon with an X-Wing starfighter. "
                "Also, tell me about the planet Tatooine and search the Jedi Archives "
                "for information about the Force."
            ),
        },
    ]

    print("[CONVERSATION] Starting messages:")
    for msg in messages:
        print(f"  [{msg['role'].upper()}] {msg['content'][:80]}...")
    print()

    # -----------------------------------------------------------------
    # STEP 2: THE LOOP
    # -----------------------------------------------------------------
    # This is the core pattern. We keep sending messages to the API
    # until the model says "stop" (I'm done) instead of "tool_calls"
    # (I need to call tools).
    #
    # Flow:
    #   User message -> API -> tool_calls -> execute -> tool results -> API -> ...
    #                                                                    ... -> "stop" -> done

    for round_num in range(1, MAX_ROUNDS + 1):
        print(f"[ROUND {round_num}] Sending {len(messages)} messages to the API...")

        response = httpx.post(
            CHAT_URL,
            headers=get_headers(),
            json={
                "model": MODEL,
                "messages": messages,
                "tools": TOOLS,
            },
            timeout=60.0,  # Longer timeout -- multi-tool responses take time
        )
        response.raise_for_status()
        data = response.json()

        assistant_msg = data["choices"][0]["message"]
        finish_reason = data["choices"][0]["finish_reason"]

        print(f"[ROUND {round_num}] finish_reason: {finish_reason}")

        # ---------------------------------------------------------
        # CRITICAL STEP: Append the assistant's message to history
        # ---------------------------------------------------------
        # You MUST add the full assistant message (including its tool_calls)
        # to the messages list BEFORE adding tool results.
        #
        # Why? The API requires conversation history to be consistent.
        # Each tool result message references a tool_call_id that must
        # exist in a previous assistant message. If you skip this step,
        # the API will reject your request with a 400 error.

        messages.append(assistant_msg)

        # ---------------------------------------------------------
        # Check: Is the model done?
        # ---------------------------------------------------------
        if finish_reason == "stop":
            print(f"[ROUND {round_num}] Model finished. Extracting final answer...")
            print()
            print("=" * 60)
            print("  FINAL ANSWER FROM THE DROID:")
            print("=" * 60)
            print()
            print(assistant_msg.get("content", "(no content)"))
            print()
            break

        # ---------------------------------------------------------
        # Process tool calls
        # ---------------------------------------------------------
        if finish_reason == "tool_calls" and assistant_msg.get("tool_calls"):
            tool_calls = assistant_msg["tool_calls"]
            print(f"[ROUND {round_num}] Model requested {len(tool_calls)} tool call(s):")
            print()

            for tool_call in tool_calls:
                fn_name = tool_call["function"]["name"]
                # REMEMBER: arguments is a JSON string, must parse it
                fn_args = json.loads(tool_call["function"]["arguments"])
                call_id = tool_call["id"]

                print(f"  Executing: {fn_name}({fn_args})")

                # Execute the mock tool
                result = execute_tool_call(fn_name, fn_args)

                print(f"  Result: {result[:100]}{'...' if len(result) > 100 else ''}")
                print()

                # -------------------------------------------------
                # Append the tool result to the conversation
                # -------------------------------------------------
                # The tool result message requires:
                #   - "role": "tool" (not "user" or "assistant")
                #   - "tool_call_id": must match the id from the tool_call
                #   - "content": the result as a string
                #
                # The tool_call_id is what links this result back to
                # the specific call. This matters when the model makes
                # multiple tool calls in one response -- each result
                # must be matched to its call.

                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": result,
                })

            print(f"[ROUND {round_num}] All tool results sent. Looping back to the API...")
            print()
        else:
            # Unexpected finish_reason -- bail out
            print(f"[ROUND {round_num}] Unexpected finish_reason: {finish_reason}")
            print(f"[ROUND {round_num}] Response: {json.dumps(assistant_msg, indent=2)}")
            break
    else:
        # This runs if the for loop completes without breaking (hit MAX_ROUNDS)
        print(f"[WARNING] Reached maximum rounds ({MAX_ROUNDS}). Stopping to prevent infinite loop.")
        print("[WARNING] The model may not have finished. Check your tool definitions and prompts.")

    # -----------------------------------------------------------------
    # STEP 3: Show the full conversation trace
    # -----------------------------------------------------------------
    print()
    print("=" * 60)
    print("  FULL CONVERSATION TRACE")
    print("  (Every message exchanged with the API)")
    print("=" * 60)

    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown").upper()
        if role == "TOOL":
            print(f"\n  [{i}] TOOL (call_id: {msg.get('tool_call_id', '?')}):")
            print(f"      {msg['content'][:120]}{'...' if len(msg['content']) > 120 else ''}")
        elif role == "ASSISTANT" and msg.get("tool_calls"):
            print(f"\n  [{i}] ASSISTANT (requesting tools):")
            for tc in msg["tool_calls"]:
                print(f"      -> {tc['function']['name']}({tc['function']['arguments']})")
        elif role == "ASSISTANT":
            content = msg.get("content", "")
            print(f"\n  [{i}] ASSISTANT:")
            print(f"      {content[:120]}{'...' if len(content) > 120 else ''}")
        else:
            content = msg.get("content", "")
            print(f"\n  [{i}] {role}: {content[:100]}{'...' if len(content) > 100 else ''}")

    print()
    print("=" * 60)
    print("  MISSION 3 COMPLETE!")
    print("  The loop is closed. You now understand the full tool-use protocol.")
    print()
    print("  WEEK 1 COMPLETE! You've earned the rank of Padawan.")
    print("  Next week: The Stream Catcher (SSE streaming with FastAPI)")
    print("=" * 60)


if __name__ == "__main__":
    mission_3()

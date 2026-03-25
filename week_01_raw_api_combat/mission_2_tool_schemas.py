"""
============================================================
  TRAINING MISSION 2: CONSTRUCTING YOUR LIGHTSABER
============================================================

  "This weapon is your life." - Obi-Wan Kenobi

  OBJECTIVE:
  Send tool definitions (raw JSON Schemas) to the LLM and
  observe it decide to call a tool. We DON'T execute the tool
  yet -- we just watch the model's decision-making.

  WHAT YOU'LL LEARN:
  - How to pass tools to the Chat Completions API
  - The JSON Schema format for tool parameters
  - How the response changes when the model wants to call a tool:
    * content becomes null
    * tool_calls array appears
    * Each tool_call has: id, function.name, function.arguments
  - The arguments come as a JSON STRING, not a parsed object
  - The tool_choice parameter and its options

============================================================
"""

import json
import httpx
from .config import CHAT_URL, MODEL, get_headers
from .sw_tools import TOOLS


def mission_2():
    print("=" * 60)
    print("  MISSION 2: CONSTRUCTING YOUR LIGHTSABER")
    print("  Teaching the LLM about your tools...")
    print("=" * 60)
    print()

    # -----------------------------------------------------------------
    # STEP 1: Review the tool schemas we're sending
    # -----------------------------------------------------------------
    # These are the raw JSON Schema definitions from sw_tools.py.
    # The LLM reads these to understand:
    #   - What tools exist (by name)
    #   - What each tool does (via description)
    #   - What parameters each tool accepts (via parameters schema)
    #
    # Good descriptions = better tool selection by the model.
    # This is prompt engineering for tools.

    print("[TOOLS] Sending these tool definitions to the model:")
    for tool in TOOLS:
        fn = tool["function"]
        print(f"  - {fn['name']}: {fn['description'][:60]}...")
    print()

    # -----------------------------------------------------------------
    # STEP 2: Build a request that should trigger a tool call
    # -----------------------------------------------------------------
    # The user message is crafted to clearly match one of our tools.
    # "What are the specs of the Millennium Falcon?" should trigger
    # the get_starship_specs tool.
    #
    # Notice the new "tools" field in the payload. This is how you
    # tell the API about available tools. Without this field, the model
    # can only respond with text.
    #
    # "tool_choice" controls when the model calls tools:
    #   - "auto" (default): model decides whether to call a tool or respond with text
    #   - "required": model MUST call at least one tool
    #   - "none": model cannot call tools (text-only response)
    #   - {"type": "function", "function": {"name": "..."}}: force a specific tool

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a droid assistant with access to the Jedi Archives "
                    "and galactic databases. Use your tools to answer questions accurately."
                ),
            },
            {
                "role": "user",
                "content": "What are the specs of the Millennium Falcon?",
            },
        ],
        "tools": TOOLS,
        # tool_choice defaults to "auto" -- the model decides.
        # Uncomment the line below to force tool use:
        # "tool_choice": "required",
    }

    print("[HTTP] Sending request with tools...")
    response = httpx.post(
        CHAT_URL,
        headers=get_headers(),
        json=payload,
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()

    print(f"[HTTP] Status: {response.status_code}")
    print()

    # -----------------------------------------------------------------
    # STEP 3: Inspect the raw response
    # -----------------------------------------------------------------
    # When the model decides to call a tool, the response looks DIFFERENT
    # from a normal text response:
    #
    # Normal response:
    #   choices[0].message.content = "The Millennium Falcon is..."
    #   choices[0].finish_reason = "stop"
    #
    # Tool-calling response:
    #   choices[0].message.content = null
    #   choices[0].message.tool_calls = [ { id, type, function: {name, arguments} } ]
    #   choices[0].finish_reason = "tool_calls"

    print("[RAW RESPONSE] Full JSON:")
    print("-" * 60)
    print(json.dumps(data, indent=2))
    print("-" * 60)
    print()

    # -----------------------------------------------------------------
    # STEP 4: Parse the tool call(s)
    # -----------------------------------------------------------------
    assistant_msg = data["choices"][0]["message"]
    finish_reason = data["choices"][0]["finish_reason"]

    print(f"[ANALYSIS] finish_reason: {finish_reason}")
    print(f"[ANALYSIS] content: {assistant_msg.get('content')}")
    print()

    if finish_reason == "tool_calls" and assistant_msg.get("tool_calls"):
        print("[TOOL CALLS] The model wants to call these tools:")
        print()

        for i, tool_call in enumerate(assistant_msg["tool_calls"]):
            print(f"  Tool Call #{i + 1}:")
            print(f"    ID:        {tool_call['id']}")
            print(f"    Type:      {tool_call['type']}")
            print(f"    Function:  {tool_call['function']['name']}")

            # IMPORTANT: arguments is a JSON STRING, not a dict!
            # You must json.loads() it to get the actual parameters.
            # This is a common gotcha that trips people up.
            raw_args = tool_call["function"]["arguments"]
            print(f"    Arguments (raw string): {raw_args}")

            parsed_args = json.loads(raw_args)
            print(f"    Arguments (parsed):     {parsed_args}")
            print()

        print("  NOTE: We received the tool call but did NOT execute it.")
        print("  That's Mission 3's job -- closing the loop.")
    else:
        # Sometimes the model responds with text instead of calling a tool.
        # This can happen with "auto" tool_choice if the model thinks
        # it can answer without tools.
        print("[INFO] The model responded with text instead of a tool call:")
        print(assistant_msg.get("content", "(no content)"))
        print()
        print("  TIP: Try changing tool_choice to 'required' to force tool use.")

    print()
    print("=" * 60)
    print("  MISSION 2 COMPLETE!")
    print("  You've assembled your lightsaber -- the tool schemas are set.")
    print("  Next: Mission 3 - Closing the Holocron Loop (full tool execution)")
    print("=" * 60)


if __name__ == "__main__":
    mission_2()

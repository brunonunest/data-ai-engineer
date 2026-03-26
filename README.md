# AI Engineering Path - Phase 1: The "No Magic" Zone

> "Your eyes can deceive you. Don't trust them." - Obi-Wan Kenobi
>
> The same applies to AI frameworks. If you can't build it raw, you can't debug it in production.

## Week 1: Raw API Combat

Three training missions that teach you to communicate with LLMs using raw HTTP. No SDKs, no LangChain, no magic.

| Mission | Name | What You'll Learn |
|---------|------|-------------------|
| 1 | The Padawan's First Swing | Raw HTTP call to Chat Completions, response anatomy |
| 2 | Constructing Your Lightsaber | Tool schemas (JSON Schema), observing tool_calls |
| 3 | Closing the Holocron Loop | Full tool-use cycle: call -> execute -> respond -> repeat |

## Week 2: The Stream Catcher

Three training missions that teach you to stream LLM responses in real-time. Build a FastAPI backend, parse SSE chunks, and tackle the hardest part: accumulating streamed tool call fragments.

| Mission | Name | What You'll Learn |
|---------|------|-------------------|
| 1 | The Hyperdrive Stream | Raw SSE parsing, `stream: true`, delta vs message, `data: [DONE]` sentinel |
| 2 | The Relay Station | FastAPI + StreamingResponse, async httpx, SSE proxy to browser |
| 3 | The Kyber Crystal Assembly | Streaming tool call accumulation, partial JSON fragments, full loop |

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -e .

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Run the Missions

From the project root:

```bash
# --- Week 1: Raw API Combat ---
python -m week_01_raw_api_combat.mission_1_first_swing
python -m week_01_raw_api_combat.mission_2_tool_schemas
python -m week_01_raw_api_combat.mission_3_tool_loop

# --- Week 2: The Stream Catcher ---
python -m week_02_stream_catcher.mission_1_hyperdrive_stream
python -m week_02_stream_catcher.mission_2_relay_station      # starts server on :8000
python -m week_02_stream_catcher.mission_3_kyber_crystal_assembly  # starts server on :8000
```

## Project Structure

```
week_01_raw_api_combat/
  config.py           - API key, headers, endpoint URL
  sw_tools.py         - Star Wars tool schemas + mock implementations
  mission_1_*.py      - Raw API call (simplest interaction)
  mission_2_*.py      - Tool schemas + observing tool_calls
  mission_3_*.py      - Full tool-use response loop

week_02_stream_catcher/
  config.py           - Same config (independent copy)
  sw_tools.py         - Same tools (independent copy)
  mission_1_*.py      - Raw SSE parsing in the terminal
  mission_2_*.py      - FastAPI SSE proxy to browser
  mission_3_*.py      - Streaming tool call accumulation (the hard one)
  static/index.html   - Minimal browser client
```

## Dependencies

Minimal. That's the point.

- `httpx` - HTTP client (replaces the SDK)
- `python-dotenv` - Loads .env files (keeps secrets out of code)
- `fastapi` - ASGI web framework (Week 2+)
- `uvicorn` - ASGI server to run FastAPI (Week 2+)

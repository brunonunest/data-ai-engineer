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

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -e .
# Or directly: pip install httpx python-dotenv

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Run the Missions

From the project root:

```bash
# Mission 1: Your first raw API call
python -m week_01_raw_api_combat.mission_1_first_swing

# Mission 2: Tool calling with JSON schemas
python -m week_01_raw_api_combat.mission_2_tool_schemas

# Mission 3: The complete tool-use loop
python -m week_01_raw_api_combat.mission_3_tool_loop
```

## Project Structure

```
week_01_raw_api_combat/
  config.py           - API key, headers, endpoint URL (shared foundation)
  sw_tools.py         - Star Wars tool schemas + mock implementations
  mission_1_*.py      - Raw API call (simplest interaction)
  mission_2_*.py      - Tool schemas + observing tool_calls
  mission_3_*.py      - Full tool-use response loop
```

## Dependencies

Only two. That's the point.

- `httpx` - HTTP client (replaces the SDK)
- `python-dotenv` - Loads .env files (keeps secrets out of code)

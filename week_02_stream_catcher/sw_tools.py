"""
=== STAR WARS TOOLS ===
The weapons in your arsenal, young Padawan.

This module contains two things:
1. TOOL DEFINITIONS - Raw JSON Schema dicts that tell the LLM what tools exist
   and how to call them. These are sent in the API request under the "tools" key.
   No Pydantic, no fancy abstractions -- just plain Python dicts matching the
   OpenAI tool-calling format.

2. MOCK IMPLEMENTATIONS - Simple Python functions that "execute" the tools locally.
   In production these would call databases, APIs, or services. Here they return
   hardcoded Star Wars data so we can focus on the protocol, not the plumbing.
"""

import json


# =============================================================================
# PART 1: TOOL DEFINITIONS (raw JSON Schema)
# =============================================================================
#
# The OpenAI API expects tools in this exact shape:
#   {
#       "type": "function",
#       "function": {
#           "name": "...",
#           "description": "...",
#           "parameters": { <JSON Schema object> }
#       }
#   }
#
# The "parameters" field is a standard JSON Schema definition.
# The model uses "description" fields to understand WHEN and HOW to call each tool.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_planet_info",
            "description": (
                "Get information about a Star Wars planet including "
                "climate, population, and notable residents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the planet, e.g. 'Tatooine', 'Coruscant', 'Hoth'",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_jedi_archives",
            "description": (
                "Search the Jedi Archives for knowledge about the Force, "
                "Jedi history, Sith lords, or galactic events."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for the archives",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_starship_specs",
            "description": (
                "Get technical specifications for a Star Wars starship "
                "including class, speed, armament, and crew capacity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ship_name": {
                        "type": "string",
                        "description": "The name of the starship, e.g. 'Millennium Falcon', 'X-Wing', 'Star Destroyer'",
                    }
                },
                "required": ["ship_name"],
            },
        },
    },
]


# =============================================================================
# PART 2: MOCK IMPLEMENTATIONS
# =============================================================================
#
# Each function returns a dict with the "tool result" data.
# In the real world, these would query databases or external APIs.

PLANETS_DB = {
    "tatooine": {
        "name": "Tatooine",
        "region": "Outer Rim Territories",
        "climate": "Arid desert",
        "population": "200,000",
        "notable_residents": ["Luke Skywalker", "Anakin Skywalker", "Jabba the Hutt"],
        "fun_fact": "Has twin suns: Tatoo I and Tatoo II",
    },
    "coruscant": {
        "name": "Coruscant",
        "region": "Core Worlds",
        "climate": "Temperate (controlled)",
        "population": "1 trillion",
        "notable_residents": ["Emperor Palpatine", "Mace Windu", "Yoda"],
        "fun_fact": "The entire surface is one giant city",
    },
    "hoth": {
        "name": "Hoth",
        "region": "Outer Rim Territories",
        "climate": "Frozen ice world",
        "population": "Unknown (Rebel base housed ~1,000)",
        "notable_residents": ["Wampa creatures", "Tauntauns"],
        "fun_fact": "Site of the Battle of Hoth against the Empire",
    },
    "dagobah": {
        "name": "Dagobah",
        "region": "Outer Rim Territories",
        "climate": "Murky swamps and bogs",
        "population": "Unknown",
        "notable_residents": ["Yoda (in exile)"],
        "fun_fact": "Strong connection to the Force masks its inhabitants from detection",
    },
    "naboo": {
        "name": "Naboo",
        "region": "Mid Rim",
        "climate": "Temperate",
        "population": "4.5 billion",
        "notable_residents": ["Padme Amidala", "Emperor Palpatine", "Jar Jar Binks"],
        "fun_fact": "Home to both the Naboo humans and the Gungan species",
    },
}

STARSHIPS_DB = {
    "millennium falcon": {
        "name": "Millennium Falcon",
        "class": "YT-1300 light freighter",
        "manufacturer": "Corellian Engineering Corporation",
        "speed": "1,050 km/h atmospheric, 0.5 past lightspeed (hyperdrive)",
        "armament": "2 quad laser cannons, 2 concussion missile tubes",
        "crew": "2 (pilot + copilot), 6 passengers",
        "notable_pilots": ["Han Solo", "Chewbacca", "Lando Calrissian"],
    },
    "x-wing": {
        "name": "T-65B X-Wing Starfighter",
        "class": "Starfighter",
        "manufacturer": "Incom Corporation",
        "speed": "1,050 km/h atmospheric, Class 1 hyperdrive",
        "armament": "4 laser cannons, 2 proton torpedo launchers",
        "crew": "1 pilot + 1 astromech droid",
        "notable_pilots": ["Luke Skywalker", "Wedge Antilles", "Poe Dameron"],
    },
    "star destroyer": {
        "name": "Imperial I-class Star Destroyer",
        "class": "Star Destroyer",
        "manufacturer": "Kuat Drive Yards",
        "speed": "975 km/h atmospheric, Class 2 hyperdrive",
        "armament": "60 turbolaser batteries, 60 ion cannons, 10 tractor beam projectors",
        "crew": "37,085 crew, 9,700 stormtroopers",
        "notable_pilots": ["Darth Vader (Devastator)", "Admiral Piett (Executor escort)"],
    },
    "tie fighter": {
        "name": "TIE/ln Space Superiority Starfighter",
        "class": "Starfighter",
        "manufacturer": "Sienar Fleet Systems",
        "speed": "1,200 km/h atmospheric, no hyperdrive",
        "armament": "2 laser cannons",
        "crew": "1 pilot",
        "notable_pilots": ["Imperial Navy pilots", "Darth Vader (TIE Advanced)"],
    },
}

ARCHIVES_DB = {
    "force": (
        "The Force is an energy field created by all living things. It surrounds us, "
        "penetrates us, and binds the galaxy together. It has two aspects: the Light Side "
        "(peace, knowledge, serenity) and the Dark Side (fear, anger, hatred). "
        "Midi-chlorians are microscopic life forms that reside within all living cells "
        "and communicate with the Force."
    ),
    "sith": (
        "The Sith are practitioners of the Dark Side of the Force. Following the Rule of Two "
        "established by Darth Bane, there can only be two Sith at any time: a master and an "
        "apprentice. Notable Sith include Darth Sidious (Emperor Palpatine), Darth Vader "
        "(Anakin Skywalker), Darth Maul, and Count Dooku (Darth Tyranus)."
    ),
    "jedi": (
        "The Jedi Order was a noble order of protectors unified by their ability to use the Force. "
        "Based in the Jedi Temple on Coruscant, they served as guardians of peace and justice in "
        "the Galactic Republic for over a thousand generations. The Order was nearly destroyed by "
        "Order 66, executed by Emperor Palpatine."
    ),
    "order 66": (
        "Order 66 was a top-secret order programmed into all clone troopers via inhibitor chips. "
        "When activated by Chancellor Palpatine, it designated all Jedi as traitors to the Republic. "
        "The clones turned on their Jedi commanders, resulting in the near-extinction of the Jedi Order. "
        "Notable survivors: Obi-Wan Kenobi, Yoda, Ahsoka Tano, Kanan Jarrus."
    ),
    "lightsaber": (
        "A lightsaber is the signature weapon of the Jedi and Sith. It consists of a plasma blade "
        "powered by a kyber crystal. Blade colors indicate the crystal and wielder: blue (Jedi Guardian), "
        "green (Jedi Consular), red (Sith, using synthetic or 'bled' crystals), purple (Mace Windu)."
    ),
}


def get_planet_info(name: str) -> dict:
    """Look up a planet by name."""
    key = name.lower().strip()
    if key in PLANETS_DB:
        return PLANETS_DB[key]
    return {
        "error": f"Planet '{name}' not found in the galactic database.",
        "known_planets": list(PLANETS_DB.keys()),
    }


def search_jedi_archives(query: str) -> dict:
    """Search the archives for a topic."""
    query_lower = query.lower()
    # Simple keyword matching against archive keys
    results = []
    for key, content in ARCHIVES_DB.items():
        if key in query_lower or query_lower in key:
            results.append({"topic": key, "content": content})

    if results:
        return {"results": results, "total_found": len(results)}

    return {
        "results": [],
        "total_found": 0,
        "message": f"No records found for '{query}'. The archives may be incomplete.",
        "available_topics": list(ARCHIVES_DB.keys()),
    }


def get_starship_specs(ship_name: str) -> dict:
    """Look up starship specifications."""
    key = ship_name.lower().strip()
    if key in STARSHIPS_DB:
        return STARSHIPS_DB[key]
    return {
        "error": f"Starship '{ship_name}' not found in the registry.",
        "known_starships": list(STARSHIPS_DB.keys()),
    }


# =============================================================================
# DISPATCH TABLE
# =============================================================================
# Maps function names (as strings from the API response) to actual callables.
# This is how we "execute" a tool call: look up the name, call the function.

TOOL_DISPATCH = {
    "get_planet_info": get_planet_info,
    "search_jedi_archives": search_jedi_archives,
    "get_starship_specs": get_starship_specs,
}


def execute_tool_call(name: str, arguments: dict) -> str:
    """
    Execute a tool call by name and return the result as a JSON string.

    This is the bridge between the LLM's tool_call response and our local
    mock functions. In production, this dispatch pattern scales to real tools:
    API calls, database queries, file operations, etc.

    Args:
        name: The function name from the LLM's tool_call (e.g., "get_planet_info")
        arguments: The parsed arguments dict (already json.loads'd from the API response)

    Returns:
        A JSON string of the result (the API expects tool results as strings)
    """
    if name not in TOOL_DISPATCH:
        return json.dumps({"error": f"Unknown tool: {name}"})

    func = TOOL_DISPATCH[name]
    result = func(**arguments)
    return json.dumps(result)

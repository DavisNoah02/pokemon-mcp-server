import httpx 
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("poke")

POKEAPI_BASE = "https://pokeapi.co/api/v2"

# --- Helper to fetch Pokémon data ---
async def fetch_pokemon_data(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{POKEAPI_BASE}/pokemon/{name.lower()}")
            if response.status_code == 200:
                return response.json()
        except httpx.HTTPError:
            pass
    return {}

async def fetch_url(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
        except httpx.HTTPError:
            pass
    return {}

# --- Tool 1: Get info about a Pokémon ---
@mcp.tool()
async def get_pokemon_info(name: str) -> str:
    """Get detailed info about a Pokémon by name."""
    data = await fetch_pokemon_data(name)
    if not data:
        return f"No data found for Pokémon: {name}"

    stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
    types_ = [t['type']['name'] for t in data['types']]
    abilities = [a['ability']['name'] for a in data['abilities']]

    return f"""
Name: {data['name'].capitalize()}
Types: {', '.join(types_)}
Abilities: {', '.join(abilities)}
Stats: {', '.join(f"{k}: {v}" for k, v in stats.items())}
"""

# --- Tool 2: Create a tournament squad ---
@mcp.tool()
async def create_tournament_squad() -> str:
    """Create a powerful squad of Pokémon for a tournament."""
    top_pokemon = ["charizard", "garchomp", "lucario", "dragonite", "metagross", "gardevoir"]
    squad = []

    for name in top_pokemon:
        data = await fetch_pokemon_data(name)
        if data:
            squad.append(data["name"].capitalize())

    return "Tournament Squad:\n" + "\n".join(squad)

# --- Tool 3: List popular Pokémon ---
@mcp.tool()
async def list_popular_pokemon() -> str:
    """List popular tournament-ready Pokémon."""
    return "\n".join([
        "Charizard", "Garchomp", "Lucario",
        "Dragonite", "Metagross", "Gardevoir"
    ])

# --- Tool: List a Pokémon's moves ---
@mcp.tool()
async def list_pokemon_moves(name: str, limit: int = 10) -> str:
    """List a Pokémon's moves (limited)."""
    data = await fetch_pokemon_data(name)
    if not data:
        return f"No data found for Pokémon: {name}"

    moves = [m["move"]["name"] for m in data.get("moves", [])]
    if not moves:
        return f"No moves found for Pokémon: {name}"

    limit = max(1, min(limit, 50))
    return f"Moves for {data['name'].capitalize()}:\n" + "\n".join(moves[:limit])

# --- Tool: Get a Pokémon's evolution chain ---
@mcp.tool()
async def get_pokemon_evolution_chain(name: str) -> str:
    """Get a Pokémon's evolution chain."""
    data = await fetch_pokemon_data(name)
    if not data:
        return f"No data found for Pokémon: {name}"

    species_url = data.get("species", {}).get("url")
    if not species_url:
        return f"No species data found for Pokémon: {name}"

    species = await fetch_url(species_url)
    chain_url = species.get("evolution_chain", {}).get("url")
    if not chain_url:
        return f"No evolution chain found for Pokémon: {name}"

    chain = await fetch_url(chain_url)
    chain_root = chain.get("chain")
    if not chain_root:
        return f"No evolution chain found for Pokémon: {name}"

    names = []
    node = chain_root
    while node:
        species_name = node.get("species", {}).get("name")
        if species_name:
            names.append(species_name.capitalize())
        evolutions = node.get("evolves_to", [])
        node = evolutions[0] if evolutions else None

    if not names:
        return f"No evolution chain found for Pokémon: {name}"
    return "Evolution Chain:\n" + " -> ".join(names)

# --- Tool 4: List popular Pokémon ---




# --- Entry point to communicate btwn client & server ---
if __name__ == "__main__":
    mcp.run(transport="stdio")

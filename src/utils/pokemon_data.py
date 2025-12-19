"""
Pokemon and Move Database with Type System
"""

# Type effectiveness system - only one table needed!
# If A is strong against B, then B is weak against A (reciprocal relationship)
TYPE_ADVANTAGE = {
    "Fire": "Ice",      # Fire > Ice, so Ice < Fire
    "Water": "Fire",    # Water > Fire, so Fire < Water
    "Ice": "Wind",      # Ice > Wind, so Wind < Ice
    "Wind": "Light",    # Wind > Light, so Light < Wind
    "Light": "Slash",   # Light > Slash, so Slash < Light
    "Slash": "Water"    # Slash > Water, so Water < Slash
}

# Move database with properties (moves have NO type - only power and animation)
MOVES_DATABASE = {
    "IceShard": {
        "name": "Ice Shard",
        "power": 18,
        "animation": "attack/attack1.png"
    },
    "LightPulse": {
        "name": "Light Pulse",
        "power": 18,
        "animation": "attack/attack2.png"
    },
    "WaterBurst": {
        "name": "Water Burst",
        "power": 18,
        "animation": "attack/attack3.png"
    },
    "FireBlast": {
        "name": "Fire Blast",
        "power": 20,
        "animation": "attack/attack4.png"
    },
    "FlameSlash": {
        "name": "Flame Slash",
        "power": 18,
        "animation": "attack/attack5.png"
    },
    "WindSpiral": {
        "name": "Wind Spiral",
        "power": 18,
        "animation": "attack/attack6.png"
    },
    "QuickSlash": {
        "name": "Quick Slash",
        "power": 15,
        "animation": "attack/attack7.png"
    },
    # Additional moves
    "NatureBurst": {
        "name": "Nature Burst",
        "power": 16,
        "animation": None
    },
    "AquaShield": {
        "name": "Aqua Shield",
        "power": 12,  # Defense buff move
        "animation": "attack/attack3.png"
    },
    "TidalStrike": {
        "name": "Tidal Strike",
        "power": 22,
        "animation": "attack/attack3.png"
    },
    "HeatDive": {
        "name": "Heat Dive",
        "power": 20,
        "animation": "attack/attack4.png"
    },
    "StonePunch": {
        "name": "Stone Punch",
        "power": 17,
        "animation": None
    },
    "EarthCrack": {
        "name": "Earth Crack",
        "power": 18,
        "animation": None
    },
    "SparkClaw": {
        "name": "Spark Claw",
        "power": 16,
        "animation": "attack/attack2.png"
    },
    "VoltDash": {
        "name": "Volt Dash",
        "power": 19,
        "animation": "attack/attack2.png"
    },
    "FrostNova": {
        "name": "Frost Nova",
        "power": 17,
        "animation": "attack/attack1.png"
    },
    "ColdBite": {
        "name": "Cold Bite",
        "power": 16,
        "animation": "attack/attack1.png"
    },
    "DarkSwipe": {
        "name": "Dark Swipe",
        "power": 15,
        "animation": "attack/attack7.png"
    },
    "ShadowBurst": {
        "name": "Shadow Burst",
        "power": 18,
        "animation": None
    },
    "FearSlash": {
        "name": "Fear Slash",
        "power": 16,
        "animation": "attack/attack7.png"
    },
    "IronWing": {
        "name": "Iron Wing",
        "power": 17,
        "animation": "attack/attack7.png"
    },
    "SteelCharge": {
        "name": "Steel Charge",
        "power": 19,
        "animation": None
    },
    "MindPierce": {
        "name": "Mind Pierce",
        "power": 18,
        "animation": None
    },
    "SpiritWave": {
        "name": "Spirit Wave",
        "power": 20,
        "animation": "attack/attack2.png"
    },
    "ToxicBite": {
        "name": "Toxic Bite",
        "power": 14,
        "animation": None
    },
    "VenomShot": {
        "name": "Venom Shot",
        "power": 16,
        "animation": None
    },
    "SandBurst": {
        "name": "Sand Burst",
        "power": 17,
        "animation": "attack/attack6.png"
    },
    "DustBlade": {
        "name": "Dust Blade",
        "power": 16,
        "animation": "attack/attack6.png"
    },
    "SoulSpark": {
        "name": "Soul Spark",
        "power": 19,
        "animation": "attack/attack2.png"
    },
    "HauntFlame": {
        "name": "Haunt Flame",
        "power": 17,
        "animation": "attack/attack4.png"
    },
    "CrystalBeam": {
        "name": "Crystal Beam",
        "power": 19,
        "animation": "attack/attack2.png"
    },
    "ShatterStrike": {
        "name": "Shatter Strike",
        "power": 18,
        "animation": "attack/attack1.png"
    },
    "GaleBlade": {
        "name": "Gale Blade",
        "power": 17,
        "animation": "attack/attack6.png"
    },
    "TempestCrash": {
        "name": "Tempest Crash",
        "power": 21,
        "animation": "attack/attack6.png"
    },
    "MagmaSmash": {
        "name": "Magma Smash",
        "power": 21,
        "animation": "attack/attack4.png"
    },
    "CosmicPulse": {
        "name": "Cosmic Pulse",
        "power": 23,
        "animation": "attack/attack2.png"
    },
    "StarfallBlaze": {
        "name": "Starfall Blaze",
        "power": 24,
        "animation": "attack/attack4.png"
    },
    "DragonRift": {
        "name": "Dragon Rift",
        "power": 25,
        "animation": None
    }
}

# Pokemon species database with types and moves
POKEMON_SPECIES = {
    # Common Pokemon
    "Leafeon": {
        "type": "Wind",
        "moves": ["QuickSlash", "WindSpiral", "NatureBurst"]
    },
    "Aquafin": {
        "type": "Water",
        "moves": ["WaterBurst", "AquaShield", "TidalStrike"]
    },
    "Blazewing": {
        "type": "Fire",
        "moves": ["FireBlast", "FlameSlash", "HeatDive"]
    },
    "Rockfist": {
        "type": "None",
        "moves": ["StonePunch", "EarthCrack", "QuickSlash"]
    },
    "Thunderpaw": {
        "type": "Light",
        "moves": ["LightPulse", "SparkClaw", "VoltDash"]
    },

    # Uncommon Pokemon
    "Frostbite": {
        "type": "Ice",
        "moves": ["IceShard", "FrostNova", "ColdBite"]
    },
    "Shadowclaw": {
        "type": "None",
        "moves": ["DarkSwipe", "ShadowBurst", "FearSlash"]
    },
    "Steelwing": {
        "type": "Wind",
        "moves": ["WindSpiral", "IronWing", "SteelCharge"]
    },
    "Mysticsoul": {
        "type": "Light",
        "moves": ["LightPulse", "MindPierce", "SpiritWave"]
    },
    "Venomfang": {
        "type": "None",
        "moves": ["ToxicBite", "VenomShot", "QuickSlash"]
    },

    # Rare Pokemon
    "Sandstorm": {
        "type": "Wind",
        "moves": ["SandBurst", "WindSpiral", "DustBlade"]
    },
    "Ghostflame": {
        "type": "Fire",
        "moves": ["FireBlast", "SoulSpark", "HauntFlame"]
    },
    "Crystalhorn": {
        "type": "Ice",
        "moves": ["IceShard", "CrystalBeam", "ShatterStrike"]
    },
    "Stormchaser": {
        "type": "Wind",
        "moves": ["WindSpiral", "GaleBlade", "TempestCrash"]
    },
    "Lavaguard": {
        "type": "Fire",
        "moves": ["FireBlast", "FlameSlash", "MagmaSmash"]
    },

    # Legendary Pokemon
    "Cosmicdrake": {
        "type": "Light",
        "moves": ["CosmicPulse", "StarfallBlaze", "DragonRift"]
    },
    "Mewtwo": {
        "type": "Light",
        "moves": ["MindPierce", "SpiritWave", "CosmicPulse", "LightPulse"]
    },

    # User's Pokemon
    "Florion": {
        "type": "Slash",
        "moves": ["QuickSlash", "FearSlash", "IronWing"]
    }
}


def calculate_type_effectiveness(attacker_type: str, defender_type: str) -> tuple[float, str]:
    """
    Calculate type effectiveness multiplier and message.
    Uses the reciprocal relationship: if A > B, then B < A.

    Returns:
        tuple[float, str]: (damage_multiplier, effectiveness_message)
        - damage_multiplier: 1.5 for super effective, 0.67 for not very effective, 1.0 for neutral
        - effectiveness_message: Message to display to the player
    """
    # None type has no advantages/disadvantages - show neutral message
    if attacker_type == "None" or defender_type == "None":
        return (1.0, "Typeless attack.")

    # Check if attacker has advantage over defender (A > B)
    if TYPE_ADVANTAGE.get(attacker_type) == defender_type:
        return (1.5, "It's super effective!")

    # Check if defender has advantage over attacker (B > A, meaning A < B)
    # This is the reciprocal relationship: if defender is strong against attacker,
    # then attacker is weak against defender
    if TYPE_ADVANTAGE.get(defender_type) == attacker_type:
        return (0.67, "It's not very effective...")

    # Neutral matchup - no type advantage either way
    return (1.0, "Normal damage.")




# Evolution chains mapping
EVOLUTION_CHAINS = {
    # Chain 1: sprite1 -> sprite2 -> sprite3
    "Leafeon": {"evolves_to": "Aquafin", "level": 16, "sprite_id": 2},
    "Aquafin": {"evolves_to": "Blazewing", "level": 32, "sprite_id": 3},

    # Chain 2: sprite7 -> sprite8 -> sprite9
    "Shadowclaw": {"evolves_to": "Steelwing", "level": 20, "sprite_id": 8},
    "Steelwing": {"evolves_to": "Mysticsoul", "level": 36, "sprite_id": 9},

    # Chain 3: sprite12 -> sprite13 -> sprite14
    "Ghostflame": {"evolves_to": "Crystalhorn", "level": 25, "sprite_id": 13},
    "Crystalhorn": {"evolves_to": "Stormchaser", "level": 40, "sprite_id": 14},

    # Chain 4: sprite15 -> sprite16
    "Lavaguard": {"evolves_to": "Cosmicdrake", "level": 45, "sprite_id": 16},
}

# Stat multipliers for evolution (all stats increased)
EVOLUTION_STAT_BOOST = {
    "hp_multiplier": 1.4,      # 40% HP increase
    "attack_multiplier": 1.3,  # 30% attack increase
    "defense_multiplier": 1.3, # 30% defense increase
    "level_boost": 0,          # No level increase, just stats
    "moves_gained": 1          # Learn 1 new move on evolution
}


def can_evolve(pokemon: dict) -> tuple[bool, str | None]:
    """
    Check if a pokemon can evolve.

    Args:
        pokemon: Pokemon data dict with name and level

    Returns:
        tuple[bool, str | None]: (can_evolve, evolution_name)
    """
    pokemon_name = pokemon.get("name")
    pokemon_level = pokemon.get("level", 1)

    if pokemon_name not in EVOLUTION_CHAINS:
        return (False, None)

    evolution_data = EVOLUTION_CHAINS[pokemon_name]
    required_level = evolution_data["level"]

    if pokemon_level >= required_level:
        return (True, evolution_data["evolves_to"])

    return (False, None)


def evolve_pokemon(pokemon: dict) -> dict:
    """
    Evolve a pokemon to its next form.
    Updates name, sprite, stats, and potentially learns new moves.

    Args:
        pokemon: Pokemon data dict to evolve

    Returns:
        dict: Evolved pokemon data
    """
    if pokemon["name"] not in EVOLUTION_CHAINS:
        return pokemon

    evolution_data = EVOLUTION_CHAINS[pokemon["name"]]
    new_name = evolution_data["evolves_to"]
    new_sprite_id = evolution_data["sprite_id"]

    # Update name and sprite
    pokemon["name"] = new_name
    pokemon["sprite_path"] = f"sprites/sprite{new_sprite_id}.png"

    # Boost stats
    old_max_hp = pokemon.get("max_hp", 100)
    new_max_hp = int(old_max_hp * EVOLUTION_STAT_BOOST["hp_multiplier"])
    pokemon["max_hp"] = new_max_hp

    # Boost attack stat
    old_attack = pokemon.get("attack", 10)
    new_attack = int(old_attack * EVOLUTION_STAT_BOOST["attack_multiplier"])
    pokemon["attack"] = new_attack

    # Boost defense stat
    old_defense = pokemon.get("defense", 10)
    new_defense = int(old_defense * EVOLUTION_STAT_BOOST["defense_multiplier"])
    pokemon["defense"] = new_defense

    # Heal to full HP on evolution
    pokemon["hp"] = new_max_hp

    # Update type and moves from species data
    if new_name in POKEMON_SPECIES:
        species_data = POKEMON_SPECIES[new_name]
        pokemon["type"] = species_data["type"]
        pokemon["moves"] = species_data["moves"].copy()

    return pokemon


def calculate_levelup_cost(current_level: int) -> int:
    """
    Calculate the coin cost to level up a Pokemon.
    Cost increases exponentially with level.

    Args:
        current_level: Current level of the Pokemon

    Returns:
        int: Coin cost to level up
    """
    # Base cost increases with level: 50 * level^1.5
    # This creates a curve where higher levels cost significantly more
    base_cost = 50
    cost = int(base_cost * (current_level ** 1.5))

    # Ensure minimum cost of 50
    return max(50, cost)


def levelup_pokemon(pokemon: dict, bag) -> tuple[bool, str]:
    """
    Level up a pokemon by spending coins.

    Args:
        pokemon: Pokemon data dict to level up
        bag: Player's bag object containing money

    Returns:
        tuple[bool, str]: (success, message)
    """
    current_level = pokemon.get("level", 1)
    cost = calculate_levelup_cost(current_level)

    # Check if player has enough coins
    coins_item = None
    for item in bag.items:
        if item.get("name") == "Coins":
            coins_item = item
            break

    if not coins_item or coins_item.get("count", 0) < cost:
        return (False, f"Not enough coins! Need {cost} coins.")

    # Deduct coins
    coins_item["count"] -= cost

    # Level up the pokemon
    pokemon["level"] = current_level + 1

    # Increase max HP slightly (5% per level)
    old_max_hp = pokemon.get("max_hp", 100)
    new_max_hp = int(old_max_hp * 1.05)
    pokemon["max_hp"] = new_max_hp

    # Increase attack stat (3% per level)
    old_attack = pokemon.get("attack", 10)
    new_attack = int(old_attack * 1.03)
    pokemon["attack"] = new_attack

    # Increase defense stat (3% per level)
    old_defense = pokemon.get("defense", 10)
    new_defense = int(old_defense * 1.03)
    pokemon["defense"] = new_defense

    # Heal by the increased amount
    pokemon["hp"] = min(pokemon.get("hp", 0) + (new_max_hp - old_max_hp), new_max_hp)

    return (True, f"{pokemon['name']} leveled up to {pokemon['level']}! Cost: {cost} coins")


def calculate_damage(move_name: str, attacker_type: str, defender_type: str, level: int = 10, attack: int = 10, defense: int = 10) -> tuple[int, str]:
    """
    Calculate damage for a move considering type effectiveness, attack stat, and defense stat.
    Type effectiveness is based on the ATTACKER'S Pokemon type, not the move.

    Args:
        move_name: Name of the move being used
        attacker_type: Type of the attacking Pokemon (this determines effectiveness!)
        defender_type: Type of the defending Pokemon
        level: Level of the attacker (default 10)
        attack: Attack stat of the attacker (default 10)
        defense: Defense stat of the defender (default 10)

    Returns:
        tuple[int, str]: (damage, effectiveness_message)
    """
    move_data = MOVES_DATABASE.get(move_name)
    if not move_data:
        # Fallback for unknown moves
        return (10, "")

    base_power = move_data["power"]

    # Calculate type effectiveness based on ATTACKER's Pokemon type vs DEFENDER's Pokemon type
    multiplier, effectiveness_msg = calculate_type_effectiveness(attacker_type, defender_type)

    # Calculate damage with some randomness - reduced scaling
    import random
    variance = random.uniform(0.85, 1.0)
    # Include attack and defense stats in damage calculation
    # Formula: (base_power / 2) * (attack / defense) * type_effectiveness * variance * level_scaling
    attack_defense_ratio = attack / defense  # Higher attack vs lower defense = more damage
    damage = int((base_power / 2) * attack_defense_ratio * multiplier * variance * (0.5 + level / 20))

    # Ensure minimum damage of 3, maximum of 30
    damage = max(3, min(damage, 30))

    return (damage, effectiveness_msg)

"""
Pokemon and Move Database with Type System
"""

# Type effectiveness system
WEAK_TO = {
    "Fire": "Water",
    "Water": "Light",
    "Ice": "Fire",
    "Wind": "Ice",
    "Light": "Wind",
    "Slash": "Light"
}

STRONG_AGAINST = {
    "Fire": "Ice",
    "Water": "Fire",
    "Ice": "Wind",
    "Wind": "Light",
    "Light": "Slash",
    "Slash": "Water"
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

    # User's Pokemon
    "Florion": {
        "type": "Slash",
        "moves": ["QuickSlash", "FearSlash", "IronWing"]
    }
}


def calculate_type_effectiveness(attacker_type: str, defender_type: str) -> tuple[float, str]:
    """
    Calculate type effectiveness multiplier and message.

    Returns:
        tuple[float, str]: (damage_multiplier, effectiveness_message)
        - damage_multiplier: 1.5 for super effective, 0.67 for not very effective, 1.0 for neutral
        - effectiveness_message: Message to display to the player
    """
    # None type has no advantages/disadvantages - show neutral message
    if attacker_type == "None" or defender_type == "None":
        return (1.0, "Typeless attack.")

    # Check if attacker is strong against defender
    if STRONG_AGAINST.get(attacker_type) == defender_type:
        return (1.5, "It's super effective!")

    # Check if attacker is weak against defender (defender resists)
    if WEAK_TO.get(attacker_type) == defender_type:
        return (0.67, "It's not very effective...")

    # Neutral matchup - any type not in "against" relationships
    return (1.0, "Normal damage.")


def calculate_damage(move_name: str, attacker_type: str, defender_type: str, level: int = 10) -> tuple[int, str]:
    """
    Calculate damage for a move considering type effectiveness.
    Type effectiveness is based on the ATTACKER'S Pokemon type, not the move.

    Args:
        move_name: Name of the move being used
        attacker_type: Type of the attacking Pokemon (this determines effectiveness!)
        defender_type: Type of the defending Pokemon
        level: Level of the attacker (default 10)

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
    # Reduce overall damage by dividing base power by 2 and reducing level scaling
    damage = int((base_power / 2) * multiplier * variance * (0.5 + level / 20))

    # Ensure minimum damage of 3, maximum of 25
    damage = max(3, min(damage, 25))

    return (damage, effectiveness_msg)

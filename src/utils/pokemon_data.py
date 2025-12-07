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

# Move database with properties
MOVES_DATABASE = {
    "IceShard": {
        "name": "Ice Shard",
        "type": "Ice",
        "power": 18,
        "animation": "attack/attack1.png"
    },
    "LightPulse": {
        "name": "Light Pulse",
        "type": "Light",
        "power": 18,
        "animation": "attack/attack2.png"
    },
    "WaterBurst": {
        "name": "Water Burst",
        "type": "Water",
        "power": 18,
        "animation": "attack/attack3.png"
    },
    "FireBlast": {
        "name": "Fire Blast",
        "type": "Fire",
        "power": 20,
        "animation": "attack/attack4.png"
    },
    "FlameSlash": {
        "name": "Flame Slash",
        "type": "Fire",
        "power": 18,
        "animation": "attack/attack5.png"
    },
    "WindSpiral": {
        "name": "Wind Spiral",
        "type": "Wind",
        "power": 18,
        "animation": "attack/attack6.png"
    },
    "QuickSlash": {
        "name": "Quick Slash",
        "type": "Slash",
        "power": 15,
        "animation": "attack/attack7.png"
    },
    # Additional moves (neutral/special attacks)
    "NatureBurst": {
        "name": "Nature Burst",
        "type": "None",
        "power": 16,
        "animation": None
    },
    "AquaShield": {
        "name": "Aqua Shield",
        "type": "Water",
        "power": 12,  # Defense buff move
        "animation": "attack/attack3.png"
    },
    "TidalStrike": {
        "name": "Tidal Strike",
        "type": "Water",
        "power": 22,
        "animation": "attack/attack3.png"
    },
    "HeatDive": {
        "name": "Heat Dive",
        "type": "Fire",
        "power": 20,
        "animation": "attack/attack4.png"
    },
    "StonePunch": {
        "name": "Stone Punch",
        "type": "None",
        "power": 17,
        "animation": None
    },
    "EarthCrack": {
        "name": "Earth Crack",
        "type": "None",
        "power": 18,
        "animation": None
    },
    "SparkClaw": {
        "name": "Spark Claw",
        "type": "Light",
        "power": 16,
        "animation": "attack/attack2.png"
    },
    "VoltDash": {
        "name": "Volt Dash",
        "type": "Light",
        "power": 19,
        "animation": "attack/attack2.png"
    },
    "FrostNova": {
        "name": "Frost Nova",
        "type": "Ice",
        "power": 17,
        "animation": "attack/attack1.png"
    },
    "ColdBite": {
        "name": "Cold Bite",
        "type": "Ice",
        "power": 16,
        "animation": "attack/attack1.png"
    },
    "DarkSwipe": {
        "name": "Dark Swipe",
        "type": "None",
        "power": 15,
        "animation": "attack/attack7.png"
    },
    "ShadowBurst": {
        "name": "Shadow Burst",
        "type": "None",
        "power": 18,
        "animation": None
    },
    "FearSlash": {
        "name": "Fear Slash",
        "type": "Slash",
        "power": 16,
        "animation": "attack/attack7.png"
    },
    "IronWing": {
        "name": "Iron Wing",
        "type": "Slash",
        "power": 17,
        "animation": "attack/attack7.png"
    },
    "SteelCharge": {
        "name": "Steel Charge",
        "type": "None",
        "power": 19,
        "animation": None
    },
    "MindPierce": {
        "name": "Mind Pierce",
        "type": "None",
        "power": 18,
        "animation": None
    },
    "SpiritWave": {
        "name": "Spirit Wave",
        "type": "Light",
        "power": 20,
        "animation": "attack/attack2.png"
    },
    "ToxicBite": {
        "name": "Toxic Bite",
        "type": "None",
        "power": 14,
        "animation": None
    },
    "VenomShot": {
        "name": "Venom Shot",
        "type": "None",
        "power": 16,
        "animation": None
    },
    "SandBurst": {
        "name": "Sand Burst",
        "type": "Wind",
        "power": 17,
        "animation": "attack/attack6.png"
    },
    "DustBlade": {
        "name": "Dust Blade",
        "type": "Wind",
        "power": 16,
        "animation": "attack/attack6.png"
    },
    "SoulSpark": {
        "name": "Soul Spark",
        "type": "Light",
        "power": 19,
        "animation": "attack/attack2.png"
    },
    "HauntFlame": {
        "name": "Haunt Flame",
        "type": "Fire",
        "power": 17,
        "animation": "attack/attack4.png"
    },
    "CrystalBeam": {
        "name": "Crystal Beam",
        "type": "Light",
        "power": 19,
        "animation": "attack/attack2.png"
    },
    "ShatterStrike": {
        "name": "Shatter Strike",
        "type": "Ice",
        "power": 18,
        "animation": "attack/attack1.png"
    },
    "GaleBlade": {
        "name": "Gale Blade",
        "type": "Wind",
        "power": 17,
        "animation": "attack/attack6.png"
    },
    "TempestCrash": {
        "name": "Tempest Crash",
        "type": "Wind",
        "power": 21,
        "animation": "attack/attack6.png"
    },
    "MagmaSmash": {
        "name": "Magma Smash",
        "type": "Fire",
        "power": 21,
        "animation": "attack/attack4.png"
    },
    "CosmicPulse": {
        "name": "Cosmic Pulse",
        "type": "Light",
        "power": 23,
        "animation": "attack/attack2.png"
    },
    "StarfallBlaze": {
        "name": "Starfall Blaze",
        "type": "Fire",
        "power": 24,
        "animation": "attack/attack4.png"
    },
    "DragonRift": {
        "name": "Dragon Rift",
        "type": "None",
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
    if attacker_type == "None" or defender_type == "None":
        return (1.0, "")

    # Check if attacker is strong against defender
    if STRONG_AGAINST.get(attacker_type) == defender_type:
        return (1.5, "It's super effective!")

    # Check if attacker is weak against defender (defender resists)
    if WEAK_TO.get(attacker_type) == defender_type:
        return (0.67, "It's not very effective...")

    return (1.0, "")


def calculate_damage(move_name: str, attacker_type: str, defender_type: str, level: int = 10) -> tuple[int, str, str]:
    """
    Calculate damage for a move considering type effectiveness.

    Args:
        move_name: Name of the move being used
        attacker_type: Type of the attacking Pokemon
        defender_type: Type of the defending Pokemon
        level: Level of the attacker (default 10)

    Returns:
        tuple[int, str, str]: (damage, effectiveness_message, move_type)
    """
    move_data = MOVES_DATABASE.get(move_name)
    if not move_data:
        # Fallback for unknown moves
        return (10, "", "None")

    base_power = move_data["power"]
    move_type = move_data["type"]

    # Calculate type effectiveness
    multiplier, effectiveness_msg = calculate_type_effectiveness(move_type, defender_type)

    # Calculate damage with some randomness - reduced scaling
    import random
    variance = random.uniform(0.85, 1.0)
    # Reduce overall damage by dividing base power by 2 and reducing level scaling
    damage = int((base_power / 2) * multiplier * variance * (0.5 + level / 20))

    # Ensure minimum damage of 3, maximum of 25
    damage = max(3, min(damage, 25))

    return (damage, effectiveness_msg, move_type)

"""
Pokemon and Move Database with Type System - REDESIGNED based on actual sprites
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

# Status effects database with properties
STATUS_EFFECTS = {
    "poison": {
        "name": "Poison",
        "color": (160, 80, 200),  # Purple
        "icon": "💀",
        "damage_per_turn": 0.1,  # 10% of max HP per turn
        "blocks_action": False,
        "affects_attack": False,
        "duration": -1  # Lasts until battle ends (-1 = infinite)
    },
    "paralysis": {
        "name": "Paralysis",
        "color": (255, 220, 50),  # Yellow
        "icon": "⚡",
        "damage_per_turn": 0.0,
        "blocks_action": 0.25,  # 25% chance to be unable to move
        "affects_attack": False,
        "duration": -1
    },
    "burn": {
        "name": "Burn",
        "color": (255, 100, 50),  # Orange-red
        "icon": "🔥",
        "damage_per_turn": 0.05,  # 5% of max HP per turn
        "blocks_action": False,
        "affects_attack": 0.5,  # Reduces physical attack by 50%
        "duration": -1
    },
    "sleep": {
        "name": "Sleep",
        "color": (150, 200, 255),  # Light blue
        "icon": "💤",
        "damage_per_turn": 0.0,
        "blocks_action": True,  # Cannot move at all
        "affects_attack": False,
        "duration_range": (1, 3)  # Lasts 1-3 turns
    }
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
        "power": 17,
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
        "animation": "attack/attack4.png",
        "status_effect": "burn",
        "status_chance": 0.15  # 15% chance to burn
    },
    "FlameSlash": {
        "name": "Flame Slash",
        "power": 18,
        "animation": "attack/attack5.png",
        "status_effect": "burn",
        "status_chance": 0.2  # 20% chance to burn
    },
    "WindSpiral": {
        "name": "Wind Spiral",
        "power": 18,
        "animation": "attack/attack6.png"
    },
    "QuickSlash": {
        "name": "Quick Slash",
        "power": 15,
        "animation": "attack/attack5.png"
    },
    "AquaShield": {
        "name": "Aqua Shield",
        "power": 16,
        "animation": "attack/attack3.png"
    },
    "TidalStrike": {
        "name": "Tidal Strike",
        "power": 19,
        "animation": "attack/attack3.png"
    },
    "HeatDive": {
        "name": "Heat Dive",
        "power": 17,
        "animation": "attack/attack4.png"
    },
    "NatureBurst": {
        "name": "Nature Burst",
        "power": 16,
        "animation": "attack/attack6.png"
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
        "animation": "attack/attack2.png",
        "status_effect": "paralysis",
        "status_chance": 0.3  # 30% chance to paralyze
    },
    "VoltDash": {
        "name": "Volt Dash",
        "power": 19,
        "animation": "attack/attack2.png",
        "status_effect": "paralysis",
        "status_chance": 0.2  # 20% chance to paralyze
    },
    "FrostNova": {
        "name": "Frost Nova",
        "power": 17,
        "animation": "attack/attack1.png"
    },
    "ColdBite": {
        "name": "Cold Bite",
        "power": 15,
        "animation": "attack/attack1.png"
    },
    "IronWing": {
        "name": "Iron Wing",
        "power": 18,
        "animation": None
    },
    "SteelCharge": {
        "name": "Steel Charge",
        "power": 19,
        "animation": None
    },
    "DarkSwipe": {
        "name": "Dark Swipe",
        "power": 16,
        "animation": None
    },
    "ShadowBurst": {
        "name": "Shadow Burst",
        "power": 18,
        "animation": None
    },
    "FearSlash": {
        "name": "Fear Slash",
        "power": 17,
        "animation": "attack/attack5.png"
    },
    "MindPierce": {
        "name": "Mind Pierce",
        "power": 18,
        "animation": "attack/attack2.png"
    },
    "SpiritWave": {
        "name": "Spirit Wave",
        "power": 20,
        "animation": "attack/attack2.png"
    },
    "ToxicBite": {
        "name": "Toxic Bite",
        "power": 14,
        "animation": None,
        "status_effect": "poison",
        "status_chance": 0.4  # 40% chance to poison
    },
    "VenomShot": {
        "name": "Venom Shot",
        "power": 16,
        "animation": None,
        "status_effect": "poison",
        "status_chance": 0.3  # 30% chance to poison
    },
    "SandBurst": {
        "name": "Sand Burst",
        "power": 17,
        "animation": "attack/attack6.png"
    },
    "DustBlade": {
        "name": "Dust Blade",
        "power": 16,
        "animation": None
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
        "animation": "attack/attack4.png",
        "status_effect": "burn",
        "status_chance": 0.25  # 25% chance to burn
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
    },
    "LeafBlade": {
        "name": "Leaf Blade",
        "power": 16,
        "animation": "attack/attack6.png"
    },
    "VineWhip": {
        "name": "Vine Whip",
        "power": 14,
        "animation": "attack/attack6.png"
    },
    "PoisonSting": {
        "name": "Poison Sting",
        "power": 13,
        "animation": None,
        "status_effect": "poison",
        "status_chance": 0.35
    },
    "BugBite": {
        "name": "Bug Bite",
        "power": 15,
        "animation": None
    },
    "WingAttack": {
        "name": "Wing Attack",
        "power": 17,
        "animation": None
    },
    "Peck": {
        "name": "Peck",
        "power": 14,
        "animation": None
    },
    "AerialAce": {
        "name": "Aerial Ace",
        "power": 19,
        "animation": None
    }
}

# Pokemon species database with types and moves
# REDESIGNED to match actual sprite appearances!
POKEMON_SPECIES = {
    # === GRASS TYPE EVOLUTION CHAIN (sprite1 -> sprite2 -> sprite3) ===
    "Budling": {  # sprite1 - 小綠葉草系
        "type": "Wind",
        "moves": ["VineWhip", "LeafBlade", "NatureBurst"]
    },
    "Florion": {  # sprite2 - 中型草系，帶葉片 (玩家初始)
        "type": "Wind",
        "moves": ["LeafBlade", "WindSpiral", "QuickSlash"]
    },
    "Verdantus": {  # sprite3 - 大型草系最終進化
        "type": "Wind",
        "moves": ["NatureBurst", "TempestCrash", "LeafBlade"]
    },

    # === GROUND TYPE (sprite4) ===
    "Rockpaw": {  # sprite4 - 棕色岩石小熊
        "type": "None",
        "moves": ["StonePunch", "EarthCrack", "QuickSlash"]
    },

    # === FLYING/DARK TYPE (sprite5) ===
    "Ravenix": {  # sprite5 - 黑色飛行鳥類
        "type": "Slash",
        "moves": ["Peck", "WingAttack", "AerialAce"]
    },

    # === ICE TYPE (sprite6) ===
    "Frostfox": {  # sprite6 - 藍白冰狐
        "type": "Ice",
        "moves": ["IceShard", "FrostNova", "ColdBite"]
    },

    # === FIRE TYPE EVOLUTION CHAIN (sprite7 -> sprite8 -> sprite9) ===
    "Embear": {  # sprite7 - 橙色火兔/火熊
        "type": "Fire",
        "moves": ["FlameSlash", "HeatDive", "QuickSlash"]
    },
    "Blazefang": {  # sprite8 - 中型火系獸
        "type": "Fire",
        "moves": ["FireBlast", "FlameSlash", "HeatDive"]
    },
    "Charizord": {  # sprite9 - 噴火龍型！
        "type": "Fire",
        "moves": ["MagmaSmash", "FireBlast", "DragonRift"]
    },

    # === POISON TYPE EVOLUTION CHAIN (sprite10 -> sprite11) ===
    "Toxling": {  # sprite10 - 紫色小毒系
        "type": "None",
        "moves": ["PoisonSting", "ToxicBite", "QuickSlash"]
    },
    "Venomcoil": {  # sprite11 - 紫色大型毒蛇/龍
        "type": "None",
        "moves": ["ToxicBite", "VenomShot", "ShadowBurst"]
    },

    # === WATER TYPE EVOLUTION CHAIN (sprite12 -> sprite13 -> sprite14) ===
    "Aquabit": {  # sprite12 - 小藍魚
        "type": "Water",
        "moves": ["WaterBurst", "AquaShield", "QuickSlash"]
    },
    "Tidecrest": {  # sprite13 - 中型水龍
        "type": "Water",
        "moves": ["TidalStrike", "WaterBurst", "AquaShield"]
    },
    "Leviathan": {  # sprite14 - 大型水系巨龍
        "type": "Water",
        "moves": ["TidalStrike", "DragonRift", "WaterBurst"]
    },

    # === BUG TYPE EVOLUTION CHAIN (sprite15 -> sprite16) ===
    "Larvite": {  # sprite15 - 綠色小蟲
        "type": "Wind",
        "moves": ["BugBite", "VineWhip", "QuickSlash"]
    },
    "Beetlord": {  # sprite16 - 大型瓢蟲/甲蟲 (傳說)
        "type": "Wind",
        "moves": ["BugBite", "NatureBurst", "CosmicPulse"]
    }
}


# Evolution chains mapping - CORRECTED to match actual sprites!
EVOLUTION_CHAINS = {
    # Chain 1: Grass evolution (sprite1 -> sprite2 -> sprite3)
    "Budling": {"evolves_to": "Florion", "level": 16, "sprite_id": 2},
    "Florion": {"evolves_to": "Verdantus", "level": 32, "sprite_id": 3},

    # Chain 2: Fire evolution (sprite7 -> sprite8 -> sprite9)
    "Embear": {"evolves_to": "Blazefang", "level": 20, "sprite_id": 8},
    "Blazefang": {"evolves_to": "Charizord", "level": 36, "sprite_id": 9},

    # Chain 3: Water evolution (sprite12 -> sprite13 -> sprite14)
    "Aquabit": {"evolves_to": "Tidecrest", "level": 25, "sprite_id": 13},
    "Tidecrest": {"evolves_to": "Leviathan", "level": 40, "sprite_id": 14},

    # Chain 4: Bug/Poison evolution (sprite10 -> sprite11) & Bug evolution (sprite15 -> sprite16)
    "Toxling": {"evolves_to": "Venomcoil", "level": 22, "sprite_id": 11},
    "Larvite": {"evolves_to": "Beetlord", "level": 30, "sprite_id": 16},
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
    return cost


def levelup_pokemon(pokemon: dict, money: int) -> tuple[bool, str]:
    """
    Level up a pokemon using coins. Returns success status and message.

    Args:
        pokemon: Pokemon dict to level up
        money: Available money

    Returns:
        tuple[bool, str]: (success, message)
    """
    current_level = pokemon.get("level", 1)
    cost = calculate_levelup_cost(current_level)

    if money < cost:
        return (False, f"Not enough money! Need {cost} coins, have {money}")

    # Level up
    pokemon["level"] = current_level + 1

    # Increase stats
    old_max_hp = pokemon.get("max_hp", 100)
    new_max_hp = int(old_max_hp * 1.1)  # 10% HP increase per level
    pokemon["max_hp"] = new_max_hp

    # Increase attack by 1
    pokemon["attack"] = pokemon.get("attack", 10) + 1

    # Increase defense by 1
    pokemon["defense"] = pokemon.get("defense", 10) + 1

    # Heal by the increased amount
    pokemon["hp"] = min(pokemon.get("hp", 0) + (new_max_hp - old_max_hp), new_max_hp)

    return (True, f"{pokemon['name']} leveled up to {pokemon['level']}! Cost: {cost} coins")


def calculate_type_effectiveness(attacker_type: str, defender_type: str) -> tuple[float, str]:
    """
    Calculate type effectiveness multiplier and message.
    Uses the reciprocal relationship: if A > B, then B < A.

    Returns:
        tuple[float, str]: (damage_multiplier, effectiveness_message)
        - damage_multiplier: 1.5 for super effective, 0.67 for not very effective, 1.0 for neutral
        - effectiveness_message: Message to display to the player
    """
    # Check if attacker has advantage
    if attacker_type in TYPE_ADVANTAGE and TYPE_ADVANTAGE[attacker_type] == defender_type:
        return (1.5, "It's super effective!")

    # Check if defender has advantage (attacker is at disadvantage)
    if defender_type in TYPE_ADVANTAGE and TYPE_ADVANTAGE[defender_type] == attacker_type:
        return (0.67, "It's not very effective...")

    # Neutral matchup
    return (1.0, "")


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

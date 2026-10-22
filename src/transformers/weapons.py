"""Weapon and damage item name resolver for VALORANT kill events."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
WEAPONS_MAP_PATH = CONFIG_DIR / "weapons_map.json"
WEAPONS_GIST_PATH = CONFIG_DIR / "weapons.json"

# In-memory cached lookup
_WEAPON_NAME_LOOKUP: Dict[str, str] = {}

ABILITY_NAME_MAP: Dict[str, str] = {
    "ability1": "Habilidade 1 (Q)",
    "ability2": "Habilidade 2 (C)",
    "grenadeability": "Habilidade de Assinatura (E)",
    "ultimate": "Ultimate (X)",
    "primary": "Disparo Primário",
    "secondary": "Disparo Secundário",
}

DAMAGE_TYPE_MAP: Dict[str, str] = {
    "bomb": "Spike (Detonação)",
    "fall": "Dano de Queda",
    "crush": "Esmagamento",
    "melee": "Faca (Melee)",
}


def _load_lookup() -> Dict[str, str]:
    global _WEAPON_NAME_LOOKUP
    if _WEAPON_NAME_LOOKUP:
        return _WEAPON_NAME_LOOKUP

    lookup: Dict[str, str] = {}

    # Load from weapons_map.json if exists
    if WEAPONS_MAP_PATH.exists():
        try:
            with open(WEAPONS_MAP_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    lookup[k.strip().upper()] = v
        except Exception:
            pass

    # Fallback to weapons.json from gist
    if not lookup and WEAPONS_GIST_PATH.exists():
        try:
            with open(WEAPONS_GIST_PATH, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
                for item in raw_list:
                    uid = item.get("ID")
                    name = item.get("Name")
                    if uid and name:
                        lookup[uid.strip().upper()] = name
        except Exception:
            pass

    # Built-in essential fallbacks
    builtin_essentials = {
        "29A0CFAB-485B-F5D5-779A-B59F85E204A8": "Classic",
        "42DA8CCC-40D5-AFFC-BEEC-15AA47B42EDA": "Shorty",
        "44D4E95C-4157-0037-81B2-17841BF2E8E3": "Frenzy",
        "1BAA85B4-4C70-1284-64BB-6481DFC3BB4E": "Ghost",
        "E336C6B8-418D-9340-D77F-7A9E4CFE0702": "Sheriff",
        "F7E1B454-4AD4-1063-EC0A-159E56B58941": "Stinger",
        "462080D1-4035-2937-7C09-27AA2A5C27A7": "Spectre",
        "910BE174-449B-C412-AB22-D0873436B21B": "Bucky",
        "EC845BF4-4F79-DDDA-A3DA-0DB3774B2794": "Judge",
        "AE3DE142-4D85-2547-DD26-4E90BED35CF7": "Bulldog",
        "4ADE7FAA-4CF1-8376-95EF-39884480959B": "Guardian",
        "EE8E8D15-496B-07AC-E5F6-8FAE5D4C7B1A": "Phantom",
        "9C82E19D-4575-0200-1A81-3EACF00CF872": "Vandal",
        "C4883E50-4494-202C-3EC3-6B8A9284F00B": "Marshal",
        "5F0AAF7A-4289-3998-D5FF-EB9A5CF7EF5C": "Outlaw",
        "A03B24D3-4319-996D-0F8C-94BBFBA1DFC7": "Operator",
        "55D8A0F4-4274-CA67-FE2C-06AB45EFDF58": "Ares",
        "63E6C2B6-4A8E-869C-3D4C-E38355226584": "Odin",
        "2F59173C-4BED-B6C3-2191-DEA9B58BE9C7": "Melee (Faca)",
        "410B2E0B-4CEB-1321-1727-20858F7F3477": "Bandit",
        "8DB0A1BF-4A50-832A-4566-FAAAA6D250CA": "Warden",
    }
    for k, v in builtin_essentials.items():
        if k not in lookup:
            lookup[k] = v

    _WEAPON_NAME_LOOKUP = lookup
    return _WEAPON_NAME_LOOKUP


def resolve_damage_item_name(damage_item: Optional[str], damage_type: Optional[str] = None) -> str:
    """Resolve a raw damage item string/UUID into a clean, human-readable name."""
    lookup = _load_lookup()
    
    item_str = str(damage_item or "").strip()
    type_str = str(damage_type or "").strip().lower()

    if not item_str:
        if type_str in DAMAGE_TYPE_MAP:
            return DAMAGE_TYPE_MAP[type_str]
        return "Arma Indeterminada" if type_str == "weapon" else (damage_type or "Não Identificado")

    # Direct UUID lookup
    upper_item = item_str.upper()
    if upper_item in lookup:
        return lookup[upper_item]

    # Ability name lookup
    lower_item = item_str.lower()
    if lower_item in ABILITY_NAME_MAP:
        return ABILITY_NAME_MAP[lower_item]

    # Damage type fallbacks
    if type_str in DAMAGE_TYPE_MAP:
        return DAMAGE_TYPE_MAP[type_str]

    return item_str


def format_damage_events(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich a dataframe of kill events with human-readable weapon/item names."""
    if df.empty or "damage_item" not in df.columns:
        return df

    out = df.copy()
    damage_types = out["damage_type"] if "damage_type" in out.columns else [None] * len(out)
    
    out["weapon_name"] = [
        resolve_damage_item_name(item, dtype)
        for item, dtype in zip(out["damage_item"], damage_types)
    ]
    return out

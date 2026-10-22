"""Unit tests for weapon and damage item name resolution."""

import pytest
from src.transformers.weapons import resolve_damage_item_name, format_damage_events
import pandas as pd


def test_resolve_standard_weapons():
    # Vandal
    assert resolve_damage_item_name("9C82E19D-4575-0200-1A81-3EACF00CF872") == "Vandal"
    # Phantom
    assert resolve_damage_item_name("EE8E8D15-496B-07AC-E5F6-8FAE5D4C7B1A") == "Phantom"
    # Operator
    assert resolve_damage_item_name("A03B24D3-4319-996D-0F8C-94BBFBA1DFC7") == "Operator"
    # Classic
    assert resolve_damage_item_name("29A0CFAB-485B-F5D5-779A-B59F85E204A8") == "Classic"
    # Sheriff
    assert resolve_damage_item_name("E336C6B8-418D-9340-D77F-7A9E4CFE0702") == "Sheriff"
    # Outlaw
    assert resolve_damage_item_name("5F0AAF7A-4289-3998-D5FF-EB9A5CF7EF5C") == "Outlaw"


def test_resolve_abilities_and_types():
    assert "Habilidade 1" in resolve_damage_item_name("Ability1")
    assert "Ultimate" in resolve_damage_item_name("Ultimate")
    assert "Spike" in resolve_damage_item_name("", damage_type="Bomb")
    assert "Queda" in resolve_damage_item_name("", damage_type="Fall")
    assert "Melee" in resolve_damage_item_name("", damage_type="Melee")


def test_format_damage_events():
    df = pd.DataFrame({
        "damage_item": ["9C82E19D-4575-0200-1A81-3EACF00CF872", "Ability2", ""],
        "damage_type": ["Weapon", "Ability", "Bomb"]
    })
    enriched = format_damage_events(df)
    assert "weapon_name" in enriched.columns
    assert enriched["weapon_name"].iloc[0] == "Vandal"
    assert "Habilidade 2" in enriched["weapon_name"].iloc[1]
    assert "Spike" in enriched["weapon_name"].iloc[2]

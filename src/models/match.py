"""Pydantic v2 schemas for VALORANT match and round structures."""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class Location(BaseModel):
    model_config = ConfigDict(extra="ignore")
    x: int
    y: int


class PlayerLocation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    puuid: str
    viewRadians: Optional[float] = None
    location: Location


class PlayerKill(BaseModel):
    model_config = ConfigDict(extra="ignore")
    timeSinceGameStartMillis: Optional[int] = None
    timeSinceRoundStartMillis: int
    killer: Optional[str] = None
    victim: Optional[str] = None
    victimLocation: Optional[Location] = None
    assistants: List[str] = Field(default_factory=list)
    playerLocations: List[PlayerLocation] = Field(default_factory=list)
    finishingDamage: Optional[Dict[str, Any]] = None


class PlayerStat(BaseModel):
    model_config = ConfigDict(extra="ignore")
    puuid: str
    kills: List[PlayerKill] = Field(default_factory=list)
    damage: List[Dict[str, Any]] = Field(default_factory=list)
    score: Optional[int] = None
    economy: Optional[Dict[str, Any]] = None
    ability: Optional[Dict[str, Any]] = None


class RoundResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    roundNum: int
    roundResult: Optional[str] = None
    roundCeremony: Optional[str] = None
    winningTeam: Optional[str] = None
    winningTeamRole: Optional[str] = None
    plantRoundTime: Optional[int] = None
    plantSite: Optional[str] = None
    defuseRoundTime: Optional[int] = None
    roundResultTimeMillis: Optional[int] = None
    playerStats: List[PlayerStat] = Field(default_factory=list)


class Player(BaseModel):
    model_config = ConfigDict(extra="ignore")
    puuid: str
    gameName: Optional[str] = None
    tagLine: Optional[str] = None
    teamId: Optional[str] = None
    partyId: Optional[str] = None
    characterId: Optional[str] = None


class Team(BaseModel):
    model_config = ConfigDict(extra="ignore")
    teamId: str
    won: Optional[bool] = None
    roundsPlayed: Optional[int] = None
    roundsWon: Optional[int] = None
    numPoints: Optional[int] = None


class MatchInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    matchId: str
    mapId: str
    gameVersion: Optional[str] = None
    gameLengthMillis: Optional[int] = None
    region: Optional[str] = None
    gameStartMillis: Optional[int] = None
    isCompleted: Optional[bool] = True
    customGameName: Optional[str] = None
    queueId: Optional[str] = None
    gameMode: Optional[str] = None
    isRanked: Optional[bool] = None
    seasonId: Optional[str] = None


class Match(BaseModel):
    model_config = ConfigDict(extra="ignore")
    matchInfo: MatchInfo
    players: List[Player] = Field(default_factory=list)
    teams: List[Team] = Field(default_factory=list)
    roundResults: List[RoundResult] = Field(default_factory=list)

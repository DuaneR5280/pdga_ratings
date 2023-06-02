from pydantic import BaseModel, HttpUrl
from datetime import date, datetime
from typing import List, Optional, Dict


class TournamentDatesBase(BaseModel):
    start: date
    end: date
    num_days: int


class TournamentBase(BaseModel):
    dates: TournamentDatesBase
    tournament: str
    link: HttpUrl


class TournamentPlayedBase(TournamentBase):
    tier: str
    division: str
    round: int
    score: int
    rating: int
    evaluated: bool
    included: bool


class PlayerBase(BaseModel):
    pdga_num: int
    pdga_page: HttpUrl
    rating: int
    career_events: int
    career_wins: int
    upcoming: List[TournamentBase]
    tournaments: List[TournamentPlayedBase]


class UDiscRounds(BaseModel):
    player: str
    course: str
    layout: str
    date: datetime
    total: int
    plus_minus: Optional[int] = None
    hole_scores: Dict[str, int]

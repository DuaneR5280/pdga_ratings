from pydantic import BaseModel, HttpUrl
from datetime import date
from typing import List

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

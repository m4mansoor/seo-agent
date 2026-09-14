"""The few shapes the local tools share."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

Tier = Literal["A", "B", "C", "D"]


class Step(BaseModel):
    model_config = ConfigDict(extra="allow")
    n: int
    text: str


class Site(BaseModel):
    model_config = ConfigDict(extra="allow")
    slug: str
    name: str
    url: str
    domain: str
    method: str
    method_label: str
    tier: Tier
    da: Optional[int] = None
    dofollow: bool = True
    steps: list[Step] = []

    @classmethod
    def from_record(cls, s: dict) -> "Site":
        return cls(**{**s, "steps": [Step(**st) for st in s.get("steps", [])]})


class JobResult(BaseModel):
    slug: str
    target_url: str
    anchor_text: str
    status: Literal["placed", "unverified", "failed", "manual", "gated"]
    live_url: Optional[str] = None
    proof_path: Optional[str] = None
    notes: str = ""
    gate: Optional[dict] = None

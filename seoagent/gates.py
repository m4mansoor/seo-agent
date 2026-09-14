"""Gates: things a site asks for that the agent cannot do alone. A gate is returned to the assistant with the ways
to clear it, so the question reaches the user in the same chat instead of the job dying."""
from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel

GateType = Literal["captcha", "bot_check", "email_verification", "phone_verification", "social_login", "payment", "blocked"]


class GateOption(BaseModel):
    action: Literal["solve_in_window", "connect_service", "provide_code", "skip"]
    label: str
    service: Optional[str] = None      # captcha | inbox | sms


class Gate(BaseModel):
    id: str
    type: GateType
    site: str
    message: str
    options: list[GateOption]
    detail: str = ""

    @staticmethod
    def make(type_: GateType, site: str, detail: str = "") -> "Gate":
        msg, opts = _describe(type_, site)
        return Gate(id=uuid.uuid4().hex[:8], type=type_, site=site, message=msg, options=opts, detail=detail)


def _describe(t: GateType, site: str) -> tuple[str, list[GateOption]]:
    win = GateOption(action="solve_in_window", label="Open the browser window and let me clear it, then continue")
    skip = GateOption(action="skip", label="Skip this site and pick another")
    if t == "captcha":
        return (f"{site} shows a captcha.", [win, GateOption(action="connect_service", service="captcha", label="Connect a captcha service (2Captcha or CapSolver key) so the agent handles it from now on"), skip])
    if t == "bot_check":
        return (f"{site} blocks automated browsers with a bot check.", [win, skip])
    if t == "email_verification":
        return (f"{site} sent a verification link or code to the sign-up inbox.", [GateOption(action="connect_service", service="inbox", label="Connect the inbox (IMAP) so the agent reads the code itself"), GateOption(action="provide_code", label="Paste the code or link here"), skip])
    if t == "phone_verification":
        return (f"{site} asks for a phone number and an SMS code.", [GateOption(action="provide_code", label="Give a number, then paste the SMS code here"), GateOption(action="connect_service", service="sms", label="Connect an SMS service"), skip])
    if t == "social_login":
        return (f"{site} only signs up through a social account.", [win, skip])
    if t == "payment":
        return (f"{site} asks for a payment to continue.", [GateOption(action="solve_in_window", label="Approve and pay in the browser window, then continue"), skip])
    return (f"{site} refused the automated request.", [skip])


def gate_from_reason(reason: str, site: str) -> Gate:
    """Map the executor's bot_gate() text to a typed gate."""
    r = reason.lower()
    if "turnstile" in r or "captcha" in r:
        return Gate.make("captcha", site, reason)
    if "challenge" in r or "empty" in r:
        return Gate.make("bot_check", site, reason)
    if "firewall" in r or "blocked" in r:
        return Gate.make("blocked", site, reason)
    return Gate.make("bot_check", site, reason)

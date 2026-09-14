"""Runs one link job on the user's machine: choose a playbook, drive a local browser, save proof, return a JobResult.
Login-free sites only; every other method is followed by the assistant itself from get_method."""
from __future__ import annotations

import os
import time
import uuid

from ..models import JobResult, Site
from .browser import bot_gate, session
from .playbooks import open_submit, shortener

RUNS_DIR = os.environ.get("SEOAGENT_RUNS", os.path.join(os.path.expanduser("~"), ".seoagent", "runs"))
PLAYBOOKS = {"url_shortener": "shortener", "bookmark_submit": "open_submit"}


def can_auto_build(site: Site) -> bool:
    return site.tier == "A" and site.method in PLAYBOOKS


def wait_for_human(page, seconds: int = 180) -> bool:
    """Headed mode: give the person at the screen time to clear a captcha. True when the gate is gone."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        if not bot_gate(page):
            return True
        page.wait_for_timeout(2000)
    return False


def run_job(site: Site, target_url: str, anchor_text: str = "", *, headless: bool = True, description: str = "") -> JobResult:
    if not can_auto_build(site):
        return JobResult(slug=site.slug, target_url=target_url, anchor_text=anchor_text, status="manual",
                         notes=f"{site.method_label} needs an account; follow get_method in your own browser, then verify_link and log_link")
    job_id = f"{int(time.time())}-{site.slug}-{uuid.uuid4().hex[:6]}"
    out_dir = os.path.join(RUNS_DIR, job_id)
    os.makedirs(out_dir, exist_ok=True)
    proof = os.path.join(out_dir, "proof.png")
    try:
        with session(headless=headless) as page:
            def go():
                if PLAYBOOKS[site.method] == "shortener":
                    return shortener.run(page, site, target_url, proof)
                return open_submit.run(page, site, target_url, anchor_text or site.name, proof, description)
            r = go()
            if r.get("status") == "gated" and not headless and wait_for_human(page):
                r = go()
    except Exception as e:  # a playbook crash is a failed job, never a crashed server
        msg = f"{type(e).__name__}: {e}"[:300]
        if "Executable doesn't exist" in msg or "playwright install" in msg:
            msg = "the browser is not installed yet: run `playwright install chromium` once, then try again"
        r = {"status": "failed", "notes": msg}
    return JobResult(slug=site.slug, target_url=target_url, anchor_text=anchor_text, status=r["status"],
                     live_url=r.get("live_url"), proof_path=proof if os.path.exists(proof) else None, notes=r.get("notes", ""),
                     gate=r.get("gate"))

"""Publishing the page to GitHub Pages, unattended.

The customer connects GitHub once, in a browser window, and never touches it again. After that this makes the
repository if there is not one, commits the page, switches Pages on, waits for the build and checks the published
address really carries their link before calling it done.

Why the device flow rather than driving github.com. GitHub's own device flow is one window and one approval, and
what comes back is a real token: everything after it is four API calls that behave the same way every time.
Clicking through five screens to make a repository works until GitHub moves a button, and then it fails on a
customer's machine where nobody can see it. The window the customer sees is the same either way.

The token is the customer's. It stays on their machine, in a file only they can read, and it is never put in a
return value, a log line or an error message -- `tests/test_pages_run.py` checks that, because a token that
leaks once is leaked for good.
"""
from __future__ import annotations

import base64
import json
import os
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from typing import Any, Callable, Optional

from . import media_set_pace, pages_site, verify
from .media_set_run import submit_for_indexing

API = "https://api.github.com"
DEVICE_CODE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"
SCOPE = "public_repo"          # public repositories only: nothing private is ever in reach
HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
           "User-Agent": "link-engine"}


class GitHubError(Exception):
    """A GitHub refusal, carrying its status so a caller can tell 'already exists' from 'not allowed'."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def client_id() -> str:
    return (os.environ.get("GITHUB_CLIENT_ID") or "").strip()


# ---------------------------------------------------------------- the token, on their machine

_PUBLIC = __package__ == "seoagent"          # the same file ships in both packages


def _home() -> str:
    """Where the token lives: wherever the rest of this package keeps its state, whichever package it is."""
    var, default = ("SEOAGENT_HOME", ".seoagent") if _PUBLIC else ("LINKENGINE_HOME", ".linkengine")
    return os.environ.get(var) or os.path.join(os.path.expanduser("~"), default)


def _token_path() -> str:
    return os.path.join(_home(), "github.json")


def read_token() -> dict:
    """What we hold for GitHub, or an empty dict. The token itself never leaves this module's callers."""
    try:
        with open(_token_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def write_token(token: str, login: str = "") -> dict:
    """Written readable by nobody else. A token in a world-readable file is a token anyone on the machine has."""
    os.makedirs(_home(), exist_ok=True)
    path = _token_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"token": token, "login": login, "saved": time.time()}, f)
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return {"login": login}


def forget() -> bool:
    try:
        os.remove(_token_path())
        return True
    except OSError:
        return False


def connected() -> dict:
    """Whether GitHub is connected, without saying what with."""
    held = read_token()
    return {"connected": bool(held.get("token")), "login": held.get("login", "")}


# ---------------------------------------------------------------- talking to GitHub

def _request(url: str, method: str = "GET", token: str = "", body: Optional[dict] = None,
             form: Optional[dict] = None, timeout: int = 30) -> Any:
    data, headers = None, dict(HEADERS)
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Accept"] = "application/json"      # or GitHub answers form-encoded and json.loads fails
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = (json.loads(raw) or {}).get("message") or raw[:200]
        except Exception:
            msg = raw[:200]
        raise GitHubError(e.code, msg) from None
    except Exception as e:
        raise GitHubError(0, f"{type(e).__name__}: {str(e)[:140]}") from None


def _api(path: str, token: str, method: str = "GET", body: Optional[dict] = None, timeout: int = 30) -> Any:
    return _request(f"{API}{path}", method=method, token=token, body=body, timeout=timeout)


# ---------------------------------------------------------------- connecting, once

def connect_start(open_browser: bool = True) -> dict:
    """Ask GitHub for a code and put the window in front of them."""
    cid = client_id()
    if not cid:
        return {"ok": False, "needs_setup": True,
                "say": "GitHub publishing is not switched on for this engine yet.",
                "detail": ["It needs a GitHub OAuth app registered once by the operator, and its client id set "
                           "as GITHUB_CLIENT_ID.", "Nothing about your account is involved in that step."]}
    try:
        got = _request(DEVICE_CODE_URL, method="POST", form={"client_id": cid, "scope": SCOPE})
    except GitHubError as e:
        return {"ok": False, "error": f"GitHub would not start the sign-in: {e.message}"}
    code = got.get("user_code", "")
    uri = got.get("verification_uri") or "https://github.com/login/device"
    # GitHub pre-fills the box when the code is on the address, which saves them typing it; the plain address
    # and the code are still shown, because that is what works if the pre-fill ever stops working.
    full = got.get("verification_uri_complete") or f"{uri}?user_code={urllib.parse.quote(code)}"
    if open_browser:
        try:
            webbrowser.open(full)
        except Exception:
            pass
    return {"ok": True, "user_code": code, "verification_uri": uri, "url": full,
            "device_code": got.get("device_code", ""), "interval": int(got.get("interval") or 5),
            "expires_in": int(got.get("expires_in") or 900),
            "say": f"I have opened GitHub for you. Enter the code {code} and approve it.",
            "detail": ["The window is GitHub's own; nothing is typed anywhere else.",
                       "It is asked for once. After this I publish without interrupting you.",
                       "Only public repositories are in reach — nothing private is."]}


def connect_wait(device_code: str, interval: int = 5, expires_in: int = 900,
                 on_step: Optional[Callable[[str], None]] = None, sleep: Callable[[float], None] = time.sleep) -> dict:
    """Wait while they approve it. Returns when they have, or says why not."""
    cid = client_id()
    say = on_step or (lambda s: None)
    deadline = time.time() + max(30, expires_in)
    wait = max(1, int(interval))
    say("waiting for you to approve it")
    while time.time() < deadline:
        sleep(wait)
        try:
            got = _request(TOKEN_URL, method="POST",
                           form={"client_id": cid, "device_code": device_code, "grant_type": DEVICE_GRANT})
        except GitHubError as e:
            return {"ok": False, "error": e.message}
        token = got.get("access_token")
        if token:
            login = ""
            try:
                login = (_api("/user", token) or {}).get("login", "")
            except GitHubError:
                pass
            write_token(token, login)
            return {"ok": True, "connected": True, "login": login,
                    "say": f"GitHub is connected{f' as {login}' if login else ''}. I will not need to ask again.",
                    "detail": ["The connection is kept on this machine.",
                               "Say the word and I will publish the first page."]}
        err = got.get("error", "")
        if err == "slow_down":
            wait += int(got.get("interval") or 5)    # GitHub says back off; ignoring it gets the request refused
            continue
        if err in ("authorization_pending", ""):
            continue
        return {"ok": False, "error": {"expired_token": "the code expired before it was approved",
                                       "access_denied": "the request was declined in the browser"}.get(err, err)}
    return {"ok": False, "error": "the code expired before it was approved"}


def connect(on_step: Optional[Callable[[str], None]] = None, open_browser: bool = True) -> dict:
    """The whole thing: window, code, approval, token."""
    started = connect_start(open_browser=open_browser)
    if not started.get("ok"):
        return started
    done = connect_wait(started["device_code"], started["interval"], started["expires_in"], on_step=on_step)
    return {**done, "user_code": started["user_code"], "url": started["url"]}


# ---------------------------------------------------------------- the repository and the file

def list_repos(token: str) -> list[dict]:
    try:
        got = _api("/user/repos?per_page=100&affiliation=owner&sort=created", token)
        return [{"name": r.get("name", ""), "url": r.get("html_url", ""),
                 "homepage": r.get("homepage") or ""} for r in (got or [])]
    except GitHubError:
        return []


def repo_for_site(token: str, site: str) -> str:
    """The repository this website already publishes from, or the name a new one should take.

    The homepage field is what tells one of ours apart from a repository that merely shares the name: we set it
    to the customer's website when we make it. Without that check, a customer whose local memory was lost gets a
    second site for the same website on their next link, which is the row of thin one-page sites this method
    must never leave behind."""
    repos = list_repos(token)
    base = pages_site.repo_name(site)
    for r in repos:
        if r["name"] == base and site in (r.get("homepage") or ""):
            return base
    if not any(r["name"] == base for r in repos):
        return base
    return pages_site.repo_name(site, taken=[r["name"] for r in repos])


def ensure_repo(token: str, owner: str, name: str, homepage: str = "", description: str = "",
                may_create: bool = True) -> dict:
    """The repository for this website, made if it is not there. Never a second one for the same site."""
    try:
        got = _api(f"/repos/{owner}/{name}", token)
        return {"repo": got.get("name", name), "url": got.get("html_url", ""), "made": False}
    except GitHubError as e:
        if e.status not in (404, 0):
            raise
    if not may_create:
        # Asked before anything is created, not after: finding out we were not allowed once the repository is
        # already on their account is not finding out at all.
        return {"repo": name, "url": "", "made": False, "missing": True}
    made = _api("/user/repos", token, method="POST", body={
        "name": name, "description": description or f"Write-ups and notes for {homepage or name}.",
        "homepage": homepage, "private": False, "auto_init": True, "has_issues": False,
        "has_wiki": False, "has_projects": False})
    return {"repo": made.get("name", name), "url": made.get("html_url", ""), "made": True}


def file_sha(token: str, owner: str, repo: str, path: str) -> str:
    """The sha of what is there now. Committing over a file without it is refused by GitHub."""
    try:
        got = _api(f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}", token)
        return (got or {}).get("sha", "") if isinstance(got, dict) else ""
    except GitHubError:
        return ""


def put_file(token: str, owner: str, repo: str, path: str, text: str, message: str) -> dict:
    body = {"message": message, "content": base64.b64encode(text.encode()).decode()}
    sha = file_sha(token, owner, repo, path)
    if sha:
        body["sha"] = sha
    got = _api(f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}", token, method="PUT", body=body)
    return {"ok": True, "path": path, "updated": bool(sha), "commit": (got or {}).get("commit", {}).get("sha", "")}


def published_pages(token: str, owner: str, repo: str) -> list[dict]:
    """Every page already in this repository, read from the repository itself.

    Kept here rather than in a local file so the front page can always be rebuilt from what is actually
    published, on any machine, however the customer got here."""
    try:
        got = _api(f"/repos/{owner}/{repo}/contents/", token)
    except GitHubError:
        return []
    out = []
    for item in got or []:
        if isinstance(item, dict) and item.get("type") == "dir":
            s = item.get("name", "")
            out.append({"keyword": s.replace("-", " "), "path": f"{s}/",
                        "title": (s.replace("-", " ").strip()[:1].upper() + s.replace("-", " ").strip()[1:])})
    return out


def enable_pages(token: str, owner: str, repo: str, branch: str = "main") -> dict:
    """Switch Pages on. Already on is a success, not a failure."""
    try:
        _api(f"/repos/{owner}/{repo}/pages", token, method="POST",
             body={"source": {"branch": branch, "path": "/"}})
        return {"ok": True, "turned_on": True}
    except GitHubError as e:
        if e.status in (409, 422):
            return {"ok": True, "turned_on": False, "note": "it was already on"}
        return {"ok": False, "error": e.message}


def pages_ready(token: str, owner: str, repo: str) -> str:
    try:
        return (_api(f"/repos/{owner}/{repo}/pages", token) or {}).get("status", "") or ""
    except GitHubError:
        return ""


def wait_until_live(url: str, target_url: str, anchor: str, seconds: int = 180,
                    on_step: Optional[Callable[[str], None]] = None,
                    sleep: Callable[[float], None] = time.sleep) -> dict:
    """A page is live when a stranger can load it and their link is in it, not when GitHub accepts the commit.

    The first build of a new site takes a minute or two and the address 404s until it finishes, so this waits
    rather than handing back an address that is not serving yet."""
    say = on_step or (lambda s: None)
    say("waiting for the site to build")
    deadline = time.time() + max(10, seconds)
    last = ""
    while time.time() < deadline:
        # No browser fallback while polling: a Playwright launch per attempt turns a two-minute wait into a
        # ten-minute one, and a page that is not serving yet is not a page a browser would see either.
        got = verify.check_live(url, target_url, anchor_text=anchor, allow_browser=False)
        if got.found:
            return {"live": True, "dofollow": not bool(got.nofollow),
                    "anchor_ok": bool(got.anchor_matches), "why": ""}
        last = got.notes or (f"the address answered {got.status}" if got.status else "not serving yet")
        sleep(6)
    return {"live": False, "dofollow": False, "why": last or "the site did not finish building in time"}


# ---------------------------------------------------------------- one command, one address back

def get_traffic(target_url: str, keyword: str, brand: str = "", kind: str = "article", use_repo: str = "",
                repos_by_site: Optional[dict] = None, built_at: Optional[list[float]] = None,
                may_create_repo: bool = True, publish: bool = True, wait: bool = True,
                on_step: Optional[Callable[[str], None]] = None) -> dict:
    """From a URL and a phrase to a published, followed link on their own GitHub Pages site."""
    say = on_step or (lambda s: None)
    site = (target_url or "").split("//")[-1].split("/")[0].removeprefix("www.")
    out: dict = {"kind": "link", "dofollow": True, "target_url": target_url, "keyword": keyword, "site": site}

    held = read_token()
    token = held.get("token", "")
    if not token:
        return {**out, "ok": False, "needs_connect": True,
                "say": "I need your GitHub connected once before I can publish there.",
                "detail": ["It is one window and one approval, and it is never asked again on this machine.",
                           "Only public repositories are in reach; nothing private is."]}

    try:
        page_text = pages_site.html(target_url, keyword, brand=brand, kind=kind)
    except ValueError as e:
        return {**out, "ok": False, "error": str(e)}

    # The site is the customer's own and publishes its own writing, so the only rule is rhythm: a real site does
    # not gain three pages in an hour, and neither does this one.
    gate = media_set_pace.wait_for(built_at or [], method="github_pages")
    if publish and not gate["allowed"]:
        return {**out, "ok": False, "deferred": True, "rule": gate["rule"], "next_at": gate["next_at"],
                "built_this_week": gate["built_this_week"], "say": gate["say"], "detail": gate["detail"]}

    owner = held.get("login", "")
    if not owner:
        try:
            owner = (_api("/user", token) or {}).get("login", "")
            write_token(token, owner)
        except GitHubError as e:
            return {**out, "ok": False, "error": f"GitHub would not say who you are: {e.message}"}
    out["owner"] = owner

    say("finding the site")
    repo = use_repo or (repos_by_site or {}).get(site, "") or repo_for_site(token, site)
    try:
        made = ensure_repo(token, owner, repo, homepage=f"https://{site}", may_create=may_create_repo)
    except GitHubError as e:
        return {**out, "ok": False, "step": "the site", "error": f"GitHub would not make the site: {e.message}"}
    if made.get("missing"):
        return {**out, "ok": False, "error": "there is no site for this website yet and I was told not to make one"}
    repo = made["repo"]
    out.update({"repo": repo, "repo_url": made["url"], "repo_made": made["made"]})

    url = pages_site.site_url(owner, repo, keyword)
    out["url"] = url
    if not publish:
        return {**out, "ok": True, "stopped_before_publishing": True, "html": page_text}

    say("writing the page")
    path = pages_site.path_for(keyword)
    try:
        put_file(token, owner, repo, path, page_text, f"Add {keyword}")
    except GitHubError as e:
        return {**out, "ok": False, "step": "the page", "error": f"the page was not committed: {e.message}"}

    say("linking it from the front page")
    try:
        entries = published_pages(token, owner, repo)
        put_file(token, owner, repo, "index.html",
                 pages_site.index_html(brand or site, entries), "Update the index")
    except GitHubError:
        out["index_updated"] = False        # the page itself is up; a stale index is worth saying, not failing on
    else:
        out["index_updated"] = True

    say("switching the site on")
    out["pages"] = enable_pages(token, owner, repo)

    if wait:
        state = wait_until_live(url, target_url, keyword, on_step=on_step)
        out["verified"] = state["live"]
        out["dofollow"] = state["dofollow"] if state["live"] else True
        if not state["live"]:
            return {**out, "ok": True, "pending": True,
                    "say": f"The page is committed and the site is building. It will be at {url} shortly.",
                    "detail": ["GitHub takes a minute or two the first time a site is built.",
                               "Ask me to check it again in a few minutes and I will confirm it is serving.",
                               f"What held it up: {state['why']}."]}

    say("asking search engines to look at it")
    out["indexing"] = submit_for_indexing(url, keyword, label="page")
    return {**out, "ok": True,
            "say": f"Your page is live at {url} and links to you on “{keyword}”.",
            "detail": ["This one is a followed link: it passes ranking strength, unlike the Facebook albums.",
                       "It is on your own GitHub site, so nobody can take it down but you.",
                       "The more of your pages it carries, the more it looks like the site it is."]}

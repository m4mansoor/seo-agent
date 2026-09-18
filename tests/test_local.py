import json, os, tempfile

import pytest


@pytest.fixture(autouse=True)
def home(monkeypatch, tmp_path):
    monkeypatch.setenv("SEOAGENT_HOME", str(tmp_path))
    monkeypatch.delenv("SEOAGENT_API_KEY", raising=False)
    monkeypatch.delenv("SEOAGENT_URL", raising=False)
    from seoagent import local
    monkeypatch.setattr(local, "HOME", str(tmp_path))
    yield


def test_free_sites_load_and_mark_auto_build():
    from seoagent.server import N_FREE, search_sites, get_method, library_summary
    res = search_sites(limit=100); rows = res["free"]
    assert len(rows) == N_FREE == 25 and sum(1 for r in rows if r["auto_build"]) >= 4 and sum(1 for r in rows if r["da"] >= 90) == 2
    assert "ask_the_user" not in res or res["free_total"] < 100
    m = get_method("ouo-press")
    assert m["method"] == "url_shortener" and "playbook" in m and any(a["is_placement"] for a in m["steps"])
    assert library_summary()["subscription"]["plans"]["yearly"]["price_usd"] == 97 and library_summary()["subscription"]["plans"]["monthly"]["price_usd"] == 27


def test_high_da_search_shows_locked_sites_and_offers_upgrade():
    from seoagent.server import build_link, get_method, search_sites
    res = search_sites(min_da=90, limit=25)
    assert res["free_total"] == 2 and len(res["locked_examples"]) == 5 and all(t["locked"] and t["da"] >= 90 for t in res["locked_examples"])
    assert "ask_the_user" in res and "$97 a year" in res["ask_the_user"] and res["full_library"]["da_90_plus"] >= 100
    slug = res["locked_examples"][0]["slug"]
    assert get_method(slug)["locked"] and "subscription" in get_method(slug)["error"]
    assert build_link(slug, "https://t.com/")["locked"]
    assert "ask_the_user" not in search_sites(query="ouo", limit=25) or search_sites(query="ouo", limit=25)["free_total"] == 1


def test_credentials_from_config_and_personal_link(monkeypatch):
    from seoagent import local, server
    assert not server.hosted()
    local.write_config(api_key="le_abc", url="https://mcp.example.com/mcp")
    assert server.hosted() and server.credentials() == ("https://mcp.example.com/mcp", "le_abc")
    monkeypatch.setenv("SEOAGENT_URL", "https://mcp.example.com/u/le_xyz/mcp")
    monkeypatch.setenv("SEOAGENT_API_KEY", "")
    assert server.credentials()[1] == "le_xyz"


def test_log_and_list_results_and_account():
    from seoagent.server import account, list_results, log_link
    r = log_link("medium-2", "https://t.com/", "https://medium.com/@x/p", "T", "placed")
    assert r["id"] == 1 and list_results()["placed"] == 1
    a = account()
    assert a["plan"] == "free" and a["links_placed"] == 1 and a["upgrade"]["plans"]["yearly"]["url"].endswith("/buy?plan=yearly")


def test_verify_html():
    from seoagent.verify import check_html
    c = check_html('<p>see <a href="https://t.com/" rel="nofollow">Anchor</a></p>', "https://t.com/", "Anchor")
    assert c.found and c.nofollow and c.anchor_matches


def test_build_link_refuses_unknown_and_reports_manual():
    from seoagent.server import build_link
    assert "error" in build_link("nope", "https://t.com/")
    r = build_link("medium-2", "https://t.com/")
    assert r["status"] == "manual" and "steps" in r


@pytest.mark.slow
def test_build_link_runs_locally_on_a_fake_shortener(monkeypatch):
    from seoagent import server
    html = "<html><body><p>Paste your long link below to shorten it.</p><form onsubmit=\"event.preventDefault();document.body.innerHTML='<p>Short link: <a href=\\'https://fake.test/abc\\'>https://fake.test/abc</a></p>'\"><input type=text name=url placeholder='Long URL'><button>Shorten</button></form></body></html>"
    fake = {"slug": "fake-short", "name": "Fake Shortener", "url": "data:text/html," + html, "domain": "fake.test", "method": "url_shortener",
            "method_label": "URL shortener", "tier": "A", "da": 10, "dofollow": True, "steps": [], "requirements": [], "placement_step": "",
            "referring_domains": 0, "organic_traffic": 0, "spam_score": 0}
    monkeypatch.setitem(server.BY_SLUG, "fake-short", fake)
    r = server.build_link("fake-short", "https://example.com/")
    assert r["status"] in ("placed", "unverified", "failed") and "links_placed" in r
    assert server.list_results()["results"][0]["slug"] == "fake-short"


# ---------------------------------------------------------------- where each tool runs

def test_browser_work_stays_on_this_machine_even_on_a_paid_plan():
    """A subscription buys the library and the planner, not a place to keep someone's Facebook session. Anything
    driving a browser needs their own signed-in accounts, so sending it to a server would break it and would put
    their password somewhere it has no business being."""
    from seoagent import server
    for name in ("get_traffic", "build_link", "facebook_sign_in", "verify_link"):
        assert server.runs_here(name), f"{name} must run on the person's machine"
    for name in ("search_sites", "plan_campaign", "monitor_backlinks", "competitor_gap", "campaign_report"):
        assert not server.runs_here(name), f"{name} belongs on the engine, where the data is"


def test_the_browser_tools_are_offered_whether_or_not_they_have_a_key():
    from seoagent import server
    names = {t.name for t in server.FREE_TOOLS}
    assert {"get_traffic", "facebook_sign_in"} <= names, "listed, so the assistant can offer them and say what they cost"


def test_the_asset_methods_are_offered_but_locked_until_they_subscribe(monkeypatch):
    """They are in the tool list on purpose: an assistant that cannot see them cannot tell anyone they exist."""
    from seoagent import server
    monkeypatch.setattr(server, "subscribed", lambda: False)
    for name, call in (("get_traffic", lambda: server.get_traffic("https://lmrify.com/x", "a phrase")),
                       ("traffic_plan", lambda: server.traffic_plan("https://lmrify.com/x")),
                       ("publish_page", lambda: server.publish_page("https://lmrify.com/x", "a phrase")),
                       ("facebook_sign_in", lambda: server.facebook_sign_in()),
                       ("github_connect", lambda: server.github_connect())):
        out = call()
        assert out["reason"] == "paid_only", name
        assert out["upgrade"]["plans"], f"{name} says what it costs, not just no"


def test_get_traffic_asks_a_subscriber_for_a_sign_in_rather_than_failing(tmp_path, monkeypatch):
    """With no signed-in browser on the machine there is nothing to do, and the person must be told plainly what
    to do next rather than shown an error."""
    from seoagent import media_set_run, server
    monkeypatch.setattr(server, "subscribed", lambda: True)
    monkeypatch.setattr(media_set_run, "profile_dir", lambda n: str(tmp_path / "nothing-here"))
    out = server.get_traffic("https://lmrify.com/x", "a phrase")
    assert out["needs_sign_in"] is True
    assert out["say"] and "sign" in out["say"].lower()
    assert not out.get("ok")


def test_an_unreachable_engine_does_not_take_the_local_tools_with_it(monkeypatch):
    """Their browser is on their machine. If our server is down, or their connection drops, the work that never
    needed us must carry on."""
    import asyncio

    from seoagent import server

    async def boom(*a, **k):
        raise ConnectionError("engine down")

    monkeypatch.setattr(server, "hosted", lambda: True)
    monkeypatch.setattr(server, "_remote_session", boom)
    tools = asyncio.run(server.list_tools())
    names = {t.name for t in tools}
    assert {"get_traffic", "facebook_sign_in", "build_link"} <= names, "browser tools must survive an outage"

    out = asyncio.run(server.call_tool("account", {}))
    text = "".join(c.text for c in out)
    assert "unreachable" not in text.lower(), "account has a local version and should have used it"
    assert "plan" in text.lower()

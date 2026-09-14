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
    from seoagent.server import search_sites, get_method, library_summary
    rows = search_sites(limit=100)
    assert len(rows) == 50 and sum(1 for r in rows if r["auto_build"]) >= 4
    m = get_method("ouo-press")
    assert m["method"] == "url_shortener" and "playbook" in m and any(a["is_placement"] for a in m["steps"])
    assert library_summary()["subscription"]["plans"]["yearly"]["price_usd"] == 97 and library_summary()["subscription"]["plans"]["monthly"]["price_usd"] == 27


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
    r = log_link("gitbook", "https://t.com/", "https://x.gitbook.io/p", "T", "placed")
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
    r = build_link("gitbook", "https://t.com/")
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

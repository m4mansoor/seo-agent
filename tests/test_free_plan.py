"""What the free plan includes: ten links, one of them strong, and neither of the two asset methods.

The rule that stops a build and the sentence a person reads come from the same function, so they cannot drift.
"""
from seoagent import free


def test_ten_links_is_the_free_plan():
    assert free.check(placed=0, strong_placed=0, da=40)["allowed"] is True
    assert free.check(placed=9, strong_placed=0, da=40)["allowed"] is True, "the tenth is still free"
    used = free.check(placed=10, strong_placed=0, da=40)
    assert used["allowed"] is False and used["reason"] == "used_up"
    assert "10 free links" in used["say"]


def test_one_of_the_ten_may_be_on_a_strong_site():
    assert free.check(placed=0, strong_placed=0, da=95)["allowed"] is True
    second = free.check(placed=1, strong_placed=1, da=95)
    assert second["allowed"] is False and second["reason"] == "strong_used"


def test_using_the_strong_one_does_not_cost_the_other_nine():
    after = free.check(placed=1, strong_placed=1, da=40)
    assert after["allowed"] is True, "nine ordinary links are still there"
    assert after["remaining"]["links"] == 8


def test_the_strong_rule_is_answered_before_the_total_because_it_is_the_true_reason():
    """Telling someone they are out of links when they have eight left sends them back with another DA 90 site."""
    got = free.check(placed=2, strong_placed=1, da=96)
    assert got["reason"] == "strong_used"
    assert "8 free links left" in " ".join(got["detail"])


def test_ninety_is_where_strong_starts():
    assert free.is_strong(90) is True
    assert free.is_strong(89) is False


def test_a_subscription_is_not_counted_at_all():
    got = free.check(placed=500, strong_placed=99, da=99, paid=True)
    assert got["allowed"] is True and got["say"] == ""


def test_facebook_and_github_are_not_in_the_free_plan():
    for name in ("get_traffic", "traffic_plan", "facebook_sign_in", "publish_page", "github_connect"):
        got = free.tool(name)
        assert got["allowed"] is False, name
        assert got["reason"] == "paid_only"
        assert "subscription" in got["say"]


def test_the_ordinary_tools_are_free():
    for name in ("build_link", "verify_link", "log_link", "list_results", "search_sites"):
        assert free.tool(name)["allowed"] is True, name


def test_a_subscriber_may_use_every_method():
    assert free.tool("publish_page", paid=True)["allowed"] is True


def test_what_is_left_is_said_in_the_two_numbers_that_matter():
    s = free.summary(placed=3, strong_placed=0)
    assert s["links_left"] == 7 and s["strong_left"] == 1
    assert "7 of 10" in s["say"] and "DA 90" in s["say"]
    spent = free.summary(placed=3, strong_placed=1)
    assert "strong one is used" in spent["say"]


def test_a_subscriber_is_not_shown_a_remaining_count():
    assert free.summary(placed=0, strong_placed=0, paid=True)["plan"] == "subscription"


def test_nothing_ever_goes_negative():
    room = free.left(placed=99, strong_placed=99)
    assert room == {"links": 0, "strong": 0}


def test_the_allowance_is_enforced_before_a_browser_is_opened(monkeypatch):
    """Spending a minute building something we will not save is worse than saying so up front."""
    from seoagent import server
    monkeypatch.setattr(server, "subscribed", lambda: False)
    monkeypatch.setattr(server, "_spent", lambda: (free.FREE_LINKS, 0))
    opened = []
    monkeypatch.setattr("seoagent.agent.executor.run_job", lambda *a, **k: opened.append(1))
    slug = next(s["slug"] for s in server.SITES)
    out = server.build_link(slug, "https://lmrify.com/x", "anchor")
    assert out["status"] == "locked" and out["reason"] == "used_up"
    assert not opened, "no browser was opened for a link we would not keep"


def test_a_strong_site_is_refused_once_the_strong_one_is_spent(monkeypatch):
    from seoagent import server
    monkeypatch.setattr(server, "subscribed", lambda: False)
    monkeypatch.setattr(server, "_spent", lambda: (2, 1))
    strong = next((s["slug"] for s in server.SITES if free.is_strong(s.get("da") or 0)), "")
    assert strong, "the free list carries at least one DA 90+ site"
    out = server.build_link(strong, "https://lmrify.com/x", "anchor")
    assert out["status"] == "locked" and out["reason"] == "strong_used"


def test_an_ordinary_site_still_builds_with_the_strong_one_spent(monkeypatch):
    from seoagent import server
    monkeypatch.setattr(server, "subscribed", lambda: False)
    monkeypatch.setattr(server, "_spent", lambda: (2, 1))
    ordinary = next(s["slug"] for s in server.SITES if not free.is_strong(s.get("da") or 0))
    out = server.build_link(ordinary, "https://lmrify.com/x", "anchor")
    assert out.get("status") != "locked", "eight links are still theirs to use"


def test_what_we_say_about_the_plan_is_what_we_enforce():
    """The number in the sentence and the number in the check are the same object, so they cannot drift."""
    from seoagent import server
    note = server.account()["note"]
    assert f"{free.FREE_LINKS} links" in note
    assert "DA 90+" in note
    assert "Facebook albums" in note and "GitHub Pages" in note, "what is not in the free plan is said, not implied"


def test_the_readme_states_the_plan_the_code_enforces():
    """A README promising fifty while the code gives ten is the complaint nobody needs to receive."""
    import pathlib
    readme = pathlib.Path(__file__).resolve().parents[1] / "README.md"
    if not readme.exists():
        return                          # installed from a wheel, where the README does not ship
    text = readme.read_text().lower()
    assert "ten links" in text
    assert "50 free" not in text and "fifty free" not in text


def test_no_file_in_the_package_still_promises_the_old_free_plan():
    """A stale number in a README is a promise someone will hold us to."""
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parents[1]
    stale = re.compile(r"free[^.\n]{0,40}\b(50|25)\b\s*(links|built)|\b50\b[^.\n]{0,30}(free|built) links", re.I)
    found = []
    for p in list(root.glob("*.md")) + list(root.glob("docs/*.md")) + list(root.glob("seoagent/**/*.py")):
        if "test_free_plan" in p.name:
            continue
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            if stale.search(line):
                found.append(f"{p.relative_to(root)}:{i}: {line.strip()[:90]}")
    assert not found, "these still promise the old free plan:\n" + "\n".join(found)


def test_every_published_link_points_at_the_domain_we_own():
    """seoagent.dev was registered by someone else while our README still sent buyers there. A published link to
    a domain we do not own is a link to whatever a stranger decides to put on it."""
    import pathlib
    import re
    from seoagent import server
    ours = server.HOST.split("//", 1)[1].rstrip("/")
    root = pathlib.Path(__file__).resolve().parents[1]
    bad = []
    for p in [root / "README.md"] + sorted(root.glob("docs/*.md")) + sorted(root.glob("docs/*.html")):
        for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
            for host in re.findall(r"https?://([a-z0-9.-]*seoagents?\.dev)", line):
                if host != ours:
                    bad.append(f"{p.relative_to(root)}:{i}: {host} (we serve {ours})")
    assert not bad, "published links point somewhere we do not own:\n" + "\n".join(bad)


def test_every_stated_library_size_is_the_real_one():
    """Four different counts were live at once, none of them current. The claim and the data are now one thing:
    a monthly sweep that changes the library fails this until the copy is updated with it."""
    import json
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parents[1]
    stats = json.loads((root / "seoagent/data/library_stats.json").read_text())
    ok = {f"{stats['reachable']:,}", f"{stats['sites']:,}", str(stats["reachable"]), str(stats["sites"])}
    # Only the shapes that are a claim about the library. A referring-domain figure like 1,371,100 is not one.
    claims = [r"([\d,]+),? (?:backlink )?sites?, (?:every one )?verified", r"([\d,]+)[- ]site library",
              r"library of ([\d,]+) sites", r"full ([\d,]+)[- ]site", r"[Ee]very one of ([\d,]+) sites",
              r"all ([\d,]+) verified-reachable sites", r"catalogue holds ([\d,]+)"]
    bad = []
    for p in [root / "README.md"] + sorted(root.glob("docs/*.md")) + sorted(root.glob("docs/*.html")):
        text = p.read_text(errors="ignore")
        for pat in claims:
            for n in re.findall(pat, text):
                if n not in ok:
                    bad.append(f"{p.relative_to(root)}: claims {n}, library has {stats['reachable']:,} reachable of {stats['sites']:,}")
    assert not bad, "stated library size is not the real one:\n" + "\n".join(sorted(set(bad)))


def test_the_package_reports_the_version_it_ships_as():
    """They disagreed: the module said 0.1.0 while the wheel said 0.2.0, so a bug report named the wrong build."""
    import pathlib
    import tomllib
    import seoagent
    root = pathlib.Path(__file__).resolve().parents[1]
    declared = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    assert seoagent.__version__ == declared

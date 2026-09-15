# SEO Agent (public) — working notes for Claude

Thin MCP client `seoagent/` plus the docs/marketing site in `docs/` (Jekyll, GitHub Pages from `/docs`, live at https://m4mansoor.github.io/seo-agent/). The engine itself is the private sibling repo `../AI Backlinks`.

## Site
- `docs/_layouts/default.html` owns the nav, the per-page deep title band and the footer — add a page there, not just in `docs/`.
- Styles: `docs/assets/site.css`. Tokens at the top (paper/ink/teal/amber/mark, Bricolage Grotesque + IBM Plex Sans); marketing rules are the `.mk-*` block at the end. Keep new pages inside this system.
- `.md` pages: the band shows the front-matter title, so the first `# H1` is hidden by CSS. Give every page a `title` and `description`.
- Numbers on the site must match the engine's last sweep (1,138 reachable, 117 DA90+, 813 followed, 25 free, 26 tools). "1,245" only as catalogue size beside the reachable count. Never name the data vendor.

## Preview without Ruby
- `python3 scripts/preview_docs.py /tmp/site 8123` renders the Liquid the layout uses and converts `.md` (needs the `markdown` package — `../AI\ Backlinks/.venv312/bin/python` has it), then serves on http://localhost:8123/.
- It copies assets at start: **restart it after CSS edits**, and confirm with `curl` that the served CSS contains the change.
- Look once with a Playwright screenshot at 1280 and 400 wide; check `document.documentElement.scrollWidth` is 400 on phone.

## Publishing
- Commit as `Inaamul Haq Mansoor <inaam@techmentions.com>`, no Claude trailer. Push only when the user says so; Pages rebuilds in ~1–3 min. Verify with `curl -s <url> | grep '<title>'`.
- github.io is sometimes unreachable from this machine for minutes; a `000` there is not a build failure — confirm via `git ls-remote` and retry.

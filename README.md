# Open-source SEO agent for link building

SEO Agent plans backlink campaigns and builds the links, working inside the AI assistant you already use: Claude, Cursor, Codex or any MCP client. It comes with a free list of 50 backlink sites, each with Domain Authority, referring domains and a step-by-step method, and connects to a library of 1,245 sites with a free API key.

```bash
pip install seo-agent
claude mcp add seo-agent -- seo-agent
```

Then ask your assistant:

> Find dofollow sites above DA 50 in the free list and build a link to https://example.com with the anchor "example".

## What it does

- **Plans**: picks sites by authority and effort, balances dofollow share, and assigns anchor text by the ratio you set (exact, partial, branded, naked, generic).
- **Builds**: for every site it hands the assistant a playbook for that kind of link, the guide's steps parsed into actions with the exact button names, and what the site requires. Sites that need no account are built automatically with a proof screenshot.
- **Verifies**: opens the live page and checks the hyperlink, the anchor text and whether it is nofollow before counting the link.
- **Logs**: every link, its proof and its status in one results table.

The library behind it: 1,245 backlink sites, 1,138 verified reachable, 900 dofollow, 117 with DA 90 or higher, with referring domains, backlinks, spam score and organic traffic for every domain. Methods covered: profile fields, articles and guest posts, social bookmarking, web 2.0 pages, forums, directories, shared documents, comments, Q&A and URL shorteners.

## Install in Claude, Cursor or Codex

Requires Python 3.10 or newer.

**Claude Code**

```bash
pip install seo-agent
claude mcp add seo-agent -- seo-agent
```

**Claude Desktop**: add to `claude_desktop_config.json`:

```json
{ "mcpServers": { "seo-agent": { "command": "seo-agent" } } }
```

**Cursor**: Settings, MCP, add a server with command `seo-agent`.

**Codex CLI**: add an `mcp_servers.seo-agent` entry with `command = "seo-agent"` to `~/.codex/config.toml`.

**With an API key** (full library, campaign planner, automatic building, verification and results):

```bash
export SEOAGENT_API_KEY=le_...
```

Everything else stays the same; the assistant simply sees the full set of tools.

## The free backlink sites list

Fifty sites from the library, all verified reachable, DA 37 to 69, 49 of them dofollow. Each has a method your assistant can follow.

| Site | DA | Referring domains | Method | Needs |
|---|---|---|---|---|
| GitBook | 69 | 212,041 | Article or blog post | sign-up |
| MyMiniFactory | 68 | 71,374 | Profile website field | sign-up |
| PromoDJ | 68 | 24,384 | Profile website field | sign-up |
| GrowthHackers | 68 | 7,690 | Forum post | sign-up |
| Gust | 67 | 11,264 | Directory listing | sign-up |
| HUD (.gov) | 66 | 2,569 | Profile website field | email verification |
| Serato | 66 | 7,121 | Profile website field | sign-up |
| Portfoliobox | 66 | 12,479 | Page builder site | no account |
| Credly | 65 | 59,462 | Profile website field | email verification |
| GrabCad | 65 | 17,418 | Profile website field | email verification |
| LeetCode | 65 | 87,346 | Profile website field | email verification |
| Kiwibox | 65 | 9,959 | Article or blog post | sign-up |
| Vingle | 64 | 28,178 | Article or blog post | email verification |
| GameKyo | 64 | 4,959 | Bookmark / link submit | email verification |
| Wantedly | 64 | 29,585 | Bookmark / link submit | sign-up |
| RoundMe | 63 | 8,631 | Profile website field | sign-up |
| ItsMyURLs | 63 | 11,263 | Bookmark / link submit | email verification |
| Zenodo | 62 | 7,015 | Profile website field | email verification |
| LongIsland | 62 | 61,555 | Bookmark / link submit | sign-up |
| Carrd | 61 | 272,016 | Article or blog post | email verification |
| Lacartes | 61 | 7,671 | Bookmark / link submit | email verification |
| Page4 | 61 | 2,162 | Page builder site | sign-up |
| MyVidSter | 60 | 14,641 | Profile website field | sign-up |
| Revue | 60 | 10,106 | Profile website field | sign-up |
| Ouo Press | 60 | 4,724 | URL shortener | no account |
| Hugo | 60 | 3,139 | Forum post | email verification |
| Jssor | 60 | 26,392 | Other | email verification |
| Brownbook | 59 | 50,108 | Profile website field | no account |
| CodeSandbox | 59 | 17,524 | Profile website field | social login |
| Folkd | 59 | 43,937 | Profile website field | sign-up |
| WHMCS | 59 | 3,925 | Bookmark / link submit | email verification |
| Teletype | 59 | 71,176 | Page builder site | no account |
| AllMyFaves | 58 | 50,030 | Bookmark / link submit | sign-up |
| u.to Shortener | 58 | 36,168 | URL shortener | no account |
| BlogFree | 58 | 5,019 | Forum signature | sign-up |
| OnRPG | 58 | 6,380 | Profile website field | sign-up |
| RawPixel | 58 | 28,316 | Profile website field | sign-up |
| Turnkey Linux | 58 | 14,662 | Profile website field | email verification |
| HotFrog | 57 | 23,144 | Bookmark / link submit | email verification |
| Smallseotools Shortener | 57 | 16,522 | URL shortener | no account |
| Tiny.pl Shortener | 56 | 15,801 | URL shortener | no account |
| Start Me | 56 | 39,120 | Page builder site | sign-up |
| Catch Themes | 53 | 46,911 | Forum post | sign-up |
| Givology | 51 | 2,077 | Article or blog post | email verification |
| AbiLogic | 50 | 6,222 | Article or blog post | sign-up |
| Storeboard | 50 | 48,200 | Article or blog post | sign-up |
| Blade Journal | 48 | 4,175 | Article or blog post | sign-up |
| Zyro | 46 | 6,557 | Page builder site | sign-up |
| Yooco | 43 | 8,568 | Comment | sign-up |
| Cgm internet marketing | 37 | 4,120 | Directory listing | email verification |

More lists, with DA and referring domains: [social bookmarking sites](docs/social-bookmarking-sites.md), [profile creation sites](docs/profile-creation-sites.md), [guest posting sites](docs/guest-posting-sites.md), [web 2.0 sites](docs/web-2-0-sites.md), [directory submission sites](docs/directory-submission-sites.md), [forum posting sites](docs/forum-posting-sites.md), [high DA backlinks](docs/high-da-backlinks.md).

## How the agent builds a link

For each site the server gives the assistant everything a careful human would want before starting:

1. A **playbook** for the method: where the link goes on a profile site versus an article site versus a forum, the pitfalls, and how to verify.
2. The guide's **steps as actions**: navigate, click, fill the form, place the link, verify email, upload, wait for moderation, verify, with the exact button and field names and the step marked as the placement.
3. **Requirements**: an account, a readable inbox, a captcha, a social login, a file, or written content.
4. **Rules**: exact URL and anchor, no duplicates, stop at captchas, verify on the public page, report the live URL.

Example, a real link built on a login-free site:

```
Site      rentry.co
Anchor    Let me Review it For You
Live URL  https://rentry.co/tu4euyew
Verified  hyperlink found, anchor matches, no nofollow attribute
```

## SEO automation from the command line

The hosted engine also ships a CLI for the same operations: search the library, plan a campaign, build a link, list results. See the [tool reference](docs/seo-mcp-server.md).

## Guides

- [How to get backlinks with an AI agent](docs/how-to-get-backlinks-with-ai.md)
- [Claude SEO: link building from Claude Code and Claude Desktop](docs/claude-seo.md)
- [Cursor SEO: link building from Cursor](docs/cursor-seo.md)
- [LLM SEO and SEO automation](docs/llm-seo.md)
- [The SEO MCP server: tool reference](docs/seo-mcp-server.md)

## Upgrade

The free list is the same engine with 50 sites. A free API key unlocks the full library of 1,245 sites, the campaign planner, automatic building for login-free sites, link verification and the results log. Get a key at the address in the docs once the hosted service opens; until then, star the repo and watch releases.

## License

MIT. The site library and its metrics are provided as-is; verify a site before relying on it.

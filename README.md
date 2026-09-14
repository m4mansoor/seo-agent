<!-- Social preview: docs/assets/img/og-seo-agent.png (1280x640). Set it in Settings, General, Social preview; the GitHub API cannot set it. -->
<p align="center"><img src="https://raw.githubusercontent.com/m4mansoor/seo-agent/main/docs/assets/img/banner.png" alt="SEO Agent: an open-source SEO agent that builds your backlinks" width="100%"></p>

# SEO Agent

*Open-source AI SEO Agent and MCP server for Claude Code, Cursor and Codex.*

[![MIT licence](https://img.shields.io/github/license/m4mansoor/seo-agent)](https://github.com/m4mansoor/seo-agent/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/m4mansoor/seo-agent?style=flat)](https://github.com/m4mansoor/seo-agent/stargazers)
[![MCP server](https://img.shields.io/badge/MCP-server-0F6E6A)](https://m4mansoor.github.io/seo-agent/seo-mcp-server.html)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-1C2229)](https://m4mansoor.github.io/seo-agent/)

SEO Agent is an open-source SEO agent for link building. It runs as an MCP server inside Claude Code, Cursor, Codex or any MCP client: you say what you need, it asks for your URL and keywords, plans the campaign, builds each link by following that site's method, checks that the link went live, and hands you the live URLs with proof.

**What it does**

- **Searches a library of 1,245 backlink sites** with Domain Authority, referring domains, spam score and dofollow status. Fifty sites ship free inside the package (`search_sites`).
- **Gives your assistant the method for each site**: the playbook for that kind of link, the guide steps parsed into actions with the exact button names, and what the site requires (`get_method`).
- **Plans a campaign** for your URL: sites inside your DA range, the dofollow share you asked for, methods spread, anchor text assigned by ratio (`plan_campaign`, Lifetime).
- **Builds links in your browser** with a proof screenshot on login-free sites, free; on account-based sites with the model-driven executor on Lifetime (`build_link`, `queue_build`).
- **Verifies every link** by fetching the live page and checking the hyperlink, the anchor text and nofollow (`verify_link`).
- **Handles gates in the chat**: at a captcha, email code or login it asks you, or on Lifetime uses a service you connected once (`resolve_gate`, `connect_service`, `read_inbox`).

**Quick start**

```bash
pip install seo-agent && playwright install chromium
claude mcp add seo-agent -- seo-agent
```

Any other MCP client, in its `mcpServers` config:

```json
{ "mcpServers": { "seo-agent": { "command": "seo-agent" } } }
```

Then ask: *Build a link to my site on a dofollow site from the free list, and verify it.*

Documentation: https://m4mansoor.github.io/seo-agent/ · Repository: https://github.com/m4mansoor/seo-agent

## A session, start to finish

<p align="center"><img src="https://raw.githubusercontent.com/m4mansoor/seo-agent/main/docs/assets/img/session.png" alt="A session: the user asks for 5 dofollow backlinks DA 40 to 70, the agent asks for URL and keywords, plans, builds and verifies" width="100%"></p>

That is the whole interaction. In detail:

1. **You ask in plain language**: *I need 5 dofollow backlinks, DA 40 to 70.*
2. **The agent asks for two things**: the URL the links should point to, and your main keywords. It stores your sign-up identity once so every form is filled the same way.
3. **It plans**: picks sites from the library by authority and effort inside your DA range, keeps the dofollow share you asked for, spreads the methods so it is not five profile pages, and assigns anchor text by ratio: exact, partial, branded, naked, generic.
4. **It builds**: login-free sites are built by scripted playbooks with a proof screenshot. Sites that need an account are built by the model-driven browser executor: it reads the site's playbook, the guide steps with the exact button names, and a snapshot of the page each turn, then signs up, fills the profile or writes the post, and places the link. Long builds run in the background so your chat never times out.
5. **It verifies**: opens the public page and checks that the target is a real hyperlink, that the anchor matches, and whether the link is nofollow. Plain-text URLs and noindex pages do not count.
6. **It reports**: live URL, anchor, dofollow status and proof per link, a campaign report, and a re-check later so you know which links still stand. When a site asks for a captcha, a verification code or a login, the agent asks you in the same chat and continues once it is cleared.

*The session above is illustrative. The table below is real.*

## Real links it built

Built for lmrify.com during development, on login-free sites, then verified by fetching each page:

| Site | DA | Live link | Verified |
|---|---|---|---|
| Netcraft site report | 77 | https://sitereport.netcraft.com/?url=https://lmrify.com | hyperlink present, nofollow |
| rentry.co | — | https://rentry.co/tu4euyew | contextual anchor "Let me Review it For You", dofollow attribute, page is noindex |
| write.as | 52 | https://write.as/uooky17nv701i.md | contextual anchor, indexed page, nofollow |
| n9.cl | 40 | https://n9.cl/aav9b | redirects to target |
| goolnk.com | 23 | https://goolnk.com/bwv0gn | redirects to target |
| yellkey.com | 20 | https://www.yellkey.com/forget | redirects to target |

Notice what the verifier caught: one dofollow link sits on a noindex page and one indexed contextual link is nofollow. The agent reports both, because a link you cannot trust is worse than no link.

## How it works

<p align="center"><img src="https://raw.githubusercontent.com/m4mansoor/seo-agent/main/docs/assets/img/flow.png" alt="Plan, build, verify, report" width="100%"></p>

## What is in the library

| | |
|---|---|
| Sites | 1,245, of which 1,138 verified reachable this month |
| Dofollow | 900 |
| DA 90 or higher | 117 |
| Metrics per site | Domain Authority, referring domains, total backlinks, spam score, organic traffic |
| Methods | profile fields, articles and guest posts, social bookmarking, web 2.0 pages, forums and signatures, directories, shared documents, comments, Q&A, URL shorteners |
| Per site | the step-by-step method parsed into actions, the placement step, and what the site requires: account, inbox, captcha, social login, upload, moderation |

Fifty of these sites, with their methods, are bundled free. The rest, the campaign planner, automatic building and verification come with a free API key when the hosted service opens.

## Free: 50 backlinks from GitHub, right now

The package is the agent. It runs on your machine, builds links in your own browser on the login-free sites, follows the method with you on the rest, verifies every link and keeps the log. No account, no key, nothing sent anywhere. Requires Python 3.10 or newer.

**Claude Code**

```bash
pip install seo-agent && playwright install chromium
claude mcp add seo-agent -- seo-agent
```

**Claude Desktop, Cursor, Codex** and any other MCP client take the same command in their config:

```json
{ "mcpServers": { "seo-agent": { "command": "seo-agent" } } }
```

Then ask: *I need 5 dofollow backlinks from the free list for https://example.com, keyword "example".* The assistant searches the 50 sites, calls `build_link` where it can build by itself, follows `get_method` where an account is needed, verifies each link and logs it. Ask *how many links have I built* any time; it calls `account`.

## Lifetime: $97 once, every site, forever

When you want more than the 50 free sites, the assistant gives you the payment link when you ask, or call `upgrade`. Pay once at **https://mcp.seoagent.dev/buy**, copy the key from the success page, and tell your assistant:

```
activate le_your_key
```

No restart, no config file. From that message on, the same MCP has the full 1,245-site library, the campaign planner, browser building on account-based sites, gates with connected services, background jobs, identity generation, monitoring, campaign reports and a dashboard. Unlimited links, no subscription.

**No pip? Use the link instead.** The success page also shows a personal MCP link, `https://mcp.seoagent.dev/u/le_…/mcp`. Paste it into Claude Desktop or claude.ai (Settings, Connectors, Add custom connector, no OAuth), ChatGPT (Settings, Connectors, Developer mode) or Cursor (`"url"` instead of `"command"`). It carries your key, so keep it private.

## The free backlink sites list

Fifty sites from the library, all verified reachable, DA 37 to 69, 49 of them dofollow. Each has a method your assistant can follow.

<details>
<summary>Show all 50</summary>

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


</details>

More lists, with DA and referring domains: [social bookmarking sites](https://m4mansoor.github.io/seo-agent/social-bookmarking-sites.html), [profile creation sites](https://m4mansoor.github.io/seo-agent/profile-creation-sites.html), [guest posting sites](https://m4mansoor.github.io/seo-agent/guest-posting-sites.html), [web 2.0 sites](https://m4mansoor.github.io/seo-agent/web-2-0-sites.html), [directory submission sites](https://m4mansoor.github.io/seo-agent/directory-submission-sites.html), [forum posting sites](https://m4mansoor.github.io/seo-agent/forum-posting-sites.html), [high DA backlinks](https://m4mansoor.github.io/seo-agent/high-da-backlinks.html).

## Why SEO Agent and not another SEO MCP server

- **It builds, not only reports.** Most SEO MCP servers wrap a metrics API. This one follows a site's method in a browser, places the link and proves it with a screenshot and a live-page check.
- **The library is the moat.** 1,245 sites, each with its parsed step-by-step method, verified reachable monthly, with DataForSEO metrics. Fifty are free with no key.
- **It is honest about limits.** A captcha or a login is a gate it asks you about, never something it fakes its way past. Links that are plain text, nofollow or on a noindex page are reported as such.

## Gates are handled in the chat, not skipped

A captcha, an email verification, a phone code, a social login or a payment step is a gate. The agent stops at the gate, tells you what the site wants, and offers the ways through, in the same conversation:

- **Clear it yourself**: it opens the page in a visible browser window and waits while you solve the captcha or log in.
- **Connect a service once**: a captcha solver, your inbox over IMAP, or an SMS number. From then on the agent reads the verification link or code itself and continues without asking.
- **Paste the code**: you read the email or SMS and paste the code into the chat.
- **Skip the site**: it moves to the next site in the plan.

It never fakes a person or works around a site's rules, which keeps your site out of trouble and the links worth having.

## Everything Lifetime adds

$97 once. Activate in the chat; nothing else changes.

| Feature | What you get |
|---|---|
| Model-driven executor | Builds on account-based sites: sign-up, profile fields, articles, forum posts, directory listings, page builders |
| Gates and services | Captcha solver, IMAP inbox and SMS connected once; verification links and codes read automatically |
| Background jobs | `queue_build` starts a build and `job_status` polls it, so clients with short tool timeouts never drop a link |
| Identity generation | `generate_identity` creates a complete, consistent sign-up identity on your catch-all domain |
| Monitoring | `recheck_links` re-fetches every placed link and marks the ones that dropped |
| Campaign reports | `campaign_report` gives planned versus placed, counts by status and method, and every live URL; CSV export |
| Dashboard | A web page per API key with credits, campaigns, results and proof screenshots |
| Per-key credits | Each key has its own balance; only verified live links are charged |

## Configuration

Nothing is required. `activate` stores your key in `~/.seoagent/config.json`; results live in `~/.seoagent/results.db`. Two optional variables override that:

| Variable | Purpose |
|---|---|
| `SEOAGENT_API_KEY` | A Lifetime key, for environments where a config file is inconvenient (CI, containers). |
| `SEOAGENT_URL` | The hosted endpoint, or a personal link `https://mcp.seoagent.dev/u/le_…/mcp`. Only needed for a self-hosted engine. |

## Guides

- [How to get backlinks with an AI agent](https://m4mansoor.github.io/seo-agent/how-to-get-backlinks-with-ai.html)
- [Claude SEO: link building from Claude Code and Claude Desktop](https://m4mansoor.github.io/seo-agent/claude-seo.html)
- [Cursor SEO: link building from Cursor](https://m4mansoor.github.io/seo-agent/cursor-seo.html)
- [LLM SEO and SEO automation](https://m4mansoor.github.io/seo-agent/llm-seo.html)
- [The SEO MCP server: tool reference](https://m4mansoor.github.io/seo-agent/seo-mcp-server.html)

Documentation site: https://m4mansoor.github.io/seo-agent/

## Licence and author

MIT. Built by Engr. Inaamul Haq Mansoor ([@m4mansoor](https://github.com/m4mansoor)).

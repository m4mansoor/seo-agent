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

- **Searches a library of 1,245 backlink sites** with Domain Authority, referring domains, spam score and dofollow status. Twenty-five ship free inside the package, two of them at DA 90+; the rest show up locked, by name and DA, and unlock with a subscription (`search_sites`).
- **Gives your assistant the method for each site**: the playbook for that kind of link, the guide steps parsed into actions with the exact button names, and what the site requires (`get_method`).
- **Plans a campaign** for your URL: sites inside your DA range, the dofollow share you asked for, methods spread, anchor text assigned by ratio (`plan_campaign`, subscription).
- **Builds links in your browser** with a proof screenshot on login-free sites, free; on account-based sites with the model-driven executor on a subscription (`build_link`, `queue_build`).
- **Verifies every link** by fetching the live page and checking the hyperlink, the anchor text and nofollow (`verify_link`).
- **Handles gates in the chat**: at a captcha, email code or login it asks you, or with a subscription uses a service you connected once (`resolve_gate`, `connect_service`, `read_inbox`).
- **Suggests the keywords and anchors** by reading the target page itself, then allocates them across the five anchor types so your profile is not one phrase forty times (`suggest_keywords`, subscription).
- **Watches the links afterwards**: weekly re-checks of everything it placed, plus every referring domain to your site, what is new and lost each month, spam flags and a disavow file (`recheck_links`, `monitor_backlinks`, subscription).
- **Finds what competitors have and you do not**, with the method to build each one attached (`competitor_gap`, subscription).
- **Paces the campaign** so links arrive steadily across days and methods rather than in a burst, and runs many sites under one subscription (`register_site`, subscription).

Twenty-six tools in all; the [tool reference](https://m4mansoor.github.io/seo-agent/seo-mcp-server.html) lists every one.

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

<p align="center"><img src="https://raw.githubusercontent.com/m4mansoor/seo-agent/main/docs/assets/img/session.png" alt="A session: the user asks for 5 dofollow backlinks at DA 60 or higher, the agent asks for URL and keywords, plans from the free list, builds on Medium, IMDB, Zotero, ArtFire and ouo.press, and verifies each" width="100%"></p>

That is the whole interaction, on the free list alone. In detail:

1. **You ask in plain language**: *I need 5 dofollow backlinks, DA 60 or higher.*
2. **The agent asks for two things**: the URL the links should point to, and your main keywords. It stores your sign-up identity once so every form is filled the same way.
3. **It plans**: picks sites by authority and effort inside your DA range, keeps the dofollow share you asked for, spreads the methods so it is not five profile pages, and assigns anchor text by ratio: exact, partial, branded, naked, generic. The free list reaches DA 96: Medium, IMDB, Zotero, ArtFire, Milkyway (.edu), all dofollow. When you ask for more at the top end, it shows what the full library holds and offers the subscription.
4. **It builds**: login-free sites are built by scripted playbooks with a proof screenshot. Sites that need an account, which is where the high DA lives, are built by the model-driven browser executor: it reads the site's playbook, the guide steps with the exact button names, and a snapshot of the page each turn, then signs up, fills the profile or writes the post, and places the link. In free mode it hands you the same method to follow in your own browser. Long builds run in the background so your chat never times out.
5. **It verifies**: opens the public page and checks that the target is a real hyperlink, that the anchor matches, and whether the link is nofollow. Plain-text URLs, redirect pages and noindex pages do not count as verified.
6. **It reports**: live URL, anchor, dofollow or nofollow and proof per link, a campaign report, and a re-check later so you know which links still stand. When a site asks for a captcha, a verification code or a login, the agent asks you in the same chat and continues once it is cleared.

*The session above is illustrative.*

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

Twenty-five of these sites, with their methods, are bundled free. The rest, the campaign planner, automatic building and verification come with a free API key when the hosted service opens.

## Free: 25 sites from GitHub, right now

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

Then ask: *I need 5 dofollow backlinks from the free list for https://example.com, keyword "example".* The assistant searches the 25 sites, calls `build_link` where it can build by itself, follows `get_method` where an account is needed, verifies each link and logs it. Ask *how many links have I built* any time; it calls `account`.

## Subscribe: every site, $97 a year or $27 a month

When you ask for more high-DA sites than the free list holds, the assistant shows what is locked and gives you the payment links; or call `upgrade`. Subscribe at **https://mcp.seoagent.dev/buy?plan=yearly** ($97 a year, about $8 a month) or **https://mcp.seoagent.dev/buy?plan=monthly** ($27 a month, cancel any time), copy the key from the success page, and tell your assistant:

```
activate le_your_key
```

No restart, no config file. From that message on, the same MCP has the full 1,245-site library, the campaign planner, browser building on account-based sites, gates with connected services, background jobs, identity generation, monitoring, campaign reports and a dashboard. Fair use is 500 placed links per key in any 30 days.

**No pip? Use the link instead.** The success page also shows a personal MCP link, `https://mcp.seoagent.dev/u/le_…/mcp`. Paste it into Claude Desktop or claude.ai (Settings, Connectors, Add custom connector, no OAuth), ChatGPT (Settings, Connectors, Developer mode) or Cursor (`"url"` instead of `"command"`). It carries your key, so keep it private.

## What it replaces

Fifty verified, dofollow-checked backlinks a month is a job. Typical ways to get it done, at typical market rates:

| | Cost | Time to 50 links | Knows the sites? |
|---|---|---|---|
| **In-house link builder** | $2,500 to $4,000 a month salary, plus tools | 3 to 6 weeks, at 30 to 60 minutes per link | Only the sites they have used before; a new hire starts from a blank list |
| **Agency or marketplace** | $150 to $400 per DA 40+ dofollow link, so $7,500 to $20,000 per 50 | 4 to 8 weeks | Their list, not yours; you never see the method |
| **Freelancer on a gig site** | $10 to $50 per link | 1 to 2 weeks | Usually the same 100 sites everyone else spams |
| **SEO Agent** | $97 a year or $27 a month | An afternoon; login-free sites build in seconds each | 1,245 sites with the exact method for each, verified reachable monthly, with DataForSEO metrics |

The library is the part a team cannot copy quickly. Every site in it came from years of link building: which DA 60 profile page still gives a dofollow link, which forum strips links from new members, which shortener sits behind a captcha, which directory approves in a day. Each entry carries the step-by-step method with the exact button names, what the site requires, and referring domains, spam score and traffic from DataForSEO. A person could rebuild that list, but it would take them the same years.

The agent does not replace judgement: you still choose the keywords, the anchor ratio and which links are worth having. It replaces the hours, and it remembers the sites.

## The free backlink sites list

Twenty-five sites from the library, all verified reachable, DA 20 to 96, 25 of them dofollow, two of them at DA 90 or higher. Each has a method your assistant can follow.

<details>
<summary>Show all 25</summary>

| Site | DA | Referring domains | Link | Method | Needs |
|---|---|---|---|---|---|
| Medium | 96 | 1,371,100 | dofollow | Article or blog post | sign-up |
| IMDB | 95 | 891,904 | dofollow | Profile website field | no account |
| Zotero | 75 | 51,364 | dofollow | Bookmark / link submit | sign-up |
| ArtFire | 75 | 31,486 | dofollow | Profile website field | sign-up |
| Milkyway (.edu) | 75 | 9,011 | dofollow | Profile website field | sign-up |
| DsiBlogger | 74 | 37,269 | dofollow | Article or blog post | sign-up |
| FireBlogz | 74 | 39,401 | dofollow | Article or blog post | sign-up |
| Beatstars | 73 | 39,465 | dofollow | Page builder site | sign-up |
| Flip HTML5 | 73 | 226,903 | dofollow | Shared document | sign-up |
| Figma | 71 | 101,339 | dofollow | Social post | sign-up |
| MD Anderson | 71 | 918 | dofollow | Other | no account |
| Wakelet | 71 | 191,490 | dofollow | Bookmark / link submit | sign-up |
| GrowthHackers | 68 | 7,690 | dofollow | Forum post | sign-up |
| Gust | 67 | 11,264 | dofollow | Directory listing | sign-up |
| RiseUp | 64 | 11,528 | dofollow | Page builder site | sign-up |
| Wantedly | 64 | 29,585 | dofollow | Bookmark / link submit | sign-up |
| XtGem | 64 | 26,727 | dofollow | Page builder site | sign-up |
| Ouo Press | 60 | 4,724 | dofollow | URL shortener | no account |
| BlogFree | 58 | 5,019 | dofollow | Forum signature | sign-up |
| Pub HTML5 | 56 | 99,088 | dofollow | Shared document | sign-up |
| AxMag | 54 | 1,668 | dofollow | Shared document | sign-up |
| Yooco | 43 | 8,568 | dofollow | Comment | sign-up |
| N9.cl Shortener | 40 | 17,321 | dofollow | URL shortener | no account |
| Goolnk.com Shortener | 23 | 1,922 | dofollow | URL shortener | no account |
| YellKey Shortener | 20 | 389 | dofollow | URL shortener | no account |


</details>

More lists, with DA and referring domains: [social bookmarking sites](https://m4mansoor.github.io/seo-agent/social-bookmarking-sites.html), [profile creation sites](https://m4mansoor.github.io/seo-agent/profile-creation-sites.html), [guest posting sites](https://m4mansoor.github.io/seo-agent/guest-posting-sites.html), [web 2.0 sites](https://m4mansoor.github.io/seo-agent/web-2-0-sites.html), [directory submission sites](https://m4mansoor.github.io/seo-agent/directory-submission-sites.html), [forum posting sites](https://m4mansoor.github.io/seo-agent/forum-posting-sites.html), [high DA backlinks](https://m4mansoor.github.io/seo-agent/high-da-backlinks.html).

## Why SEO Agent and not another SEO MCP server

- **It builds, not only reports.** Most SEO MCP servers wrap a metrics API. This one follows a site's method in a browser, places the link and proves it with a screenshot and a live-page check.
- **The library is the moat.** 1,245 sites, each with its parsed step-by-step method, verified reachable monthly, with DataForSEO metrics. Twenty-five are free with no key, two of them at DA 90 or higher; the rest appear locked by name and DA.
- **It is honest about limits.** A captcha or a login is a gate it asks you about, never something it fakes its way past. Links that are plain text, nofollow or on a noindex page are reported as such.

## Gates are handled in the chat, not skipped

A captcha, an email verification, a phone code, a social login or a payment step is a gate. The agent stops at the gate, tells you what the site wants, and offers the ways through, in the same conversation:

- **Clear it yourself**: it opens the page in a visible browser window and waits while you solve the captcha or log in.
- **Connect a service once**: a captcha solver, your inbox over IMAP, or an SMS number. From then on the agent reads the verification link or code itself and continues without asking.
- **Paste the code**: you read the email or SMS and paste the code into the chat.
- **Skip the site**: it moves to the next site in the plan.

It never fakes a person or works around a site's rules, which keeps your site out of trouble and the links worth having.

## Everything a subscription adds

Activate in the chat; nothing else changes.

| Feature | What you get |
|---|---|
| Model-driven executor | Builds on account-based sites: sign-up, profile fields, articles, forum posts, directory listings, page builders |
| Your own AI model | Connect an Anthropic, OpenAI, Google or OpenRouter key once; it drives the browser on account-based sites, so model cost is yours and under your control |
| Gates and services | Captcha solver, IMAP inbox and SMS connected once; verification links and codes read automatically |
| Background jobs | `queue_build` starts a build and `job_status` polls it, so clients with short tool timeouts never drop a link |
| Identity generation | `generate_identity` creates a complete, consistent sign-up identity on your catch-all domain |
| Monitoring | `recheck_links` re-fetches every placed link and marks the ones that dropped |
| Campaign reports | `campaign_report` gives planned versus placed, counts by status and method, and every live URL; CSV export |
| Dashboard | A web page per API key with credits, campaigns, results and proof screenshots |
| Competitor gap | The referring domains your competitors have and you do not, each row carrying the method to build it |
| Keyword and anchor suggestions | Read a target page and get keywords and a full anchor plan across the five types |
| Link velocity pacing | Links spread across days and methods, never fired in a burst |
| Multi-site | Register many sites under one subscription, each with its own caps and reports |
| Fair use | 500 placed links per key in any 30 days; only verified live links count |

## Configuration

Nothing is required. `activate` stores your key in `~/.seoagent/config.json`; results live in `~/.seoagent/results.db`. Two optional variables override that:

| Variable | Purpose |
|---|---|
| `SEOAGENT_API_KEY` | A subscription key, for environments where a config file is inconvenient (CI, containers). |
| `SEOAGENT_URL` | The hosted endpoint, or a personal link `https://mcp.seoagent.dev/u/le_…/mcp`. Only needed for a self-hosted engine. |

## Where it runs

One engine, one library, one subscription. Four ways in, at four different stages.

| Door | Status | What it is |
|---|---|---|
| **Any AI assistant** | Live | Claude Code, Claude Desktop, claude.ai, Cursor, Codex, ChatGPT, Windsurf. `pip install seo-agent`, 25 sites free, links built in your own browser. |
| **[WordPress plugin](https://m4mansoor.github.io/seo-agent/wordpress-backlink-plugin.html)** | In development | Posts, pages and WooCommerce products as targets. Campaigns, gates, weekly monitoring and white-label reports inside wp-admin. |
| **[Shopify app](https://m4mansoor.github.io/seo-agent/shopify-seo-app.html)** | In development | Products and collections as targets, embedded in the Shopify admin, billed through Shopify. |
| **[Windows and macOS app](https://m4mansoor.github.io/seo-agent/seo-desktop-app.html)** | In development | The only door that uses accounts you are already signed in to. Its own browser, your own model key, nothing uploaded. |

The [roadmap](https://m4mansoor.github.io/seo-agent/roadmap.html) says plainly what is live, what is being built, and what will never be built.

## Guides

- [How to get backlinks with an AI agent](https://m4mansoor.github.io/seo-agent/how-to-get-backlinks-with-ai.html)
- [Link building software, and what most of it leaves out](https://m4mansoor.github.io/seo-agent/link-building-software.html)
- [Claude SEO: link building from Claude Code and Claude Desktop](https://m4mansoor.github.io/seo-agent/claude-seo.html)
- [Cursor SEO: link building from Cursor](https://m4mansoor.github.io/seo-agent/cursor-seo.html)
- [LLM SEO and SEO automation](https://m4mansoor.github.io/seo-agent/llm-seo.html)
- [The SEO MCP server: tool reference](https://m4mansoor.github.io/seo-agent/seo-mcp-server.html)
- [Roadmap and status](https://m4mansoor.github.io/seo-agent/roadmap.html)

Documentation site: https://m4mansoor.github.io/seo-agent/

## Licence and author

MIT. Built by Engr. Inaamul Haq Mansoor ([@m4mansoor](https://github.com/m4mansoor)).

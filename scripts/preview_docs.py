"""Render docs/ to plain HTML and serve it, without Ruby or Jekyll.

    python3 scripts/preview_docs.py [out_dir] [port]      # default /tmp/seo-agent-site, 8123

Handles the Liquid the layout actually uses (page.title/description, the landing/doc main class, the doc-page
title band) and converts .md pages with the `markdown` package. Copies assets at start: restart after CSS edits."""
import os, re, shutil, sys, http.server, socketserver, threading
DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/seo-agent-site"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8123
layout = open(f"{DOCS}/_layouts/default.html").read()

def front(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = {}
    if not m: return meta, text
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2)

def render(page_html, meta, url):
    out = layout
    is_home = url in ("/", "/index.html")
    title = "SEO Agent — Open-source AI SEO Agent (MCP) for Claude Code" if is_home else f"{meta.get('title','')} · SEO Agent"
    # the one conditional that carries a value: main's class. Resolve it before the generic strip.
    out = re.sub(r'class="\{% if page\.url[^%]*%\}landing\{% else %\}doc\{% endif %\}"',
                 f'class="{"landing" if is_home else "doc"}"', out)
    # the title band shows on every page but the homepage
    def unless(m): return "" if is_home else m.group(1)
    out = re.sub(r"\{% unless page\.url[^%]*%\}(.*?)\{% endunless %\}", unless, out, flags=re.S)
    out = re.sub(r"\{% if page\.description %\}(.*?)\{% endif %\}",
                 lambda m: m.group(1) if meta.get("description") else "", out, flags=re.S)
    out = out.replace("{{ page.title }}", meta.get("title", "")).replace("{{ page.description }}", meta.get("description", ""))
    # collapse the remaining liquid conditionals/assigns the layout uses into their values
    out = re.sub(r"\{%.*?%\}", "", out, flags=re.S)
    out = out.replace("{{ t }}", title).replace("{{ d }}", meta.get("description", ""))
    out = out.replace("{{ u }}", "http://localhost/" + url.lstrip("/"))
    out = out.replace("{{ site.baseurl }}", "").replace("{{ site.url }}", "http://localhost")
    out = out.replace("{{ site.description }}", "").replace("{{ site.time | date: '%Y%m%d%H%M%S' }}", "dev")
    out = out.replace('class="{% if page.url == \'/\' or page.url == \'/index.html\' %}landing{% else %}doc{% endif %}"', "")
    out = out.replace("{{ content }}", page_html)
    # the main class survives the tag strip as an empty class=""; restore it
    out = out.replace('<main class="">', f'<main class="{"landing" if is_home else "doc"}">')
    return out

if os.path.exists(OUT): shutil.rmtree(OUT)
shutil.copytree(f"{DOCS}/assets", f"{OUT}/assets")
for f in ("favicon.svg", "favicon.png", "apple-touch-icon.png"):
    if os.path.exists(f"{DOCS}/{f}"): shutil.copy(f"{DOCS}/{f}", f"{OUT}/{f}")
import markdown
for name in os.listdir(DOCS):
    if name.startswith("_"): continue
    if name.endswith(".html"):
        meta, body = front(open(f"{DOCS}/{name}").read())
        open(f"{OUT}/{name}", "w").write(render(body, meta, "/" + name))
    elif name.endswith(".md"):
        meta, body = front(open(f"{DOCS}/{name}").read())
        html = markdown.markdown(body, extensions=["tables", "fenced_code", "attr_list"])
        # pages link to each other with .html, as Jekyll serves them
        html = html.replace('.md"', '.html"')
        out_name = name[:-3] + ".html"
        open(f"{OUT}/{out_name}", "w").write(render(html, meta, "/" + out_name))
print("rendered ->", OUT)
os.chdir(OUT)
socketserver.TCPServer.allow_reuse_address = True   # a just-killed server leaves the port in TIME_WAIT
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
with socketserver.TCPServer(("127.0.0.1", PORT), Quiet) as httpd:
    print(f"serving http://localhost:{PORT}/ (ctrl-c to stop)", flush=True)
    httpd.serve_forever()

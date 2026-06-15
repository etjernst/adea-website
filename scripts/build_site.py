"""Render the ADEA static site: Markdown content + Jinja2 templates -> _site/.

Editors only ever touch the Markdown in content/. This script (and the GitHub
Actions workflow that runs it) turns that into the deployed HTML. Run locally with
`python scripts/build_site.py` to preview; output lands in _site/.
"""
import os
import re
import json
import shutil
import datetime
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
TEMPLATES = os.path.join(ROOT, "templates")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "_site")

SITE = {
    "name": "Australasian Development Economics Association",
    "short": "ADEA",
    "description": "A non-profit community of researchers advancing development "
                   "economics across the Australasian region.",
}
# Build year is passed in so the result is deterministic in CI.
YEAR = datetime.date.today().year

md = markdown.Markdown(extensions=["extra", "sane_lists"])
env = Environment(
    loader=FileSystemLoader(TEMPLATES),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def parse_frontmatter(path):
    """Return (meta_dict, markdown_body) for a file beginning with a --- block."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


def render_body(body):
    md.reset()
    return md.convert(body.strip()) if body.strip() else ""


def display_date(value):
    if not value:
        return ""
    if isinstance(value, datetime.date):
        d = value
    else:
        d = datetime.date.fromisoformat(str(value))
    return f"{d.day} {d.strftime('%B %Y')}"


def first_paragraph(body):
    for block in body.strip().split("\n\n"):
        block = block.strip()
        if block and not block.startswith(("#", "-", ">", "!")):
            return re.sub(r"\s+", " ", block)
    return ""


def load_news():
    """Load news posts, newest first, with url/date_display/excerpt and prev/next."""
    posts = []
    news_dir = os.path.join(CONTENT, "news")
    for fn in os.listdir(news_dir):
        if not fn.endswith(".md"):
            continue
        meta, body = parse_frontmatter(os.path.join(news_dir, fn))
        slug = os.path.splitext(fn)[0]
        meta["url"] = f"news/{slug}.html"
        meta["slug"] = slug
        meta["body"] = body
        meta["date_display"] = display_date(meta.get("date"))
        meta.setdefault("excerpt", first_paragraph(body))
        posts.append(meta)
    posts.sort(key=lambda p: str(p.get("date", "")), reverse=True)
    # wire prev (older) / next (newer) for in-article navigation
    for i, p in enumerate(posts):
        p["next"] = posts[i - 1] if i > 0 else None          # newer
        p["prev"] = posts[i + 1] if i < len(posts) - 1 else None  # older
    return posts


def write(out_relpath, html):
    dst = os.path.join(OUT, out_relpath)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  wrote {out_relpath}")


def rel_for(out_relpath):
    """Path back to site root from a given output file (for asset/links)."""
    depth = out_relpath.count("/")
    return "../" * depth


def load_members():
    path = os.path.join(ROOT, "data", "members.json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return {"leadership": [], "members": [], "topics": [], "countries": []}


def render_page(meta, body, out_relpath, news=None, members_data=None):
    template = env.get_template(meta["template"] + ".html")
    html = template.render(
        site=SITE, page=meta, body=render_body(body),
        news=news or [], members_data=members_data or {}, year=YEAR,
        rel=rel_for(out_relpath),
    )
    write(out_relpath, html)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    news = load_news()
    members_data = load_members()

    # top-level pages
    for fn, out in [("home.md", "index.html"), ("about.md", "about.html"),
                    ("news.md", "news.html"), ("members.md", "members.html")]:
        meta, body = parse_frontmatter(os.path.join(CONTENT, fn))
        render_page(meta, body, out, news=news, members_data=members_data)

    # news posts
    for p in news:
        render_page(p, p["body"], p["url"], news=news)

    # static assets
    shutil.copytree(ASSETS, os.path.join(OUT, "assets"), dirs_exist_ok=True)
    print(f"\nBuilt site -> {OUT}  ({len(news)} news posts)")


if __name__ == "__main__":
    main()

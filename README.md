# ADEA website

A static rebuild of the Australasian Development Economics Association site
(currently on Squarespace), hosted on GitHub Pages.
Content is authored in Markdown; a small Python build renders it to static HTML.

## Editing content (no tools needed)

Edit the Markdown files in [`content/`](content/) directly in GitHub's web editor:

- `content/home.md`, `content/about.md`, `content/members.md`: page text and settings
- `content/news.md`: the news index and the featured event
- `content/news/*.md`: individual news posts (one file per post)

Commit the change and GitHub Actions rebuilds and redeploys the site automatically.

## Members directory

Member data lives in [`data/members.json`](data/members.json). To add or edit a
member by hand, edit that file (each entry has `name`, `institution`, `topics`,
`countries`, `link`, `photo`). The directory and its topic/country filters update
from this file on the next build.

`data/members_enrichment.json` holds researched topics for members whose original
entry listed none, with a source URL per entry; these are pending member confirmation.

## Building locally (optional)

```bash
pip install jinja2 markdown pyyaml pillow beautifulsoup4
python scripts/build_site.py      # renders content/ + templates/ -> _site/
```

Open `_site/index.html` in a browser. Maintainer-only regeneration of member data
from the scraped source uses `python scripts/build_members.py`.

## Layout

| Path | What it is |
|------|------------|
| `content/` | Markdown content (the part editors touch) |
| `templates/` | Jinja2 HTML templates and the design system |
| `assets/` | CSS, JS, images (member headshots in `assets/images/members/`) |
| `data/` | `members.json` and enrichment |
| `scripts/` | `build_site.py` (render), `build_members.py` (member data) |
| `.github/workflows/deploy.yml` | builds and deploys to GitHub Pages on push |

## Status

Demo / work in progress. Membership login and dues will run through Stripe at launch;
the "Join" button and newsletter form are placeholders for now.

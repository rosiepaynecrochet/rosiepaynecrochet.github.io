#!/usr/bin/env python3
"""Build the Rosie Payne crochet reference site.

Every page shares one head, one nav, one footer and one stylesheet, so a
design change happens in exactly one place. To add a page: drop a content
fragment in pages/ and add an entry to PAGES.

Output goes to out/, which mirrors what is deployed:

    out/index.html            ->  rosiepaynecrochet.com/
    out/hook-sizes/index.html ->  rosiepaynecrochet.com/hook-sizes/
    out/style.css, cover.jpg, cover2.jpg, CNAME
"""

import pathlib
import re
import shutil
from html import escape as html_escape

ROOT = pathlib.Path(__file__).parent
PAGEDIR = ROOT / "pages"
OUT = ROOT / "out"

SITE = "https://rosiepaynecrochet.com"
AUTHOR = "Rosie Payne"
# The masthead carries no label line above the h1: the wordmark already sits
# in the nav directly above it, and a second "Rosie Payne" there was repetition
# dressed up as design.
PINTEREST_VERIFY = "af0567b0329eaeff9bea56c7104d49d6"
UPDATED = "October 2026"
PUBLISHED = "2026-10-21"

AMZ = "tag=rosiepayne0a-20&utm_source=pinterest&utm_medium=social&utm_campaign=crochet_hacks"

# --------------------------------------------------------------------------
# Pages. `slug` of "" is the home page.
# --------------------------------------------------------------------------

PAGES = [
    {
        "slug": "",
        "file": "sizing.html",
        "nav": "Sizing chart",
        "title": "Small Project Sizing Chart",
        "h1": "Small Project Sizing Chart",
        "standfirst": "Finished measurements for the projects people make most — and the "
                      "gauge math that turns each one into your own stitch and row count.",
        "desc": "Finished measurements for the crochet projects people make most, plus the "
                "gauge math that turns each one into your own stitch and row count.",
        "card": "Finished sizes for hats, blankets, dishcloths and more, with the gauge math behind them.",
        "book": "full",
    },
    {
        "slug": "hook-sizes",
        "file": "hook-sizes.html",
        "nav": "Hook sizes",
        "title": "Crochet Hook Size Conversion Chart",
        "h1": "Hook Size Conversion Chart",
        "standfirst": "US letters, UK numbers and millimetres side by side — and why the "
                      "millimetre is the only one of the three you can actually trust.",
        "desc": "Crochet hook size conversion chart: US letter sizes, UK numbers and metric "
                "millimetres side by side, with the yarn weight each hook normally pairs with.",
        "card": "US letters, UK numbers and millimetres, plus the yarn weight each hook suits.",
        "book": "compact",
    },
    {
        "slug": "crochet-terms",
        "file": "crochet-terms.html",
        "nav": "US vs UK terms",
        "title": "US vs UK Crochet Terms",
        "h1": "US vs UK Crochet Terms",
        "standfirst": "The same abbreviation means two different stitches depending on which "
                      "side of the Atlantic the pattern was written. Here is how to tell, and how to translate.",
        "desc": "US and UK crochet terms translated side by side, plus how to work out which "
                "system a pattern is written in before you start.",
        "card": "Translate any pattern, and spot which system it uses before you start.",
        "book": "compact",
    },
    {
        "slug": "yarn-weights",
        "file": "yarn-weights.html",
        "nav": "Yarn weights",
        "title": "Yarn Weight Chart and Substitution Guide",
        "h1": "Yarn Weights &amp; Substitutions",
        "standfirst": "Weights 0 to 7 with the hook and gauge each one expects — and the part "
                      "most charts leave out: what to do when you cannot get the yarn the pattern names.",
        "desc": "Yarn weight chart covering lace through jumbo with hook sizes and gauge, plus "
                "a practical guide to substituting one yarn for another without ruining the project.",
        "card": "Weights 0–7 with hooks and gauge, plus how to substitute without ruining the fit.",
        "book": "compact",
    },
    {
        "slug": "calculators",
        "file": "calculators.html",
        "nav": "Calculators",
        "title": "Crochet Gauge and Yarn Calculators",
        "h1": "Crochet Calculators",
        "standfirst": "Two tools that do the arithmetic you would otherwise do wrong at "
                      "eleven at night: your stitch and row counts, and how much yarn the project will actually eat.",
        "desc": "Free crochet calculators: turn your gauge into exact stitch and row counts, "
                "and work out how much yarn a project needs by weighing your swatch.",
        "card": "Turn your gauge into exact counts, and work out the yarn a project really needs.",
        "book": "compact",
    },
    {
        "slug": "about",
        "file": "about.html",
        "nav": "About",
        "title": "About These Charts",
        "h1": "About These Charts",
        "standfirst": "What this site is, where the numbers come from, and how to check them "
                      "against your own work.",
        "desc": "About the Rosie Payne crochet reference charts — what they cover, where the "
                "numbers come from, and how they are checked.",
        "card": "What this site is and where the numbers come from.",
        "book": "compact",
        "no_related": True,
    },
]

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

FAVICON = (
    '<link rel="icon" href="data:image/svg+xml,'
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='6' fill='%23b2502c'/%3E"
    "%3Ccircle cx='16' cy='16' r='7' fill='none' stroke='%23faf6f0' stroke-width='2'/%3E"
    "%3Cpath d='M16 9v14' stroke='%23faf6f0' stroke-width='2' stroke-linecap='round'/%3E"
    '%3C/svg%3E">'
)

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=Fraunces:opsz,wght,SOFT,WONK@9..144,300..700,0..100,0..1"
    "&family=Instrument+Sans:wght@400..600&display=swap\">"
)

BOOKCARD = f"""  <section class="bookcard">
    <img src="/cover.jpg" width="520" height="780" alt="Cover of Crazy Crochet Hacks Every Beginner Wishes They Knew by Rosie Payne" loading="lazy">
    <div class="bookcard-copy">
      <h2>Where the rest of it lives</h2>
      <p>These charts cover the numbers. The book covers what goes wrong between casting on and finishing — 100+ fixes, including the full gauge and yardage tables these pages were pulled from.</p>
      <div class="bookcard-links">
        <a href="https://www.amazon.com/Crazy-Crochet-Hacks-Beginner-Wishes-ebook/dp/B0H87TYJW7?{AMZ}&amp;utm_content=secondary" target="_blank" rel="noopener">Kindle on Amazon</a>
        <a href="https://www.amazon.com/Crazy-Crochet-Hacks-Beginner-Wishes/dp/B0H89DZP89?{AMZ}&amp;utm_content=secondary" target="_blank" rel="noopener">Paperback on Amazon</a>
      </div>
      <p class="series">Book 1 of the <strong>Crazy Crochet Hacks</strong> series.</p>
    </div>
  </section>"""

FOOTER = f"""  <footer>
    <p>Every measurement here assumes you have checked your own gauge. Two crocheters working the same pattern with the same yarn will not get the same size, and the swatch is the only thing that tells you which one you are.</p>
    <p>As an Amazon Associate I earn from qualifying purchases.</p>
    <p class="fineprint"><span>&copy; {AUTHOR}</span> <span>Last checked {UPDATED}</span> <a href="/about/">About these charts</a></p>
  </footer>"""


def url_for(slug):
    return f"/{slug}/" if slug else "/"


def nav_html(current):
    items = []
    for p in PAGES:
        href = url_for(p["slug"])
        cur = ' aria-current="page"' if p["slug"] == current else ""
        items.append(f'      <li><a href="{href}"{cur}>{p["nav"]}</a></li>')
    links = "\n".join(items)
    return (
        '  <nav class="sitenav no-print" aria-label="Main">\n'
        f'    <a class="brand" href="/">{AUTHOR}</a>\n'
        "    <ul>\n"
        f"{links}\n"
        "    </ul>\n"
        "  </nav>"
    )


def related_html(current):
    others = [p for p in PAGES if p["slug"] != current and p["slug"] != "about"][:3]
    if not others:
        return ""
    cards = "\n".join(
        f'      <a href="{url_for(p["slug"])}">\n'
        f'        <span class="t">{p["nav"]}</span>\n'
        f'        <span class="d">{p["card"]}</span>\n'
        f"      </a>"
        for p in others
    )
    return (
        '  <section class="related no-print">\n'
        "    <h2>More reference charts</h2>\n"
        '    <div class="related-grid">\n'
        f"{cards}\n"
        "    </div>\n"
        "  </section>"
    )


def label_table_cells(html):
    """Copy each table's column headings onto its body cells as data-label.

    On a phone the stylesheet turns every table row into a card, and a cell
    showing "B-1" on its own means nothing without the "US" heading that sat
    above it. The CSS reads these attributes to print the label beside the
    value, so a four-column chart stays readable at 360px without the
    sideways scroll it used to need.

    Done here rather than by hand in the fragments so it stays true for any
    table added later, and so the fragments remain plain semantic HTML.
    """
    tag = re.compile(r"<(t[dh])\b([^>]*)>", re.I)

    def do_table(m):
        table = m.group(0)

        head = re.search(r"<thead\b.*?</thead>", table, re.I | re.S)
        if not head:
            return table
        headings = [
            re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()
            for c in re.findall(r"<th\b[^>]*>(.*?)</th>", head.group(0), re.I | re.S)
        ]
        if not headings:
            return table

        body = re.search(r"<tbody\b.*?</tbody>", table, re.I | re.S)
        if not body:
            return table

        def do_row(rm):
            row = rm.group(0)
            col = iter(range(len(headings)))

            def do_cell(cm):
                name, attrs = cm.group(1), cm.group(2)
                if name.lower() != "td" or "data-label" in attrs.lower():
                    return cm.group(0)
                try:
                    i = next(col)
                except StopIteration:
                    return cm.group(0)
                heading = headings[i]
                if not heading or i == 0:
                    return cm.group(0)
                esc = html_escape(heading)
                return f"<td{attrs} data-label=\"{esc}\">"

            return tag.sub(do_cell, row)

        newbody = re.sub(r"<tr\b.*?</tr>", do_row, body.group(0), flags=re.I | re.S)
        return table.replace(body.group(0), newbody)

    return re.sub(r"<table\b.*?</table>", do_table, html, flags=re.I | re.S)


def render(page, book_full):
    slug = page["slug"]
    canonical = f"{SITE}{url_for(slug)}"
    title = page["title"]
    desc = page["desc"]
    content = (PAGEDIR / page["file"]).read_text(encoding="utf-8").rstrip()
    content = label_table_cells(content)

    book = book_full if page["book"] == "full" else BOOKCARD
    related = "" if page.get("no_related") else related_html(slug)

    # The nav and the footer are full-width colour bands, so they sit outside
    # the reading column rather than inside it.
    nav = ('<div class="navband no-print">\n'
           '  <div class="bandinner">\n'
           f'{nav_html(slug)}\n'
           "  </div>\n"
           "</div>")

    foot = ('<div class="footband">\n'
            '  <div class="bandinner">\n'
            f"{FOOTER}\n"
            "  </div>\n"
            "</div>")

    blocks = ['  <header class="masthead">\n'
              f'    <h1>{page["h1"]}</h1>\n'
              f'    <p class="standfirst">{page["standfirst"]}</p>\n'
              "  </header>",
              content,
              related,
              book]

    body = "\n\n".join(b for b in blocks if b)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

<meta name="p:domain_verify" content="{PINTEREST_VERIFY}">

<!-- Rich Pins - Article type (Open Graph) -->
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="{AUTHOR}">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/cover.jpg">
<meta property="og:image:width" content="800">
<meta property="og:image:height" content="1200">
<meta property="og:image:alt" content="Cover of Crazy Crochet Hacks Every Beginner Wishes They Knew by Rosie Payne">
<meta property="article:author" content="{AUTHOR}">
<meta property="article:published_time" content="{PUBLISHED}">

<meta name="description" content="{desc}">
<meta name="author" content="{AUTHOR}">
<link rel="canonical" href="{canonical}">

{FAVICON}
<title>{title}</title>

{FONTS}
<link rel="stylesheet" href="/style.css">

<!-- Cloudflare Web Analytics -->
<script defer type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "5bd7aab32dd1469f88eba23e5c27101e"}}'></script>
<!-- End Cloudflare Web Analytics -->
</head>
<body>
{nav}

<div class="wrap">

{body}

</div>

{foot}
</body>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    book_full = (PAGEDIR / "_book.html").read_text(encoding="utf-8").rstrip()

    written = []
    for page in PAGES:
        html = render(page, book_full)
        if page["slug"]:
            target = OUT / page["slug"] / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
        else:
            target = OUT / "index.html"
        target.write_text(html, encoding="utf-8")
        written.append((target.relative_to(OUT), len(html)))

    # static assets
    shutil.copy(ROOT / "style.css", OUT / "style.css")
    for asset in ("cover.jpg", "cover2.jpg"):
        src = ROOT / asset
        if src.exists():
            shutil.copy(src, OUT / asset)
    (OUT / "CNAME").write_text("rosiepaynecrochet.com\n", encoding="utf-8")

    # sitemap + robots, so Google indexes this as well as Pinterest
    urls = "\n".join(
        f"  <url><loc>{SITE}{url_for(p['slug'])}</loc><lastmod>{PUBLISHED}</lastmod></url>"
        for p in PAGES
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8"
    )

    for path, size in written:
        print(f"  {str(path):34} {size:>7,} bytes")
    print(f"\n{len(written)} pages + style.css, sitemap.xml, robots.txt, CNAME -> {OUT}")


if __name__ == "__main__":
    main()

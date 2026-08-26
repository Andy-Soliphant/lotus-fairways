#!/usr/bin/env python3
"""
build_hotel_pages.py — Lotus & Fairways
Builds one page per property at /hotels/<slug>/index.html from data/hotels.json.

Run from the repo root:   python3 build_hotel_pages.py

THE BAR FOR A PAGE: a hero image on disk AND a verdict. A page without both is
a name, a tier and a picture — it breaks the "pages must earn depth" rule, so
it is not built. As images and verdicts are added, re-run and pages appear.

UNCONFIRMED PROPERTIES get the page but carry <meta robots="noindex, follow">
and are kept out of the sitemap, per the verified-content-only rule. They are
reachable and linkable; they are simply not offered to Google until cleared.

Prints a sitemap fragment at the end for pasting into sitemap.xml.
"""

import json
import os
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(ROOT, "hotels")

TIER_LABEL = {"ultra": "Ultra Luxury", "premium": "Premium", "classic": "Classic"}
COUNTRY_LABEL = {
    "thailand": "Thailand", "vietnam": "Vietnam",
    "cambodia": "Cambodia", "laos": "Laos",
}

# Areas with a golf trip page, so a hotel can link back to it.
TRIP_AREAS = {
    ("thailand", "bangkok"), ("thailand", "chiang-mai"),
    ("thailand", "hua-hin"), ("thailand", "phuket"),
    ("vietnam", "hanoi"), ("vietnam", "da-nang"), ("vietnam", "ho-chi-minh"),
    ("cambodia", "phnom-penh"), ("cambodia", "siem-reap"),
}

# Signature journeys that name a property. Verified against the live pages
# 26 Aug 2026. EDIT THIS BY HAND when a journey's route changes — it is
# deliberately explicit rather than scraped, so a copy edit cannot silently
# rewire the links. Replaced by journeys.json when that exists.
JOURNEY_USE = {
    "the-architects-asia.html": {
        "title": "The Architect's Asia",
        "eyebrow": "Signature Journey",
        "note": "Thailand &middot; Laos &middot; Cambodia &middot; Vietnam &mdash; the hotels of Bill Bensley",
        "slugs": [
            "the-siam-bangkok", "fs-tented-camp-golden-triangle",
            "rosewood-luang-prabang", "bensley-collection-shinta-mani-siem-reap",
            "shinta-mani-wild", "intercontinental-danang",
        ],
    },
    "the-cham-tour.html": {
        "title": "The Cham Tour",
        "eyebrow": "Signature Journey",
        "note": "Through the lost kingdom of Champa",
        "slugs": [
            "capella-bangkok", "chakrabongse-villas", "raffles-grand-angkor",
            "raffles-le-royal", "amanoi", "anantara-quy-nhon",
            "four-seasons-nam-hai", "namia-riverside-da-nang",
        ],
    },
}

AREA_FIXES = {
    "ho-chi-minh": "Ho Chi Minh City", "hoi-an": "Hoi An", "cam-ranh": "Cam Ranh",
    "can-tho": "Can Tho", "quy-nhon": "Quy Nhon", "nha-trang": "Nha Trang",
    "da-nang": "Da Nang", "koh-yao-noi": "Koh Yao Noi", "koh-kood": "Koh Kood",
    "koh-samui": "Koh Samui", "koh-rong": "Koh Rong", "khao-lak": "Khao Lak",
    "golden-triangle": "The Golden Triangle",
    "cardamom-mountains": "The Cardamom Mountains",
    "luang-prabang": "Luang Prabang", "siem-reap": "Siem Reap",
    "phnom-penh": "Phnom Penh", "chiang-mai": "Chiang Mai", "hua-hin": "Hua Hin",
}


def e(s):
    return html.escape(s or "", quote=True)


def area_label(a):
    return AREA_FIXES.get(a, (a or "").replace("-", " ").title())


def images_for(h):
    base = "hotel-%s-%s-%s" % (h["destination"], h["area"], h["slug"])
    out = []
    for suffix in ["", "-2", "-3"]:
        rel = "images/%s%s.jpg" % (base, suffix)
        if os.path.exists(os.path.join(ROOT, rel)):
            out.append("/" + rel)
    return out


def journeys_for(slug):
    out = []
    for href, j in JOURNEY_USE.items():
        if slug in j["slugs"]:
            out.append((href, j))
    return out


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}, {area} | Lotus &amp; Fairways</title>
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="https://lotusfairways.com/hotels/{slug}/">

  <meta property="og:title" content="{name} | Lotus &amp; Fairways">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://lotusfairways.com/hotels/{slug}/">
  <meta property="og:image" content="https://lotusfairways.com{hero}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&amp;family=DM+Sans:wght@300;400;500&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css?v=3">
  <link rel="icon" type="image/svg+xml" href="/images/favicon.svg">

  <style>
{styles}
  </style>
</head>
<body>

<script src="/components/nav.js"></script>

<section class="signature-hero">
  <img src="{hero}" alt="{name}, {area}">
  <div class="signature-hero-content">
    <div class="tier-badge">{tier_label}</div>
    <h1>{name}</h1>
    <p class="hotel-locale">{area}, {country}</p>
  </div>
</section>

<div class="at-a-glance">
  <div class="at-a-glance-grid">
{tiles}
  </div>
</div>
{verdict_block}
{prose_block}
{gallery_block}
{used_block}
<section class="cta-band">
  <h2>Every great holiday starts with a conversation</h2>
  <p>Tell us when you want to travel and who is coming, and we will tell you whether this
     is the right place for you &mdash; and where else to look if it is not.</p>
  <a href="/contact.html" class="btn btn-primary">Start the conversation</a>
</section>

<script src="/components/footer.js"></script>
<script src="/js/main.js"></script>
</body>
</html>
"""

# The signature-journey style block, carried whole per the standing rule, plus
# the hotel-page-local additions. Kept in one string so a page can never ship
# with correct markup and no styling (the 5 Aug Cham fault).
STYLES = open(os.path.join(ROOT, "hotel-page-styles.css")).read() \
    if os.path.exists(os.path.join(ROOT, "hotel-page-styles.css")) else ""


def tile(label, value):
    return ('    <div class="at-a-glance-item">\n'
            '      <h4>%s</h4>\n      <p>%s</p>\n    </div>' % (e(label), value))


def build(h, styles):
    imgs = h["_images"]
    slug = h["slug"]
    name = e(h.get("name", ""))
    area = e(area_label(h.get("area", "")))
    country = e(COUNTRY_LABEL.get(h["destination"], h["destination"].title()))
    tier = h.get("tier", "classic")
    confirmed = bool(h.get("confirmed"))

    # ── At a glance ──────────────────────────────────────────────
    tiles = [tile("Where", "%s, %s" % (area, country))]
    if h.get("arrival"):
        tiles.append(tile("Arrival", e(h["arrival"])))
    if h.get("character"):
        tiles.append(tile("What marks it out", e(h["character"])))
    if h.get("we_send"):
        tiles.append(tile("We send", e(h["we_send"])))
    if h.get("room_types"):
        tiles.append(tile("Rooms", e(", ".join(h["room_types"]))))

    # ── Verdict — the signature element ──────────────────────────
    verdict_block = ""
    if h.get("verdict"):
        verdict_block = """
<section class="section verdict-band">
  <div class="verdict">
    <blockquote>&ldquo;%s&rdquo;</blockquote>
    <cite>Our founder</cite>
  </div>
</section>
""" % e(h["verdict"])

    # ── Prose ────────────────────────────────────────────────────
    paras = [p for p in [h.get("prose")] if p]
    prose_block = ""
    if paras:
        prose_block = """
<section class="section" style="background:var(--white);">
  <div class="hotel-prose">
%s
  </div>
</section>
""" % "\n".join("    <p>%s</p>" % e(p) for p in paras)

    # ── Gallery: images 2 and 3, lazy, so first paint costs one image ──
    gallery_block = ""
    extras = imgs[1:]
    if extras:
        cols = len(extras)
        frames = "\n".join(
            '      <img src="%s" alt="%s" loading="lazy" decoding="async">' % (s, name)
            for s in extras
        )
        gallery_block = """
<section class="section">
  <div class="container">
    <div class="gallery-strip" style="grid-template-columns:repeat(%d,1fr);">
%s
    </div>
  </div>
</section>
""" % (cols, frames)

    # ── Where we use it — INTERNAL LINKS ONLY, never the property's own site ──
    lines = []
    for href, j in journeys_for(slug):
        lines.append(
            '    <a class="journey-line" href="/%s">\n'
            '      <div class="jl-eyebrow">&mdash; %s &mdash;</div>\n'
            '      <div class="jl-title">%s</div>\n'
            '      <p class="jl-note">%s</p>\n    </a>' % (href, j["eyebrow"], j["title"], j["note"])
        )
    if (h["destination"], h["area"]) in TRIP_AREAS:
        lines.append(
            '    <a class="journey-line" href="/golf-in-asia/%s/%s/">\n'
            '      <div class="jl-eyebrow">&mdash; Golf Week &mdash;</div>\n'
            '      <div class="jl-title">The %s golf week</div>\n'
            '      <p class="jl-note">Seven nights, played and stayed</p>\n    </a>'
            % (h["destination"], h["area"], area)
        )
    lines.append(
        '    <a class="journey-line" href="/hotels/">\n'
        '      <div class="jl-eyebrow">&mdash; The Collection &mdash;</div>\n'
        '      <div class="jl-title">The Houses</div>\n'
        '      <p class="jl-note">Every property we put people in, and what we think of each</p>\n    </a>'
    )
    used_block = """
<section class="section" style="background:var(--white);">
  <div class="section-header"><h2>Where we use it</h2></div>
  <div class="where-used">
%s
  </div>
</section>
""" % "\n".join(lines)

    meta = (h.get("character") or h.get("prose") or name)[:155]

    return PAGE.format(
        name=name, area=area, country=country, slug=slug,
        tier_label=TIER_LABEL.get(tier, tier.title()),
        hero=imgs[0], meta_desc=e(meta),
        robots="index, follow" if confirmed else "noindex, follow",
        styles=styles,
        tiles="\n".join(tiles),
        verdict_block=verdict_block, prose_block=prose_block,
        gallery_block=gallery_block, used_block=used_block,
    )


def main():
    with open(os.path.join(ROOT, "data", "hotels.json")) as f:
        data = json.load(f)
    hotels = data["hotels"] if isinstance(data, dict) else data

    styles = STYLES
    built, skipped, indexable = [], [], []
    for h in hotels:
        imgs = images_for(h)
        has_verdict = bool((h.get("verdict") or "").strip())
        if not imgs or not has_verdict:
            reason = []
            if not imgs:
                reason.append("no image")
            if not has_verdict:
                reason.append("no verdict")
            skipped.append((h["slug"], ", ".join(reason)))
            continue
        h["_images"] = imgs
        d = os.path.join(OUT_ROOT, h["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(build(h, styles))
        built.append(h["slug"])
        if h.get("confirmed"):
            indexable.append(h["slug"])

    print("BUILT %d pages (%d indexable, %d noindex pending confirmation)"
          % (len(built), len(indexable), len(built) - len(indexable)))
    print("\nSKIPPED %d — these need content, not code:" % len(skipped))
    for s, r in skipped:
        print("  %-44s %s" % (s, r))
    print("\n--- SITEMAP FRAGMENT (confirmed properties only) ---")
    for s in indexable:
        print("  <url><loc>https://lotusfairways.com/hotels/%s/</loc>"
              "<changefreq>monthly</changefreq><priority>0.6</priority></url>" % s)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
build_hotels_page.py — Lotus & Fairways
Builds /hotels/index.html from data/hotels.json.

Run from the repo root:   python3 build_hotels_page.py

Only properties with a hero image on disk are shown. As images are filed for
more properties, re-run this and they appear automatically. Nothing is
hardcoded — hotels.json is the single source of truth.
"""

import json
import os
import html
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "hotels")
OUT = os.path.join(OUT_DIR, "index.html")

# Page hero for The Houses. Chosen 11 Aug 2026 — 2000x1091 (ratio 1.83), the only
# filed image wide enough for a full-bleed band, and it shows actual houses.
PAGE_HERO = "/images/hotel-cambodia-siem-reap-phum-baitang.jpg"

TIER_ORDER = {"ultra": 0, "premium": 1, "classic": 2}
TIER_LABEL = {"ultra": "Ultra Luxury", "premium": "Premium", "classic": "Classic"}

COUNTRY_LABEL = {
    "thailand": "Thailand",
    "vietnam": "Vietnam",
    "cambodia": "Cambodia",
    "laos": "Laos",
}
COUNTRY_ORDER = ["thailand", "vietnam", "cambodia", "laos"]

# Areas that have a golf trip page, so a hotel card can link back to it.
TRIP_AREAS = {
    ("thailand", "bangkok"), ("thailand", "chiang-mai"),
    ("thailand", "hua-hin"), ("thailand", "phuket"),
    ("vietnam", "hanoi"), ("vietnam", "da-nang"), ("vietnam", "ho-chi-minh"),
    ("cambodia", "phnom-penh"), ("cambodia", "siem-reap"),
}


def e(s):
    return html.escape(s or "", quote=True)


def area_label(area):
    fixes = {
        "ho-chi-minh": "Ho Chi Minh City",
        "hoi-an": "Hoi An",
        "cam-ranh": "Cam Ranh",
        "can-tho": "Can Tho",
        "quy-nhon": "Quy Nhon",
        "nha-trang": "Nha Trang",
        "da-nang": "Da Nang",
        "koh-yao-noi": "Koh Yao Noi",
        "koh-kood": "Koh Kood",
        "koh-samui": "Koh Samui",
        "koh-rong": "Koh Rong",
        "khao-lak": "Khao Lak",
        "golden-triangle": "The Golden Triangle",
        "cardamom-mountains": "The Cardamom Mountains",
        "luang-prabang": "Luang Prabang",
        "siem-reap": "Siem Reap",
        "phnom-penh": "Phnom Penh",
        "chiang-mai": "Chiang Mai",
        "hua-hin": "Hua Hin",
    }
    return fixes.get(area, area.replace("-", " ").title())


def images_for(h):
    """Hero plus up to two extras, only those that exist on disk."""
    base = "hotel-%s-%s-%s" % (h["destination"], h["area"], h["slug"])
    out = []
    for suffix in ["", "-2", "-3"]:
        rel = "images/%s%s.jpg" % (base, suffix)
        if os.path.exists(os.path.join(ROOT, rel)):
            out.append("/" + rel)
    return out


def load():
    with open(os.path.join(ROOT, "data", "hotels.json")) as f:
        data = json.load(f)
    hotels = data["hotels"] if isinstance(data, dict) and "hotels" in data else data
    live = []
    for h in hotels:
        imgs = images_for(h)
        if not imgs:
            continue
        h["_images"] = imgs
        live.append(h)
    return hotels, live


def card(h, idx):
    imgs = h["_images"]
    tier = h.get("tier", "classic")
    name = e(h.get("name", ""))
    area = area_label(h.get("area", ""))
    country = COUNTRY_LABEL.get(h["destination"], h["destination"].title())
    loading = "eager" if idx < 3 else "lazy"

    # Extra frames become a hover-swap strip; only rendered when they exist.
    thumbs = ""
    if len(imgs) > 1:
        buttons = "".join(
            '<button type="button" class="h-dot%s" data-src="%s" aria-label="View image %d of %s"></button>'
            % (" is-on" if i == 0 else "", src, i + 1, name)
            for i, src in enumerate(imgs)
        )
        thumbs = '<div class="h-dots">%s</div>' % buttons

    verdict = ""
    if h.get("verdict"):
        verdict = (
            '<blockquote class="h-verdict"><p>%s</p>'
            '<cite>Our founder</cite></blockquote>' % e(h["verdict"])
        )

    character = ""
    if h.get("character"):
        character = '<p class="h-character">%s</p>' % e(h["character"])

    trip = ""
    if (h["destination"], h["area"]) in TRIP_AREAS:
        trip = (
            '<a class="h-trip" href="/golf-in-asia/%s/%s/">The %s golf week &rarr;</a>'
            % (h["destination"], h["area"], area)
        )

    # A property page exists only where there is an image AND a verdict.
    # Linking to one that was never generated is worse than not linking.
    title = name
    if h.get("verdict"):
        title = '<a class="h-link" href="/hotels/%s/">%s</a>' % (h["slug"], name)

    flag = ""
    if h.get("preferred"):
        flag = '<span class="h-pref" title="A property we hold direct terms with">Preferred</span>'

    return """
      <article class="h-card" data-country="{country_slug}" data-tier="{tier}">
        <div class="h-img">
          <img src="{hero}" alt="{name}, {area}" loading="{loading}" decoding="async"
               onerror="this.closest('.h-card').remove()">
          {thumbs}
          <span class="h-tier h-tier-{tier}">{tier_label}</span>
        </div>
        <div class="h-body">
          <div class="h-place">{area} &middot; {country}</div>
          <h3>{title} {flag}</h3>
          {character}
          {verdict}
          {trip}
        </div>
      </article>""".format(
        country_slug=h["destination"],
        tier=tier,
        tier_label=TIER_LABEL.get(tier, tier.title()),
        hero=imgs[0],
        name=name,
        title=title,
        area=e(area),
        country=e(country),
        loading=loading,
        thumbs=thumbs,
        character=character,
        verdict=verdict,
        trip=trip,
        flag=flag,
    )


def build():
    all_hotels, live = load()

    live.sort(key=lambda h: (
        COUNTRY_ORDER.index(h["destination"]) if h["destination"] in COUNTRY_ORDER else 99,
        area_label(h["area"]),
        TIER_ORDER.get(h.get("tier"), 9),
        h.get("name", ""),
    ))

    countries = [c for c in COUNTRY_ORDER if any(h["destination"] == c for h in live)]
    counts = {c: sum(1 for h in live if h["destination"] == c) for c in countries}

    filters = ['<button type="button" class="h-filter is-on" data-filter="country" data-value="all">Everywhere <span>%d</span></button>' % len(live)]
    for c in countries:
        filters.append(
            '<button type="button" class="h-filter" data-filter="country" data-value="%s">%s <span>%d</span></button>'
            % (c, COUNTRY_LABEL[c], counts[c])
        )

    tier_filters = ['<button type="button" class="h-filter is-on" data-filter="tier" data-value="all">All levels</button>']
    for t in ["classic", "premium", "ultra"]:
        n = sum(1 for h in live if h.get("tier") == t)
        if n:
            tier_filters.append(
                '<button type="button" class="h-filter" data-filter="tier" data-value="%s">%s <span>%d</span></button>'
                % (t, TIER_LABEL[t], n)
            )

    cards = "".join(card(h, i) for i, h in enumerate(live))

    verdict_count = sum(1 for h in live if h.get("verdict"))

    page = TEMPLATE.format(
        total=len(live),
        country_count=len(countries),
        verdict_count=verdict_count,
        filters="\n          ".join(filters),
        tier_filters="\n          ".join(tier_filters),
        cards=cards,
        hero_image=PAGE_HERO,
        page_hero=PAGE_HERO,
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w") as f:
        f.write(page)

    print("Wrote %s" % OUT)
    print("  %d properties shown, %d in hotels.json" % (len(live), len(all_hotels)))
    print("  %d carry a founder's verdict" % verdict_count)
    missing = [h for h in all_hotels if not images_for(h)]
    if missing:
        print("\n  %d properties held back — no photography yet:" % len(missing))
        for h in sorted(missing, key=lambda x: (x["destination"], x["area"])):
            print("    %-10s %-18s %s" % (h["destination"], h["area"], h.get("name", "")))


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Houses &mdash; Where We Put People | Lotus &amp; Fairways</title>
  <meta name="description" content="The hotels and resorts we use across Thailand, Vietnam, Cambodia and Laos &mdash; with an honest word on each from the person who has stayed in them.">
  <link rel="canonical" href="https://lotusfairways.com/hotels/">
  <meta property="og:title" content="The Houses &mdash; Where We Put People | Lotus &amp; Fairways">
  <meta property="og:type" content="website">
  <meta property="og:description" content="Every property we use across Southeast Asia, with an honest word on each.">
  <meta property="og:image" content="https://lotusfairways.com{hero_image}">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-QT9QGJB8ET"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "G-QT9QGJB8ET");
  </script>
  <script type="text/javascript">
    window.$crisp=[];window.CRISP_WEBSITE_ID="46bc36a3-c147-4baa-9228-b066166829d2";
    (function(){{var d=document;var s=d.createElement("script");s.src="https://client.crisp.chat/l.js";s.async=1;d.getElementsByTagName("head")[0].appendChild(s);}})();
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css?v=3">
  <link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
  <style>
    .hh-head {{ position:relative; background:var(--green); color:var(--parchment);
      background-image:linear-gradient(180deg, rgba(42,74,46,0.70) 0%, rgba(42,74,46,0.86) 55%, rgba(42,74,46,0.96) 100%), url('{page_hero}');
      background-size:cover; background-position:center 62%; background-repeat:no-repeat;
      padding:var(--space-3xl) var(--space-xl) var(--space-2xl); }}
    .hh-head-inner {{ max-width:var(--max-width); margin:0 auto; }}
    .hh-head .breadcrumb {{ font-family:var(--font-sans); font-size:0.72rem; letter-spacing:0.1em; text-transform:uppercase; color:rgba(247,243,236,0.55); margin-bottom:var(--space-md); }}
    .hh-head .breadcrumb a {{ color:rgba(247,243,236,0.55); text-decoration:none; }}
    .hh-head .breadcrumb a:hover {{ color:var(--bronze-light); }}
    .hh-head h1 {{ color:var(--white); font-size:clamp(2.4rem,5vw,3.8rem); line-height:1.08; max-width:14ch; margin-bottom:var(--space-md); }}
    .hh-lead {{ font-family:var(--font-serif); font-style:italic; font-size:1.15rem; line-height:1.7; color:var(--parchment-dark); max-width:52ch; }}
    .hh-stats {{ display:flex; flex-wrap:wrap; gap:var(--space-xl); margin-top:var(--space-lg); padding-top:var(--space-md); border-top:1px solid rgba(247,243,236,0.28); }}
    .hh-stats .s small {{ display:block; font-family:var(--font-sans); font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase; color:rgba(247,243,236,0.6); margin-bottom:4px; }}
    .hh-stats .s b {{ font-family:var(--font-serif); font-weight:400; font-size:1.6rem; color:var(--bronze-light); }}

    .hh-bar {{ background:var(--white); border-bottom:1px solid var(--rule); position:sticky; top:66px; z-index:10; }}
    .hh-bar-inner {{ max-width:var(--max-width); margin:0 auto; padding:var(--space-md) var(--space-xl); display:flex; flex-wrap:wrap; gap:var(--space-lg); align-items:center; }}
    .hh-group {{ display:flex; flex-wrap:wrap; gap:var(--space-sm); align-items:center; }}
    .hh-group > .lbl {{ font-family:var(--font-sans); font-size:0.62rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--warm-grey); margin-right:var(--space-xs); }}
    .h-filter {{ font-family:var(--font-sans); font-size:0.74rem; letter-spacing:0.04em; color:var(--slate); background:none; border:1px solid var(--rule); border-radius:999px; padding:7px 15px; cursor:pointer; transition:all .18s ease; }}
    .h-filter span {{ color:var(--warm-grey); font-size:0.66rem; margin-left:5px; }}
    .h-filter:hover {{ border-color:var(--bronze-light); color:var(--green); }}
    .h-filter.is-on {{ background:var(--green); border-color:var(--green); color:var(--white); }}
    .h-filter.is-on span {{ color:var(--bronze-light); }}
    .h-filter:focus-visible {{ outline:2px solid var(--rose); outline-offset:2px; }}
    @media(max-width:820px) {{ .hh-bar {{ position:static; }} .hh-bar-inner {{ gap:var(--space-md); padding:var(--space-md); }} }}

    .hh-grid-wrap {{ max-width:var(--max-width); margin:0 auto; padding:var(--space-2xl) var(--space-xl) var(--space-3xl); }}
    .hh-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:var(--space-xl) var(--space-lg); }}
    @media(max-width:1000px) {{ .hh-grid {{ grid-template-columns:repeat(2,1fr); }} }}
    @media(max-width:640px)  {{ .hh-grid {{ grid-template-columns:1fr; }} }}

    .h-card {{ display:flex; flex-direction:column; }}
    .h-link {{ color:inherit; text-decoration:none; border-bottom:1px solid var(--rule); transition:color var(--transition), border-color var(--transition); }}
    .h-link:hover {{ color:var(--rose); border-bottom-color:var(--rose); }}
    .h-card.is-hidden {{ display:none; }}
    .h-img {{ position:relative; aspect-ratio:16/10; overflow:hidden; background:var(--parchment-dark); }}
    .h-img img {{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .7s cubic-bezier(.2,.7,.3,1); }}
    .h-card:hover .h-img img {{ transform:scale(1.04); }}
    .h-tier {{ position:absolute; left:0; bottom:0; font-family:var(--font-sans); font-size:0.58rem; letter-spacing:0.16em; text-transform:uppercase; padding:6px 12px; color:var(--white); }}
    .h-tier-ultra {{ background:var(--rose); }}
    .h-tier-premium {{ background:var(--green); }}
    .h-tier-classic {{ background:var(--bronze); }}
    .h-dots {{ position:absolute; right:10px; bottom:10px; display:flex; gap:6px; }}
    .h-dot {{ width:9px; height:9px; border-radius:50%; border:1px solid rgba(255,255,255,0.9); background:rgba(0,0,0,0.25); cursor:pointer; padding:0; transition:background .2s ease; }}
    .h-dot.is-on {{ background:var(--white); }}
    .h-dot:focus-visible {{ outline:2px solid var(--white); outline-offset:2px; }}

    .h-body {{ padding-top:var(--space-md); }}
    .h-place {{ font-family:var(--font-sans); font-size:0.63rem; letter-spacing:0.15em; text-transform:uppercase; color:var(--rose); margin-bottom:6px; }}
    .h-body h3 {{ font-family:var(--font-serif); font-weight:400; font-size:1.42rem; line-height:1.25; color:var(--green); margin:0 0 8px; }}
    .h-pref {{ font-family:var(--font-sans); font-size:0.55rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--bronze); border:1px solid var(--bronze-light); border-radius:2px; padding:2px 6px; vertical-align:middle; margin-left:4px; }}
    .h-character {{ font-size:0.92rem; line-height:1.75; color:var(--warm-grey); margin:0 0 var(--space-md); }}

    /* The signature: a verdict in the founder's own words, set apart by a bronze rule. */
    .h-verdict {{ border-left:2px solid var(--bronze-light); padding:2px 0 2px var(--space-md); margin:0 0 var(--space-md); }}
    .h-verdict p {{ font-family:var(--font-serif); font-style:italic; font-size:1.06rem; line-height:1.6; color:var(--slate); margin:0 0 6px; }}
    .h-verdict cite {{ font-family:var(--font-sans); font-style:normal; font-size:0.6rem; letter-spacing:0.16em; text-transform:uppercase; color:var(--bronze); }}

    .h-trip {{ font-family:var(--font-sans); font-size:0.7rem; letter-spacing:0.06em; text-transform:uppercase; color:var(--green); text-decoration:none; border-bottom:1px solid var(--rule); padding-bottom:3px; }}
    .h-trip:hover {{ color:var(--rose); border-color:var(--rose); }}

    .hh-empty {{ display:none; text-align:center; padding:var(--space-2xl) 0; }}
    .hh-empty p {{ font-family:var(--font-serif); font-style:italic; font-size:1.2rem; color:var(--warm-grey); }}
    .hh-empty.is-on {{ display:block; }}

    .hh-note {{ background:var(--parchment); border-top:1px solid var(--rule); }}
    .hh-note-inner {{ max-width:62ch; margin:0 auto; padding:var(--space-2xl) var(--space-xl); text-align:center; }}
    .hh-note h2 {{ font-size:1.9rem; color:var(--green); margin-bottom:var(--space-md); }}
    .hh-note p {{ font-size:1rem; line-height:1.85; color:var(--slate); margin-bottom:var(--space-lg); }}

    @media(prefers-reduced-motion:reduce) {{
      .h-img img, .h-card:hover .h-img img {{ transition:none; transform:none; }}
    }}
  </style>
</head>
<body>

<script src="/components/nav.js?v=2"></script>

<header class="hh-head">
  <div class="hh-head-inner">
    <nav class="breadcrumb"><a href="/">Lotus &amp; Fairways</a> &rsaquo; The Houses</nav>
    <h1>Where we put people</h1>
    <p class="hh-lead">Not a list of everything available. These are the houses we return to &mdash; chosen because
      of where they stand, how they are run, and how they behave when something goes wrong.</p>
    <div class="hh-stats">
      <div class="s"><small>Properties</small><b>{total}</b></div>
      <div class="s"><small>Countries</small><b>{country_count}</b></div>
      <div class="s"><small>Stayed in and written up</small><b>{verdict_count}</b></div>
    </div>
  </div>
</header>

<div class="hh-bar">
  <div class="hh-bar-inner">
    <div class="hh-group">
      <span class="lbl">Where</span>
      {filters}
    </div>
    <div class="hh-group">
      <span class="lbl">Level</span>
      {tier_filters}
    </div>
  </div>
</div>

<main class="hh-grid-wrap">
  <div class="hh-grid" id="hhGrid">{cards}
  </div>
  <div class="hh-empty" id="hhEmpty"><p>Nothing in that combination yet &mdash; try another level.</p></div>
</main>

<section class="hh-note">
  <div class="hh-note-inner">
    <h2>Why the same names keep appearing</h2>
    <p>We are not a booking site reselling someone else's inventory. We operate on the ground across
      Southeast Asia, which means we hold our own terms with these houses and know the people who run
      them. It is also why the list is shorter than you might expect &mdash; a property earns its place
      here by being somewhere we would send a friend, not by paying for the position.</p>
    <a href="/contact.html" class="btn btn-rose">Tell us where you're going &rarr;</a>
  </div>
</section>

<script src="/components/footer.js?v=2"></script>
<script src="/js/main.js"></script>
<script>
(function () {{
  var grid = document.getElementById('hhGrid');
  if (!grid) return;
  var empty = document.getElementById('hhEmpty');
  var state = {{ country: 'all', tier: 'all' }};

  function apply() {{
    var shown = 0;
    grid.querySelectorAll('.h-card').forEach(function (c) {{
      var ok = (state.country === 'all' || c.dataset.country === state.country) &&
               (state.tier === 'all' || c.dataset.tier === state.tier);
      c.classList.toggle('is-hidden', !ok);
      if (ok) shown++;
    }});
    empty.classList.toggle('is-on', shown === 0);
  }}

  document.querySelectorAll('.h-filter').forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      var key = btn.dataset.filter;
      state[key] = btn.dataset.value;
      document.querySelectorAll('.h-filter[data-filter="' + key + '"]')
        .forEach(function (b) {{ b.classList.remove('is-on'); }});
      btn.classList.add('is-on');
      apply();
    }});
  }});

  // Image dots swap the frame in place — no lightbox, no dependency.
  grid.addEventListener('click', function (ev) {{
    var dot = ev.target.closest('.h-dot');
    if (!dot) return;
    var wrap = dot.closest('.h-img');
    wrap.querySelector('img').src = dot.dataset.src;
    wrap.querySelectorAll('.h-dot').forEach(function (d) {{ d.classList.remove('is-on'); }});
    dot.classList.add('is-on');
  }});
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()

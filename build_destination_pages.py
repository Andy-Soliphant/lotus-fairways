#!/usr/bin/env python3
"""
build_destination_pages.py  —  Lotus & Fairways leisure tree.

Writes /destinations/<country>/<place>/index.html for every entry in PLACES,
built entirely from data/hotels.json. No prose is invented here: each property
block uses its own `character`, `we_send` and Andy's `verdict`.

Run from the repo root:  python3 build_destination_pages.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
def e(s): return html.escape(str(s or ""), quote=True)

COUNTRY_LABEL = {"thailand":"Thailand","vietnam":"Vietnam","cambodia":"Cambodia","laos":"Laos"}

# slug -> (country, [hotels.json area codes], H1, standfirst, golf city page or None)
PLACES = [
 ("bangkok","thailand",["bangkok"],"Bangkok",
  "Eleven properties we use in Bangkok, and the reason we choose between them is almost always the river.",
  "/golf-in-asia/thailand/bangkok/"),
 ("chiang-mai","thailand",["chiang-mai"],"Chiang Mai",
  "The old city, the valley beyond it, and the question of whether you want to walk out into Chiang Mai or look at it from a distance.",
  "/golf-in-asia/thailand/chiang-mai/"),
 ("hua-hin","thailand",["hua-hin"],"Hua Hin",
  "Three hours from Bangkok by road, and the only Thai beach town with a royal history, a working railway station and championship golf behind it.",
  "/golf-in-asia/thailand/hua-hin/"),
 ("phuket","thailand",["phuket"],"Phuket",
  "Phuket is not one place. Which coast you stay on decides the holiday, and that is the whole of the advice.",
  "/golf-in-asia/thailand/phuket/"),
 ("krabi","thailand",["krabi"],"Krabi",
  "Limestone, longtails and the Andaman coast at its least developed. The properties are few and the choice between them is straightforward.",
  None),
 ("hanoi","vietnam",["hanoi"],"Hanoi",
  "Six properties in Hanoi, and they divide almost exactly between the Old Quarter and the French Quarter.",
  "/golf-in-asia/vietnam/hanoi/"),
 ("saigon","vietnam",["ho-chi-minh"],"Saigon",
  "Ho Chi Minh City to the map, Saigon to almost everyone who lives there. The hotels sit in District 1 and the difference between them is noise.",
  "/golf-in-asia/vietnam/ho-chi-minh/"),
 ("da-nang","vietnam",["da-nang"],"Da Nang",
  "The central coast, the airport that opens it, and the beach that runs south towards Hoi An.",
  "/golf-in-asia/vietnam/da-nang/"),
 ("mekong-delta","vietnam",["can-tho"],"The Mekong Delta",
  "The Delta is a place you travel through rather than to, and the reason to stop is to see it at first light before the floating market disperses.",
  None),
 ("sapa","vietnam",["sapa"],"Sapa",
  "The northern mountains, the rice terraces and the villages of the Hoang Lien range. One property, and it is the reason the region works at all.",
  None),
 ("siem-reap","cambodia",["siem-reap"],"Siem Reap",
  "Seven properties in one small town, and the only thing that genuinely separates them is how each one relates to the temples.",
  "/golf-in-asia/cambodia/siem-reap/"),
 ("phnom-penh","cambodia",["phnom-penh"],"Phnom Penh",
  "The riverfront, the Royal Palace and a city most itineraries give one night. Four properties, and a case for giving it two.",
  "/golf-in-asia/cambodia/phnom-penh/"),
 ("kep","cambodia",["kep"],"Kep &amp; Kampot",
  "Cambodia's south coast: pepper farms, the crab market, and the modernist villas of a seaside town that was fashionable before the war.",
  None),
]

# Optional feature band. Siem Reap carries Angkor per Andy's ruling, 2 Sep 2026:
# the page is Siem Reap, Angkor is the argument.
FEATURES = {
 "siem-reap": ("Angkor",
   "Nobody comes to Siem Reap for Siem Reap. The temples are the reason, and every "
   "property below answers the same question differently &mdash; how far you are from "
   "them at five in the morning, and what you come back to afterwards. That is the "
   "only comparison worth making here, and it is the one no hotel list makes."),
}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Where to Stay in {h1_plain} | Lotus &amp; Fairways</title>
  <meta name="description" content="{meta}">
  <link rel="canonical" href="https://lotusfairways.com/destinations/{country}/{slug}/">
  <meta property="og:title" content="Where to Stay in {h1_plain} | Lotus &amp; Fairways">
  <meta property="og:description" content="{meta}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://lotusfairways.com/destinations/{country}/{slug}/">
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
  <img src="{hero}" alt="{h1_plain}, {country_label}">
  <div class="signature-hero-content">
    <div class="tier-badge">{country_label}</div>
    <h1>{h1}</h1>
    <p class="hotel-locale">Where to stay</p>
  </div>
</section>

<section class="dest-standfirst">
  <p>{standfirst}</p>
  <p class="dest-crumb"><a href="/destinations/{country}.html">All of {country_label}</a>{golf_link}</p>
</section>
{feature_block}
<section class="dest-houses">
  <h2>The houses we use</h2>
{cards}
</section>

<section class="cta-band">
  <h2>Every great holiday starts with a conversation</h2>
  <p>Tell us when you want to travel and who is coming, and we will tell you which of these
     is the right place for you &mdash; and where else to look if none of them is.</p>
  <a href="/contact.html" class="btn btn-primary">Start the conversation</a>
</section>

<script src="/components/footer.js"></script>
<script src="/js/main.js"></script>
</body>
</html>
"""

EXTRA_CSS = """
    .dest-standfirst { max-width:760px; margin:0 auto; padding:var(--space-2xl) var(--space-xl) var(--space-lg); text-align:center; }
    .dest-standfirst p { font-family:var(--font-serif); font-size:1.22rem; line-height:1.75; color:var(--deep); }
    .dest-crumb { font-family:var(--font-sans) !important; font-size:0.8rem !important; letter-spacing:0.06em; text-transform:uppercase; margin-top:var(--space-lg); }
    .dest-crumb a { color:var(--bronze); text-decoration:none; border-bottom:1px solid var(--rule); }
    .dest-crumb span { color:var(--rule); margin:0 12px; }

    .dest-feature { background:var(--parchment); padding:var(--space-2xl) var(--space-xl); margin:var(--space-lg) 0; }
    .dest-feature-inner { max-width:760px; margin:0 auto; }
    .dest-feature .eyebrow { color:var(--bronze); margin-bottom:var(--space-sm); }
    .dest-feature h2 { margin-bottom:var(--space-md); }
    .dest-feature p { color:var(--slate); line-height:1.9; font-size:1rem; }

    .dest-houses { max-width:var(--max-width); margin:0 auto; padding:var(--space-2xl) var(--space-xl); }
    .dest-houses > h2 { text-align:center; margin-bottom:var(--space-2xl); }
    .house-row { display:grid; grid-template-columns:340px 1fr; gap:var(--space-xl); align-items:start;
                 padding:var(--space-xl) 0; border-top:1px solid var(--rule); }
    .house-row:last-child { border-bottom:1px solid var(--rule); }
    @media(max-width:800px){ .house-row{ grid-template-columns:1fr; } }
    .house-row img { width:100%; height:230px; object-fit:cover; border-radius:2px; }
    .house-row .noimg { width:100%; height:230px; background:var(--parchment); border-radius:2px; }
    .house-row h3 { font-size:1.5rem; margin-bottom:6px; }
    .house-row .house-meta { font-size:0.76rem; letter-spacing:0.08em; text-transform:uppercase; color:var(--bronze); margin-bottom:var(--space-md); }
    .house-row .house-char { color:var(--slate); line-height:1.8; font-size:0.95rem; margin-bottom:var(--space-md); }
    .house-row blockquote { border-left:2px solid var(--bronze); padding-left:var(--space-md); margin:0 0 var(--space-md);
                            font-family:var(--font-serif); font-style:italic; font-size:1.02rem; line-height:1.7; color:var(--deep); }
    .house-row .house-send { font-size:0.88rem; color:var(--slate); }
    .house-row .house-send strong { color:var(--deep); font-weight:500; }
    .house-row .house-more { display:inline-block; margin-top:var(--space-md); font-size:0.8rem; letter-spacing:0.06em;
                             text-transform:uppercase; color:var(--bronze); text-decoration:none; border-bottom:1px solid var(--rule); }
"""

def card(h):
    slug = h["slug"]
    has_page = bool(h.get("verdict")) and bool(h.get("image"))
    img = ('<img src="%s" alt="%s" loading="lazy">' % (e(h["image"]), e(h["name"]))
           if h.get("image") else '<div class="noimg"></div>')
    bits = []
    bits.append('  <div class="house-row">')
    bits.append('    <div>%s</div>' % img)
    bits.append('    <div>')
    bits.append('      <h3>%s</h3>' % e(h["name"]))
    bits.append('      <p class="house-meta">%s</p>' % e(h.get("tier","").title()))
    if h.get("character"):
        bits.append('      <p class="house-char">%s</p>' % e(h["character"]))
    if h.get("verdict"):
        bits.append('      <blockquote>%s</blockquote>' % e(h["verdict"]))
    if h.get("we_send"):
        bits.append('      <p class="house-send"><strong>We send:</strong> %s</p>' % e(h["we_send"]))
    if has_page:
        bits.append('      <a class="house-more" href="/hotels/%s/">More on %s &rarr;</a>' % (slug, e(h["name"])))
    bits.append('    </div>')
    bits.append('  </div>')
    return "\n".join(bits)


def main():
    data = json.load(open(os.path.join(ROOT, "data", "hotels.json")))
    hotels = data["hotels"]
    styles = ""
    css = os.path.join(ROOT, "hotel-page-styles.css")
    if os.path.exists(css):
        styles = open(css).read()
    styles += EXTRA_CSS

    written, skipped, urls = [], [], []
    for slug, country, areas, h1, standfirst, golf in PLACES:
        rows = [h for h in hotels if h["destination"] == country and h["area"] in areas]
        if not rows:
            skipped.append("%s/%s — no properties in hotels.json, page NOT written" % (country, slug))
            continue
        # hero: first property that has an image
        hero = next((h["image"] for h in rows if h.get("image")), "")
        if not hero:
            skipped.append("%s/%s — no photography on any property, page NOT written" % (country, slug))
            continue
        # order: properties with a verdict and a page first, then the rest
        rows.sort(key=lambda h: (not (h.get("verdict") and h.get("image")), h["name"]))

        h1_plain = re.sub(r"&amp;", "&", h1)
        feature = ""
        if slug in FEATURES:
            ft, fb = FEATURES[slug]
            feature = ('<section class="dest-feature">\n  <div class="dest-feature-inner">\n'
                       '    <p class="eyebrow">&mdash; Featured &mdash;</p>\n'
                       '    <h2>%s</h2>\n    <p>%s</p>\n  </div>\n</section>\n' % (e(ft), fb))

        golf_link = ('<span>&middot;</span><a href="%s">Golf in %s</a>' % (golf, h1_plain)) if golf else ""
        meta = ("%s The houses we use in %s, each with our own verdict on it. Trade and private clients, "
                "Lotus &amp; Fairways." % (re.sub(r"<[^>]+>", "", standfirst), h1_plain))[:300]

        page = PAGE.format(
            slug=slug, country=country, country_label=COUNTRY_LABEL[country],
            h1=h1, h1_plain=e(h1_plain), standfirst=standfirst, meta=e(meta),
            hero=e(hero), styles=styles, feature_block=feature, golf_link=golf_link,
            cards="\n".join(card(h) for h in rows),
        )
        out = os.path.join(ROOT, "destinations", country, slug)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w") as f:
            f.write(page)
        written.append("destinations/%s/%s/index.html  (%d properties, %d linked)"
                       % (country, slug, len(rows),
                          sum(1 for h in rows if h.get("verdict") and h.get("image"))))
        urls.append("https://lotusfairways.com/destinations/%s/%s/" % (country, slug))

    print("WRITTEN (%d):" % len(written))
    for w in written: print("  " + w)
    if skipped:
        print("\nSKIPPED (%d):" % len(skipped))
        for s in skipped: print("  " + s)
    print("\nSITEMAP URLS to add:")
    for u in urls: print("  " + u)
    open(os.path.join(ROOT, "destinations-sitemap-urls.txt"), "w").write("\n".join(urls) + "\n")

if __name__ == "__main__":
    main()

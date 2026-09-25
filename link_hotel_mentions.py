#!/usr/bin/env python3
"""
link_hotel_mentions.py  —  Lotus & Fairways internal linking.

Turns the FIRST plain-text mention of each hotel on a page into a link to that
hotel's own page at /hotels/<slug>/.  Safe to re-run: it never touches text that
is already inside a link, never links a hotel twice on one page, and never adds
a link a page already has.

Rules (the standing L&F rules):
  * internal links only — never to a hotel's own website
  * only hotels that HAVE a page (hero image + verdict) are linked
  * only body copy (<p> and <li>), never headings, captions, nav or buttons
  * hotel pages themselves and the generated destination pages are skipped
    (the generators handle those)

Run from the repo root:   python3 link_hotel_mentions.py          (dry run)
                          python3 link_hotel_mentions.py --write  (apply)
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WRITE = "--write" in sys.argv

# Extra names a hotel is written as in running copy. Longest match wins.
ALIASES = {
    "fs-tented-camp-golden-triangle": ["Four Seasons Tented Camp Golden Triangle", "Four Seasons Tented Camp"],
    "anantara-golden-triangle": ["Anantara Golden Triangle Elephant Camp & Resort",
                                 "Anantara Golden Triangle Elephant Camp", "Anantara Golden Triangle"],
    "four-seasons-chiang-mai": ["Four Seasons Resort Chiang Mai", "Four Seasons Chiang Mai"],
    "four-seasons-nam-hai": ["Four Seasons Resort The Nam Hai", "Four Seasons The Nam Hai", "The Nam Hai"],
    "intercontinental-danang": ["InterContinental Danang Sun Peninsula Resort", "InterContinental Danang",
                                "InterContinental Da Nang"],
    "raffles-le-royal": ["Raffles Hotel Le Royal", "Raffles Le Royal"],
    "raffles-grand-angkor": ["Raffles Grand Hotel d'Angkor", "Raffles Grand Hotel d&#39;Angkor",
                             "Raffles Grand Hotel d’Angkor"],
    "bensley-collection-shinta-mani-siem-reap": ["Bensley Collection Shinta Mani Siem Reap",
                                                 "Bensley Collection Pool Villas", "Bensley Collection"],
    "metropole-hanoi": ["Sofitel Legend Metropole Hanoi", "Metropole Hanoi", "the Metropole"],
    "mandarin-oriental-bangkok": ["Mandarin Oriental Bangkok", "Mandarin Oriental, Bangkok"],
    "peninsula-bangkok": ["The Peninsula Bangkok", "Peninsula Bangkok"],
    "the-siam-bangkok": ["The Siam"],
    "salil-hotel-riverside": ["The Salil Hotel Riverside", "Salil Hotel Riverside"],
    "anantara-hua-hin": ["Anantara Hua Hin Resort", "Anantara Hua Hin"],
    "centara-grand-hua-hin": ["Centara Grand Beach Resort", "Centara Grand Hua Hin", "Centara Grand"],
    "hotel-des-arts-saigon": ["Hotel des Arts Saigon", "Hotel des Arts"],
    "the-reverie-saigon": ["The Reverie Saigon", "The Reverie"],
    "palace-gate-phnom-penh": ["Palace Gate Hotel & Resort", "Palace Gate Hotel &amp; Resort", "Palace Gate"],
    "aviary-siem-reap": ["Aviary Hotel"],
    "song-saa": ["Song Saa Private Island", "Song Saa"],
    "cape-nidhra-hua-hin": ["Cape Nidhra"],
    "namia-riverside-da-nang": ["Namia River Retreat", "Namia Riverside", "Namia"],
    "chicland-da-nang": ["Chicland Hotel", "Chicland"],
}

SKIP_PREFIXES = ("hotels/", "destinations/thailand/", "destinations/vietnam/",
                 "destinations/cambodia/", "destinations/laos/", ".git/", "node_modules/")
SKIP_FILES = {"thank-you.html", "contact.html"}

BLOCK = re.compile(r"(<(p|li)\b[^>]*>)(.*?)(</\2>)", re.S | re.I)
ANCHOR = re.compile(r"<a\b[^>]*>.*?</a>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")


def load_targets():
    data = json.load(open(os.path.join(ROOT, "data", "hotels.json")))
    have_page = {p.split(os.sep)[-2] for p in glob.glob(os.path.join(ROOT, "hotels", "*", "index.html"))}
    pairs = []
    for h in data["hotels"]:
        if h["slug"] not in have_page:
            continue
        names = set([h["name"]] + ALIASES.get(h["slug"], []))
        for n in names:
            pairs.append((n, h["slug"]))
    pairs.sort(key=lambda p: -len(p[0]))          # longest name first
    return pairs


def link_text(text, pairs, done, counts):
    """Link names inside a run of plain text (no tags in it)."""
    out, i = [], 0
    while i < len(text):
        hit = None
        for name, slug in pairs:
            if slug in done:
                continue
            if text.startswith(name, i):
                before = text[i - 1] if i else " "
                after = text[i + len(name)] if i + len(name) < len(text) else " "
                if not (before.isalnum() or after.isalnum()):
                    hit = (name, slug)
                    break
        if hit:
            name, slug = hit
            out.append('<a class="hotel-link" href="/hotels/%s/">%s</a>' % (slug, name))
            done.add(slug)
            counts[slug] = counts.get(slug, 0) + 1
            i += len(name)
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def process(html, pairs, own_slug=None):
    done = set(re.findall(r'href="/hotels/([a-z0-9-]+)/?"', html))
    if own_slug:
        done.add(own_slug)
    counts = {}

    def fix_block(m):
        open_tag, _, inner, close_tag = m.groups()
        pieces, last = [], 0
        for a in ANCHOR.finditer(inner):          # leave existing links alone
            pieces.append(("t", inner[last:a.start()]))
            pieces.append(("a", a.group(0)))
            last = a.end()
        pieces.append(("t", inner[last:]))
        new = []
        for kind, chunk in pieces:
            if kind == "a":
                new.append(chunk)
                continue
            parts, pos = [], 0                    # split round inline tags (<strong>, <em>)
            for t in TAG.finditer(chunk):
                parts.append(link_text(chunk[pos:t.start()], pairs, done, counts))
                parts.append(t.group(0))
                pos = t.end()
            parts.append(link_text(chunk[pos:], pairs, done, counts))
            new.append("".join(parts))
        return open_tag + "".join(new) + close_tag

    head, sep, body = html.partition("<body")
    if not sep:
        return html, counts
    # never touch scripts or styles in the body
    chunks = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", body, flags=re.S | re.I)
    chunks = [c if c.lower().startswith(("<script", "<style")) else BLOCK.sub(fix_block, c) for c in chunks]
    return head + sep + "".join(chunks), counts


def main():
    pairs = load_targets()
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
    total, report = 0, []
    for f in files:
        rel = os.path.relpath(f, ROOT)
        if rel.startswith(SKIP_PREFIXES) or rel in SKIP_FILES:
            continue
        html = open(f, encoding="utf-8").read()
        new, counts = process(html, pairs)
        if counts:
            total += len(counts)
            report.append("%-58s +%d  %s" % (rel, len(counts), ", ".join(sorted(counts))))
            if WRITE:
                open(f, "w", encoding="utf-8").write(new)
    print("\n".join(report))
    print("\n%s: %d new links across %d pages" % ("WRITTEN" if WRITE else "DRY RUN", total, len(report)))


if __name__ == "__main__":
    main()

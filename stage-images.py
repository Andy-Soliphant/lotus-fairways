#!/usr/bin/env python3
"""
Lotus & Fairways - image filing assistant.

WHAT IT IS FOR
You have hotel photographs on OneDrive with names like "IMG_4471.jpg" or
"amanoi pool.jpg". The website needs them named exactly - and a wrong name
fails silently, which is how this went unnoticed for weeks.

This script does the naming for you. You only have to get the hotel name
roughly right; it works out the rest, shows you what it plans to do, and
waits for you to say yes.

HOW TO USE IT

1. Make a staging folder:        mkdir -p ~/Downloads/lf-images-in
2. Copy images into it from OneDrive - COPY, do not move. Keep your originals.
3. EITHER put images in a folder named after the hotel - the easiest way,
   and it works straight from a OneDrive download:

       lf-images-in/Capella Bangkok/anything.jpg
       lf-images-in/Capella Bangkok/whatever.jpg      <- becomes image 2
       lf-images-in/Amanoi/DSC_0041.jpg

   Nested folders are fine too, so an unzipped OneDrive download can go in whole:

       lf-images-in/OneDrive_2026-08-06/Capella Bangkok/IMG_4471.jpg

   OR name the files themselves, if they are loose:

       amanoi.jpg
       raffles le royal.jpg
       capella bangkok 2.jpg          <- a trailing 2 or 3 sets the position
4. Run:
       cd ~/Documents/GitHub/lotus-fairways-live && python3 stage-images.py

It will show each file, the property it matched, and the final filename,
then ask before doing anything. Nothing is deployed and nothing is deleted.

ALSO HANDLED
  - HEIC and PNG files are converted to JPG (browsers do not show HEIC).
  - Images narrower than 1600px are flagged, not silently accepted.
  - Portrait images are flagged, because they crop badly in a hero band.
  - hotels.json is updated to match, so the data never drifts from the files.

Uses only what macOS already has. Nothing to install.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

REPO = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(REPO, "images")
DATA = os.path.join(REPO, "data", "hotels.json")
STAGING = os.path.expanduser("~/Downloads/lf-images-in")

MIN_WIDTH = 1600
THUMBNAIL_WIDTH = 800
STOPWORDS = {"hotel", "resort", "the", "a", "and", "villas", "collection",
             "img", "dsc", "photo", "image", "copy", "final", "edit"}


def normalise(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def tokens(text):
    return {t for t in normalise(text).split() if t and t not in STOPWORDS}


def sips(path, *args):
    """macOS built-in image tool. Returns None if unavailable."""
    if not shutil.which("sips"):
        return None
    try:
        return subprocess.run(["sips", *args, path], capture_output=True,
                              text=True, timeout=60)
    except Exception:
        return None


def dimensions(path):
    r = sips(path, "-g", "pixelWidth", "-g", "pixelHeight")
    if not r or r.returncode != 0:
        try:                                    # fallback if sips is unavailable
            from PIL import Image
            with Image.open(path) as im:
                return im.size
        except Exception:
            return None
    w = re.search(r"pixelWidth:\s*(\d+)", r.stdout)
    h = re.search(r"pixelHeight:\s*(\d+)", r.stdout)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def target_name(hotel, n):
    base = f"hotel-{hotel['destination']}-{hotel['area']}-{hotel['slug']}"
    return f"{base}.jpg" if n == 1 else f"{base}-{n}.jpg"


def match(filename, hotels):
    """Score every property against the filename and return the best two."""
    stem = os.path.splitext(filename)[0]
    n = 0                                   # 0 = no position stated in the filename
    m = re.search(r"[-_ ]([23])$", stem.strip())
    if m:
        n = int(m.group(1))
        stem = stem[: m.start()]

    want = tokens(stem)
    if not want:
        return (0, None), (0, None), n

    scored = []
    for h in hotels:
        have = tokens(h["name"]) | tokens(h["slug"]) | tokens(h["area"])
        if not have:
            continue
        overlap = len(want & have)
        if not overlap:
            continue
        scored.append((overlap / len(want | have) + overlap * 0.1, h))

    scored.sort(key=lambda x: -x[0])
    best = scored[0] if scored else (0, None)
    second = scored[1] if len(scored) > 1 else (0, None)
    return best, second, n


def main():
    auto = "--yes" in sys.argv

    for path, what in ((IMAGES, "images folder"), (DATA, "data/hotels.json")):
        if not os.path.exists(path):
            sys.exit(f"Cannot find the {what}. Run this from the repo root:\n"
                     f"  cd ~/Documents/GitHub/lotus-fairways-live && python3 stage-images.py")

    if not os.path.isdir(STAGING):
        os.makedirs(STAGING, exist_ok=True)
        sys.exit(f"Created a staging folder for you:\n  {STAGING}\n\n"
                 "Copy your images in there from OneDrive, give each one a name "
                 "with the hotel in it, then run this again.")

    zips = [z for z in os.listdir(STAGING) if z.lower().endswith(".zip")]
    if zips:
        print("\n  Zip files in the staging folder - double-click them in Finder "
              "to unpack, then delete the zip:")
        for z in zips:
            print(f"      {z}")

    data = json.load(open(DATA))
    hotels = data["hotels"]

    files = []
    for root, dirs, names in os.walk(STAGING):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for nm in sorted(names):
            if nm.lower().endswith((".jpg", ".jpeg", ".png", ".heic")) \
                    and not nm.startswith("."):
                files.append(os.path.join(root, nm))
    if not files:
        sys.exit(f"No images found in {STAGING}")

    print(f"\n  {len(files)} image(s) found.\n")

    plan, unmatched, candidates = [], [], []
    for src in files:
        f = os.path.basename(src)
        try:
            (best_score, best), (second_score, _), explicit_n = match(f, hotels)
        except Exception as e:
            unmatched.append((os.path.relpath(src, STAGING), f"could not read this one ({e})"))
            continue

        if not best:
            # fall back to the folder name, nearest parent first
            rel = os.path.relpath(os.path.dirname(src), STAGING)
            parts = [] if rel == "." else rel.split(os.sep)
            for parent in reversed(parts):
                (bs, b), (ss, _), _ = match(parent, hotels)
                if b:
                    best, best_score, second_score = b, bs, ss
                    break
        if not best:
            unmatched.append((f, "no property recognised in the filename"))
            continue
        twins = [h for h in hotels
                 if normalise(h["name"]) == normalise(best["name"])]
        if len(twins) > 1 and not (tokens(f) & set().union(
                *(tokens(t["area"]) for t in twins))):
            names = " or ".join(t["area"] for t in twins)
            unmatched.append((f, f'"{best["name"]}" exists in more than one place - '
                                 f'add the city to the filename ({names})'))
            continue
        if second_score and best_score - second_score < 0.08:
            unmatched.append((f, "ambiguous - could be more than one property"))
            continue

        rel = os.path.relpath(src, STAGING)
        dims = dimensions(src)
        w, h = dims if dims else (0, 0)

        if dims and w < THUMBNAIL_WIDTH:
            unmatched.append((rel, f"only {w}px wide - this is a thumbnail, not usable"))
            continue

        candidates.append({"rel": rel, "src": src, "hotel": best,
                           "explicit": explicit_n, "w": w, "h": h})

    # Largest image becomes the hero unless the filename said otherwise.
    by_hotel = {}
    for c in candidates:
        by_hotel.setdefault(c["hotel"]["slug"], []).append(c)

    for slug, group in by_hotel.items():
        group.sort(key=lambda c: -c["w"])
        taken = {c["explicit"] for c in group if c["explicit"]}
        nxt = (n for n in (1, 2, 3) if n not in taken)
        for c in group:
            c["n"] = c["explicit"] or next(nxt, None)
        for c in sorted(group, key=lambda c: (c["n"] is None, c["n"] or 0)):
            if c["n"] is None:
                unmatched.append((c["rel"], "only three images per property - "
                                            "this one was not among the largest three"))
                continue
            warns = []
            if c["w"] and c["w"] < MIN_WIDTH:
                warns.append(f"only {c['w']}px wide, wanted {MIN_WIDTH}+")
            if c["h"] > c["w"] > 0:
                warns.append("portrait - will crop badly in the hero")
            plan.append((c["rel"], c["src"], c["hotel"], c["n"],
                         target_name(c["hotel"], c["n"]), warns))

    if unmatched:
        print("  COULD NOT PLACE THESE - rename them with the hotel name and rerun:\n")
        for f, why in unmatched:
            print(f"      {f}\n        {why}")
        print()

    if not plan:
        sys.exit("  Nothing to file.\n")

    print("  PLANNED:\n")
    for f, _, h, n, tgt, warns in plan:
        label = h["name"] if n == 1 else f"{h['name']}  (image {n})"
        print(f"      {f}")
        print(f"        -> {label}")
        print(f"        -> {tgt}")
        for w in warns:
            print(f"        !! {w}")
        print()

    if not auto:
        if input("  File these? [y/N] ").strip().lower() not in ("y", "yes"):
            sys.exit("  Nothing done.")

    filed = 0
    for f, src, h, n, tgt, _ in plan:
        dst = os.path.join(IMAGES, tgt)
        if src.lower().endswith((".png", ".heic")):
            r = sips(src, "-s", "format", "jpeg", "--out", dst)
            if not r or r.returncode != 0:
                print(f"      could not convert {f} - skipped")
                continue
        else:
            shutil.copy2(src, dst)
        if n == 1:
            h["image"] = f"/images/{tgt}"
        filed += 1

    json.dump(data, open(DATA, "w"), indent=2, ensure_ascii=False)

    print(f"\n  Filed {filed} image(s) into images/ and updated hotels.json.")
    print("  Your originals in the staging folder are untouched.\n")
    print("  Check what changed, then commit:\n")
    print("      git status")
    print('      git add -A && git commit -m "Add hotel photography" && git push\n')


if __name__ == "__main__":
    main()

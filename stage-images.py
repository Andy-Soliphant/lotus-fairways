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
   OR, if OneDrive is installed on this Mac, skip all copying and read it
   directly - nothing is downloaded, zipped or moved:

       python3 stage-images.py --from "/Users/you/Library/CloudStorage/OneDrive-Personal/.../Hotels/Cambodia"

   (Drag the folder from Finder onto the Terminal window to get its path.)

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
  - Everything is resampled to 2400px wide and re-encoded as JPEG. Media-pack
    originals are often 5-15MB each; a web hero needs a fraction of that, and
    a git repo really does not want the difference.
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
TINY_BYTES = 60_000     # below this it is a thumbnail; judged without opening the file
# Subfolders that reliably hold the WRONG kind of picture for a hotel hero.
# Their images are still usable, but only after everything in the main folder.
BACK_OF_HOUSE = ("spa", "wellness", "gym", "fitness", "travel craft", "travel",
                 "meeting", "wedding", "yoga", "map", "thumb")
MAX_WIDTH = 2000        # anything wider is resampled DOWN. Never up.
JPEG_QUALITY = 76
MIN_SCORE = 0.5         # at least half the hotel's own name must appear
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


def place_names(hotels):
    out = set()
    for h in hotels:
        out.add(normalise(h["area"].replace("-", " ")))
        out.add(normalise(h["destination"].replace("-", " ")))
    out |= {"north", "central", "south", "east", "west", "hotels", "images", "asia"}
    return out


# ── FOLDER OVERRIDES ────────────────────────────────────────────────────────
# The scorer strips a property's AREA out of its name so a folder called
# "Emeralda Ninh Binh" cannot match Amanoi on the word "Ninh". That rule breaks
# for hotels whose distinguishing words ARE their area: strip "golden" and
# "triangle" from "Anantara Golden Triangle Elephant Camp & Resort" and only
# "anantara" is left, which loses to every other Anantara. Rather than loosen
# the scorer and risk silent misfiling elsewhere, name the exceptions here.
# Key = folder name as it appears in OneDrive. Value = slug in hotels.json.
FOLDER_OVERRIDES = {
    "anantara golden triangle chiang rai": "anantara-golden-triangle",
    "four seasons tented camp golden triangle": "fs-tented-camp-golden-triangle",
    "the legend bouqitue": "the-legend-chiang-rai",          # folder is misspelt in OneDrive
    "the legend boutique": "the-legend-chiang-rai",
    # Strip the area and "Rosewood Luang Prabang" reduces to "rosewood",
    # which ties with Rosewood Bangkok and Rosewood Phnom Penh.
    "rosewood luang prabang": "rosewood-luang-prabang",
}


def folder_override(src, hotels):
    """Return (hotel, folder_that_matched) for an explicitly assigned path.

    The folder name matters: images inside "Rosewood Luang Prabang/Spa and
    Wellness" must be credited to the Rosewood FOLDER, not to "Spa and
    Wellness", or the two-folders-one-property guard below sees a conflict
    and skips the property.
    """
    by_slug = {h["slug"]: h for h in hotels}
    for part in os.path.normpath(src).split(os.sep):
        slug = FOLDER_OVERRIDES.get(normalise(part).strip())
        if slug and slug in by_slug:
            return by_slug[slug], part
    return None, ""


# ── IMAGE PINS ──────────────────────────────────────────────────────────────
# Normally the three largest files win. File size is a poor proxy for a good
# hero: at Rosewood Luang Prabang the biggest file was a PORTRAIT, which crops
# to a strip in a full-bleed hero band. Where a property is pinned, these exact
# files are used in this exact order and size is ignored. Filename only, no path.
IMAGE_PINS = {
    "rosewood-luang-prabang": [
        "the-great-house-008_WIDE-LARGE-16-9.jpg",
        "hilltop-tent-007_WIDE-LARGE-16-9.jpg",
        "waterfall-pool-villa-bedroom-001_WIDE-LARGE-16-9.jpg",
    ],
}


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
        # The hotel's OWN name is what qualifies a match. The area may only
        # break a tie - never make one. Without this, a folder called
        # "Emeralda Ninh Binh" matches Amanoi purely on the word "Ninh".
        # Strip the area out of BOTH name and slug: "Royal Sands Koh Rong" must
        # not be matchable by a folder called "Koh Rong Map".
        named = (tokens(h["name"]) | tokens(h["slug"])) - tokens(h["area"])
        if not named:
            named = tokens(h["name"]) | tokens(h["slug"])
        if not named:
            continue
        hits = want & named
        if not hits:
            continue
        # Score on how much of the HOTEL's own name is present, not on overlap
        # with the whole folder name - folders carry extra words ("Siem Reap",
        # "Hotel", "Resort") that should not dilute a confident match.
        score = len(hits) / len(named)
        if want & tokens(h["area"]):
            score += 0.02
        if score < MIN_SCORE:
            continue
        scored.append((score, h))

    scored.sort(key=lambda x: -x[0])
    best = scored[0] if scored else (0, None)
    second = scored[1] if len(scored) > 1 else (0, None)
    return best, second, n


def reprocess():
    """Re-compress the hotel images already in images/. Shrink only."""
    import glob
    files = sorted(glob.glob(os.path.join(IMAGES, "hotel-*.jpg")))
    if not files:
        sys.exit("No hotel images found in images/")
    print(f"\n  Re-optimising {len(files)} image(s). Shrink only, never enlarge.\n")
    before_total = after_total = 0
    for f in files:
        before = os.path.getsize(f)
        dims = dimensions(f)
        w = dims[0] if dims else 0
        tmp = f + ".tmp.jpg"
        args = ["-s", "format", "jpeg", "-s", "formatOptions", str(JPEG_QUALITY)]
        if w > MAX_WIDTH:
            args = ["-Z", str(MAX_WIDTH)] + args
        r = sips(f, *args, "--out", tmp)
        if not r or r.returncode != 0:
            try:
                from PIL import Image
                with Image.open(f) as im:
                    im = im.convert("RGB")
                    if im.width > MAX_WIDTH:
                        im = im.resize((MAX_WIDTH,
                                        round(im.height * MAX_WIDTH / im.width)),
                                       Image.LANCZOS)
                    im.save(tmp, "JPEG", quality=JPEG_QUALITY, optimize=True)
            except Exception as e:
                print(f"      skipped {os.path.basename(f)} ({e})")
                continue
        after = os.path.getsize(tmp)
        if after < before:
            os.replace(tmp, f)
        else:
            os.remove(tmp)
            after = before
        before_total += before
        after_total += after
    mb = (before_total - after_total) / 1_048_576
    print(f"  Done. {before_total/1_048_576:.0f}MB -> {after_total/1_048_576:.0f}MB "
          f"({mb:.0f}MB saved).\n")
    print("  Check a few look fine, then commit:\n")
    print('      git add -A && git commit -m "Optimise hotel images for the web" && git push\n')


def main():
    global STAGING
    if "--reprocess" in sys.argv:
        return reprocess()
    auto = "--yes" in sys.argv

    # --from lets you read straight out of the OneDrive folder on this Mac,
    # so nothing has to be downloaded, zipped or copied first.
    src_arg = None
    for i, a in enumerate(sys.argv):
        if a == "--from":
            if i + 1 >= len(sys.argv):
                sys.exit("--from needs a folder after it. Tip: drag the folder "
                         "from Finder onto the Terminal window.")
            src_arg = sys.argv[i + 1]
            break
        if a.startswith("--from"):          # --from=/path or --from/path, no space
            src_arg = a[len("--from"):].lstrip("=")
            if src_arg:
                break
            src_arg = None
    if src_arg:
        STAGING = os.path.expanduser(src_arg.rstrip("/"))
        if not os.path.isdir(STAGING):
            sys.exit(f"No folder at:\n  {STAGING}")
        print(f"\n  Reading from: {STAGING}")

    for path, what in ((IMAGES, "images folder"), (DATA, "data/hotels.json")):
        if not os.path.exists(path):
            sys.exit(f"Cannot find the {what}. Run this from the repo root:\n"
                     f"  cd ~/Documents/GitHub/lotus-fairways-live && python3 stage-images.py")

    if not os.path.isdir(STAGING):
        os.makedirs(STAGING, exist_ok=True)
        sys.exit(f"Created a staging folder for you:\n  {STAGING}\n\n"
                 "Copy images in there, or point at OneDrive directly with:\n"
                 "  python3 stage-images.py --from <folder>")

    zips = [z for z in os.listdir(STAGING) if z.lower().endswith(".zip")]
    if zips:
        print("\n  Zip files in the staging folder - double-click them in Finder "
              "to unpack, then delete the zip:")
        for z in zips:
            print(f"      {z}")

    data = json.load(open(DATA))
    hotels = data["hotels"]

    country = None
    here = normalise(os.path.basename(STAGING))
    for h in data["hotels"]:
        if normalise(h["destination"]) == here:
            country = h["destination"]
            break
    if country:
        hotels = [h for h in data["hotels"] if h["destination"] == country]
        print(f"  Only matching {country.title()} properties "
              f"({len(hotels)} in hotels.json).")
    places = place_names(data["hotels"])

    files = []
    for root, dirs, names in os.walk(STAGING):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for nm in sorted(names):
            if nm.lower().endswith((".jpg", ".jpeg", ".png", ".heic")) \
                    and not nm.startswith("."):
                files.append(os.path.join(root, nm))
    if not files:
        sys.exit(f"No images found in {STAGING}")

    print(f"\n  {len(files)} image(s) found.")
    print("  Matching them up - this part is quick.\n")

    plan, unmatched, candidates = [], [], []
    checked = 0
    for src in files:
        checked += 1
        if checked % 25 == 0 or checked == len(files):
            print(f"      {checked} of {len(files)}...", flush=True)
        f = os.path.basename(src)
        matched_on = ""
        forced, forced_folder = folder_override(src, hotels)
        if forced:
            best, best_score, second_score = forced, 1.0, 0.0
            matched_on = forced_folder
            explicit_n = 0
            m = re.search(r"[-_ ]([23])$", os.path.splitext(f)[0].strip())
            if m:
                explicit_n = int(m.group(1))
        else:
          try:
                (best_score, best), (second_score, _), explicit_n = match(f, hotels)
          except Exception as e:
            unmatched.append((os.path.relpath(src, STAGING), f"could not read this one ({e})"))
            continue

        if not best:
            # fall back to the folder name, nearest parent first
            rel = os.path.relpath(os.path.dirname(src), STAGING)
            parts = [] if rel == "." else rel.split(os.sep)
            matched_on = ""
            for parent in reversed(parts):
                if normalise(parent) in places:      # a region, not a property
                    continue
                (bs, b), (ss, _), _ = match(parent, hotels)
                if b:
                    best, best_score, second_score = b, bs, ss
                    matched_on = parent
                    break
        if not best:
            unmatched.append((os.path.relpath(src, STAGING),
                              "not a property in hotels.json"))
            continue
        twins = [h for h in hotels
                 if normalise(h["name"]) == normalise(best["name"])]
        if len(twins) > 1 and not (tokens(f) & set().union(
                *(tokens(t["area"]) for t in twins))):
            names = " or ".join(t["area"] for t in twins)
            unmatched.append((os.path.relpath(src, STAGING),
                              f'"{best["name"]}" exists in more than one place - '
                              f'say which ({names})'))
            continue
        if not forced and second_score and best_score - second_score < 0.08:
            unmatched.append((os.path.relpath(src, STAGING),
                              "ambiguous - could be more than one property"))
            continue

        rel = os.path.relpath(src, STAGING)
        # os.path.getsize works on a OneDrive placeholder WITHOUT downloading it.
        # Reading pixel dimensions does not - so that is deferred until we know
        # which three images per property we actually want.
        try:
            nbytes = os.path.getsize(src)
        except OSError:
            nbytes = 0
        if nbytes and nbytes < TINY_BYTES:
            unmatched.append((rel, "too small to be a usable photograph"))
            continue

        sub = normalise(os.path.basename(os.path.dirname(rel)))
        back = any(w in sub for w in BACK_OF_HOUSE) and sub != normalise(matched_on)
        candidates.append({"rel": rel, "src": src, "hotel": best,
                           "explicit": explicit_n, "bytes": nbytes, "w": 0, "h": 0,
                           "back": back, "folder": matched_on})

    # Largest image becomes the hero unless the filename said otherwise.
    by_hotel = {}
    for c in candidates:
        by_hotel.setdefault(c["hotel"]["slug"], []).append(c)

    for slug, group in by_hotel.items():
        folders = sorted({c["folder"] for c in group if c["folder"]})
        if len(folders) > 1:
            print(f"  !! {len(folders)} different folders both look like "
                  f"\"{group[0]['hotel']['name']}\":")
            for fo in folders:
                print(f"       {fo}")
            print("     These are probably different properties. Skipped - tell "
                  "Claude which one is the right one.\n")
            continue
        # Main-folder pictures first; spa, gym and thumbnail folders only if
        # there is nothing better. Size decides within each band.
        pinned = IMAGE_PINS.get(slug)
        if pinned:
            order = {nm: i for i, nm in enumerate(pinned)}
            keep = [c for c in group if os.path.basename(c["rel"]) in order]
            missing = [nm for nm in pinned
                       if nm not in {os.path.basename(c["rel"]) for c in keep}]
            for nm in missing:
                print(f"  !! pinned file not found for {slug}: {nm}")
            for c in group:
                if c not in keep:
                    unmatched.append((c["rel"], "not one of the pinned three"))
            keep.sort(key=lambda c: order[os.path.basename(c["rel"])])
            for i, c in enumerate(keep, 1):
                c["explicit"] = i
            group = keep
        group.sort(key=lambda c: (c["back"], -c["bytes"]))
        seen = set()
        for c in group:                      # group is already largest-first
            if c["explicit"] and c["explicit"] in seen:
                c["explicit"] = 0
            elif c["explicit"]:
                seen.add(c["explicit"])
        taken = seen
        nxt = (n for n in (1, 2, 3) if n not in taken)
        for c in group:
            c["n"] = c["explicit"] or next(nxt, None)
        for c in sorted(group, key=lambda c: (c["n"] is None, c["n"] or 0)):
            if c["n"] is None:
                unmatched.append((c["rel"], "only three images per property - "
                                            "this one was not among the largest three"))
                continue
            dims = dimensions(c["src"])          # only the chosen few get read
            c["w"], c["h"] = dims if dims else (0, 0)
            if c["w"] and c["w"] < THUMBNAIL_WIDTH:
                unmatched.append((c["rel"],
                                  f"only {c['w']}px wide - a thumbnail, not usable"))
                continue
            warns = []
            if c["w"] and c["w"] < MIN_WIDTH:
                warns.append(f"only {c['w']}px wide, wanted {MIN_WIDTH}+")
            if c["h"] > c["w"] > 0:
                warns.append("portrait - will crop badly in the hero")
            plan.append((c["rel"], c["src"], c["hotel"], c["n"],
                         target_name(c["hotel"], c["n"]), warns))

    if unmatched:
        byfolder = {}
        for f, why in unmatched:
            key = (os.path.dirname(f) or "(loose files)", why)
            byfolder.setdefault(key, []).append(f)
        print("  NOT FILED:\n")
        for (folder, why), fs in sorted(byfolder.items()):
            n = len(fs)
            print(f"      {folder}   ({n} image{'s' if n != 1 else ''})")
            print(f"        {why}")
        print("\n  Properties above that are not in hotels.json are expected - "
              "your library is larger than the site. Tell Claude if any should "
              "be added.\n")

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

    filed, saved = 0, 0
    widths = {c["rel"]: c["w"] for c in candidates}
    for f, src, h, n, tgt, _ in plan:
        dst = os.path.join(IMAGES, tgt)
        before = os.path.getsize(src)
        c_width = widths.get(f, 0)

        # Originals from a media pack are often 5-15MB. A web hero needs
        # nothing like that, and a git repo really does not want it.
        # NEVER upscale: sips -Z resizes in BOTH directions, so a 1280px source
        # would be blown up to 2400px - a bigger file with no extra detail.
        args = ["-s", "format", "jpeg", "-s", "formatOptions", str(JPEG_QUALITY)]
        if c_width and c_width > MAX_WIDTH:
            args = ["-Z", str(MAX_WIDTH)] + args
        r = sips(src, *args, "--out", dst)
        if not r or r.returncode != 0:
            try:                                    # fallback if sips is absent
                from PIL import Image
                with Image.open(src) as im:
                    im = im.convert("RGB")
                    if im.width > MAX_WIDTH:      # shrink only, never enlarge
                        im = im.resize((MAX_WIDTH,
                                        round(im.height * MAX_WIDTH / im.width)),
                                       Image.LANCZOS)
                    im.save(dst, "JPEG", quality=JPEG_QUALITY, optimize=True)
            except Exception as e:
                print(f"      could not process {f} ({e}) - skipped")
                continue

        saved += before - os.path.getsize(dst)
        if n == 1:
            h["image"] = f"/images/{tgt}"
        filed += 1

    json.dump(data, open(DATA, "w"), indent=2, ensure_ascii=False)

    mb = saved / 1_048_576
    print(f"\n  Filed {filed} image(s) into images/ and updated hotels.json.")
    print("  Nothing in the source folder was changed.")
    if mb > 1:
        print(f"  Resized for the web - {mb:.0f}MB smaller than the originals.")

    print("  Check what changed, then commit:\n")
    print("      git status")
    print('      git add -A && git commit -m "Add hotel photography" && git push\n')


if __name__ == "__main__":
    main()

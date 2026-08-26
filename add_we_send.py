#!/usr/bin/env python3
"""
add_we_send.py — one-shot patch. Adds a `we_send` field to data/hotels.json.

`we_send` answers one question on the hotel page: who do we send here.
It is a PLACEMENT judgement, not a description — the thing a booking site
cannot write. Drafted by Claude from each record's own character/prose/verdict,
for Andy to correct. Voice set by Andy 26 Aug 2026, and six lines rewritten by him the same day:
"travellers who want the place to be the point, and understand the destination
is worth the journey."

Also corrects Shinta Mani Wild's prose: the old line claimed "there is no road
in", which is untrue — the zipline is the intended arrival, not the only one.
"""
import json, os, sys

WE_SEND = {
    # ── Cambodia ──────────────────────────────────────────────────
    "shinta-mani-wild": "Travellers who want the place to be the point, and understand the destination is worth the journey",
    "royal-sands-koh-rong": "Anyone finishing a temples-and-cities trip who wants a beach at the end of it",
    "song-saa": "Couples who want the island to themselves and are not counting the transfer time",
    "palace-gate-phnom-penh": "Guests who want a quiet riverside base in the city rather than a landmark",
    "raffles-le-royal": "Anyone who wants to sleep inside Cambodia's twentieth century, not beside it",
    "rosewood-phnom-penh": "Guests who want the modern city and the best views in it",
    "amansara": "Travellers who have seen Angkor before, or want to see it properly the first time",
    "aviary-siem-reap": "Guests who want an amazing location, fantastically run, at a great price point",
    "heritage-suites-siem-reap": "Anyone who wants character and a pool without the scale of the grand hotels",
    "phum-baitang": "Guests who want to come back from the temples to quiet, and have been told it is out of town",
    "raffles-grand-angkor": "Guests who want the hotel to be part of the story of the place",
    "shinta-mani-angkor": "Travellers who want Bensley's hand at a sensible price, minutes from the temples",
    # ── Thailand ─────────────────────────────────────────────────
    "capella-bangkok": "Guests who want the river, consistency and a room they do not have to choose between",
    "chakrabongse-villas": "For those who want to experience how royal life was lived in Bangkok. This is it.",
    "mandarin-oriental-bangkok": "Anyone for whom the name is part of the point",
    "peninsula-bangkok": "Guests who love the grandeur and the service that goes with it",
    "salil-hotel-riverside": "Travellers who want river views and a modern twist",
    "the-siam-bangkok": "Guests who would rather stay somewhere designed than somewhere large",
    "137-pillars-house": "Anyone who wants Chiang Mai's history in the building they sleep in",
    "rachamankha": "Guests who want to walk to the temples and stay inside the old city",
    "raya-heritage": "Guests who want the river and the craft, and are happy to be out of the old city",
    "cape-nidhra-hua-hin": "Couples who want the seafront and a suite, not a resort",
    "centara-grand-hua-hin": "Guests who want the beach and the city from one location",
    "hyatt-regency-hua-hin": "Families and golf groups who want facilities and the beach in one place",
    "the-sarojin": "Adults who want the beach quiet and mean it",
    "rayavadee": "Travellers who accept that arriving by boat is the whole idea",
    "amanpuri": "Guests who want the original Aman and do not mind the walk between things",
    "keemala": "Guests who want something with a point of view rather than another beach resort",
    "trisara": "Couples who want a private bay and a villa pool, and would rather be north than south",
    # ── Vietnam ──────────────────────────────────────────────────
    "chicland-da-nang": "Guests who want the beach city on a sensible budget",
    "intercontinental-danang": "Guests who want the design and the bay, and are not planning to leave often",
    "namia-riverside-da-nang": "Travellers who want Hoi An within cycling distance and the spa included",
    "capella-hanoi": "Guests who want theatre in the building and the Opera House on the doorstep",
    "la-siesta-premium-hang-be": "Travellers who want the Old Quarter and character over a star rating",
    "la-siesta-classic-hang-than": "Guests who want the same house style at a lower price",
    "la-siesta-ma-may": "Guests who want the Old Quarter address and a smaller house",
    "metropole-hanoi": "Anyone who wants the history of Hanoi under the same roof they sleep in",
    "hotel-des-arts-saigon": "Guests who want design and a rooftop without the Reverie's price",
    "park-hyatt-saigon": "Guests who want the city's best address and nothing shouted",
    "the-reverie-saigon": "Guests who want opulence and know exactly what they are choosing",
    "four-seasons-nam-hai": "Guests who want the beach and the space, and are content to be out of town",
    "amanoi": "Travellers who want somewhere almost nobody they know has been",
    "thai-akara": "Guests who want a small Lanna house in the old city at a sensible price",
    "hyatt-regency-phnom-penh": "Guests who want reliable comfort and a pool in the middle of the city",
}

PROSE_FIX = {
    "shinta-mani-wild": (
        "Tents strung along a river in a stretch of the Cardamoms that was slated for "
        "logging until the camp took on the concession. The arrival is the zipline, "
        "down a wire over the water, and it sets the tone for everything after it. "
        "Rangers patrol from the property and you can go out with them."
    ),
}

ARRIVAL = {
    "shinta-mani-wild": "By zipline, down a wire over the water — the intended way in",
    "rayavadee": "By boat — there is no road to Railay",
    "song-saa": "By speedboat from Sihanoukville",
    "royal-sands-koh-rong": "40–45 minutes by speedboat from Sihanoukville",
    "amanoi": "Flying into Cam Ranh, then up into Nui Chua National Park",
}


def main(path):
    with open(path) as f:
        data = json.load(f)
    hotels = data["hotels"] if isinstance(data, dict) else data

    touched = missing = 0
    for h in hotels:
        s = h["slug"]
        if s in WE_SEND:
            h["we_send"] = WE_SEND[s]
            touched += 1
        if s in PROSE_FIX:
            h["prose"] = PROSE_FIX[s]
        if s in ARRIVAL:
            h["arrival"] = ARRIVAL[s]

    known = {h["slug"] for h in hotels}
    for s in WE_SEND:
        if s not in known:
            print("  !! slug not in hotels.json:", s)
            missing += 1

    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("we_send written to %d records, %d unmatched slugs" % (touched, missing))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/hotels.json")

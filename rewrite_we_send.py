#!/usr/bin/env python3
"""Rewrite the we_send lines to lead with what the guest GETS, not what the
property lacks. Pattern set by Andy's own six rewrites, 26 Aug 2026.
His seven lines are untouched."""
import json, sys

ANDYS = {"shinta-mani-wild","chakrabongse-villas","peninsula-bangkok",
         "salil-hotel-riverside","centara-grand-hua-hin",
         "namia-riverside-da-nang","aviary-siem-reap"}

NEW = {
 # Cambodia
 "royal-sands-koh-rong":"Guests who want a proper island beach at the end of a temples-and-cities trip",
 "song-saa":"Couples who want their own island, and the quiet that comes with it",
 "palace-gate-phnom-penh":"Guests who want a calm riverside base with a pool, in the middle of the city",
 "raffles-le-royal":"Guests who want to sleep inside Cambodia's twentieth century, with the grandeur intact",
 "rosewood-phnom-penh":"Guests who want the modern city and the best views in it",
 "amansara":"Guests who want Angkor at its quietest, from the old royal guesthouse",
 "heritage-suites-siem-reap":"Guests who want colonial villas, a pool and real character, minutes from town",
 "phum-baitang":"Guests who want to finish at the temples and come back to rice paddies and quiet",
 "raffles-grand-angkor":"Guests who want the hotel to be part of the story of the place",
 "shinta-mani-angkor":"Guests who want Bensley's hand and a warm welcome, minutes from the temples",
 "hyatt-regency-phnom-penh":"Guests who want simple luxury done well, and a pool in the middle of the city",
 # Thailand
 "capella-bangkok":"Guests who want the river, and the same high standard whichever room they get",
 "mandarin-oriental-bangkok":"Guests who want a hotel run the way a great hotel should be, on the river since 1876",
 "the-siam-bangkok":"Guests who want to reach the city from the river, the way people used to",
 "137-pillars-house":"Guests who want Chiang Mai's history in the building they sleep in",
 "rachamankha":"Guests who want to walk out of the door into the old city and its temples",
 "raya-heritage":"Guests who want the Ping river and northern craft, with room to breathe",
 "cape-nidhra-hua-hin":"Couples who want a suite, a plunge pool and the sea in front of them",
 "hyatt-regency-hua-hin":"Families and golf groups who want the beach and the facilities in one place",
 "the-sarojin":"Adults who want the beach quiet, and a hotel with a real story behind it",
 "rayavadee":"Guests who want to arrive by boat and wake up among the limestone karsts",
 "amanpuri":"Guests who want the original Aman, and the space and pavilions that come with it",
 "keemala":"Guests who want design above everything, and something they will see nowhere else",
 "trisara":"Couples who want a private bay, a villa pool and a Michelin star on site",
 # Vietnam
 "chicland-da-nang":"Guests who want the beach city, a rooftop and a sensible price",
 "intercontinental-danang":"Guests who want Bensley's design and a private bay to settle into",
 "capella-hanoi":"Guests who want theatre in the building and the Opera House on the doorstep",
 "la-siesta-premium-hang-be":"Travellers who want the Old Quarter, real character and a rooftop bar",
 "la-siesta-classic-hang-thung":"Guests who want the same La Siesta welcome, with a pool and river views",
 "la-siesta-ma-may":"Guests who want the same La Siesta welcome, right in the middle of the Old Quarter",
 "metropole-hanoi":"Guests who want the history of Hanoi under the roof they sleep under",
 "hotel-des-arts-saigon":"Guests who want design, a rooftop pool and the city at their feet",
 "park-hyatt-saigon":"Guests who want the city's best address, done quietly and beautifully",
 "the-reverie-saigon":"Guests who want opulence on a scale few hotels attempt",
 "four-seasons-nam-hai":"Guests who want villas on the sand and the space to spread out",
 "amanoi":"Travellers who want somewhere almost nobody they know has been",
 "thai-akara":"Guests who want a small Lanna house inside the old city walls",
}

def main(path):
    d = json.load(open(path))
    changed = kept = same = 0
    for h in d["hotels"]:
        s = h["slug"]
        if s in ANDYS:
            kept += 1; continue
        if s in NEW:
            if h.get("we_send") == NEW[s]: same += 1
            else: changed += 1
            h["we_send"] = NEW[s]
    json.dump(d, open(path, "w"), indent=2, ensure_ascii=False); open(path,"a").write("\n")
    print("rewritten %d | already fitted %d | Andy's kept %d" % (changed, same, kept))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/hotels.json")

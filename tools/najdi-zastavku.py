#!/usr/bin/env python3
"""Najde ASW ID zastávky PID podle jména — to potřebuje Golemio API.

    python3 tools/najdi-zastavku.py "Národní třída"
    python3 tools/najdi-zastavku.py Zličín --linka 22

Golemio odjezdové tabule se ptají kódem ASW (`aswIds`), ne jménem. Kód se
skládá jako `node_platform`, například `539_1` je Národní třída, stanoviště 1.
Veřejný seznam zastávek na data.pid.cz má obojí, ale má 18 MB — proto se
překlad dělá tady na počítači a do tabule se vloží hotový kód.

Bez argumentu `--vse` vypíše jen zastávky, kde jméno odpovídá; s ním všechny
nalezené shody včetně částečných.
"""
import argparse
import json
import os
import sys
import unicodedata
import urllib.request

URL = "https://data.pid.cz/stops/json/stops.json"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".stops-cache.json")


def fold(s):
    """Bez diakritiky a malými — ať „Nádraží Podbaba“ najde i „nadrazi podbaba“."""
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()


def load(refresh=False):
    if not refresh and os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)

    print("Stahuji seznam zastávek z data.pid.cz (~18 MB, jednorázově)…",
          file=sys.stderr)
    with urllib.request.urlopen(URL, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))

    # ukládáme jen to, co potřebujeme — z 18 MB zbyde pár set kB
    slim = []
    for g in data.get("stopGroups", []):
        stops = []
        for s in g.get("stops", []):
            sid = str(s.get("id", ""))
            node, _, platform = sid.partition("/")
            stops.append({
                "asw": (node + "_" + platform) if platform else node,
                "platform": s.get("platform") or "",
                "zone": s.get("zone") or "",
                "lines": sorted({str(l.get("name")) for l in s.get("lines", []) if l.get("name")},
                                key=lambda x: (len(x), x)),
            })
        slim.append({
            "name": g.get("name") or "",
            "municipality": g.get("municipality") or "",
            "district": g.get("districtCode") or "",
            "stops": stops,
        })

    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump({"generatedAt": data.get("generatedAt"), "groups": slim},
                  f, ensure_ascii=False)
    return {"generatedAt": data.get("generatedAt"), "groups": slim}


def main():
    ap = argparse.ArgumentParser(description="Najde ASW ID zastávky PID podle jména.")
    ap.add_argument("jmeno", help="název zastávky nebo jeho část")
    ap.add_argument("--linka", help="ukázat jen zastávky, kde jede tato linka")
    ap.add_argument("--vse", action="store_true", help="vypsat i částečné shody")
    ap.add_argument("--obnovit", action="store_true", help="stáhnout seznam znovu")
    a = ap.parse_args()

    data = load(a.obnovit)
    q = fold(a.jmeno)

    presne = [g for g in data["groups"] if fold(g["name"]) == q]
    castecne = [g for g in data["groups"] if q in fold(g["name"]) and fold(g["name"]) != q]
    hits = presne + (castecne if (a.vse or not presne) else [])

    if a.linka:
        want = fold(a.linka)
        hits = [g for g in hits
                if any(any(fold(l) == want for l in s["lines"]) for s in g["stops"])]

    if not hits:
        print("Nic nenalezeno. Zkus část jména, nebo --vse.", file=sys.stderr)
        sys.exit(1)

    print("Seznam zastávek vygenerován: %s\n" % (data.get("generatedAt") or "?"))

    for g in hits[:15]:
        kde = ", ".join(x for x in [g["municipality"], g["district"]] if x)
        print("%s  (%s)" % (g["name"], kde))
        for s in g["stops"]:
            if a.linka and not any(fold(l) == fold(a.linka) for l in s["lines"]):
                continue
            linky = ", ".join(s["lines"][:14]) or "—"
            print("   aswIds=%-10s stanoviště %-3s pásmo %-3s linky: %s"
                  % (s["asw"], s["platform"] or "-", s["zone"] or "-", linky))
        print()

    if len(hits) > 15:
        print("… a další (%d celkem). Zpřesni jméno." % len(hits))

    print("Kód za `aswIds=` vlož do CONFIG.PID v Apps Scriptu.")
    print("Víc stanovišť odděl čárkou, například 539_1,539_2")


if __name__ == "__main__":
    main()

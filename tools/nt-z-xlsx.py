#!/usr/bin/env python3
"""Z exportu časů spínání NT od distributora udělá text pro tabuli.

    python3 tools/nt-z-xlsx.py ~/Downloads/Časy_spínání_NT.xlsx

Distributoři (ČEZ, EG.D, PRE) umí vyexportovat časy spínání nízkého tarifu
jako xlsx: řádek na den, sloupce po párech „NT Za“ a „NT Vy“. Tenhle skript
z toho udělá kompaktní text, který se vloží do tabule v Nastavení:

    # a1b2dp01
    Po-Pá: 02:00-06:00, 12:30-14:30, 22:00-24:00
    So-Ne: 00:00-08:00, 13:00-17:00

Dny se stejnými časy se slučují do rozsahů, ať je výsledek krátký a dá se
zkontrolovat okem. Čte se bez openpyxl — xlsx je zip s XML, takže to jde
bez instalace čehokoli.

Výstup obsahuje tvoje časy spínání, tedy nepatří do repozitáře. Ulož si ho
mimo projekt, nebo ho hned vlož do tabule.
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
DNY = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
KRATKE = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]


def cell_text(c, shared):
    t = c.get("t")
    v = c.find(NS + "v")
    inline = c.find(NS + "is")
    if t == "s" and v is not None:
        return shared[int(v.text)]
    if t == "inlineStr" and inline is not None:
        return "".join(x.text or "" for x in inline.iter(NS + "t"))
    return v.text if v is not None else ""


def read_rows(path):
    z = zipfile.ZipFile(path)

    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si"):
            shared.append("".join(t.text or "" for t in si.iter(NS + "t")))

    sheets = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet")]
    if not sheets:
        sys.exit("V souboru není žádný list.")

    rows = []
    for row in ET.fromstring(z.read(sorted(sheets)[0])).iter(NS + "row"):
        cells = {}
        for c in row.iter(NS + "c"):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            cells[col] = (cell_text(c, shared) or "").strip()
        rows.append(cells)
    return rows


def col_order(cells):
    """Sloupce zleva doprava — páry Za/Vy jdou v tomhle pořadí."""
    def key(c):
        n = 0
        for ch in c:
            n = n * 26 + (ord(ch) - 64)
        return n
    return sorted(cells.keys(), key=key)


def parse(rows):
    """Vrátí {povel: {index dne: [(od, do), …]}} v minutách od půlnoci."""
    out = {}
    for cells in rows:
        povel = cells.get("A", "")
        den = cells.get("C", "")
        if not povel or den not in DNY:
            continue

        # sloupce s časy jsou všechny kromě A (povel), B (upřesnění), C (den)
        times = [cells[c] for c in col_order(cells)
                 if c not in ("A", "B", "C") and re.match(r"^\d{1,2}:\d{2}$", cells[c] or "")]

        okna = []
        for i in range(0, len(times) - 1, 2):
            od, do = to_min(times[i]), to_min(times[i + 1])
            if do > od:
                okna.append((od, do))

        out.setdefault(povel, {})[DNY.index(den)] = okna
    return out


def to_min(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def fmt(m):
    return "%02d:%02d" % (m // 60, m % 60) if m < 1440 else "24:00"


def sluc_dny(dny):
    """Dny se stejnými časy do rozsahů: [0,1,2,3,4] → 'Po-Pá'."""
    if not dny:
        return ""
    parts, start, prev = [], dny[0], dny[0]
    for d in dny[1:] + [None]:
        if d is not None and d == prev + 1:
            prev = d
            continue
        if start == prev:
            parts.append(KRATKE[start])
        elif prev == start + 1:
            parts.append(KRATKE[start] + "," + KRATKE[prev])
        else:
            parts.append(KRATKE[start] + "-" + KRATKE[prev])
        if d is not None:
            start = prev = d
    return ",".join(parts)


def main():
    ap = argparse.ArgumentParser(description="Z xlsx s časy spínání NT udělá text pro tabuli.")
    ap.add_argument("soubor")
    ap.add_argument("--povel", help="jen tenhle povel")
    a = ap.parse_args()

    data = parse(read_rows(a.soubor))
    if not data:
        sys.exit("Nenašel jsem žádné časy. Čekám sloupec A = povel, C = den, "
                 "dál páry časů ve tvaru HH:MM.")

    bloky = []
    for povel in sorted(data):
        if a.povel and povel != a.povel:
            continue

        # dny se stejným rozvrhem k sobě
        podle_casu = {}
        for den, okna in sorted(data[povel].items()):
            klic = tuple(okna)
            podle_casu.setdefault(klic, []).append(den)

        radky = ["# " + povel]
        for okna, dny in sorted(podle_casu.items(), key=lambda x: min(x[1])):
            if not okna:
                radky.append("%s: —" % sluc_dny(sorted(dny)))
                continue
            radky.append("%s: %s" % (
                sluc_dny(sorted(dny)),
                ", ".join("%s-%s" % (fmt(o), fmt(d)) for o, d in okna)
            ))
        bloky.append("\n".join(radky))

    text = "\n\n".join(bloky)
    print(text)

    hodin = {}
    for povel in data:
        celkem = sum(sum(d - o for o, d in okna) for okna in data[povel].values())
        hodin[povel] = celkem / 60.0
    print("\n— kontrola: NT za týden —", file=sys.stderr)
    for p in sorted(hodin):
        print("  %-12s %5.1f h  (%.1f h/den)" % (p, hodin[p], hodin[p] / 7), file=sys.stderr)
    print("\nVlož do tabule: záložka Tarif → Upravit", file=sys.stderr)


if __name__ == "__main__":
    main()

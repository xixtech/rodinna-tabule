#!/usr/bin/env python3
"""Vygeneruje .ics kalendář svozu odpadů z datového souboru obce.

    python3 tools/gen-svoz.py tools/svoz-data-moje-obec-2026.json svozy-2026.ics

Termíny se opisují z obecního harmonogramu (obvykle PDF) ručně, proto si je
skript sám kontroluje — každé datum musí padnout na deklarovaný den v týdnu
a volitelně na sudý ISO týden nebo do týdenní řady bez mezer. Když kontrola
selže, skript spadne. To je záměr: lepší chyba při generování než tichý špatný
termín na tabuli.

Formát datového souboru — vlastní obec si popíšeš takhle:

    {
      "year": 2026,
      "calname": "Svoz odpadu 2026",
      "source": "https://www.moje-obec.cz - harmonogram 2026",
      "alarmHoursBefore": 6,
      "streams": [
        {
          "key": "bio",
          "label": "\U0001F33F Bioodpad",
          "note": "hnědá popelnice",
          "weekday": 0,
          "dates": ["2026-01-26", "2026-02-23"]
        }
      ],
      "checks": {
        "evenIsoWeek": ["smesny"],
        "weeklySeason": { "bio": ["2026-04-06", "2026-11-30"] }
      }
    }

`weekday` je 0 = pondělí až 6 = neděle. `evenIsoWeek` vyžaduje sudý ISO týden,
`weeklySeason` hlídá, že v daném rozmezí jdou termíny přesně po 7 dnech.

Datový soubor obsahuje harmonogram konkrétní obce, což prozrazuje bydliště —
proto ho .gitignore drží mimo repozitář.
"""
import datetime as dt
import json
import sys

DNY = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]


def die(msg, details=()):
    print(msg, file=sys.stderr)
    for d in details:
        print("  -", d, file=sys.stderr)
    sys.exit(1)


def parse_date(s, where):
    try:
        return dt.date.fromisoformat(s)
    except (ValueError, TypeError):
        die("Nečitelné datum %r v %s (čekán formát 2026-01-26)." % (s, where))


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        die("Datový soubor %s neexistuje. Popis formátu je v hlavičce skriptu." % path)
    except json.JSONDecodeError as e:
        die("Datový soubor %s není platný JSON: %s" % (path, e))


def validate(data):
    """Vrátí seznam chyb. Prázdný seznam = data jsou v pořádku."""
    errors = []
    year = data.get("year")
    streams = data.get("streams") or []
    if not streams:
        errors.append("streams je prázdné – není co generovat")

    by_key = {}
    for s in streams:
        key = s.get("key") or "?"
        by_key[key] = s

        if not isinstance(s.get("weekday"), int) or not 0 <= s["weekday"] <= 6:
            errors.append("%s: weekday musí být 0-6 (0 = pondělí)" % key)
            continue

        dates = [parse_date(x, "streams/" + key) for x in s.get("dates", [])]
        s["_dates"] = dates

        if not dates:
            errors.append("%s: prázdný seznam dates" % key)
        if len(set(dates)) != len(dates):
            errors.append("%s: duplicitní datum" % key)

        for d in dates:
            if year and d.year != year:
                errors.append("%s: %s není v roce %s" % (key, d, year))
            if d.weekday() != s["weekday"]:
                errors.append("%s: %s je %s, čekáno %s"
                              % (key, d, DNY[d.weekday()], DNY[s["weekday"]]))

    checks = data.get("checks") or {}

    for key in checks.get("evenIsoWeek", []):
        s = by_key.get(key)
        if not s:
            errors.append("checks.evenIsoWeek odkazuje na neznámý stream %r" % key)
            continue
        for d in s.get("_dates", []):
            wk = d.isocalendar()[1]
            if wk % 2 != 0:
                errors.append("%s: %s je ISO týden %d (nesudý)" % (key, d, wk))

    for key, span in (checks.get("weeklySeason") or {}).items():
        s = by_key.get(key)
        if not s:
            errors.append("checks.weeklySeason odkazuje na neznámý stream %r" % key)
            continue
        a = parse_date(span[0], "checks/weeklySeason/" + key)
        b = parse_date(span[1], "checks/weeklySeason/" + key)
        season = [d for d in s.get("_dates", []) if a <= d <= b]
        if not season:
            errors.append("%s: v sezóně %s-%s není žádný termín" % (key, a, b))
        for x, y in zip(season, season[1:]):
            if (y - x).days != 7:
                errors.append("%s: mezera %d dní mezi %s a %s" % (key, (y - x).days, x, y))

    return errors


def fold(line):
    """RFC 5545: řádek max 75 oktetů, pokračování začíná mezerou."""
    if len(line.encode("utf-8")) <= 74:
        return line
    out, cur = [], b""
    for ch in line:
        raw = ch.encode("utf-8")
        if len(cur) + len(raw) > 73:
            out.append(cur.decode("utf-8"))
            cur = b""
        cur += raw
    out.append(cur.decode("utf-8"))
    return "\r\n ".join(out)


def esc(s):
    return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")


def build_ics(data):
    alarm = int(data.get("alarmHoursBefore", 6))
    uid_domain = data.get("uidDomain") or "rodinna-tabule.local"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//rodinna-tabule//svoz-odpadu//CS",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:" + esc(data.get("calname", "Svoz odpadu")),
        "X-WR-TIMEZONE:Europe/Prague",
    ]
    stamp = "%04d0101T000000Z" % int(data.get("year") or 2026)
    count = 0

    for s in data["streams"]:
        for d in s["_dates"]:
            nxt = d + dt.timedelta(days=1)
            lines += [
                "BEGIN:VEVENT",
                "UID:svoz-%s-%s@%s" % (s["key"], d.strftime("%Y%m%d"), uid_domain),
                "DTSTAMP:" + stamp,
                "DTSTART;VALUE=DATE:" + d.strftime("%Y%m%d"),
                "DTEND;VALUE=DATE:" + nxt.strftime("%Y%m%d"),
                "SUMMARY:" + esc(s["label"]),
                "DESCRIPTION:" + esc(s.get("note", "")),
                "CATEGORIES:Svoz odpadu",
                "TRANSP:TRANSPARENT",
                "BEGIN:VALARM",
                "TRIGGER:-PT%dH" % alarm,
                "ACTION:DISPLAY",
                "DESCRIPTION:" + esc(s["label"]) + " – vyndat popelnici",
                "END:VALARM",
                "END:VEVENT",
            ]
            count += 1

    lines.append("END:VCALENDAR")
    out = "\r\n".join(fold(l) for l in lines) + "\r\n"

    for i, l in enumerate(out.split("\r\n")):
        if len(l.encode("utf-8")) > 75:
            die("Řádek %d má %d oktetů, RFC 5545 dovoluje 75: %s"
                % (i, len(l.encode("utf-8")), l))

    return out, count


def main():
    if len(sys.argv) < 2:
        die("Použití: gen-svoz.py <data.json> [vystup.ics]")

    data = load(sys.argv[1])
    out_path = sys.argv[2] if len(sys.argv) > 2 else "svoz-odpadu.ics"

    errors = validate(data)
    if errors:
        die("KONTROLA NEPROŠLA – termíny neodpovídají deklarovanému vzoru:", errors)

    ics, count = build_ics(data)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics)

    print("OK – %d událostí do %s" % (count, out_path))
    for s in data["streams"]:
        d = s["_dates"]
        print("  %-24s %3d×   první %s  poslední %s" % (s["label"], len(d), d[0], d[-1]))


if __name__ == "__main__":
    main()

"""Sample data for the Asian Games design pages.

Everything here is invented: athlete names are generated from name pools, and
marks, records and medal counts are synthetic. It is seeded so every run looks
the same. Nothing should be read as a real result.
"""
from __future__ import annotations

import datetime as dt
import random

from aspire_dash.asian_games import AG_DISCIPLINES

TODAY = "2026-09-24"
GAMES_START = dt.date(2026, 9, 19)
GAMES_DAYS = [(GAMES_START + dt.timedelta(days=i)).isoformat() for i in range(16)]

VENUES = {
    "ATH": "Main Stadium", "SWM": "Aquatics Centre", "SQU": "Squash Courts",
    "FEN": "Fencing Hall", "PAD": "Padel Centre", "TTE": "Table Tennis Arena",
    "SHO": "Shooting Range", "BDM": "Badminton Arena", "BK3": "Urban Park",
    "WLF": "Weightlifting Hall", "JUD": "Martial Arts Hall", "CRD": "Road Course",
}

# given names (men, women) and surnames per NOC, used to build fictional athletes
_NAMES = {
    "QAT": (["Abdulrahman", "Hamad", "Saeed", "Tamim", "Khalid", "Mubarak", "Yousef"],
            ["Mariam", "Noora", "Aisha", "Hessa"],
            ["Al-Harmi", "Al-Marri", "Al-Kuwari", "Al-Sulaiti", "Al-Naimi", "Al-Mohannadi"]),
    "CHN": (["Wei", "Hao", "Jun", "Lei", "Yifan", "Zhen"], ["Xin", "Yu", "Jing", "Lan"],
            ["Zhang", "Wang", "Liu", "Chen", "Yang", "Zhao"]),
    "JPN": (["Haruto", "Ren", "Sota", "Yuki", "Daiki", "Kaito"], ["Hina", "Yui", "Aoi", "Sakura"],
            ["Sato", "Suzuki", "Takahashi", "Tanaka", "Ito", "Nakamura"]),
    "KOR": (["Minjun", "Jiho", "Seojun", "Hyun", "Dohyun"], ["Seoyeon", "Jiwoo", "Minji"],
            ["Kim", "Lee", "Park", "Choi", "Jung"]),
    "IND": (["Arjun", "Rohan", "Vikram", "Aditya", "Karan"], ["Priya", "Ananya", "Kavya"],
            ["Sharma", "Singh", "Nair", "Reddy", "Patel"]),
    "KAZ": (["Nurlan", "Daniyar", "Arman", "Yerlan"], ["Aigerim", "Dana", "Madina"],
            ["Abenov", "Serikov", "Tulegenov", "Nurpeisov"]),
    "UZB": (["Timur", "Bekzod", "Jasur", "Sardor"], ["Dilnoza", "Malika", "Zarina"],
            ["Karimov", "Rakhimov", "Tursunov", "Yusupov"]),
    "BRN": (["Yousif", "Ali", "Hussain"], ["Fatima", "Zainab"], ["Al-Doseri", "Juma", "Salman"]),
    "KSA": (["Faisal", "Turki", "Nawaf"], ["Lama", "Reem"], ["Al-Otaibi", "Al-Qahtani", "Al-Harbi"]),
    "THA": (["Somchai", "Anan", "Kittisak"], ["Ploy", "Nattaya"], ["Srisai", "Chaiyaphum", "Wongsa"]),
    "IRI": (["Reza", "Amir", "Hossein"], ["Sara", "Maryam"], ["Rahimi", "Karimi", "Moradi"]),
    "HKG": (["Ka Ho", "Chun Yin", "Tsz Hin"], ["Hoi Yan", "Wing Sze"], ["Chan", "Wong", "Leung"]),
    "SGP": (["Ethan", "Jun Wei", "Marcus"], ["Chloe", "Rachel"], ["Tan", "Lim", "Ng"]),
    "TPE": (["Chih-Wei", "Yu-Cheng", "Po-Han"], ["Yi-Ting", "Hsin-Yu"], ["Lin", "Huang", "Tsai"]),
    "MAS": (["Hafiz", "Irfan", "Danial"], ["Nurul", "Aina"], ["Rahman", "Ismail", "Hassan"]),
    "INA": (["Budi", "Rizky", "Agus"], ["Putri", "Dewi"], ["Santoso", "Wijaya", "Pratama"]),
}
NOCS = list(_NAMES)

_rng = random.Random(2026)
ATHLETES: dict[str, dict] = {}
_used: set[tuple] = set()


def _new_athlete(noc, gender, sport, age_range=(19, 31)):
    men, women, surnames = _NAMES[noc]
    for _ in range(40):
        given = _rng.choice(men if gender == "Men" else women)
        surname = _rng.choice(surnames)
        if (given, surname, noc) not in _used:
            break
    _used.add((given, surname, noc))
    aid = f"A{len(ATHLETES) + 1:03d}"
    ATHLETES[aid] = {
        "id": aid, "given": given, "surname": surname.upper(), "noc": noc,
        "sport": sport, "gender": "Male" if gender == "Men" else "Female",
        "age": _rng.randint(*age_range),
        "height": f"{_rng.randint(158 if gender == 'Women' else 172, 182 if gender == 'Women' else 199)} cm",
        "events": [], "schedule": [], "medals": [],
    }
    return aid


def _fmt_time(sec):
    if sec >= 60:
        m, s = divmod(sec, 60)
        return f"{int(m)}:{s:05.2f}"
    return f"{sec:.2f}"


# ── Events and their units (heats / finals) ─────────────────────────────────
# (code, discipline, gender, name, lower_is_better, base, spread, units)
# units: (label, phase, day offset, time, kind) where kind is heat or final
_EVENT_SPECS = [
    ("SWM-M100FR", "SWM", "Men", "Men's 100m Freestyle", True, 48.2, 1.9,
     [("Heat 1", "Heats", 5, "10:00"), ("Heat 2", "Heats", 5, "10:06"), ("Heat 3", "Heats", 5, "10:12"),
      ("Final", "Final", 5, "19:30")]),
    ("SWM-W200IM", "SWM", "Women", "Women's 200m Individual Medley", True, 131.4, 4.5,
     [("Heat 1", "Heats", 4, "10:40"), ("Heat 2", "Heats", 4, "10:47"), ("Final", "Final", 4, "19:52")]),
    ("SWM-M200BK", "SWM", "Men", "Men's 200m Backstroke", True, 117.3, 3.6,
     [("Heat 1", "Heats", 2, "10:20"), ("Heat 2", "Heats", 2, "10:27"), ("Final", "Final", 2, "19:40")]),
    ("ATH-MHJ", "ATH", "Men", "Men's High Jump", False, 2.30, 0.12,
     [("Group A", "Qualification", 3, "09:10"), ("Group B", "Qualification", 3, "09:10"), ("Final", "Final", 5, "19:05")]),
    ("ATH-W400", "ATH", "Women", "Women's 400m", True, 51.4, 2.2,
     [("Heat 1", "Round 1", 4, "10:15"), ("Heat 2", "Round 1", 4, "10:23"), ("Final", "Final", 4, "20:10")]),
    ("ATH-M100", "ATH", "Men", "Men's 100m", True, 10.05, 0.35,
     [("Heat 1", "Round 1", 5, "11:00"), ("Heat 2", "Round 1", 5, "11:08"), ("Final", "Final", 5, "21:15")]),
]

EVENTS: dict[str, dict] = {}


def _status_for(day_iso, time):
    if day_iso < TODAY:
        return "official"
    if day_iso > TODAY:
        return "scheduled"
    return "live" if time >= "19:00" and time < "20:00" else ("official" if time < "19:00" else "scheduled")


def _build_events():
    for code, disc, gender, name, lower, base, spread, units in _EVENT_SPECS:
        sport = AG_DISCIPLINES[disc][0]
        field = [(_rng.choice(NOCS), gender) for _ in range(8 * (len(units) - 1))]
        entrants = [_new_athlete(noc, g, sport) for noc, g in field]
        # every entrant gets a "true level"; heats draw from it
        level = {a: base + _rng.random() * spread for a in entrants}
        if not lower:
            level = {a: base + 0.08 - _rng.random() * spread for a in entrants}
        ev = {"code": code, "discipline": disc, "name": name, "lower": lower, "gender": gender,
              "units": []}
        heats = [u for u in units if u[1] != "Final"]
        pools = [entrants[i::len(heats)] for i in range(len(heats))]
        finalists = sorted(entrants, key=lambda a: level[a], reverse=not lower)[:8]
        for i, (label, phase, day_off, time) in enumerate(units):
            day = GAMES_DAYS[day_off]
            status = _status_for(day, time)
            ids = finalists if phase == "Final" else pools[i]
            rows = []
            for lane, aid in enumerate(ids, start=1):
                noise = (_rng.random() - 0.5) * (spread * 0.12)
                mark = round(level[aid] + noise, 2)
                if not lower:
                    mark = round(round(mark / 0.03) * 0.03, 2)   # bars go up in 3cm steps
                rows.append({"athlete_id": aid, "noc": ATHLETES[aid]["noc"],
                             "surname": ATHLETES[aid]["surname"], "given": ATHLETES[aid]["given"],
                             "lane": lane if lower else None, "_mark": mark,
                             "rt": f"0.{_rng.randint(58, 74)}" if disc == "SWM" else
                                   (f"0.{_rng.randint(128, 175)}" if lower else None)})
            has_results = status != "scheduled"
            if has_results:
                rows.sort(key=lambda r: r["_mark"], reverse=not lower)
                best = rows[0]["_mark"]
                for rank, r in enumerate(rows, start=1):
                    r["rank"] = rank
                    r["mark"] = r["_mark"]
                    r["mark_display"] = _fmt_time(r["_mark"]) if lower else f"{r['_mark']:.2f}"
                    diff = abs(r["_mark"] - best)
                    r["gap"] = "" if rank == 1 or diff < 0.005 else (f"+{diff:.2f}" if lower else f"-{diff:.2f}")
                    r["records"] = []
                    if phase == "Final" and rank <= 3 and status == "official":
                        r["medal"] = ("gold", "silver", "bronze")[rank - 1]
                    if rank == 1 and phase == "Final" and _rng.random() < 0.6:
                        r["records"].append("GR")
                    elif _rng.random() < 0.18:
                        r["records"].append("PB")
            else:
                for r in rows:
                    r.update(rank=None, mark=None, mark_display="", gap="", records=[])
            for r in rows:
                r.pop("_mark", None)
                a = ATHLETES[r["athlete_id"]]
                a["schedule"].append({"date": dt.date.fromisoformat(day).strftime("%a %d %b"),
                                      "time": time, "event": name, "phase": f"{phase} · {label}"
                                      if label != phase else phase, "venue": VENUES[disc],
                                      "status": status})
                if r.get("medal"):
                    a["medals"].append(r["medal"])
            ev["units"].append({"value": f"{code}-{i}", "label": label, "phase": phase, "day": day,
                                "time": time, "status": status, "rows": rows,
                                "when": f"{dt.date.fromisoformat(day).strftime('%b %d')}, {time}"})
        for aid in entrants:
            final_row = next((r for r in ev["units"][-1]["rows"] if r["athlete_id"] == aid), None)
            ATHLETES[aid]["events"].append({"label": name,
                                            "rank": final_row.get("rank") if final_row else None,
                                            "medal": final_row.get("medal") if final_row else None})
        # sample records for the records panel (fictional holders)
        fmt = (lambda v: _fmt_time(v)) if lower else (lambda v: f"{v:.2f}")
        wr = base - spread * 0.25 if lower else base + 0.15
        ev["records"] = [
            {"type": "WR", "noc": _rng.choice(NOCS), "athlete": "Sample holder", "mark": fmt(wr),
             "date": "2024", "place": "Sample city"},
            {"type": "AR", "noc": _rng.choice(NOCS), "athlete": "Sample holder",
             "mark": fmt(wr + (0.2 if lower else -0.03)), "date": "2023", "place": "Sample city"},
            {"type": "GR", "noc": _rng.choice(NOCS), "athlete": "Sample holder",
             "mark": fmt(wr + (0.45 if lower else -0.06)), "date": "2022", "place": "Sample city"},
        ]
        EVENTS[code] = ev


_build_events()

# padel / squash / fencing athletes so the participants page spans more sports
for _sport, _n in (("Squash", 10), ("Fencing", 10), ("Padel", 8), ("Table Tennis", 8)):
    for _ in range(_n):
        _aid = _new_athlete(_rng.choice(NOCS), _rng.choice(["Men", "Women"]), _sport)
        ATHLETES[_aid]["events"].append({"label": f"{ATHLETES[_aid]['gender'].replace('Male', 'Men').replace('Female', 'Women')}'s singles",
                                         "rank": None, "medal": None})


# ── Medal standings ─────────────────────────────────────────────────────────
_MEDAL_BASE = [("CHN", 58, 41, 30), ("JPN", 31, 35, 38), ("KOR", 24, 27, 36), ("IND", 12, 18, 24),
               ("UZB", 10, 9, 17), ("IRI", 9, 12, 13), ("KAZ", 7, 11, 19), ("QAT", 7, 3, 5),
               ("TPE", 6, 12, 15), ("THA", 6, 7, 16), ("BRN", 5, 4, 3), ("HKG", 4, 8, 14),
               ("KSA", 3, 4, 6), ("INA", 3, 3, 10), ("MAS", 2, 5, 9), ("SGP", 2, 1, 5)]
_BREAK_DISCS = ["ATH", "SWM", "SQU", "FEN", "SHO", "WLF", "JUD", "TTE"]


def _split(n, k):
    cuts = sorted(_rng.randint(0, n) for _ in range(k - 1))
    return [b - a for a, b in zip([0] + cuts, cuts + [n])]


MEDAL_TABLE = []
for _i, (_noc, _g, _s, _b) in enumerate(sorted(_MEDAL_BASE, key=lambda x: (-x[1], -x[2], -x[3])), start=1):
    gs, ss, bs = _split(_g, 8), _split(_s, 8), _split(_b, 8)
    breakdown = [{"label": AG_DISCIPLINES[d][0], "icon": AG_DISCIPLINES[d][1], "code": d,
                  "gold": gs[j], "silver": ss[j], "bronze": bs[j]}
                 for j, d in enumerate(_BREAK_DISCS) if gs[j] + ss[j] + bs[j]]
    MEDAL_TABLE.append({"rank": _i, "noc": _noc, "gold": _g, "silver": _s, "bronze": _b,
                        "total": _g + _s + _b, "breakdown": breakdown})


def medallists():
    """One row per medal won in a finished final."""
    out = []
    for ev in EVENTS.values():
        final = ev["units"][-1]
        for r in final["rows"]:
            if r.get("medal"):
                out.append({**r, "event": ev["name"], "discipline": ev["discipline"], "day": final["day"],
                            "medal_order": ("gold", "silver", "bronze").index(r["medal"])})
    return sorted(out, key=lambda r: (r["day"], r["event"], r["medal_order"]), reverse=False)


# ── Schedule ────────────────────────────────────────────────────────────────
_FILLER = [
    ("SQU", "Men's Singles", ["Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final"]),
    ("SQU", "Women's Singles", ["Round of 16", "Quarter-final", "Semi-final", "Final"]),
    ("FEN", "Men's Épée Individual", ["Pools", "Table of 32", "Final"]),
    ("FEN", "Women's Foil Team", ["Quarter-final", "Semi-final", "Final"]),
    ("PAD", "Mixed Doubles", ["Group stage", "Quarter-final", "Semi-final", "Final"]),
    ("TTE", "Men's Team", ["Group stage", "Quarter-final", "Semi-final", "Final"]),
    ("SHO", "10m Air Rifle Women", ["Qualification", "Final"]),
    ("BDM", "Women's Singles", ["Round of 32", "Round of 16", "Quarter-final", "Final"]),
    ("WLF", "Men's 73kg", ["Group B", "Group A"]),
    ("JUD", "Women's -57kg", ["Elimination", "Repechage", "Final Block"]),
]

SCHEDULE: dict[str, list] = {d: [] for d in GAMES_DAYS}
for ev in EVENTS.values():
    for u in ev["units"]:
        SCHEDULE[u["day"]].append({
            "time": u["time"], "discipline": ev["discipline"], "event": ev["name"], "phase": u["phase"],
            "unit": u["label"] if u["label"] != u["phase"] else None, "venue": VENUES[ev["discipline"]],
            "status": u["status"], "medal": u["phase"] == "Final",
        })
_finals_done = set()
for _i, _day in enumerate(GAMES_DAYS):
    for _disc, _event, _phases in _rng.sample(_FILLER, _rng.randint(3, 6)):
        _phase = _phases[min(len(_phases) - 1, _i * len(_phases) // len(GAMES_DAYS))]
        _time = f"{_rng.randint(9, 20):02d}:{_rng.choice(['00', '15', '30', '45'])}"
        SCHEDULE[_day].append({
            "time": _time, "discipline": _disc, "event": _event, "phase": _phase, "unit": None,
            "venue": VENUES.get(_disc, "Sports Hall"), "status": _status_for(_day, _time),
            "medal": _phase == _phases[-1] and (_disc, _event) not in _finals_done,
        })
        if _phase == _phases[-1]:
            _finals_done.add((_disc, _event))
for _d in SCHEDULE:
    SCHEDULE[_d].sort(key=lambda u: u["time"])
    # one delayed unit on today's card, to show the pill
    if _d == TODAY and len(SCHEDULE[_d]) > 3:
        SCHEDULE[_d][-1]["status"] = "delayed"

MEDAL_DAYS = {d for d, units in SCHEDULE.items() if any(u["medal"] for u in units)}


def days_strip():
    return [{"value": d, "medal": d in MEDAL_DAYS and d != TODAY, "today": d == TODAY} for d in GAMES_DAYS]


def discipline_days():
    """{discipline code: sorted list of {"value", "medal"}} for the by-discipline view."""
    out: dict[str, dict] = {}
    for d, units in SCHEDULE.items():
        for u in units:
            slot = out.setdefault(u["discipline"], {})
            slot[d] = slot.get(d, False) or u["medal"]
    return {k: [{"value": d, "medal": m, "today": d == TODAY} for d, m in sorted(v.items())]
            for k, v in out.items()}


NEWS = [
    {"title": "Sample: a first swimming gold for the host pool", "date": "24 Sep 2026",
     "text": "A placeholder story that shows how a news card lays out: date, headline, two lines of text and tags.",
     "tags": ["Swimming", "Medals"], "icon": "fa-person-swimming", "tone": None},
    {"title": "Sample: high jump final set for Friday night", "date": "23 Sep 2026",
     "text": "Twelve jumpers go through from qualifying. The card image is a branded gradient, since the demo ships no photos.",
     "tags": ["Athletics"], "icon": "fa-person-running", "tone": "gold"},
    {"title": "Sample: squash draw published", "date": "22 Sep 2026",
     "text": "Seeds are placed and the first round starts on day three. Tags use the lavender chip style from the org site.",
     "tags": ["Squash", "Draw"], "icon": "fa-table-tennis-paddle-ball", "tone": "green"},
]

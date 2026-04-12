"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

try:
    from tabulate import tabulate as _tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False

from recommender import load_songs, recommend_songs, SCORING_MODES, DEFAULT_MODE


def _print_table(headers: list, rows: list) -> None:
    """Print a results table via tabulate when available, plain ASCII otherwise."""
    if _HAS_TABULATE:
        print(_tabulate(rows, headers=headers, tablefmt="grid"))
        return
    # ASCII fallback — standard library only
    widths = [
        max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    def _fmt(row: list) -> str:
        return "|" + "|".join(f" {str(c):<{widths[i]}} " for i, c in enumerate(row)) + "|"
    print(sep)
    print(_fmt(headers))
    print(sep)
    for row in rows:
        print(_fmt(row))
    print(sep)

CSV_PATH = Path(__file__).parent.parent / "data" / "songs.csv"

# ── Change this one variable to switch scoring strategy ───────────────────────
# Available modes: "Genre-First", "Mood-First", "Energy-Focused"
MODE = DEFAULT_MODE   # currently "Energy-Focused"

def main() -> None:
    songs = load_songs(CSV_PATH)
    available = ", ".join(SCORING_MODES.keys())
    renderer = "tabulate" if _HAS_TABULATE else "ASCII fallback"
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring mode: {MODE}  (available: {available})")
    print(f"Table renderer: {renderer}")

    # User taste profile — keys align with UserProfile dataclass fields
    # and extend it with target values for every scored song feature.
    user_prefs = {
        "genre":            "pop",
        "mood":             "happy",
        "energy":           0.80,
        "preferred_decade": 2020,
        "mood_tags":        ["uplifting", "bright", "danceable"],
    }

    high_energy_pop = {
        "genre":            "pop",
        "mood":             "happy",
        "energy":           0.93,
        "preferred_decade": 2020,
        "mood_tags":        ["energetic", "aggressive", "motivating"],
    }

    chill_lofi = {
        "genre":            "lofi",
        "mood":             "chill",
        "energy":           0.38,
        "preferred_decade": 2010,
        "mood_tags":        ["calm", "focused", "dreamy"],
    }

    deep_intense_rock = {
        "genre":            "rock",
        "mood":             "intense",
        "energy":           0.91,
        "preferred_decade": 2010,
        "mood_tags":        ["aggressive", "powerful", "driving"],
    }

    profiles = [
        ("Default Pop/Happy",   user_prefs),
        ("High-Energy Pop",     high_energy_pop),
        ("Chill Lofi",          chill_lofi),
        ("Deep Intense Rock",   deep_intense_rock),
    ]

    headers = ["Rank", "Title", "Artist", "Score", "Reasons"]

    for label, prefs in profiles:
        recommendations = recommend_songs(prefs, songs, k=5, mode=MODE)
        print(f"\n{'=' * 60}")
        print(f"  Profile: {label}")
        print(f"{'=' * 60}")
        rows = [
            [rank, song["title"], song["artist"], f"{score:.2f}", explanation]
            for rank, (song, score, explanation) in enumerate(recommendations, 1)
        ]
        _print_table(headers, rows)

if __name__ == "__main__":
    main()

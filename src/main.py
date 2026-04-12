"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path
from recommender import load_songs, recommend_songs

CSV_PATH = Path(__file__).parent.parent / "data" / "songs.csv"

def main() -> None:
    songs = load_songs(CSV_PATH)
    print(f"Loaded songs: {len(songs)}")

    # User taste profile — keys align with UserProfile dataclass fields
    # and extend it with target values for every scored song feature.
    user_prefs = {
        "genre":    "pop",   # matched exactly against song["genre"]
        "mood":     "happy", # matched exactly against song["mood"]
        "energy":   0.80,    # proximity scored against song["energy"]
    }

    high_energy_pop = {
        "genre":  "pop",
        "mood":   "happy",
        "energy": 0.93,
    }

    chill_lofi = {
        "genre":  "lofi",
        "mood":   "chill",
        "energy": 0.38,
    }

    deep_intense_rock = {
        "genre":  "rock",
        "mood":   "intense",
        "energy": 0.91,
    }

    profiles = [
        ("Default Pop/Happy",   user_prefs),
        ("High-Energy Pop",     high_energy_pop),
        ("Chill Lofi",          chill_lofi),
        ("Deep Intense Rock",   deep_intense_rock),
    ]

    for label, prefs in profiles:
        recommendations = recommend_songs(prefs, songs, k=5)
        print(f"\n{'=' * 40}")
        print(f"Profile: {label}")
        print(f"{'=' * 40}\n")
        separator = "-" * 40
        for song, score, explanation in recommendations:
            print(f"{song['title']} by {song['artist']}")
            print(f"Score: {score:.2f}")
            for reason in explanation.split(", "):
                print(f"  * {reason}")
            print(separator)

if __name__ == "__main__":
    main()

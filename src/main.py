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

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    separator = "-" * 40
    for song, score, explanation in recommendations:
        print(f"{song['title']} by {song['artist']}")
        print(f"Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"  * {reason}")
        print(separator)


if __name__ == "__main__":
    main()

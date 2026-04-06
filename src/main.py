"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # User taste profile — keys align with UserProfile dataclass fields
    # and extend it with target values for every scored song feature.
    user_prefs = {
        # --- Categorical preferences (matched exactly) ---
        "favorite_genre": "pop",       # strongest signal; worth 3.0 pts on match
        "favorite_mood": "happy",      # second strongest; worth 2.0 pts on match

        # --- Numerical targets (scored by proximity, range 0.0–1.0) ---
        "target_energy": 0.80,         # wants upbeat, energetic tracks
        "target_valence": 0.80,        # wants positive, feel-good sound
        "target_danceability": 0.85,   # wants groovy, rhythmically engaging tracks

        # --- Boolean preference ---
        "likes_acoustic": False,       # prefers produced/electric sound over acoustic

        # --- Optional tempo hint (BPM, not 0–1 scale) ---
        "target_tempo_bpm": 120,       # typical pop/dance tempo
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()

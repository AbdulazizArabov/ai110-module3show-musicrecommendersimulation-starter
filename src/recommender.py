from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

# ── Scoring Modes (Strategy Pattern) ────────────────────────────────────────
# Each entry is a weight config consumed by score_song.
# Change DEFAULT_MODE to affect every call that omits the mode argument, or
# pass mode= explicitly to recommend_songs to switch per-call.
#
# Weight keys
#   genre       flat bonus for an exact genre match
#   energy_max  ceiling for energy-proximity  (score = energy_max * (1 - |diff|))
#   pop_max     ceiling for popularity bonus  (score = popularity/100 * pop_max)
#   decade_max  ceiling for decade-proximity  (score = decade_max * (1 - gap/30))
#   tag_weight  points awarded per matching mood tag (max = tag_weight × 3)

SCORING_MODES: Dict[str, Dict[str, float]] = {
    "Genre-First": {
        "genre":      2.0,   # genre is the primary signal
        "energy_max": 1.5,
        "pop_max":    0.5,
        "decade_max": 0.75,
        "tag_weight": 0.5,
    },
    "Mood-First": {
        "genre":      1.0,
        "energy_max": 1.5,
        "pop_max":    0.5,
        "decade_max": 0.5,
        "tag_weight": 0.8,   # each matching mood tag is worth more
    },
    "Energy-Focused": {      # reproduces the current experimental weights exactly
        "genre":      1.0,
        "energy_max": 2.0,
        "pop_max":    0.5,
        "decade_max": 1.0,
        "tag_weight": 0.5,
    },
}

DEFAULT_MODE = "Energy-Focused"


def score_song(user_prefs: Dict, song: Dict,
               weights: Optional[Dict] = None) -> Tuple[float, List[str]]:
    """Score one song against user_prefs and return (total_score, list_of_reason_strings).

    Pass a weight config dict directly, or omit to use SCORING_MODES[DEFAULT_MODE].
    All five factors are scaled by the values in that config.
    """
    if weights is None:
        weights = SCORING_MODES[DEFAULT_MODE]

    score = 0.0
    reasons = []

    # EXPERIMENT: genre weight halved (2.0 → 1.0), energy weight doubled (max 1.0 → 2.0)
    if song["genre"] == user_prefs["genre"]:
        g = weights["genre"]
        score += g
        reasons.append(f"genre match (+{g:.1f})")

    # EXPERIMENT: mood match commented out to isolate genre + energy as sole signals
    # if song["mood"] == user_prefs["mood"]:
    #     score += 1.5
    #     reasons.append("mood match (+1.5)")

    # Energy proximity: linear score from 0 → energy_max as distance shrinks to 0.
    energy_score = max(0.0, weights["energy_max"] * (1.0 - abs(user_prefs["energy"] - song["energy"])))
    score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.1f})")

    # Popularity bonus: scales the song's 0–100 rating down to a 0–pop_max bonus.
    popularity_score = (song["popularity"] / 100) * weights["pop_max"]
    score += popularity_score
    reasons.append(f"popularity bonus (+{popularity_score:.2f})")

    # Decade proximity: linear score from 0 → decade_max; each 10-year gap costs ~decade_max/3.
    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade is not None:
        decade_score = max(0.0, weights["decade_max"] * (1.0 - abs(preferred_decade - song["release_decade"]) / 30))
        score += decade_score
        reasons.append(f"decade proximity (+{decade_score:.2f})")

    # Mood tag matches: tag_weight points per matching tag (up to 3 tags).
    user_tags = set(user_prefs.get("mood_tags", []))
    if user_tags:
        song_tags = {song["mood_tag_1"], song["mood_tag_2"], song["mood_tag_3"]}
        tag_matches = len(song_tags & user_tags)
        if tag_matches:
            tag_score = tag_matches * weights["tag_weight"]
            score += tag_score
            reasons.append(f"mood tag matches x{tag_matches} (+{tag_score:.1f})")

    return (score, reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Read csv_path with csv.DictReader and return a list of song dicts with numeric fields cast to int or float."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id":             int(row["id"]),
                "title":          row["title"],
                "artist":         row["artist"],
                "genre":          row["genre"],
                "mood":           row["mood"],
                "energy":         float(row["energy"]),
                "tempo_bpm":      int(row["tempo_bpm"]),
                "valence":        float(row["valence"]),
                "danceability":   float(row["danceability"]),
                "acousticness":   float(row["acousticness"]),
                "popularity":     int(row["popularity"]),
                "release_decade": int(row["release_decade"]),
                "mood_tag_1":     row["mood_tag_1"],
                "mood_tag_2":     row["mood_tag_2"],
                "mood_tag_3":     row["mood_tag_3"],
            })
    return songs

# ── Diversity Penalties ──────────────────────────────────────────────────────
# Applied during greedy re-ranking in recommend_songs (not during scoring).
# A song pays a penalty for each of its attributes that already appears in the
# slots selected above it.  The penalty is subtracted from its raw score to
# produce an "effective score" used only for comparison — the raw score is
# kept in the output so explanations stay honest.
#
# Tuning intent:
#   ARTIST_PENALTY 1.0 — strong enough to demote a second song from the same
#     artist unless it beats the next-best alternative by more than 1.0 point.
#   GENRE_PENALTY  0.5 — softer, because genre overlap is expected; this just
#     nudges variety without hard-blocking any genre from appearing twice.

ARTIST_PENALTY: float = 1.0
GENRE_PENALTY:  float = 0.5


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = DEFAULT_MODE) -> List[Tuple[Dict, float, str]]:
    """Score every song, then greedy-rerank the top-k with diversity penalties.

    Pass mode= to select a scoring strategy: "Genre-First", "Mood-First", or
    "Energy-Focused".  Omitting mode falls back to DEFAULT_MODE.

    Diversity logic
    ---------------
    After scoring all songs, we build the top-k list one slot at a time.  For
    each open slot we scan every remaining candidate and subtract ARTIST_PENALTY
    and/or GENRE_PENALTY from its raw score if its artist or genre already
    appears in the slots above.  The candidate with the highest *effective*
    score wins the slot.  Penalties are noted in the explanation string but
    do not alter the displayed raw score.
    """
    weights = SCORING_MODES[mode]

    # Step 1 — score every song and sort by raw score descending.
    candidates: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        candidates.append((song, score, ", ".join(reasons)))
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Step 2 — greedy re-ranking: pick one slot at a time, applying diversity
    # penalties based on what is already in `selected`.
    selected: List[Tuple[Dict, float, str]] = []
    seen_artists: set = set()
    seen_genres:  set = set()

    while len(selected) < k and candidates:
        best_idx = 0
        best_effective = float("-inf")
        best_penalty_parts: List[str] = []

        for i, (song, raw, _) in enumerate(candidates):
            # Compute this candidate's penalty given what's already selected.
            penalty = 0.0
            parts: List[str] = []
            if song["artist"] in seen_artists:
                penalty += ARTIST_PENALTY
                parts.append(f"artist dup -{ARTIST_PENALTY:.1f}")
            if song["genre"] in seen_genres:
                penalty += GENRE_PENALTY
                parts.append(f"genre dup -{GENRE_PENALTY:.1f}")

            effective = raw - penalty
            if effective > best_effective:
                best_effective = effective
                best_idx = i
                best_penalty_parts = parts

        song, raw_score, explanation = candidates.pop(best_idx)

        # Append penalty details to the explanation so the output is transparent.
        if best_penalty_parts:
            explanation += f", diversity penalty ({', '.join(best_penalty_parts)})"

        selected.append((song, raw_score, explanation))
        seen_artists.add(song["artist"])
        seen_genres.add(song["genre"])

    return selected

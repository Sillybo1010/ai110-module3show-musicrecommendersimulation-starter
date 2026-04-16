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
    popularity:        int   = 50
    release_decade:    int   = 2020
    instrumentalness:  float = 0.0
    speechiness:       float = 0.05
    liveness:          float = 0.10

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
    """OOP wrapper around score_song; ranks Song objects for a given UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects sorted from highest to lowest score."""
        prefs = {
            "favorite_genre":      user.favorite_genre,
            "favorite_mood":       user.favorite_mood,
            "target_energy":       user.target_energy,
            "target_tempo":        100.0,
            "target_valence":      0.5,
            "target_danceability": 0.5,
            "target_acousticness": 0.5,
            "likes_acoustic":      user.likes_acoustic,
        }
        scored = sorted(
            self.songs,
            key=lambda s: score_song(prefs, vars(s))[0],
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a comma-separated string of reasons why song matched user."""
        prefs = {
            "favorite_genre":      user.favorite_genre,
            "favorite_mood":       user.favorite_mood,
            "target_energy":       user.target_energy,
            "target_tempo":        100.0,
            "target_valence":      0.5,
            "target_danceability": 0.5,
            "target_acousticness": 0.5,
            "likes_acoustic":      user.likes_acoustic,
        }
        _, reasons = score_song(prefs, vars(song))
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numerics cast to float/int."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":            int(row["id"]),
                "title":         row["title"],
                "artist":        row["artist"],
                "genre":         row["genre"],
                "mood":          row["mood"],
                "energy":        float(row["energy"]),
                "tempo_bpm":     float(row["tempo_bpm"]),
                "valence":       float(row["valence"]),
                "danceability":  float(row["danceability"]),
                "acousticness":  float(row["acousticness"]),
                "popularity":        int(row["popularity"]),
                "release_decade":    int(row["release_decade"]),
                "instrumentalness":  float(row["instrumentalness"]),
                "speechiness":       float(row["speechiness"]),
                "liveness":          float(row["liveness"]),
            })
    print(f"Loaded {len(songs)} songs.")
    return songs

_DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre":          2.00,
    "mood":           1.00,
    "energy":         1.50,
    "acousticness":   1.00,
    "tempo":          1.00,
    "valence":        0.75,
    "danceability":   0.50,
    "acoustic_bonus": 0.50,
}

# ── Stretch: Ranking Modes ────────────────────────────────────────────────────
# Each mode is a partial weight override merged on top of _DEFAULT_WEIGHTS.
# "balanced" uses the defaults unchanged.
RANKING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {},                              # no overrides — pure defaults
    "genre-first":  {"genre": 4.00, "mood": 0.50, "energy": 0.75},
    "mood-first":   {"mood":  3.00, "genre": 0.75, "energy": 0.75},
    "energy-first": {"energy": 4.00, "genre": 0.75, "acousticness": 0.50},
}


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Score one song against user_prefs using the Algorithm Recipe; return (score, reasons)."""
    w = {**_DEFAULT_WEIGHTS, **(weights or {})}
    score = 0.0
    reasons: List[str] = []

    # --- Categorical matches ---
    if song["genre"] == user_prefs.get("favorite_genre", ""):
        score += w["genre"]
        reasons.append(f"genre match ({song['genre']}, +{w['genre']:.1f})")

    if song["mood"] == user_prefs.get("favorite_mood", ""):
        score += w["mood"]
        reasons.append(f"mood match ({song['mood']}, +{w['mood']:.1f})")

    # --- Energy similarity ---
    energy_sim = 1.0 - abs(song["energy"] - user_prefs.get("target_energy", 0.5))
    score += w["energy"] * energy_sim
    reasons.append(f"energy {song['energy']:.2f} (sim {energy_sim:.2f})")

    # --- Acousticness similarity ---
    acoustic_sim = 1.0 - abs(song["acousticness"] - user_prefs.get("target_acousticness", 0.5))
    score += w["acousticness"] * acoustic_sim
    reasons.append(f"acousticness {song['acousticness']:.2f} (sim {acoustic_sim:.2f})")

    # --- Tempo similarity normalized over 100 BPM window ---
    tempo_sim = max(0.0, 1.0 - abs(song["tempo_bpm"] - user_prefs.get("target_tempo", 100.0)) / 100.0)
    score += w["tempo"] * tempo_sim
    reasons.append(f"tempo {song['tempo_bpm']:.0f} bpm (sim {tempo_sim:.2f})")

    # --- Valence similarity ---
    valence_sim = 1.0 - abs(song["valence"] - user_prefs.get("target_valence", 0.5))
    score += w["valence"] * valence_sim

    # --- Danceability similarity ---
    dance_sim = 1.0 - abs(song["danceability"] - user_prefs.get("target_danceability", 0.5))
    score += w["danceability"] * dance_sim

    # --- Instrumentalness similarity (weight: 0.75) ---
    if "target_instrumentalness" in user_prefs:
        instr_sim = 1.0 - abs(song["instrumentalness"] - user_prefs["target_instrumentalness"])
        score += 0.75 * instr_sim

    # --- Popularity similarity (weight: 0.50) ---
    if "target_popularity" in user_prefs:
        pop_sim = 1.0 - abs(song["popularity"] - user_prefs["target_popularity"]) / 100.0
        score += 0.50 * pop_sim

    # --- Decade similarity (weight: 0.50) ---
    if "target_decade" in user_prefs:
        decade_sim = max(0.0, 1.0 - abs(song["release_decade"] - user_prefs["target_decade"]) / 50.0)
        score += 0.50 * decade_sim

    # --- Acoustic bonus ---
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
        score += w["acoustic_bonus"]
        reasons.append(f"acoustic bonus (+{w['acoustic_bonus']:.1f})")

    return score, reasons


def apply_artist_penalty(
    scored: List[Tuple[Dict, float, List[str]]],
    penalty: float = 0.20,
) -> List[Tuple[Dict, float, List[str]]]:
    """Reduce scores of duplicate artists to prevent filter bubbles.

    The first song by each artist keeps its full score.  Every subsequent song
    by the same artist has its score multiplied by (1 - penalty).  This pushes
    variety into the top-K without removing any song from the catalog.
    """
    seen_artists: set = set()
    result = []
    for song, score, reasons in scored:
        artist = song["artist"]
        if artist in seen_artists:
            score = score * (1.0 - penalty)
            reasons = reasons + [f"artist repeat penalty (×{1-penalty:.2f})"]
        else:
            seen_artists.add(artist)
        result.append((song, score, reasons))
    return result


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
    mode: str = "balanced",
    diversity_penalty: float = 0.20,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, apply diversity penalty, sort, and return top-k.

    Args:
        user_prefs:        User preference dict.
        songs:             Full catalog as a list of dicts.
        k:                 Number of results to return.
        weights:           Optional per-key weight overrides (highest priority).
        mode:              One of RANKING_MODES keys — preset weight profile.
        diversity_penalty: Fraction (0–1) to discount repeated-artist songs.
                           Set to 0.0 to disable.
    """
    # Merge: defaults <- mode overrides <- caller-supplied weights
    merged_weights = {**_DEFAULT_WEIGHTS, **RANKING_MODES.get(mode, {}), **(weights or {})}

    scored = [
        (song, *score_song(user_prefs, song, merged_weights))
        for song in songs
    ]
    # Sort before penalty so we penalise the lower-ranked duplicate, not the best one
    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    if diversity_penalty > 0.0:
        scored = apply_artist_penalty(scored, penalty=diversity_penalty)
        # Re-sort after penalty adjustment
        scored = sorted(scored, key=lambda x: x[1], reverse=True)

    return [(song, score, ", ".join(reasons)) for song, score, reasons in scored[:k]]

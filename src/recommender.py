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

    # --- Acoustic bonus ---
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
        score += w["acoustic_bonus"]
        reasons.append(f"acoustic bonus (+{w['acoustic_bonus']:.1f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest-to-lowest, and return the top-k as (song, score, explanation)."""
    scored = [
        (song, *score_song(user_prefs, song, weights))
        for song in songs
    ]
    # sorted() returns a new list; .sort() would mutate songs in place
    scored = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, ", ".join(reasons)) for song, score, reasons in scored[:k]]

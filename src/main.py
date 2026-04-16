"""
Command line runner for the Music Recommender Simulation.

Runs six user profiles through recommend_songs() and prints ranked results,
then runs one weight-shift experiment to test system sensitivity.
"""

try:
    from recommender import load_songs, recommend_songs          # python src/main.py
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs      # python -m src.main


# ── User Profiles ─────────────────────────────────────────────────────────────

PROFILES = {

    # --- Standard profiles ---------------------------------------------------

    "High-Energy Pop": {
        "favorite_genre":      "pop",
        "favorite_mood":       "happy",
        "target_energy":       0.88,   # wants intense, driving tracks
        "target_tempo":        125.0,  # upbeat dance pace
        "target_valence":      0.85,   # very positive emotional tone
        "target_danceability": 0.85,   # made for moving
        "target_acousticness": 0.10,   # produced, not acoustic
        "likes_acoustic":      False,
    },

    "Chill Lofi Study": {
        "favorite_genre":      "lofi",
        "favorite_mood":       "focused",
        "target_energy":       0.45,   # calm but not completely passive
        "target_tempo":        82.0,   # steady pace, not driving or sleepy
        "target_valence":      0.60,   # slightly positive
        "target_danceability": 0.55,   # moderate
        "target_acousticness": 0.75,   # warm, organic sounds
        "likes_acoustic":      True,
    },

    "Deep Intense Rock": {
        "favorite_genre":      "rock",
        "favorite_mood":       "intense",
        "target_energy":       0.92,   # maximum aggression
        "target_tempo":        150.0,  # fast and driving
        "target_valence":      0.45,   # darker emotional tone
        "target_danceability": 0.65,   # headbanging counts
        "target_acousticness": 0.08,   # fully electric/distorted
        "likes_acoustic":      False,
    },

    # --- Adversarial / edge-case profiles ------------------------------------

    # Profile 4: Conflicting preferences — ambient genre but workout energy.
    # Tests whether numeric similarity can override a genre match.
    "Conflicting: Ambient + High Energy": {
        "favorite_genre":      "ambient",
        "favorite_mood":       "sad",
        "target_energy":       0.95,   # contradicts "ambient" (avg energy ~0.28)
        "target_tempo":        140.0,  # also contradicts ambient feel
        "target_valence":      0.20,   # very dark
        "target_danceability": 0.90,
        "target_acousticness": 0.90,   # wants acoustic but also high energy
        "likes_acoustic":      True,
    },

    # Profile 5: Ghost genre — genre not in the catalog at all.
    # No song will ever earn the +2.0 genre bonus.
    # Tests whether numeric features alone produce sensible results.
    "Ghost Genre: K-Pop": {
        "favorite_genre":      "k-pop",   # not in songs.csv
        "favorite_mood":       "happy",
        "target_energy":       0.80,
        "target_tempo":        120.0,
        "target_valence":      0.88,
        "target_danceability": 0.88,
        "target_acousticness": 0.15,
        "likes_acoustic":      False,
    },

    # Profile 6: Maximum mismatch — every numeric preference is the
    # opposite of the lowest-scoring corner of the dataset.
    # Tests floor behaviour and whether explanations still make sense.
    "Max Mismatch: Classical Serenity": {
        "favorite_genre":      "classical",
        "favorite_mood":       "peaceful",
        "target_energy":       0.18,   # below the quietest song (0.22)
        "target_tempo":        55.0,   # below the slowest song (58 bpm)
        "target_valence":      0.65,
        "target_danceability": 0.20,   # very low
        "target_acousticness": 0.98,   # fully acoustic
        "likes_acoustic":      True,
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

DIVIDER = "─" * 60


def print_profile_results(label: str, results: list) -> None:
    """Print ranked recommendations for one profile in a readable layout."""
    print(f"\n{'═' * 60}")
    print(f"  PROFILE: {label}")
    print(f"{'═' * 60}")
    for rank, (song, score, explanation) in enumerate(results, start=1):
        print(f"  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Score : {score:.2f} / 8.25")
        print(f"       Why   : {explanation}")
        print(f"  {DIVIDER}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")

    # --- Run all six profiles ------------------------------------------------
    for label, prefs in PROFILES.items():
        results = recommend_songs(prefs, songs, k=5)
        print_profile_results(label, results)

    # ── Experiment: Weight Shift ──────────────────────────────────────────────
    # Hypothesis: doubling energy weight (1.5 → 3.0) and halving genre weight
    # (2.0 → 1.0) should push the High-Energy Pop list toward purely high-energy
    # songs regardless of genre, rather than rewarding genre matches first.
    #
    # Why sorted() not .sort()?
    #   sorted() returns a NEW list — the original `songs` list is untouched so
    #   every subsequent profile run sees the same unmodified order.
    #   .sort() mutates the list in place, which would corrupt later calls.
    print(f"\n{'═' * 60}")
    print("  EXPERIMENT: Weight Shift on 'High-Energy Pop'")
    print("  Genre weight: 2.0 → 1.0  |  Energy weight: 1.5 → 3.0")
    print(f"{'═' * 60}")

    exp_results = recommend_songs(
        PROFILES["High-Energy Pop"],
        songs,
        k=5,
        weights={
            "genre":         1.0,   # halved
            "mood":          1.0,
            "energy":        3.0,   # doubled
            "acousticness":  1.0,
            "tempo":         1.0,
            "valence":       0.75,
            "danceability":  0.50,
            "acoustic_bonus":0.50,
        },
    )
    for rank, (song, score, explanation) in enumerate(exp_results, start=1):
        print(f"  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Score : {score:.2f}")
        print(f"       Why   : {explanation}")
        print(f"  {DIVIDER}")


if __name__ == "__main__":
    main()

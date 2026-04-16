"""
Command line runner for the Music Recommender Simulation.

Runs six user profiles and a ranking-mode comparison through recommend_songs(),
printing results as formatted tables via tabulate.
"""

try:
    from recommender import load_songs, recommend_songs, RANKING_MODES   # python src/main.py
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs, RANKING_MODES  # python -m src.main

from tabulate import tabulate


# ── User Profiles ─────────────────────────────────────────────────────────────

PROFILES = {

    # --- Standard profiles ---------------------------------------------------

    "High-Energy Pop": {
        "favorite_genre":         "pop",
        "favorite_mood":          "happy",
        "target_energy":          0.88,
        "target_tempo":           125.0,
        "target_valence":         0.85,
        "target_danceability":    0.85,
        "target_acousticness":    0.10,
        "target_instrumentalness":0.02,
        "target_popularity":      78,
        "target_decade":          2020,
        "likes_acoustic":         False,
    },

    "Chill Lofi Study": {
        "favorite_genre":         "lofi",
        "favorite_mood":          "focused",
        "target_energy":          0.45,
        "target_tempo":           82.0,
        "target_valence":         0.60,
        "target_danceability":    0.55,
        "target_acousticness":    0.75,
        "target_instrumentalness":0.85,
        "target_popularity":      60,
        "target_decade":          2020,
        "likes_acoustic":         True,
    },

    "Deep Intense Rock": {
        "favorite_genre":         "rock",
        "favorite_mood":          "intense",
        "target_energy":          0.92,
        "target_tempo":           150.0,
        "target_valence":         0.45,
        "target_danceability":    0.65,
        "target_acousticness":    0.08,
        "target_instrumentalness":0.05,
        "target_popularity":      65,
        "target_decade":          2010,
        "likes_acoustic":         False,
    },

    # --- Adversarial / edge-case profiles ------------------------------------

    "Conflicting: Ambient + High Energy": {
        "favorite_genre":      "ambient",
        "favorite_mood":       "sad",
        "target_energy":       0.95,
        "target_tempo":        140.0,
        "target_valence":      0.20,
        "target_danceability": 0.90,
        "target_acousticness": 0.90,
        "likes_acoustic":      True,
    },

    "Ghost Genre: K-Pop": {
        "favorite_genre":      "k-pop",
        "favorite_mood":       "happy",
        "target_energy":       0.80,
        "target_tempo":        120.0,
        "target_valence":      0.88,
        "target_danceability": 0.88,
        "target_acousticness": 0.15,
        "likes_acoustic":      False,
    },

    "Max Mismatch: Classical Serenity": {
        "favorite_genre":         "classical",
        "favorite_mood":          "peaceful",
        "target_energy":          0.18,
        "target_tempo":           55.0,
        "target_valence":         0.65,
        "target_danceability":    0.20,
        "target_acousticness":    0.98,
        "target_instrumentalness":0.95,
        "target_popularity":      48,
        "target_decade":          2000,
        "likes_acoustic":         True,
    },
}


# ── Display helpers ───────────────────────────────────────────────────────────

def results_to_table(results: list) -> str:
    """Format recommend_songs() output as a tabulate grid table."""
    rows = []
    for rank, (song, score, explanation) in enumerate(results, start=1):
        # Wrap reasons across two lines so the table stays readable
        reasons = explanation.replace(", ", "\n")
        rows.append([
            rank,
            f"{song['title']}\n{song['artist']}",
            f"{score:.2f}",
            f"{song['genre']} / {song['mood']}",
            f"e={song['energy']:.2f}  "
            f"ac={song['acousticness']:.2f}  "
            f"bpm={song['tempo_bpm']:.0f}  "
            f"pop={song.get('popularity','?')}  "
            f"instr={song.get('instrumentalness','?'):.2f}",
            reasons,
        ])
    headers = ["#", "Song / Artist", "Score", "Genre / Mood", "Audio Features", "Why"]
    return tabulate(rows, headers=headers, tablefmt="rounded_grid",
                    maxcolwidths=[3, 22, 6, 18, 28, 36])


def print_profile(label: str, results: list) -> None:
    print(f"\n{'═'*90}")
    print(f"  PROFILE: {label}")
    print(f"{'═'*90}")
    print(results_to_table(results))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")

    # --- All six profiles (balanced mode, diversity penalty on) --------------
    for label, prefs in PROFILES.items():
        results = recommend_songs(prefs, songs, k=5, mode="balanced",
                                  diversity_penalty=0.20)
        print_profile(label, results)

    # ── Stretch: Ranking Mode Comparison ─────────────────────────────────────
    # Run the High-Energy Pop profile through all four ranking modes so the
    # difference in weight emphasis is visible side-by-side.
    print(f"\n\n{'═'*90}")
    print("  RANKING MODE COMPARISON — Profile: High-Energy Pop")
    print(f"{'═'*90}")

    mode_rows = []
    for mode in RANKING_MODES:
        results = recommend_songs(PROFILES["High-Energy Pop"], songs,
                                  k=3, mode=mode, diversity_penalty=0.0)
        top3 = " | ".join(
            f"#{r} {s['title']} ({sc:.2f})"
            for r, (s, sc, _) in enumerate(results, 1)
        )
        mode_rows.append([mode, top3])

    print(tabulate(
        mode_rows,
        headers=["Mode", "Top 3 results  (title, score)"],
        tablefmt="rounded_grid",
        maxcolwidths=[14, 72],
    ))

    # ── Stretch: Diversity Penalty Demo ──────────────────────────────────────
    print(f"\n\n{'═'*90}")
    print("  DIVERSITY PENALTY DEMO — Profile: Chill Lofi Study")
    print("  Same profile, penalty OFF vs ON — watch artist variety change")
    print(f"{'═'*90}")

    for label, penalty in [("No penalty  (0.0)", 0.0), ("20% penalty (0.2)", 0.20)]:
        results = recommend_songs(PROFILES["Chill Lofi Study"], songs,
                                  k=5, diversity_penalty=penalty)
        rows = [[r, s["title"], s["artist"], f"{sc:.2f}"]
                for r, (s, sc, _) in enumerate(results, 1)]
        print(f"\n  {label}")
        print(tabulate(rows, headers=["#", "Title", "Artist", "Score"],
                       tablefmt="simple"))


if __name__ == "__main__":
    main()

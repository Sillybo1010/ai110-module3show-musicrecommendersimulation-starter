"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs          # python src/main.py
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs      # python -m src.main


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # ── Taste Profile ────────────────────────────────────────────────────────
    # This profile represents a user who wants focused, mid-energy study music:
    # acoustic-leaning, moderately positive, not too fast, not too slow.
    #
    # Copilot critique (inline):
    #
    # Q: Will this profile differentiate "intense rock" from "chill lofi"?
    # A: Yes — primarily through three features working together:
    #    - target_energy  : rock scores 0.91, lofi scores ~0.38 → large gap
    #    - target_tempo   : rock is 152 bpm, lofi is ~75 bpm → large gap
    #    - target_acousticness: rock is 0.10, lofi is ~0.78 → large gap
    #    Any one of these alone would separate the two; all three together
    #    make the separation robust and hard to accidentally collapse.
    #
    # Q: Is the profile too narrow?
    # A: Somewhat — "favorite_genre" and "favorite_mood" are exact-match
    #    string fields, so a user who likes "lofi" gets zero genre credit for
    #    "ambient" even though those songs feel very similar. Likewise, a
    #    profile targeting only one mood ("focused") gives no partial credit
    #    to "chill" or "relaxed," which may be close enough. The numeric
    #    features (energy, tempo, valence, danceability, acousticness) handle
    #    gradation well because they produce continuous scores, but the string
    #    fields are all-or-nothing. A future improvement would be a "mood
    #    family" mapping (e.g., focused ≈ chill ≈ relaxed) so nearby moods
    #    earn partial credit instead of zero.
    # ─────────────────────────────────────────────────────────────────────────
    user_prefs = {
        # Categorical preferences (exact-match in scoring)
        "favorite_genre": "lofi",       # primary genre target
        "favorite_mood":  "focused",    # primary mood target

        # Numeric targets — scored by closeness (1 - abs(song_val - target))
        "target_energy":        0.45,   # calm but not completely passive
        "target_tempo":         82.0,   # steady pace, not driving or sleepy
        "target_valence":       0.60,   # slightly positive, not euphoric
        "target_danceability":  0.55,   # moderate; not a workout playlist
        "target_acousticness":  0.75,   # prefers warm/organic sounds

        # Boolean flag (songs matching this get a bonus in scoring)
        "likes_acoustic": True,
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

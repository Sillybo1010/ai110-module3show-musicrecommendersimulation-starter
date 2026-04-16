# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world music recommenders like Spotify or YouTube Music work by building a numerical model of both the song and the listener — capturing audio features (tempo, energy, mood) alongside behavioral signals (play history, skips, saves) — then ranking candidates by how closely they match a user's learned profile. They rely on massive datasets and often blend collaborative filtering (what similar users liked) with content-based matching (how the song's features compare to past favorites). This simulation focuses on the **content-based** side of that pipeline: it prioritizes explicit, interpretable features — genre, mood, energy, and acoustic character — and scores each song by how well it matches a user's stated preferences. The goal is transparency: every recommendation can be explained by pointing directly to the feature weights that drove the score.

### Song features

Each `Song` object tracks the following attributes:

- `id` — unique identifier for the track
- `title` — song title
- `artist` — performing artist
- `genre` — musical genre (e.g., pop, hip-hop, jazz)
- `mood` — emotional tone (e.g., happy, melancholic, energetic)
- `energy` — float 0–1 representing intensity and activity level
- `tempo_bpm` — beats per minute
- `valence` — float 0–1 representing musical positivity
- `danceability` — float 0–1 representing how suitable the track is for dancing
- `acousticness` — float 0–1 representing how acoustic (vs. electronic) the track sounds

### UserProfile features

Each `UserProfile` object stores the following preferences:

- `favorite_genre` — the genre the user most wants to hear
- `favorite_mood` — the mood the user is currently seeking
- `target_energy` — the energy level the user prefers (float 0–1)
- `target_tempo` — beats per minute the user is targeting (float)
- `target_valence` — emotional positivity the user is targeting (float 0–1)
- `target_danceability` — danceability level the user prefers (float 0–1)
- `target_acousticness` — acoustic warmth the user prefers (float 0–1)
- `likes_acoustic` — boolean flag indicating whether the user prefers acoustic tracks

---

### Algorithm Recipe

Every song in the catalog is scored against the user profile using the following rules. Scores are summed, and the top-K songs are returned as recommendations.

| Rule | Points | How it is calculated |
|---|---|---|
| Genre match | +2.00 | Exact string match between `song.genre` and `favorite_genre` |
| Mood match | +1.00 | Exact string match between `song.mood` and `favorite_mood` |
| Energy similarity | 0 – 1.50 | `1.5 × (1 − |song.energy − target_energy|)` |
| Acousticness similarity | 0 – 1.00 | `1.0 × (1 − |song.acousticness − target_acousticness|)` |
| Tempo similarity | 0 – 1.00 | `1.0 × max(0, 1 − |song.tempo_bpm − target_tempo| ÷ 100)` |
| Valence similarity | 0 – 0.75 | `0.75 × (1 − |song.valence − target_valence|)` |
| Danceability similarity | 0 – 0.50 | `0.50 × (1 − |song.danceability − target_danceability|)` |
| Acoustic bonus | +0.50 | Applied when `likes_acoustic` is `True` and `song.acousticness > 0.6` |
| **Max possible score** | **8.25** | |

The weights reflect priority: genre is the strongest signal, energy separates feel more than any other numeric feature, and danceability is a tiebreaker. Every recommendation includes a plain-language explanation listing which rules fired and the similarity values.

### Potential Biases

- **Genre over-prioritization.** With +2.0 points for a genre match, a mediocre song in the right genre can outscore an excellent song in a related genre. A lofi fan will never see an ambient track ranked first, even though ambient and lofi feel nearly identical.
- **Mood all-or-nothing.** Mood is an exact match — "focused" earns 1.0 point and "chill" earns 0. In practice, focused and chill are close neighbors, but the system treats them as completely different, suppressing songs a real listener would enjoy.
- **Acoustic bonus skews warm.** Users who set `likes_acoustic = True` get a permanent +0.50 on every song with `acousticness > 0.6`, which can push acoustic tracks above better numerical matches. The bonus is not scaled by how acoustic the song is.
- **Catalog size amplifies gaps.** With only 20 songs, a user whose favorite genre appears once (e.g., reggae) gets almost no genre-match competition, so numeric features decide everything. A user whose genre appears five times is more sensitive to the +2.0 weight.
- **No novelty or diversity.** The system always returns the closest match. If the top five songs are all lofi tracks, nothing in the ranking pushes for variety.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"


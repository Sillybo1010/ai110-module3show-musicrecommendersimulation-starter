# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

VibeFinder 1.0 scores every song in a 20-song catalog against a user's stated preferences — genre, mood, energy, tempo, valence, danceability, and acousticness — using a weighted point system, then returns the top-K matches with a plain-language explanation of what drove each score. It was tested against six distinct user profiles (three standard, three adversarial) and one weight-shift experiment to evaluate bias and sensitivity.

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

## Terminal Output — All Profiles

Six profiles were run with `python -m src.main`. Output below is the exact terminal result.

### Profile 1 — High-Energy Pop
```
#1  Sunrise City by Neon Echo          Score: 7.47 / 8.25
    Why: genre match (pop, +2.0), mood match (happy, +1.0), energy 0.82 (sim 0.94),
         acousticness 0.18 (sim 0.92), tempo 118 bpm (sim 0.93)

#2  Gym Hero by Max Pulse               Score: 6.48 / 8.25
    Why: genre match (pop, +2.0), energy 0.93 (sim 0.95), acousticness 0.05 (sim 0.95),
         tempo 132 bpm (sim 0.93)

#3  Rooftop Lights by Indigo Parade     Score: 5.27 / 8.25
    Why: mood match (happy, +1.0), energy 0.76 (sim 0.88), acousticness 0.35 (sim 0.75),
         tempo 124 bpm (sim 0.99)

#4  Salsa Fuego by Ritmo Libre          Score: 4.47 / 8.25
    Why: energy 0.89 (sim 0.99), acousticness 0.09 (sim 0.99), tempo 142 bpm (sim 0.83)

#5  Drop Zone by Pulse Circuit          Score: 4.39 / 8.25
    Why: energy 0.95 (sim 0.93), acousticness 0.03 (sim 0.93), tempo 138 bpm (sim 0.87)
```

### Profile 2 — Chill Lofi Study
```
#1  Focus Flow by LoRoom                Score: 8.09 / 8.25
    Why: genre match (lofi, +2.0), mood match (focused, +1.0), energy 0.40 (sim 0.95),
         acousticness 0.78 (sim 0.97), tempo 80 bpm (sim 0.98), acoustic bonus (+0.5)

#2  Midnight Coding by LoRoom           Score: 7.06 / 8.25
    Why: genre match (lofi, +2.0), energy 0.42 (sim 0.97), acousticness 0.71 (sim 0.96),
         tempo 78 bpm (sim 0.96), acoustic bonus (+0.5)

#3  Library Rain by Paper Lanterns      Score: 6.88 / 8.25
    Why: genre match (lofi, +2.0), energy 0.35 (sim 0.90), acousticness 0.86 (sim 0.89),
         tempo 72 bpm (sim 0.90), acoustic bonus (+0.5)

#4  Coffee Shop Stories by Slow Stereo  Score: 4.82 / 8.25
    Why: energy 0.37 (sim 0.92), acousticness 0.89 (sim 0.86), tempo 90 bpm (sim 0.92),
         acoustic bonus (+0.5)

#5  Dirt Road Anthem by Hayfield Jones  Score: 4.60 / 8.25
    Why: energy 0.61 (sim 0.84), acousticness 0.72 (sim 0.97), tempo 96 bpm (sim 0.86),
         acoustic bonus (+0.5)
```

### Profile 3 — Deep Intense Rock
```
#1  Storm Runner by Voltline            Score: 7.67 / 8.25
    Why: genre match (rock, +2.0), mood match (intense, +1.0), energy 0.91 (sim 0.99),
         acousticness 0.10 (sim 0.98), tempo 152 bpm (sim 0.98)

#2  Gym Hero by Max Pulse               Score: 5.17 / 8.25
    Why: mood match (intense, +1.0), energy 0.93 (sim 0.99), acousticness 0.05 (sim 0.97),
         tempo 132 bpm (sim 0.82)

#3  Iron Collapse by Ashfall            Score: 4.20 / 8.25
    Why: energy 0.97 (sim 0.95), acousticness 0.04 (sim 0.96), tempo 168 bpm (sim 0.82)

#4  Salsa Fuego by Ritmo Libre          Score: 4.13 / 8.25
    Why: energy 0.89 (sim 0.97), acousticness 0.09 (sim 0.99), tempo 142 bpm (sim 0.92)

#5  Drop Zone by Pulse Circuit          Score: 4.08 / 8.25
    Why: energy 0.95 (sim 0.97), acousticness 0.03 (sim 0.95), tempo 138 bpm (sim 0.88)
```

### Profile 4 — Adversarial: Conflicting Ambient + High Energy
```
#1  Spacewalk Thoughts by Orbit Bloom   Score: 4.84 / 8.25
    Why: genre match (ambient, +2.0), energy 0.28 (sim 0.33), acousticness 0.92 (sim 0.98),
         tempo 60 bpm (sim 0.20), acoustic bonus (+0.5)

#2  Rainy Day Blues by Delta Mae        Score: 4.29 / 8.25
    Why: mood match (sad, +1.0), energy 0.34 (sim 0.39), acousticness 0.82 (sim 0.92),
         tempo 70 bpm (sim 0.30), acoustic bonus (+0.5)

#3  Dirt Road Anthem by Hayfield Jones  Score: 3.53 / 8.25
    Why: energy 0.61 (sim 0.66), acousticness 0.72 (sim 0.82), tempo 96 bpm (sim 0.56),
         acoustic bonus (+0.5)

#4  Storm Runner by Voltline            Score: 3.44 / 8.25
    Why: energy 0.91 (sim 0.96), acousticness 0.10 (sim 0.20), tempo 152 bpm (sim 0.88)

#5  Gym Hero by Max Pulse               Score: 3.35 / 8.25
    Why: energy 0.93 (sim 0.98), acousticness 0.05 (sim 0.15), tempo 132 bpm (sim 0.92)
```

> **Surprise:** Spacewalk Thoughts won despite an energy score of only 0.28 vs. the
> target of 0.95. The +2.0 genre bonus plus the +0.5 acoustic bonus (1.90 points of
> "free" categorical credit) outweighed a 0.67-point energy gap (penalty ≈ 0.50 pts).
> The system had no way to flag the contradiction.

### Profile 5 — Adversarial: Ghost Genre (K-Pop not in catalog)
```
#1  Sunrise City by Neon Echo           Score: 5.59 / 8.25
    Why: mood match (happy, +1.0), energy 0.82 (sim 0.98), acousticness 0.18 (sim 0.97),
         tempo 118 bpm (sim 0.98)

#2  Rooftop Lights by Indigo Parade     Score: 5.37 / 8.25
    Why: mood match (happy, +1.0), energy 0.76 (sim 0.96), acousticness 0.35 (sim 0.80),
         tempo 124 bpm (sim 0.96)

#3  Dirt Road Anthem by Hayfield Jones  Score: 4.52 / 8.25
    Why: mood match (happy, +1.0), energy 0.61 (sim 0.81), acousticness 0.72 (sim 0.43),
         tempo 96 bpm (sim 0.76)

#4  Salsa Fuego by Ritmo Libre          Score: 4.29 / 8.25
    Why: energy 0.89 (sim 0.91), acousticness 0.09 (sim 0.94), tempo 142 bpm (sim 0.78)

#5  Gym Hero by Max Pulse               Score: 4.25 / 8.25
    Why: energy 0.93 (sim 0.87), acousticness 0.05 (sim 0.90), tempo 132 bpm (sim 0.88)
```

> No song earned the +2.0 genre bonus. The system fell back silently to numeric and
> mood matching. Max scores dropped to ~5.6 — a clear signal that genre is missing.

### Profile 6 — Adversarial: Max Mismatch Classical Serenity
```
#1  Moonlit Sonata by Clara Voss        Score: 8.11 / 8.25
    Why: genre match (classical, +2.0), mood match (peaceful, +1.0), energy 0.22 (sim 0.96),
         acousticness 0.97 (sim 0.99), tempo 58 bpm (sim 0.97), acoustic bonus (+0.5)

#2  Spacewalk Thoughts by Orbit Bloom   Score: 4.88 / 8.25
#3  Faded Photographs by Birch & Wire   Score: 4.54 / 8.25
#4  Library Rain by Paper Lanterns      Score: 4.48 / 8.25
#5  Coffee Shop Stories by Slow Stereo  Score: 4.31 / 8.25
```

---

## Experiments You Tried

### Weight Shift: Genre 2.0 → 1.0 / Energy 1.5 → 3.0 (High-Energy Pop profile)

**Hypothesis:** Halving genre weight and doubling energy weight should pull
non-pop high-energy songs (Salsa Fuego, Drop Zone) higher in the list.

```
#1  Sunrise City by Neon Echo    Score: 7.88   (was 7.47)
#2  Gym Hero by Max Pulse        Score: 6.91   (was 6.48)
#3  Rooftop Lights by Indigo     Score: 6.59   (was 5.27)  ← jumped
#4  Salsa Fuego by Ritmo Libre   Score: 5.96   (was 4.47)  ← jumped
#5  Drop Zone by Pulse Circuit   Score: 5.78   (was 4.39)  ← jumped
```

**Finding:** The top-2 order did not change because Sunrise City and Gym Hero
both have high energy *and* a genre match — they benefit from both weights. But
#3–5 all rose significantly because the reduced genre penalty now lets high-energy
songs from other genres compete on equal footing. The gap between #2 (pop, 6.91)
and #3 (non-pop, 6.59) shrank from 1.21 to 0.32 — energy weight now almost
compensates for the missing genre bonus.

**Conclusion:** The original genre weight of 2.0 is too dominant for users whose
primary interest is a *feel* (high energy) rather than a specific genre label.

---

## Limitations and Risks

- **Genre dominance.** The +2.0 genre bonus is the single largest score component. A song with a genre match and mediocre numeric fit outscores a song with no genre match and near-perfect numeric fit. This is the primary source of filter-bubble behavior.
- **No partial mood credit.** "Focused" and "chill" are treated as completely different. A song will score 0 mood points even if its mood is a natural neighbor.
- **Contradictory profiles produce silent failures.** The system cannot detect when preferences conflict (e.g., high-energy + highly-acoustic) and returns a best-effort answer without warning.
- **20-song catalog.** Genre-unique tracks (classical, metal, reggae each appear once) face no in-genre competition. Results are highly sensitive to catalog size.
- **No diversity enforcement.** The top-5 can be 5 songs from the same genre if that genre has enough entries and the user's profile matches.

See [model_card.md](model_card.md) for deeper analysis.

---

## Reflection

[**Model Card**](model_card.md)

**What I learned about recommenders turning data into predictions:**
The most important insight is that a recommender is only as good as its feature weights, and those weights encode assumptions about what matters most to users. Choosing +2.0 for genre and +1.5 for energy is a hypothesis about human taste — not a fact. When I ran the weight-shift experiment and halved the genre bonus, the rankings changed meaningfully, which means the original system was really answering the question "who matches this genre?" rather than "who sounds like what this user wants?" A more honest system would learn those weights from actual listening behavior rather than guessing.

**Profile comparison — EDM vs. Acoustic user:**
Comparing the High-Energy Pop profile (energy 0.88, acousticness 0.10) and the Max Mismatch Classical Serenity profile (energy 0.18, acousticness 0.98) shows the system behaving exactly as designed: the two lists share zero songs. The EDM-adjacent profile surfaces Salsa Fuego and Drop Zone; the classical profile surfaces Moonlit Sonata and Spacewalk Thoughts. The energy and acousticness features are doing real work — they pull the lists in completely opposite directions. This makes sense: a person studying quietly and a person running a 5K want fundamentally different audio environments, and those features capture that difference cleanly.

**Where bias or unfairness could show up:**
The conflicting-preferences edge case is the clearest example. A user who asks for "ambient + high energy" is probably imagining a niche style (cinematic, lo-fi electronic) that simply does not exist in this catalog. The system returned Spacewalk Thoughts as #1 — a genuinely quiet ambient track — because the genre label matched and the categorical bonus overrode the failed numeric match. The user would get results and never know the system had effectively ignored half their request. In a real product, that silent failure erodes trust over time.


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


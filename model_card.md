# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder scores and ranks songs from a small 20-song catalog based on a user's
stated genre preference, mood preference, and numeric audio targets (energy, tempo,
valence, danceability, acousticness). It is a classroom simulation of the
content-based filtering layer found in real music apps. It is not trained on play
history and makes no personalization beyond the preferences the caller explicitly
provides.

---

## 3. How the Model Works

Imagine a judge who reads a description card for every song in the library and gives
it points based on how well it matches what you asked for. That is exactly what
VibeFinder does.

For each song it checks two things first: does the song's genre match your favorite
genre? Does its mood match the mood you want right now? A genre match earns the most
points because genre is the strongest signal of whether you will enjoy a song. A mood
match earns slightly fewer points.

Then it measures how close the song's numbers are to your targets. If you want
high-energy music and the song is high-energy, it scores close to the maximum for
that feature. If the song is quiet and you wanted loud, it scores near zero for that
feature. The same check runs for tempo, emotional positivity (valence), danceability,
and acoustic warmth.

Finally, if you said you prefer acoustic music and the song is genuinely acoustic, it
gets a small bonus.

All those individual scores are added up into one total number. Every song in the
catalog gets scored this way, the list is sorted from highest to lowest, and the top
five are returned as recommendations along with a plain-language explanation of what
drove the score.

---

## 4. Data

The catalog contains **20 songs** across 17 distinct genres: pop, lofi, rock, ambient,
jazz, synthwave, indie pop, hip-hop, classical, r&b, country, latin, metal, folk,
electronic, blues, and reggae. Each genre appears exactly once except pop (2 songs:
Sunrise City, Gym Hero) and lofi (3 songs: Midnight Coding, Library Rain, Focus Flow).

Moods represented: happy, chill, intense, relaxed, focused, moody, nostalgic,
peaceful, romantic, energetic, angry, euphoric, melancholic, sad.

No songs were removed. The data was not augmented. The catalog skews toward Western
contemporary music; there are no songs representing genres like J-pop, Afrobeats,
Bollywood, or traditional folk from non-Western cultures.

---

## 5. Strengths

- **Clear genre leaders score convincingly.** When the catalog contains multiple songs
  in the user's genre (lofi has 3 entries), the top results are well-separated and
  internally ranked by numeric fit. Focus Flow scores 8.09/8.25 because it matches on
  genre, mood, energy, acousticness, and tempo simultaneously.

- **Single-song genres still work.** The classical profile found Moonlit Sonata (the
  only classical song) at #1 with 8.11/8.25 — nearly a perfect score — because all
  its numeric features matched the target profile closely.

- **Explanations are transparent.** Every recommendation comes with a reason string
  that names exactly which rules fired and the similarity value for each numeric
  feature. A user can read "energy 0.82 (sim 0.94)" and understand what happened.

- **Weights are configurable.** The experiment API lets any caller override individual
  weights without touching the core logic, making sensitivity tests simple to run.

---

## 6. Limitations and Bias

**Genre over-prioritization creates a filter bubble.** The +2.0 genre bonus is so
large that even a mediocre numeric match within the correct genre beats a nearly
perfect numeric match in a related genre. In the Chill Lofi Study run, the #3 result
(Library Rain, score 6.88) is a lofi song with slightly worse numeric fit than Coffee
Shop Stories (jazz, score 4.82) — a song that would likely feel identical to a real
listener. The system will never recommend an ambient track to a lofi fan even though
the two genres share virtually the same sonic character, because no partial genre
credit exists.

**Mood is all-or-nothing with no neighborhood.** "Focused" and "chill" feel like
close neighbors — in practice most study-music listeners accept both — but the system
treats them as completely separate categories. A song with mood "chill" earns zero
mood points for a user targeting "focused," which suppresses songs a real listener
would enjoy.

**Conflicting profiles expose acousticness vs. energy tension.** The Conflicting
(Ambient + High Energy) profile asked for acousticness 0.90 AND energy 0.95 at the
same time. No song in the catalog scores high on both — high-acoustic songs are
uniformly low-energy. The genre bonus kept Spacewalk Thoughts (ambient, energy 0.28)
at #1 with only 4.84/8.25, even though it failed badly on energy. The system has no
way to signal "this was a contradictory request."

**The ghost genre problem.** When a user's favorite genre does not appear in the
catalog at all (the K-Pop profile), the system silently falls back to mood and numeric
features. Sunrise City still ranked first purely on numeric similarity. This is
reasonable behavior but is never communicated to the user.

**Small catalog amplifies all biases.** With 20 songs, a genre that appears 3 times
(lofi) dominates any lofi user's top results by default. A genre that appears once
(classical, metal, reggae) means the system is choosing between 19 songs where 18
earn zero genre bonus. In a real catalog of millions of songs these gaps would be
invisible; here they control the entire ranking.

---

## 7. Evaluation

Six user profiles were run through the recommender and their top-5 results were
inspected:

| Profile | Top result | Score | Observation |
|---|---|---|---|
| High-Energy Pop | Sunrise City | 7.47 | Genre + mood + numeric all aligned — felt right |
| Chill Lofi Study | Focus Flow | 8.09 | Near-perfect match; all lofi songs filled top 3 |
| Deep Intense Rock | Storm Runner | 7.67 | Correct — only rock song, all features matched |
| Conflicting: Ambient + High Energy | Spacewalk Thoughts | 4.84 | Genre won despite terrible energy/tempo match |
| Ghost Genre: K-Pop | Sunrise City | 5.59 | Fell back cleanly to numeric; no genre bonus fired |
| Max Mismatch: Classical Serenity | Moonlit Sonata | 8.11 | Perfect — single classical song, all numerics fit |

**Weight-shift experiment (High-Energy Pop, genre 2.0→1.0 / energy 1.5→3.0):**
The ranking order did not change — Sunrise City stayed #1 — but Salsa Fuego and Drop
Zone moved up from #4 and #5, while their scores grew relative to the pop songs,
showing the energy weight now pulls non-pop high-energy tracks closer to the leaders.
The experiment confirmed that halving the genre bonus narrows the gap between in-genre
and out-of-genre songs without fully inverting the list.

**Surprise:** The Conflicting profile revealed that the acousticness preference was
far more influential than expected. Spacewalk Thoughts won its genre bonus (+2.0) and
then also won the acoustic bonus (+0.5) even though its energy (0.28) was 0.67 points
away from the user's target (0.95). The energy penalty was only 0.33 × 1.5 = 0.50
points. Two bonuses covering completely different features can easily outvote a large
miss on a single feature.

---

## 8. Future Work

- **Mood neighborhood mapping.** Group moods into families (e.g., focused ≈ chill ≈
  relaxed; intense ≈ energetic ≈ angry) and award partial points for adjacent moods
  instead of treating mood as all-or-nothing.

- **Genre similarity graph.** Score partial credit for related genres (lofi ≈
  ambient ≈ jazz; metal ≈ rock) so the +2.0 bonus decays gracefully rather than
  cutting off completely.

- **Conflict detection.** Warn when the user's numeric targets contradict each other
  (e.g., high-energy + high-acousticness) so the user understands why scores are low.

- **Diversity re-ranking.** After scoring, apply a penalty for consecutive songs by
  the same artist or in the same genre so the top-5 list is not always dominated by
  one genre cluster.

- **Catalog expansion.** With 20 songs, every genre appears once or twice. A
  meaningful evaluation requires at least 5–10 songs per genre.

---

## 9. Personal Reflection

Building this system made it clear how much a single design choice — the +2.0 genre
bonus — shapes every output. Before running the experiments I expected the numeric
features (energy, tempo, acousticness) to do most of the work because they are
continuous and fine-grained. In practice, the flat two-point reward for a genre string
match overrode everything else in almost every profile. This is the same dynamic that
causes Spotify to lock users into one corner of its catalog: if the system weights
past genre too heavily, it never discovers that you might enjoy something adjacent.

The conflicting-preferences experiment was the most revealing. A real listener who
wanted "ambient but high-energy" is probably describing lo-fi electronic or cinematic
orchestral music — something that exists in the real world but is absent from this
catalog. The recommender had no way to express "I cannot satisfy this combination" and
instead returned its best approximation using the genre bonus as a tiebreaker. That
gap between "the system found an answer" and "the answer was actually good" is exactly
the kind of silent failure that makes AI systems hard to trust in production.

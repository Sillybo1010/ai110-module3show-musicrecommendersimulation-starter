# 🎧 Model Card — VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender simulation built for a classroom AI course.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *given what a user says they like right now,
which songs in the catalog are the best match?*

It does not predict what you will listen to next based on history. It does not learn
over time. It takes a snapshot of your stated preferences — genre, mood, energy level,
tempo, and acoustic warmth — and ranks every song in the catalog by how well it fits
those preferences at that moment.

---

## 3. Data Used

- **Catalog size:** 20 songs
- **Features per song:** genre (string), mood (string), energy (0–1), tempo in BPM,
  valence (0–1), danceability (0–1), acousticness (0–1)
- **Genres covered:** 17 — pop, lofi, rock, ambient, jazz, synthwave, indie pop,
  hip-hop, classical, r&b, country, latin, metal, folk, electronic, blues, reggae
- **Moods covered:** happy, chill, intense, relaxed, focused, moody, nostalgic,
  peaceful, romantic, energetic, angry, euphoric, melancholic, sad

**Limits of this data:**
- 20 songs is tiny. Most genres appear only once.
- The catalog is almost entirely Western music. Genres like Afrobeats, Bollywood,
  J-pop, and traditional folk from non-Western cultures are completely absent.
- No song has explicit lyrics data, language data, or release year.
- The numeric features (energy, valence, etc.) were assigned by hand for this
  simulation — they are not derived from audio analysis tools like Spotify's API.

---

## 4. Algorithm Summary

VibeFinder is a scoring engine, not a machine learning model. It never trains on data.
Here is how it works in plain language:

For every song in the catalog, a "judge" runs down a checklist:

1. **Does the genre match?** If yes, the song earns the biggest reward — 2 full points.
   Genre is the strongest signal of whether you will enjoy a track.

2. **Does the mood match?** If yes, the song earns 1 point. Mood matters, but it is
   slightly less reliable than genre as a predictor.

3. **How close is the energy?** If you want high-energy music and this song is
   high-energy, it scores near the maximum for this check (up to 1.5 points). If they
   are far apart, the score drops toward zero.

4. **How acoustic does it sound?** Acoustic warmth is scored the same way — the closer
   the song is to your target, the more points it earns (up to 1.0 point).

5. **How close is the tempo?** Measured in beats per minute. A gap of 100 BPM or more
   scores zero; a perfect match scores 1.0 point.

6. **How positive does it feel?** Valence (musical positivity) adds up to 0.75 points.

7. **How danceable is it?** Danceability adds up to 0.5 points as a tiebreaker.

8. **Acoustic bonus.** If you said you like acoustic music and this song is genuinely
   acoustic, it earns an extra 0.5 points.

All eight numbers are added together into one score. The catalog is sorted from
highest to lowest score, and the top 5 songs are returned as recommendations. Every
recommendation also includes a plain sentence explaining which rules fired and by how
much.

**Maximum possible score: 8.25 points.**

---

## 5. Observed Behavior and Biases

**Genre creates a filter bubble.**
The 2-point genre bonus is the largest single reward in the system. A song in the
right genre with mediocre numeric fit almost always beats a song in a related genre
with near-perfect numeric fit. A lofi fan will never see an ambient track in their
top-5, even though the two genres feel nearly identical. This is the same filter
bubble problem that real apps like Spotify face when they over-weight past genre
history.

**Mood is all-or-nothing.**
"Focused" and "chill" feel like close neighbors, but the system treats them as
completely different. A song tagged "chill" earns zero mood points for a user who
asked for "focused." This suppresses songs a real listener would find perfectly
acceptable.

**Conflicting preferences produce silent failures.**
When a user asks for "ambient" (which is always quiet) but also sets energy target
to 0.95 (workout level), no song in the catalog can satisfy both. The system returns
its best guess — a quiet ambient track — without ever telling the user that their
request was contradictory. In testing, the top score for this profile was only 4.84
out of 8.25, a signal the system cannot communicate.

**The catalog is too small.**
With only 20 songs, any genre that appears three times (lofi) automatically dominates
results for users who prefer that genre. Genres that appear once (classical, metal,
reggae) produce a top result that is essentially just "the only song we have." In a
real catalog of millions of songs this would not be a problem; here it controls the
entire ranking.

---

## 6. Evaluation Process

Six user profiles were defined and run through the recommender. Three were designed to
test normal use; three were designed to find edge cases and break points.

| Profile | Type | What it tested |
|---|---|---|
| High-Energy Pop | Standard | Genre + mood + high numerics all aligned |
| Chill Lofi Study | Standard | Quiet, acoustic, focus-oriented |
| Deep Intense Rock | Standard | High energy, electric, aggressive feel |
| Conflicting: Ambient + High Energy | Adversarial | What happens when preferences contradict |
| Ghost Genre: K-Pop | Adversarial | What happens when the genre is not in the catalog |
| Max Mismatch: Classical Serenity | Adversarial | Extreme quiet and acoustic preferences |

For each profile the top-5 results were inspected and compared against musical
intuition. The key questions were: does the #1 result feel right? Are there any
surprising entries that should not be there?

**Weight-shift experiment:** The High-Energy Pop profile was re-run with the genre
weight halved (2.0 → 1.0) and the energy weight doubled (1.5 → 3.0). The top-2 order
did not change, but non-pop high-energy songs (Salsa Fuego, Drop Zone) moved
significantly up the list, confirming that the original genre weight was strong enough
to suppress songs that matched the user's actual feel.

**Key findings:**
- When genre and numerics aligned (standard profiles), the results felt accurate.
- The conflicting profile exposed the biggest weakness: categorical bonuses can
  override large numeric misses without any warning to the user.
- The ghost genre profile showed graceful degradation — no crash, no wrong behavior,
  just lower scores across the board.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- A classroom simulation to explore how content-based filtering works.
- A starting point for experimenting with different feature weights and scoring rules.
- A tool to understand why filter bubbles happen in real recommender systems.

**Not intended for:**
- Real music discovery for real users. The 20-song catalog is far too small.
- Replacing behavior-based recommendations. VibeFinder knows nothing about what you
  have listened to before, skipped, or saved.
- Any application where fairness or representation matters. The catalog is culturally
  narrow and the genre weights would disadvantage users whose preferred genres are
  underrepresented.
- Production deployment of any kind.

---

## 8. Ideas for Improvement

**Mood neighborhoods.** Instead of treating "focused" and "chill" as completely
different, group moods into families and give partial credit for adjacent moods. A
user asking for "focused" music would still prefer "focused" songs, but a "chill" song
would score 0.5 mood points instead of zero.

**Genre similarity.** Give partial genre credit for related genres — lofi ≈ ambient ≈
jazz, metal ≈ rock — so the +2.0 bonus decays smoothly rather than cutting off
completely. This alone would eliminate most of the filter-bubble behavior.

**Conflict detection.** Before scoring, check whether the user's numeric targets are
internally consistent. If energy target is above 0.8 and acousticness target is above
0.8 at the same time, flag it: "These preferences rarely appear together in the
catalog. Results may not feel satisfying."

---

## 9. Personal Reflection

**Biggest learning moment:**
I expected the numeric features — energy, tempo, acousticness — to drive the
rankings, because they are continuous and can express fine-grained differences between
songs. What actually happened is the opposite: the flat +2.0 genre bonus dominated
almost every result. A song that matched on genre and failed on everything else still
usually beat a song that matched on every numeric feature but had the wrong genre
label. That one design choice — treating genre as a yes/no worth two full points —
determined the character of the entire system. The lesson is that in a scoring system,
weights are not just numbers; they are opinions about what matters most, and they
should be chosen deliberately.

**How AI tools helped and when I had to double-check:**
AI was useful for generating boilerplate code (the CSV loader, the sorted/sort
comparison) and for suggesting the structure of the scoring function. But I had to
verify every piece of math myself. The AI-generated reason-list logic initially joined
reasons before checking if the list was empty, which would have produced empty
explanations for songs that matched nothing. I also had to manually check that
`sorted()` was used instead of `.sort()` — the AI suggested both at different points
in the same session and I had to confirm which one was non-mutating. The general rule
I learned: trust the AI for structure, verify the details yourself.

**What surprised me about how a simple algorithm can feel like a recommendation:**
The results for the standard profiles genuinely felt right the first time I ran them.
Focus Flow came up #1 for the study-music profile, Storm Runner came up #1 for the
rock profile, and the explanations were readable and made sense. There is no
intelligence here — just addition and comparison — but because the features were
chosen to reflect things humans actually care about (energy, acoustic feel, tempo),
the outputs felt meaningful. That is the core trick of content-based filtering: if you
pick the right features, simple math produces outputs that feel like taste. It does
not actually understand music; it just measures the things that correlate with whether
you will enjoy it.

**What I would try next:**
The single change that would most improve VibeFinder is replacing the exact-match
genre and mood fields with similarity scores. Instead of "lofi = 1, everything else =
0," a genre graph would let ambient score 0.7, jazz score 0.5, and metal score 0.0
against a lofi user. That change alone would eliminate the filter bubble without
touching any other part of the system. After that, I would want to test on a real
user — give someone the recommender with no explanation, ask them to set their
preferences, and then ask them whether the top-5 results matched what they actually
wanted to hear. Human evaluation of one real user would tell me more than six
synthetic profiles ever could.

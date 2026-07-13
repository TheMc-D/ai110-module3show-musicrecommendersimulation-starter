# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeCheck 1.0**

---

## 2. Intended Use  

**Goal:** VibeCheck is a toy recommender. You give it four things you like (a genre, a
mood, a target energy level, and whether you like acoustic songs), and it picks the top
5 songs out of a small 18-song catalog that best match those four things. It also prints
a plain-English reason for every point each song earned.

**What it assumes about the user:**
- You have exactly one favorite genre and one favorite mood, not a mix of several
- You can name a single "target energy" number (0 to 1) and every song either gets
  closer to it or farther away — there's no "I like variety" option
- Your taste doesn't change from song to song

**This is for classroom exploration, not real users.** It's a teaching tool for
understanding how a recommender turns preferences into a ranked list, and for spotting
bias in that process — not a music app anyone should actually use to find songs.

**Intended use:**
- Learning how simple, rule-based recommenders work
- Practicing how to test a scoring system for bias and edge cases

**Not intended for:**
- Recommending music to real listeners
- Any situation where the ranking needs to be fair, unbiased, or accurate (e.g.
  deciding what music gets promoted, paid for, or played)
- Anything beyond this exact 18-song catalog — the weights were hand-tuned for this
  small dataset and would need rework on a bigger, real one

---

## 3. How the Model Works  

Every song gets scored out of 6 points, built from four simple checks:

1. **Genre match (worth 2 points):** Is the song's genre the one you said you like? If
   yes, +2.
2. **Mood match (worth 1 point):** Is the song's mood the one you said you like? If yes,
   +1.
3. **Energy closeness (worth up to 2 points):** How close is the song's energy to the
   energy level you asked for? A perfect match earns the full 2 points, and the points
   shrink smoothly the farther off it is — so even a song with the "wrong" energy still
   earns *some* credit for being close.
4. **Acoustic fit (worth 1 point):** Did you say you like or dislike acoustic songs? If
   the song matches what you said, +1.

The app scores every song in the catalog this way, sorts them from highest score to
lowest, and hands back the top 5 with an explanation for each one.

Genre gets the most weight because I treat it as your strongest, most personal taste
signal. Energy is tied with genre for the same max points because it's the one signal
that contributes *something* even when genre and mood don't match at all — which
happens a lot, since most songs in this small catalog have a genre no other song
shares. Mood and acoustic fit are worth less because they act more like a bonus than a
dealbreaker.

I didn't change the core idea from the starter logic, but I did add: the point values
for each of the four checks, the closeness math for energy, the acoustic yes/no
threshold, and the plain-English explanation printed under each song.

---

## 4. Data  

The catalog has 18 songs, hand-made for this project — not real streaming data. Each
song has a title, artist, genre, mood, energy (0–1), tempo, valence, danceability,
acousticness (0–1), instrumentalness, and popularity.

15 of the 18 genres only appear once — only "lofi" (3 songs) and "pop" (2 songs) show up
more than once. That means most "favorite genre" answers will only ever match one song
in the whole catalog, if any. Moods are just as spread out: 13 different moods across 18
songs.

I didn't add or remove any songs from the starter dataset. Because the catalog is so
small and so spread across genres, it's missing a lot of real musical variety — there's
no way to test two songs that share both a genre *and* a mood, and common real-world
genres like metal, k-pop, or Latin music aren't represented at all.

---

## 5. Strengths  

The system does well when a user's taste matches a genre/mood combo that actually
exists in the catalog and doesn't fight with itself. For example, "High-Energy Pop"
(pop, happy, high energy, non-acoustic) returns songs that genuinely feel right — bright,
upbeat pop tracks land at the top, and the printed explanation for each one matches what
I'd expect just from reading the song's genre and mood.

It's also good at telling apart two very different users. Comparing a "Chill Lofi"
profile (quiet, acoustic) against a "Deep Intense Rock" profile (loud, non-acoustic),
their top-5 lists shared zero songs — exactly what should happen for two people with
opposite taste.

The scoring is also consistent and easy to explain: every score traces back to the same
four rules, and the app prints out exactly why each song earned its points, so a
recommendation is never a mystery.

---

## 6. Limitations and Bias 

The stress test in the Evaluation section below surfaced a genuine filter-bubble effect:
the five highest-energy tracks in the entire 18-song catalog (energy 0.82–0.97) —
`Gym Hero`, `Storm Runner`, `Sunrise City`, `Neon Pulse`, and `Broken Amp` — dominated the
top-5 results for almost every profile with `target_energy >= 0.85`, regardless of the
requested genre or mood; `Gym Hero` alone appeared in 5 of the 7 profiles tested. This
happens because `ENERGY_MATCH_MAX_POINTS` (2.0) is weighted equal to
`GENRE_MATCH_POINTS` and applies continuously to *every* song, while 15 of the catalog's
18 songs have a genre that appears nowhere else in the data — so once no exact
genre/mood match exists (the common case), the ranking collapses almost entirely to
"which songs sit closest to the target energy," independent of what the user actually
asked for. The practical effect is that a fan of `edm`, a fan of `rock`, and a fan of a
genre that isn't even in the catalog (e.g. `metal`) all get funneled toward nearly the
same handful of loud tracks once their `target_energy` is high, even though their stated
tastes are otherwise unrelated. This also compounds with a data imbalance — `lofi` (3 of
18 songs) and `pop` (2 of 18) are the only genres with more than one entry, so fans of
those two get a real chance at a genre-match bonus while fans of the other 13
single-song genres are scored almost entirely on energy/acoustic proximity alone.

---

## 7. Evaluation  

### Profiles tested

I stress-tested `src/main.py` (`USER_PROFILES` dict) with three distinct "normal" taste
profiles plus four adversarial / edge-case profiles suggested by an AI assistant acting
as a "system evaluation" reviewer — the goal of the adversarial set was specifically to
try to break the scoring logic or expose silently wrong behavior (conflicting signals,
genres that don't exist in the catalog, boundary values).

Command: `python -m src.main`

**High-Energy Pop** — genre=pop, mood=happy, target_energy=0.9, likes_acoustic=False

```
============================================================
                  PROFILE: High-Energy Pop                  
============================================================
genre=pop, mood=happy, target_energy=0.90, likes_acoustic=False

1. Sunrise City by Neon Echo
   Score: 5.84 / 6.00
   - genre match: pop (+2.0)
   - mood match: happy (+1.0)
   - energy (0.82 vs target 0.90) (+1.84)
   - non-acoustic fit (+1.0)

2. Gym Hero by Max Pulse
   Score: 4.94 / 6.00
   - genre match: pop (+2.0)
   - energy (0.93 vs target 0.90) (+1.94)
   - non-acoustic fit (+1.0)

3. Rooftop Lights by Indigo Parade
   Score: 3.72 / 6.00
   - mood match: happy (+1.0)
   - energy (0.76 vs target 0.90) (+1.72)
   - non-acoustic fit (+1.0)

4. Storm Runner by Voltline
   Score: 2.98 / 6.00
   - energy (0.91 vs target 0.90) (+1.98)
   - non-acoustic fit (+1.0)

5. Neon Pulse by Kilowatt
   Score: 2.90 / 6.00
   - energy (0.95 vs target 0.90) (+1.90)
   - non-acoustic fit (+1.0)
```

**Chill Lofi** — genre=lofi, mood=chill, target_energy=0.3, likes_acoustic=True

```
============================================================
                    PROFILE: Chill Lofi                     
============================================================
genre=lofi, mood=chill, target_energy=0.30, likes_acoustic=True

1. Library Rain by Paper Lanterns
   Score: 5.90 / 6.00
   - genre match: lofi (+2.0)
   - mood match: chill (+1.0)
   - energy (0.35 vs target 0.30) (+1.90)
   - acoustic fit (+1.0)

2. Midnight Coding by LoRoom
   Score: 5.76 / 6.00
   - genre match: lofi (+2.0)
   - mood match: chill (+1.0)
   - energy (0.42 vs target 0.30) (+1.76)
   - acoustic fit (+1.0)

3. Focus Flow by LoRoom
   Score: 4.80 / 6.00
   - genre match: lofi (+2.0)
   - energy (0.40 vs target 0.30) (+1.80)
   - acoustic fit (+1.0)

4. Spacewalk Thoughts by Orbit Bloom
   Score: 3.96 / 6.00
   - mood match: chill (+1.0)
   - energy (0.28 vs target 0.30) (+1.96)
   - acoustic fit (+1.0)

5. River Bend Hymn by Willow Creek
   Score: 3.00 / 6.00
   - energy (0.30 vs target 0.30) (+2.00)
   - acoustic fit (+1.0)
```

**Deep Intense Rock** — genre=rock, mood=intense, target_energy=0.95, likes_acoustic=False

```
============================================================
                 PROFILE: Deep Intense Rock                 
============================================================
genre=rock, mood=intense, target_energy=0.95, likes_acoustic=False

1. Storm Runner by Voltline
   Score: 5.92 / 6.00
   - genre match: rock (+2.0)
   - mood match: intense (+1.0)
   - energy (0.91 vs target 0.95) (+1.92)
   - non-acoustic fit (+1.0)

2. Gym Hero by Max Pulse
   Score: 3.96 / 6.00
   - mood match: intense (+1.0)
   - energy (0.93 vs target 0.95) (+1.96)
   - non-acoustic fit (+1.0)

3. Neon Pulse by Kilowatt
   Score: 3.00 / 6.00
   - energy (0.95 vs target 0.95) (+2.00)
   - non-acoustic fit (+1.0)

4. Broken Amp by Fault Line
   Score: 2.96 / 6.00
   - energy (0.97 vs target 0.95) (+1.96)
   - non-acoustic fit (+1.0)

5. Sunrise City by Neon Echo
   Score: 2.74 / 6.00
   - energy (0.82 vs target 0.95) (+1.74)
   - non-acoustic fit (+1.0)
```

### Adversarial / edge-case profiles

**Conflicting: High Energy + Sad Mood** — genre=pop, mood=melancholic, target_energy=0.9,
likes_acoustic=False. Designed to see what happens when a user asks for something
internally tense (very high energy *and* a sad/melancholic mood) that no real song in
the catalog embodies.

```
============================================================
        PROFILE: Conflicting: High Energy + Sad Mood        
============================================================
genre=pop, mood=melancholic, target_energy=0.90, likes_acoustic=False

1. Gym Hero by Max Pulse
   Score: 4.94 / 6.00
   - genre match: pop (+2.0)
   - energy (0.93 vs target 0.90) (+1.94)
   - non-acoustic fit (+1.0)

2. Sunrise City by Neon Echo
   Score: 4.84 / 6.00
   - genre match: pop (+2.0)
   - energy (0.82 vs target 0.90) (+1.84)
   - non-acoustic fit (+1.0)

3. Storm Runner by Voltline
   Score: 2.98 / 6.00
   - energy (0.91 vs target 0.90) (+1.98)
   - non-acoustic fit (+1.0)

4. Neon Pulse by Kilowatt
   Score: 2.90 / 6.00
   - energy (0.95 vs target 0.90) (+1.90)
   - non-acoustic fit (+1.0)

5. Broken Amp by Fault Line
   Score: 2.86 / 6.00
   - energy (0.97 vs target 0.90) (+1.86)
   - non-acoustic fit (+1.0)
```

**Out-of-Catalog Genre (metal)** — genre=metal, mood=angry, target_energy=0.85,
likes_acoustic=False. There is no "metal" genre anywhere in `songs.csv`, so this checks
whether the system errors out or silently degrades when a preference can never be
satisfied.

```
============================================================
           PROFILE: Out-of-Catalog Genre (metal)            
============================================================
genre=metal, mood=angry, target_energy=0.85, likes_acoustic=False

1. Broken Amp by Fault Line
   Score: 3.76 / 6.00
   - mood match: angry (+1.0)
   - energy (0.97 vs target 0.85) (+1.76)
   - non-acoustic fit (+1.0)

2. Sunrise City by Neon Echo
   Score: 2.94 / 6.00
   - energy (0.82 vs target 0.85) (+1.94)
   - non-acoustic fit (+1.0)

3. Storm Runner by Voltline
   Score: 2.88 / 6.00
   - energy (0.91 vs target 0.85) (+1.88)
   - non-acoustic fit (+1.0)

4. Gym Hero by Max Pulse
   Score: 2.84 / 6.00
   - energy (0.93 vs target 0.85) (+1.84)
   - non-acoustic fit (+1.0)

5. Rooftop Lights by Indigo Parade
   Score: 2.82 / 6.00
   - energy (0.76 vs target 0.85) (+1.82)
   - non-acoustic fit (+1.0)
```

**Contradiction: Acoustic-Loving Raver** — genre=edm, mood=euphoric, target_energy=0.95,
likes_acoustic=True. This pairs a maximally energetic genre/mood combo with a preference
(likes_acoustic=True) that almost never co-occurs with high energy in this catalog —
designed to see if the system silently "gives up" one of the conflicting signals.

```
============================================================
       PROFILE: Contradiction: Acoustic-Loving Raver        
============================================================
genre=edm, mood=euphoric, target_energy=0.95, likes_acoustic=True

1. Neon Pulse by Kilowatt
   Score: 5.00 / 6.00
   - genre match: edm (+2.0)
   - mood match: euphoric (+1.0)
   - energy (0.95 vs target 0.95) (+2.00)

2. Dusty Backroads by Cotton & Rye
   Score: 2.00 / 6.00
   - energy (0.45 vs target 0.95) (+1.00)
   - acoustic fit (+1.0)

3. Gym Hero by Max Pulse
   Score: 1.96 / 6.00
   - energy (0.93 vs target 0.95) (+1.96)

4. Broken Amp by Fault Line
   Score: 1.96 / 6.00
   - energy (0.97 vs target 0.95) (+1.96)

5. Midnight Coding by LoRoom
   Score: 1.94 / 6.00
   - energy (0.42 vs target 0.95) (+0.94)
   - acoustic fit (+1.0)
```

**Boundary: Zero Energy Target** — genre=classical, mood=melancholic, target_energy=0.0,
likes_acoustic=True. Tests the extreme edge of the valid `[0, 1]` energy range rather
than an out-of-range value.

```
============================================================
           PROFILE: Boundary: Zero Energy Target            
============================================================
genre=classical, mood=melancholic, target_energy=0.00, likes_acoustic=True

1. Winter Sonata by Elena Vasquez
   Score: 5.56 / 6.00
   - genre match: classical (+2.0)
   - mood match: melancholic (+1.0)
   - energy (0.22 vs target 0.00) (+1.56)
   - acoustic fit (+1.0)

2. Spacewalk Thoughts by Orbit Bloom
   Score: 2.44 / 6.00
   - energy (0.28 vs target 0.00) (+1.44)
   - acoustic fit (+1.0)

3. River Bend Hymn by Willow Creek
   Score: 2.40 / 6.00
   - energy (0.30 vs target 0.00) (+1.40)
   - acoustic fit (+1.0)

4. Library Rain by Paper Lanterns
   Score: 2.30 / 6.00
   - energy (0.35 vs target 0.00) (+1.30)
   - acoustic fit (+1.0)

5. Coffee Shop Stories by Slow Stereo
   Score: 2.26 / 6.00
   - energy (0.37 vs target 0.00) (+1.26)
   - acoustic fit (+1.0)
```

### What I looked for, and what surprised me

- **No crashes, but no warnings either.** Every adversarial profile ran cleanly and
  returned a ranked top-5 with plausible-looking scores — there is no validation that
  flags a `favorite_genre` that doesn't exist in the catalog, or a preference
  combination (e.g. very high energy + `likes_acoustic=True`) that is internally
  unlikely. The system always produces *an* answer, and nothing in the output signals
  "this profile can't really be satisfied well." A user could easily mistake a
  low-confidence best-effort guess for a genuinely good match.
- **Conflicting mood silently loses.** In "Conflicting: High Energy + Sad Mood," no pop
  song in the catalog is also melancholic, so the mood preference contributes 0 points
  to every candidate — the ranking collapses to pure genre+energy, and the winner
  (Gym Hero, mood="intense") is the emotional opposite of what the user asked for. The
  score (4.94/6.00) still looks respectable, which could mislead a user into thinking
  their mood preference was honored.
- **Out-of-catalog genre caps the max score, silently.** With `favorite_genre="metal"`,
  no song can ever earn the +2.0 genre bonus, so the best possible score in this run is
  capped at 4.0/6.00 well before scoring starts. The system doesn't message this ceiling
  to the user — a 3.76/6.00 top score reads the same as a middling match for a valid
  genre, when it's actually the *best available* result for a genre that isn't in the
  data at all.
- **Contradictory profiles produce a "winner take most" gap.** In the "Acoustic-Loving
  Raver" case, the single song matching genre+mood+energy (Neon Pulse) wins by a huge
  margin (5.00 vs. 2.00) precisely because it fails the one contradictory constraint
  (acoustic fit) while nothing else comes close on the other three. This is a case where
  the internal contradiction happens to resolve cleanly because only one song is a near
  match — with a larger catalog, the gap likely wouldn't be so stark and more low-scoring
  contradictory profiles would be indistinguishable from each other.
- **Boundary value (target_energy = 0.0) behaved exactly as expected** — no off-by-one
  or division issues at the edge of the valid range, and the quietest song in the
  catalog won cleanly. I did not test out-of-range values (e.g. `target_energy = 1.5` or
  `-0.2`); see Future Work.
- **Score magnitude is not a reliable confidence signal.** Across all seven profiles, a
  "good-looking" score in the high 2s to low 3s can mean either "a solid partial match"
  or "the best available result for an unsatisfiable/contradictory profile" — the number
  alone doesn't distinguish the two, which is the main risk this stress test surfaced.

### Accuracy vs. intuition

**Does "High-Energy Pop" feel right?** `#1 Sunrise City` (pop, happy, energy 0.82) is
exactly what I'd expect to top an upbeat pop/happy list — an easy "yes." `#2 Gym Hero`
(pop, *intense*, energy 0.93) is still reasonable since it's genuinely pop and even
closer to the 0.9 energy target. But `#4 Storm Runner` (rock, intense, energy 0.91) and
`#5 Neon Pulse` (edm, euphoric, energy 0.95) landing in a "High-Energy **Pop**" top 5
does *not* match intuition — a rock track and an EDM track showing up on a pop
recommendation list, purely because their energy happens to sit near 0.9, is the kind
of genre miss a human listener would notice immediately.

**Prompt I asked my AI coding assistant** (pointing it at the terminal output above and
`src/recommender.py`):

> "Looking at the High-Energy Pop run in my terminal, `Sunrise City` scored 5.84/6.00 and
> ranked #1. Walk me through exactly how that score was built from my current weights in
> `recommender.py` — which points did it earn and which did it lose, and why did it beat
> `Gym Hero`?"

**Answer:** `Sunrise City` is `genre=pop, mood=happy, energy=0.82, acousticness=0.18`
scored against `genre=pop, mood=happy, target_energy=0.9, likes_acoustic=False`. Walking
through `_score_features()` in `recommender.py`:
- Genre match (`pop == pop`): `+GENRE_MATCH_POINTS` → **+2.0**
- Mood match (`happy == happy`): `+MOOD_MATCH_POINTS` → **+1.0**
- Energy closeness: gap `|0.82 - 0.9| = 0.08` → `(1 - 0.08) * 2.0` → **+1.84**
- Acousticness fit: `0.18 < 0.5` → non-acoustic, matches `likes_acoustic=False` →
  `+ACOUSTIC_FIT_POINTS` → **+1.0**
- Total: `2.0 + 1.0 + 1.84 + 1.0 = 5.84` ✓

It beat `Gym Hero` (pop, *intense*, energy 0.93 → 4.94/6.00) purely on the **mood
point**. Gym Hero's energy is actually *closer* to the 0.9 target (gap 0.03 vs. 0.08,
worth +1.94 vs. +1.84 — a +0.10 edge), but it loses the full 1.0-point mood bonus
because its mood is "intense," not "happy." The mood match single-handedly flips the
ranking here, which shows mood isn't irrelevant — it's just weighted low enough (1.0 vs.
genre's 2.0) that it only decides *close* races, not runaway ones.

**Cross-profile repetition check.** Across all 7 profiles in this stress test, one song —
`Gym Hero` (pop, intense, energy 0.93, non-acoustic) — appeared in the top 5 of **5 of
7** profiles (High-Energy Pop, Deep Intense Rock, Conflicting, Out-of-Catalog metal, and
Contradiction), more than any other song. This matches the concern the assignment
raised almost exactly — the same song keeps resurfacing — but the cause isn't genre
weight alone: genre only matched in 2 of those 5 appearances. The real driver is that
**energy carries the same max weight as genre (2.0 each)**, is continuous (so it
contributes to *every* song's score, not just exact matches), and 5 of 7 test profiles
used `target_energy >= 0.85`. On an 18-song catalog where 0.93 is close to the top of
the whole energy distribution, `Gym Hero` becomes a strong generalist answer for almost
any "high energy" request regardless of genre/mood. This confirms the bias already
flagged in `README.md` ("Potential biases to expect") and points to two concrete Future
Work fixes: lower `ENERGY_MATCH_MAX_POINTS` relative to `GENRE_MATCH_POINTS`, or grow the
catalog so more songs cluster near each energy level.

### Profile-to-profile comparisons

Rather than compare all 21 possible pairs among the 7 tested profiles, I picked the
pairings that actually test something meaningful — each one isolates a specific
difference in taste (energy, acousticness, genre/mood, or catalog coverage) and checks
whether the output changes in a way that makes sense. Every one of the 7 profiles
appears in at least one comparison below.

1. **High-Energy Pop vs. Chill Lofi** — opposite ends of both energy (0.9 vs. 0.3) and
   acousticness (dislikes vs. likes). Result: zero song overlap in the top 5 — Pop gets
   bright, plugged-in tracks (`Sunrise City`, `Gym Hero`); Lofi gets quiet, acoustic
   tracks (`Library Rain`, `Midnight Coding`). Makes sense — these two users would
   genuinely hate each other's playlists.
2. **High-Energy Pop vs. Deep Intense Rock** — both want loud, non-acoustic music (0.9
   vs. 0.95), so their top 5s overlap heavily (`Gym Hero`, `Storm Runner`, `Sunrise
   City`, `Neon Pulse` show up in both). The difference is genre/mood: Pop's #1 is the
   happy pop track `Sunrise City`; Rock's #1 is the intense rock track `Storm Runner`.
   Makes sense — when two profiles agree on loudness, genre/mood is what's left to break
   the tie, and it does.
3. **Chill Lofi vs. Deep Intense Rock** — the most opposite pair tested (quiet+acoustic
   vs. loud+non-acoustic). Zero overlap in top 5. This is the cleanest sanity check: when
   every dial is turned the opposite way, the system separates the catalog cleanly.
4. **High-Energy Pop vs. Conflicting: High Energy + Sad Mood** — same genre (pop),
   nearly the same energy target (0.9), only the mood differs (happy vs. melancholic).
   Result: almost the *same* top 5 (`Sunrise City`, `Gym Hero`, `Storm Runner`, `Neon
   Pulse` in both) — asking for "sad" instead of "happy" barely moved the needle. Makes
   sense mechanically (no pop song in the catalog is melancholic, so that request had
   nothing to match against) but is a red flag in practice: a user who explicitly asked
   for something sad got a nearly identical "happy" playlist back with no indication
   their mood preference was ignored.
5. **Deep Intense Rock vs. Contradiction: Acoustic-Loving Raver** — both want very high
   energy, so their lists share several loud tracks (`Gym Hero`, `Broken Amp`, `Storm
   Runner`). But the Raver profile also wants `likes_acoustic=True`, which almost no
   loud song in this catalog satisfies. Its #1 pick, `Neon Pulse`, actually *fails* the
   acoustic check and still wins by a wide margin on genre+mood+energy alone. Makes
   sense mathematically, but shows the system doesn't detect or flag the contradiction —
   it just quietly drops the one preference it can't satisfy.
6. **Chill Lofi vs. Out-of-Catalog Genre (metal)** — opposite ends of energy/acousticness
   again, so zero song overlap, as expected. But unlike the lofi fan (who gets 3 real
   genre matches to work with), the metal fan can *never* get a genre match since no
   metal song exists in the data — their entire top 5 (`Broken Amp`, `Sunrise City`,
   `Storm Runner`, `Gym Hero`, `Rooftop Lights`) rests on energy closeness plus one
   lucky mood match. Same "quiet vs. loud" logic, but the metal fan's results are built
   on a much thinner foundation of genuine matches.
7. **Boundary: Zero Energy Target vs. High-Energy Pop** — literal opposite ends of the
   energy scale (0.0 vs. 0.9) and different genre/mood (classical/melancholic vs.
   pop/happy). Zero overlap: `Winter Sonata` (the quietest, saddest, most acoustic song
   in the catalog) vs. `Sunrise City` (bright, upbeat, plugged-in pop). The cleanest
   possible confirmation that maximally different requests produce maximally different,
   appropriate answers.

### Explaining it in plain language: why does "Gym Hero" keep showing up for people who just want "Happy Pop"?

Imagine you tell the app "I want Happy Pop music," expecting cheerful pop songs and
nothing else. `Gym Hero` is technically pop, but its actual vibe is "intense," not
"happy" — and yet it shows up near the top again and again, for all kinds of different
requests, not just this one. Here's why: the app isn't only checking "does this match
the exact genre and mood you asked for" — it's *also* checking "how close is this song's
energy level to what you want," and it treats getting the energy right as being just as
important as getting the genre right. `Gym Hero` happens to be one of the loudest,
most high-energy songs in the whole collection. So any time someone asks for something
energetic — whether they wanted Happy Pop, Intense Rock, or even a type of music the app
doesn't have at all — `Gym Hero`'s "closeness in energy" alone is enough to make up for
not actually matching the mood (or sometimes even the genre) the listener wanted. It's a
bit like a restaurant app that's supposed to match your favorite cuisine, but ends up
recommending the loudest, most crowded restaurant in town to everyone who says they want
"a lively atmosphere" — even someone who wanted a lively Italian bistro gets handed a
lively sports bar instead. The energy match isn't wrong, exactly — it's just weighted
heavily enough to override the genre/mood match the user actually cared about.

No numeric metrics beyond the scores the recommender itself produces.

---

## 8. Future Work  

If I kept developing this, here's what I'd change next:

1. **Let preferences have a strength, not just an on/off match.** Right now genre and
   mood are all-or-nothing, and energy is the only "how close" signal. A slider for "how
   much do I care about genre vs. mood vs. energy" would stop one strong signal (like
   energy) from quietly overriding what the user actually asked for.
2. **Add a confidence flag when a request can't really be satisfied.** If
   `favorite_genre` doesn't exist in the catalog, or a profile's preferences contradict
   each other (like wanting both very high energy and acoustic songs), the app should
   say "this is a best-effort guess" instead of returning a normal-looking score. See the
   Evaluation section for real examples where this fooled me.
3. **Grow the catalog so genres and moods actually repeat.** With 15 of 18 genres
   appearing only once, most recommendations rest almost entirely on energy closeness. A
   bigger, denser catalog would let genre and mood do more of the work they're supposed
   to.
4. **Improve variety in the top 5.** A handful of "generalist" high-energy songs (like
   `Gym Hero`) currently dominate many different profiles' results. The system could
   favor variety in the top 5 instead of just re-ranking the same score-topping songs
   every time.

---

## 9. Personal Reflection  

**Biggest learning moment:** score is not the same thing as confidence. A song can score
4.9 out of 6 and look like a strong pick, but that same 4.9 might be the *best available*
answer for a genre that isn't even in the catalog, or for a profile whose preferences
contradict each other. The number by itself doesn't tell you which situation you're in —
I only found this out by deliberately testing profiles designed to break the system, not
by looking at any single "good" result.

**How AI helped, and where I double-checked it:** the AI coding assistant was genuinely
useful for coming up with adversarial profiles I wouldn't have thought to try myself —
things like a genre that doesn't exist in the data, or preferences that contradict each
other on purpose. But I didn't just trust its explanations of *why* a song ranked where
it did — I re-traced the actual point math by hand against `recommender.py` (genre +
mood + energy + acoustic = total) to make sure the explanation actually matched the
real score before writing it down.

**What surprised me:** how "personal" a result can feel from nothing more than basic
addition and a couple of threshold checks. There's no learning, no real understanding of
music, no ML model underneath — just four numbers added together and sorted. And yet the
top result for "High-Energy Pop" or "Chill Lofi" genuinely felt like it "got" the
request. That's a little unsettling in a good way: it means a recommendation *feeling*
right isn't strong evidence that anything sophisticated is happening behind it.

**What I'd try next:** add a confidence flag for weak matches. Right now the app returns
the same clean-looking top 5 whether the match is genuinely strong or just the least-bad
option available. I'd want it to say, in plain language, "this is a rough guess" when
the requested genre doesn't exist or the preferences don't fit together well — so a
best-effort answer never gets mistaken for a real one.

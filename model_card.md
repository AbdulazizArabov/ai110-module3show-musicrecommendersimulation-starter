# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

*Other names considered:*
- *MoodSorter — clear and action-oriented, but focuses only on mood and undersells the genre and energy signals*
- *SoundScore — emphasizes the scoring mechanic, but feels more like a review tool than a personal recommender*

---

## 2. Intended Use and Non-Intended Use  

VibeMatch takes three simple inputs from a listener — their favorite music genre, the mood they are in, and how energetic they want the music to feel — and uses those to rank a catalog of songs from best match to worst, returning the top five. It is designed for classroom exploration, not for real-world deployment: the catalog is small, the preferences are manually defined, and there is no account system or listening history. The problem it solves is a simple one: given what a person tells you they want right now, which songs in the room should you play first?

**This system should NOT be used for:**

1. **A production streaming service.** With only 20 songs and no ability to learn from what users skip or replay, it cannot serve the variety or personalization that real listeners expect from an app like Spotify or Apple Music.
2. **Any high-stakes personalization.** The scoring weights were chosen by hand, not measured against real listener data — so the system's assumptions about what matters may not match what any actual person prefers.
3. **Discovering new or niche music.** Because most genres have only one song in the catalog, the system cannot meaningfully compare options within a genre. It will always return the same single song for most genre requests, which is the opposite of discovery.

---

## 3. Algorithm Summary  

For every song in the catalog, the system calculates a single number — a score — that represents how well that song matches what the listener is looking for, then returns the five songs with the highest scores. Energy is the most influential factor: every song receives between 0 and 2 points based on how close its energy level is to the listener's target, so a perfectly matching song earns the full 2 points while one that is far off earns close to none. Genre adds a flat 1-point bonus if the song belongs to the listener's preferred style — it either matches or it doesn't, with no in-between. Mood matching is part of the original design but was set aside during a development experiment to test how well the system performs on genre and energy alone. Once every song has a score, the list is sorted from highest to lowest and the top five are returned. There is no learning involved: the point values were chosen in advance by the developer and stay fixed for every listener, every time.

---

## 4. Data Used  

The catalog contains 20 songs. Each song comes with a label for its genre and mood, plus several numeric ratings: how energetic it feels (on a scale of 0 to 1), its tempo in beats per minute, how positive it sounds, how easy it is to dance to, and how acoustic versus produced it sounds. The 20 songs cover 17 different genres and 16 different moods — which means almost every genre and mood shows up only once, leaving the system very little to work with when a listener picks anything outside the two or three most common styles. The songs also lean toward higher energy overall, so listeners who want something quiet or calm will find that most of the catalog is simply not a close match for them. The collection reflects a narrow, mostly Western view of music and does not include global styles like Afrobeats, K-pop, or Latin music.

---

## 5. Observed Behavior / Biases

**What the system reliably gets right:**
When a listener's preferences line up with one of the well-represented corners of the catalog, the results are both correct and easy to explain. Ask for intense rock with high energy and "Storm Runner" comes back at the top — it is the only rock song in the catalog, the mood label matches, and its energy of 0.91 nearly identical to a high-energy target. The score and the right answer point to the same place, and the explanation the system prints holds up to scrutiny.

**The "Gym Hero" problem — when mood is invisible:**
With mood matching currently disabled, the system cannot tell "happy pop" from "intense pop" — it only sees the word "pop." There are exactly two pop songs in the catalog: "Sunrise City" (happy, energy 0.82) and "Gym Hero" (intense, energy 0.93). A listener who asks for something happy and upbeat will still receive "Gym Hero" — a high-intensity workout anthem — because both songs earn the same genre bonus and the only thing separating them is how close their energy is to the listener's target. If that target is closer to 0.93 than to 0.82, "Gym Hero" will actually outscore "Sunrise City" despite being entirely the wrong mood. The system returns a confident-looking ranked list with a score attached, but the result is quietly wrong in a way you would only notice by pressing play.

**The quiet bias toward high energy:**
Only four songs in the catalog have an energy level below 0.40. That means a listener who wants something calm or quiet will almost always receive results that are louder and more intense than what they asked for — not because the system made a mistake, but because the options simply are not there. The scores may look reasonable, but the gap between what was requested and what is returned will be audible.

---

## 6. Strengths  

The system works best when a listener's preferences align closely with one of the better-represented corners of the catalog. A listener who wants high-energy rock, for example, will reliably receive "Storm Runner" at the top — a song that genuinely matches their genre and energy target — because the rules are transparent and the math is simple enough to follow by hand. Listeners with very distinct taste profiles, like someone who wants chill lofi versus someone who wants intense rock, will receive almost completely non-overlapping recommendations, which shows that the system is actually reading the input rather than returning the same songs to everyone. The plain-language explanations attached to each result ("genre match +1.0, energy proximity +1.8") are also a genuine strength: unlike a black-box AI system, every recommendation in VibeMatch can be fully explained in one sentence.

---

## 7. Limitations and Bias 

Because most genres appear only once in the 20-song catalog, the top result for most listeners is effectively decided before any real comparison happens — whichever single song shares their genre automatically wins, regardless of whether the mood or energy is a good fit. The energy scoring also quietly favors people who like high-energy music, because there are simply more high-energy songs in the catalog; someone who wants something soft and quiet will consistently get worse matches because the options just aren't there. The listener most likely to walk away disappointed is someone who thinks about music emotionally — for example, someone who wants something romantic or melancholic — because mood matching is currently disabled entirely, meaning the system cannot distinguish between a sad song and a happy one in the same genre. The system has no memory of past interactions, so it cannot improve over time or adjust to feedback — it gives the same five songs every single time the same preferences are entered. And because the point values were chosen by the developer rather than calculated from real listener behavior, there is no guarantee they reflect what most people actually care about.

---

## 8. Evaluation Process  

The recommender was tested by creating several different listener profiles and reading the terminal output by hand to judge whether the results felt right. Profiles ranged from straightforward cases — like a high-energy pop fan or a chill lofi listener — to edge cases designed to break the system, such as a listener whose favorite genre does not exist in the catalog at all. Two logic experiments were also run: one that doubled the weight of energy and halved the weight of genre to see how the rankings shifted, and one that removed mood matching entirely to measure how much influence it had. Results were judged informally — if the top song genuinely matched what the profile asked for in terms of sound and feel, the result was considered correct; if the top song was clearly off despite a confident-looking score, that was flagged as a weakness. No numeric accuracy metric was used, since the catalog is too small and the preferences are defined by hand rather than collected from real listeners.

**Profiles tested:**

- **High-Energy Pop** — a listener who wants upbeat, danceable pop music with high energy
- **Chill Lofi** — a listener who prefers calm, low-energy background music in the lofi style
- **Deep Intense Rock** — a listener who wants loud, aggressive rock with very high energy
- **Ghost Genre (adversarial)** — a listener whose favorite genre (k-pop) does not exist anywhere in the song catalog

**What matched expectations:**

The Deep Intense Rock profile behaved exactly as hoped. "Storm Runner" by Voltline ranked first — it matched the genre (rock) and had an energy level of 0.91, nearly identical to the target, earning close to the maximum score possible under the current two-factor system. This result felt correct and trustworthy; the system identified the one song in the catalog that genuinely fit the profile.

**What was surprising:**

The Ghost Genre adversarial profile exposed an unexpected weakness. When the requested genre (k-pop) did not exist in the catalog, the system did not warn the user or signal low confidence — it simply returned five songs as if everything were normal. The top results were decided entirely by mood and energy, which meant the output looked reasonable on the surface but was actually missing the most important signal the user had provided. A real music app would likely tell the user "we don't have many songs in that genre" rather than quietly ignoring the preference.

---

## 9. Ideas for Improvement  

1. **Expand the song catalog to at least 5–10 songs per genre.** Right now most genres have only one song, so the top result is decided before any preferences are even compared — more songs per genre would let the scoring actually do its job of finding the best match within a style.

2. **Re-enable mood matching and calibrate its weight against real listener feedback.** Mood scoring was removed during a development experiment and never restored — turning it back on, with a weight tuned to reflect how much mood actually influences listener satisfaction, would stop the system from treating "happy pop" and "intense pop" as identical requests.

3. **Show a confidence warning when no songs match the user's genre.** If a listener asks for a genre that does not exist in the catalog, the system currently returns results anyway without any indication that the most important preference was ignored — a simple message like "no songs found in this genre, showing closest matches" would make the output honest and easier to trust.

---

## 10. Personal Reflection  

Building this project felt smaller than I expected going in — and then more interesting than I expected once it was running. What I didn't anticipate was how much the small, quiet moments would end up teaching me the most.

My biggest learning moment came from a bug I almost missed: I named the preference keys one way and the scoring function expected something different. Nothing crashed — the program just quietly ignored my genre preference and returned songs as if I had none. That taught me something I won't forget: the most dangerous bugs aren't the ones that throw errors, they're the ones that return a confident-looking wrong answer with a smile. Using Claude helped me move faster in moments like figuring out `.sort()` versus `sorted()`, but I also had to push back when the generated code used the wrong field names — which reminded me that AI tools work best when you already understand enough to notice when something is off.

The moment that surprised me most was watching `Sunrise City` come back at #1 for a pop/happy profile with a clean explanation attached. I knew it was just three if-statements adding up to a number. But it felt like the system had actually *listened* — and that gap between how simple the logic is and how convincing the output feels is exactly what makes real recommendation systems so easy to overtrust.

If I kept building, I'd add more songs per genre, re-enable mood matching, and let users rate results so the weights could shift based on real feedback. This project taught me that the interesting part of building an AI system isn't writing the algorithm — it's deciding what to measure, what to ignore, and how honest to be when the answer isn't good enough.

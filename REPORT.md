# IMDb project report (group gr-02)

> Sections follow the team responsibilities in CONTRIBUTING.md. Result tables come from the notebooks. AI assistance is disclosed in PROJECT.md.

## 1. Data preparation

Source: `notebooks/01_data_preparation.ipynb`, result tables in `results/preparation/`. The profile and the checks are computed on the bronze layer (raw IMDb files typed as Parquet, before any cleaning), on the full dataset: 7 tables, about 228 million rows in total.

### 1.1 Percentage of null, missing or empty values per column

A value counts as missing when it is `null` (IMDb writes `\N`, read as null in bronze), an empty or blank string, or an empty list.

| Table | Column | Rows | Missing | % missing |
|---|---|---:|---:|---:|
| name.basics | nconst | 15,802,420 | 0 | 0.00 |
| name.basics | primaryName | 15,802,420 | 89 | 0.00 |
| name.basics | birthYear | 15,802,420 | 15,116,831 | 95.66 |
| name.basics | deathYear | 15,802,420 | 15,537,057 | 98.32 |
| name.basics | primaryProfession | 15,802,420 | 3,216,642 | 20.36 |
| name.basics | knownForTitles | 15,802,420 | 1,915,685 | 12.12 |
| title.akas | titleId | 60,321,594 | 0 | 0.00 |
| title.akas | ordering | 60,321,594 | 0 | 0.00 |
| title.akas | title | 60,321,594 | 0 | 0.00 |
| title.akas | region | 60,321,594 | 12,991,240 | 21.54 |
| title.akas | language | 60,321,594 | 19,639,034 | 32.56 |
| title.akas | types | 60,321,594 | 40,342,236 | 66.88 |
| title.akas | attributes | 60,321,594 | 60,004,431 | 99.47 |
| title.akas | isOriginalTitle | 60,321,594 | 0 | 0.00 |
| title.basics | tconst | 12,951,113 | 0 | 0.00 |
| title.basics | titleType | 12,951,113 | 0 | 0.00 |
| title.basics | primaryTitle | 12,951,113 | 0 | 0.00 |
| title.basics | originalTitle | 12,951,113 | 0 | 0.00 |
| title.basics | isAdult | 12,951,113 | 0 | 0.00 |
| title.basics | startYear | 12,951,113 | 1,487,768 | 11.49 |
| title.basics | endYear | 12,951,113 | 12,786,793 | 98.73 |
| title.basics | runtimeMinutes | 12,951,113 | 8,052,653 | 62.18 |
| title.basics | genres | 12,951,113 | 547,430 | 4.23 |
| title.crew | tconst | 12,949,786 | 0 | 0.00 |
| title.crew | directors | 12,949,786 | 5,784,342 | 44.67 |
| title.crew | writers | 12,949,786 | 6,425,630 | 49.62 |
| title.episode | tconst | 10,025,088 | 0 | 0.00 |
| title.episode | parentTconst | 10,025,088 | 0 | 0.00 |
| title.episode | seasonNumber | 10,025,088 | 2,120,177 | 21.15 |
| title.episode | episodeNumber | 10,025,088 | 2,120,177 | 21.15 |
| title.principals | tconst | 102,649,609 | 0 | 0.00 |
| title.principals | ordering | 102,649,609 | 0 | 0.00 |
| title.principals | nconst | 102,649,609 | 0 | 0.00 |
| title.principals | category | 102,649,609 | 0 | 0.00 |
| title.principals | job | 102,649,609 | 82,794,746 | 80.66 |
| title.principals | characters | 102,649,609 | 52,649,325 | 51.29 |
| title.ratings | tconst | 1,730,885 | 0 | 0.00 |
| title.ratings | averageRating | 1,730,885 | 0 | 0.00 |
| title.ratings | numVotes | 1,730,885 | 0 | 0.00 |

All identifiers and keys are complete. The missing values are concentrated in descriptive columns. Two of them matter directly for the analyses: `runtimeMinutes` is missing for 62 % of the titles, and `startYear` for 11.5 %.

### 1.2 Five columns with the highest percentage of nulls

| Rank | Table | Column | % missing | Why it is missing |
|---:|---|---|---:|---|
| 1 | title.akas | attributes | 99.47 | optional free note (e.g. "literal title"), only set when there is something to say |
| 2 | title.basics | endYear | 98.73 | only defined for TV series; null for every other title type and for running series |
| 3 | name.basics | deathYear | 98.32 | most people in the database are alive, or their death is not recorded |
| 4 | name.basics | birthYear | 95.66 | rarely filled except for well-known people |
| 5 | title.principals | job | 80.66 | only filled when the role is more precise than `category` |

These five columns are mostly empty by design of the IMDb schema, not because of errors. A null here usually means "not applicable" or "not known", so filling them in would invent information.

### 1.3 Other data quality issues

| Table | Check | Rows |
|---|---|---:|
| name.basics | deathYear < birthYear | 28 |
| name.basics | lifespan > 120 years | 2 |
| name.basics | no deathYear and born more than 120 years ago | 2,793 |
| name.basics | birthYear or deathYear after 2026 | 0 |
| title.principals | credited on a title released before their birth | 3,101 |
| title.principals | credited more than 2 years after death (excluding `archive_*` categories) | 240,345 |
| title.basics | startYear > 2026 (announced, not released) | 6,017 |
| title.basics | runtimeMinutes <= 0 | 4 |
| title.basics | runtimeMinutes > 600 (more than 10 hours) | 1,133 |
| title.basics | startYear < 1874, endYear < startYear, endYear on a non-series, isAdult not in (0, 1), more than 3 genres | 0 |
| title.ratings | averageRating outside [1, 10], numVotes <= 0 | 0 |
| title.episode | seasonNumber or episodeNumber missing | 2,120,177 |
| title.episode | parent title is not a series | 0 |
| all tables | duplicated primary key | 0 |
| title.principals | nconst -> name.basics: missing parent | 8,441 |
| title.crew | writers -> name.basics: missing parent | 1,149 |
| title.crew | directors -> name.basics: missing parent | 423 |
| name.basics | knownForTitles -> title.basics: missing parent | 69 |
| title.crew | tconst -> title.basics: missing parent | 30 |
| title.episode | parentTconst -> title.basics: missing parent | 5 |
| title.akas | titleId -> title.basics: missing parent | 2 |
| title.ratings, title.episode (tconst), title.principals (tconst) | missing parent | 0 |

Observations:

- The 28 people who died before they were born are mostly ancient authors whose years are BC dates stored as positive numbers (Aesop 620/560, Socrates 470/399, Sophocles 496/406). The others are input errors (e.g. born 1995, died 1984).
- Among the 3,101 credits before birth, the largest gaps are composers credited on silent films from 1900 to 1925, whose music was written much later for a restoration (e.g. the members of Air on *A Trip to the Moon*, 1902). In these cases the credit is real; it is the release year of the film that does not describe it.
- Many of the 240,345 credits more than 2 years after death are probably legitimate too: posthumous releases, writers of adapted works, reused music. They cannot be separated from real errors with the data alone.
- The runtimes above 10 hours are mostly videos (370) and series or miniseries (349); only 109 are movies, often experimental ones (*Logistics*, 2012, 51,420 min). Some are plausible, some are errors.
- 21 % of episodes have no season or episode number: specials, or series whose episodes were never numbered on IMDb.
- Foreign keys are almost always valid: the worst case, `title.principals.nconst`, concerns 0.008 % of the rows.

### 1.4 Handling of these values

The cleaned tables are written to the silver layer (`data/silver/`), which every other notebook reads.

| Issue | Handling | Reason |
|---|---|---|
| empty strings, empty lists | turned into `null` | one single representation of "missing" |
| missing years, runtimes, ratings, birth/death years | left as `null`, **not imputed** | an imputed runtime or year would create fake results in the analyses (e.g. a film counted in a year it was not released) |
| duplicated primary keys | one row kept per key (none found) | the step stays in place in case a future IMDb dump has some |
| child rows whose foreign key has no parent | removed; in list columns (`directors`, `writers`, `knownForTitles`) only the unknown ids are removed | these rows can never be joined, and the share is tiny |
| `runtimeMinutes <= 0` | set to `null` | a runtime of 0 is not a measurement |
| runtime above 600 min | kept, flagged `is_runtime_suspicious` | some are real; each analysis decides whether to exclude them |
| `startYear` after 2026 | kept, flagged `is_unreleased` | announced titles are valid records but must not be counted as released films |
| impossible birth / death years | kept, flagged `has_invalid_life_dates` | we do not know which of the two years is wrong |
| credits before birth / after death | kept as they are | mostly legitimate (restorations, posthumous credits, adaptations) |
| `averageRating` outside [1, 10], `numVotes <= 0` | rows removed (none found) | an impossible rating cannot be used |

Two shared definitions are added to the silver `title.basics`, so that the whole group uses the same ones: `is_movie` (`titleType = "movie"`) and `is_feature_film` (movie with a runtime above 40 minutes, the threshold used by the Academy, the AFI and the BFI). A movie without a known runtime is therefore not considered a feature film.

Effect of the cleaning on the row counts:

| Table | Bronze rows | Silver rows | Removed | % removed |
|---|---:|---:|---:|---:|
| title.basics | 12,951,113 | 12,951,113 | 0 | 0.000 |
| title.akas | 60,321,594 | 60,321,592 | 2 | 0.000 |
| title.crew | 12,949,786 | 12,949,756 | 30 | 0.000 |
| title.episode | 10,025,088 | 10,025,083 | 5 | 0.000 |
| title.principals | 102,649,609 | 102,641,168 | 8,441 | 0.008 |
| title.ratings | 1,730,885 | 1,730,885 | 0 | 0.000 |
| name.basics | 15,802,420 | 15,802,420 | 0 | 0.000 |

### Methodological explanation

**Layers.** The raw `.tsv.gz` files are first converted to Parquet with an explicit schema (bronze): `\N` becomes `null`, the comma-separated lists become arrays and CSV quoting is disabled, because titles contain `"` characters that are not quotes. Gzip files cannot be split, so this conversion runs on one core, but every later read of the Parquet files is parallel. The cleaning then produces the silver layer. Keeping bronze untouched means the quality checks always describe the original data, and the cleaning rules can be changed and replayed without downloading again.

**Profiling.** For each table, all the "missing" conditions are computed as sums in a single aggregation, so each table is read once instead of once per column.

**Checks.** The logical checks are filters, and the foreign key checks are `left_anti` joins (child keys without a parent), after exploding the list columns. Every check records its row count in one summary table, which is the table of section 1.3.

**Strategy: flag rather than delete or impute.** We remove a row only when it is unusable (an orphan foreign key, or an impossible rating). Most anomalies are kept with a boolean flag, because many of them are real (restorations, posthumous credits, very long films), and deleting them would hide information that some analyses need. We never impute: with 62 % of runtimes and 96 % of birth years missing, any imputed value would weigh more than the observed data and bias the results. Each analysis filters on the flags it needs and states how it treats nulls.

**Performance constraints.** The pipeline runs in Docker on a laptop: Spark is limited to 2 cores and a 2 GB driver, which avoids the JVM being killed for lack of memory. Several choices follow from this:
- The silver layer is written table by table, parents first: the child tables are filtered against the parent tables actually written, which keeps each Spark job small.
- For orphan foreign keys, the few missing ids are computed on the distinct keys and removed with a broadcast anti join, so the 100 million rows of `title.principals` are not shuffled.
- The duplicate check runs on the key columns only, and the full deduplication only runs when a duplicate exists.

## 2. Data exploration

Results from the full silver-layer run of [notebook 02](notebooks/02_data_exploration.ipynb):

### 2.1 Feature-length movies with an unusual runtime for their genre

- 30,232 film–genre rows; 20,873 distinct films across 26 genres.
- 25,945 rows are longer and 4,287 are shorter than their genre reference.
- [Complete result](results/exploration/q1_unusual_runtimes.csv).

### 2.2 Top three genres per year (1980-2025)

| Release year | Top three by votes | Top three by film count |
|---|---|---|
| 1980 | Drama, Adventure, Horror | Drama, Comedy, Action |
| 2025 | Drama, Action, Comedy | Drama, Documentary, Comedy |

Both rankings contain three genres for each of the 46 years. [Votes ranking](results/exploration/q2_top_three_by_votes.csv); [film-count ranking](results/exploration/q2_top_three_by_movie_count.csv); [all genres](results/exploration/q2_all_genres.csv).

Across the 46 vote rankings, Drama appears in the top three every year, followed by Comedy (34 years), Action (29) and Adventure (16). The two years in the table illustrate the ranking; the linked CSV gives all 46.

### 2.3 Top three genres compared to the other genres

| 2025 film group | Films | Share of films | Share of votes |
|---|---:|---:|---:|
| At least one top-three genre | 9,751 | 45.30% | 74.46% |
| Other listed genres only | 10,496 | 48.76% | 24.92% |
| Unknown genre | 1,278 | 5.94% | 0.62% |

[Disjoint film comparison](results/exploration/q3_disjoint_movie_comparison.csv); [genre-membership comparison](results/exploration/q3_genre_comparison.csv).

Across 1980–2025, films with at least one top-three genre average **49.53% of films** but **85.66% of votes** within each year. These are unweighted averages of the 46 yearly percentages, so each release year contributes equally to this summary.

### 2.4 Directors with exactly one movie rated >= 8.0 and other movies averaging <= 6.0

- 183 directors in the result.
- Example: James McTeigue — *V for Vendetta* rated 8.1; other eligible rated films average 5.975.
- [Director table](results/exploration/q4_directors.csv).
- The five qualifying high-rated films with the most votes are associated with James McTeigue (*V for Vendetta*), Richard Marquand (*Return of the Jedi*), M. Night Shyamalan (*The Sixth Sense*), Richard Kelly (*Donnie Darko*) and Frank Miller and Robert Rodriguez (*Sin City*, co-directed).

### 2.5 TV series whose worst episode is in the last season and best episode in the first two

- 412 qualifying series.
- Example: *Two and a Half Men* has 12 full seasons in the result, with best eligible episode rating 8.7 and worst 3.6.
- [Series table](results/exploration/q5_series.csv); [episode evidence](results/exploration/q5_episode_evidence.csv).
- By number of eligible rated episodes, the first five qualifying series are *The Beverly Hillbillies*, *Two and a Half Men*, *Murphy Brown*, *Bewitched* and *The Virginian*.

### 2.6 Actors and actresses successful in several languages

- 14,185 films meet the success threshold; 12,412 (87.50%) have a language estimate.
- 4,623 candidates have successful films in at least two estimated languages; 867 have at least three.
- [Coverage](results/exploration/q6_language_coverage.csv); [two-language candidates](results/exploration/q6_candidates_two_or_more_languages.csv); [three-language candidates](results/exploration/q6_candidates_three_or_more_languages.csv); [film estimates](results/exploration/q6_movie_language_estimates.csv); [evidence](results/exploration/q6_language_evidence.csv).

**These lists are unvalidated candidates, not confirmed multilingual careers.** Matching a romanized original title can select a foreign-release AKA rather than an AKA from the film's home country. For example, the evidence assigns *In the Mood for Love* to Korean and *Hero* to English for Maggie Cheung; several Japanese films involving Toshirō Mifune receive European language labels. Of the 12,412 film estimates, 959 have tied leading languages and 2,537 rest on only one supporting AKA. Requiring one clear winner, at least two supporting AKAs and complete agreement leaves 2,587 films. The candidate counts above must therefore not be interpreted as verified original spoken languages.

### 2.7 Actors and actresses whose popularity peaked early

- 4,638 selected actors and actresses; median early-minus-later mean-rating difference 0.66 point within this group.
- [Career table](results/exploration/q7_early_peak_actors.csv); [peak-film evidence](results/exploration/q7_peak_movies.csv).
- The five largest early-minus-later mean-rating differences in the selected group are Saroj Khanal (4.18), Oya Aydogan (3.44), Mahesh (2.99), Jean-Claude La Marre (2.82) and Kristine DeBell (2.77). This ranking is within the selected group.

### 2.8 Multi-talented film professionals

- 59,577 professionals have rated films in both the single-role and multiple-role groups.
- Mean person-level rating difference (multiple minus single): +0.059 point; median: +0.033 point.
- [Paired differences](results/exploration/q8_paired_differences.csv); [overall summary](results/exploration/q8_overall_comparison.csv).
- The mean and median differences are both close to zero on IMDb's ten-point rating scale. In this comparison, taking multiple roles shows no substantial average rating advantage; the result is descriptive and does not establish an effect of taking additional roles.

### Methodological explanation

I accessed the cleaned Silver tables through `jobs/common.py`, joined records using IMDb IDs, and used names only for display. I left missing ratings as-is. The thresholds are configurable in notebook 02, so the same analysis can be rerun on a new IMDb snapshot using the same criteria. Changing a threshold can change which records are included. For each question, I explain the approach I chose and the alternatives I considered.

| Question | Method and rationale | Alternatives and trade-offs |
|---|---|---|
| Q1 — Unusual runtime | I calculated a z-score for each feature-length film using its genre’s mean runtime and population standard deviation. I required at least 30 films in the reference group and flagged films with an absolute z-score of at least 2. I excluded suspicious runtimes from both the reference groups and the results. | A rule based on the median and interquartile range would be less sensitive to extreme runtimes, though its cutoff would have a different meaning across genres. Z-scores give a common scale for comparison, and their interpretation depends on the shape of each genre’s runtime distribution. |
| Q2 — Popular genres | For each release year from 1980 through 2025, I ranked genres by the total number of IMDb votes their films had received at the time of the analysis. I also exported a ranking by film count to show production volume. | Average ratings measure how well films were received, and film counts measure how many were released. Vote totals capture voting activity to date and tend to favour older films, which have had more time to accumulate votes. |
| Q3 — Top three versus the rest | I assigned each film to a single group. A film entered the top-three group if at least one of its genres ranked in the top three by votes for its release year. Films with no known genre formed a separate group. This counted each film and its votes once. | An analysis based on film–genre memberships preserves more genre detail, and a multi-genre film can contribute to several totals. I exported both views and reported their percentages separately because they use different denominators. |
| Q4 — Directors | I identified directors using the IDs in title.crew. To qualify, a director needed one film rated at least 8.0 with at least 100 votes and at least two other eligible films with an average rating of 6.0 or lower. Each eligible film contributed equally to the average. | Weighting ratings by vote count would give the most widely rated films more influence. Including films with very few votes would increase coverage and make the average more sensitive to ratings based on small samples. A film with a missing rating could not qualify as a hit. |
| Q5 — Television series | I counted numbered episodes before applying the ratings filter. A series needed at least three seasons with ten or more episodes each. I identified the highest- and lowest-rated episodes among those with at least 20 votes. Ties qualified if at least one highest-rated episode was in season 1 or 2 and at least one lowest-rated episode was in the latest numbered season. | Requiring ten episodes in every season would exclude series with a short final season. Including all rated episodes would give ratings based on very few votes the same influence as those based on larger samples. Excluding season 0 and episodes with unknown season numbers allowed me to retain the series in the analysis. |
| Q6 — Languages | I defined a successful film as one with a rating of at least 7.0 and at least 1,000 votes. I estimated its language from IMDb AKA entries that matched originalTitle. I used the explicit language when available and otherwise applied a limited region-to-language mapping. I selected the candidate with the most supporting entries. | An external catalogue could help validate the original spoken language, but it would require matching titles across sources and checking coverage. IMDb’s AKA language field describes the title as presented, so it provides an estimate of the film’s language. Films without an estimate were excluded from the multilingual candidate counts. |
| Q7 — Early peak | I required an observed career span of at least 20 years and at least 15 films with release dates. I used the first quarter of that span as the early period and required at least three films with 100 or more votes in each period. The early period had to have both a higher maximum rating and a higher mean rating. | Vote counts would better reflect audience reach, though they depend on how widely a film was seen and how long it has been available. Ratings measure reception and follow the question’s example of a highest-rated film. Incomplete principal credits can affect the estimated start and end of a career. |
| Q8 — Multiple roles | I combined acting, directing and writing credits and kept one entry per person, film and role. For each person with rated films in both categories, I compared their single-role and multiple-role films. I then averaged those differences, giving each person equal weight. | Pooling all films would give more weight to people with more credits and combine differences between people with differences between their projects. The paired comparison limits this effect, covers only people with both types of credits, and leaves factors such as budget, genre and career stage unaccounted for. |

The results are descriptive and reflect the IMDb snapshot used for the analysis. Incomplete credits, missing genres and release dates, and differences in ratings coverage limit how broadly the findings can be interpreted. I ran the full notebook to check for errors and used the exported CSVs to verify year coverage, the season thresholds, language coverage and the mean paired difference for Q8.

## 3. Data enrichment

### Results

### Methodological explanation

## 4. Streaming

Source: `notebooks/04_streaming.ipynb` and `streaming/wikistream_producer.py`, result tables in `results/streaming/`. Test window: 14 November 2026, from 17:53 to 18:20 UTC (25 minutes of production).

### Results and streaming metrics

**Pipeline.**
1. The producer (on the host) reads the Wikimedia `recentchange` stream, keeps `en.wikipedia.org` edits and page creations, and sends each event as JSON to the Kafka topic `wiki-changes` (3 partitions, key = page title).
2. Spark Structured Streaming reads the topic, parses the JSON with an explicit schema, keeps the articles (namespace 0), and joins each event to a static IMDb lookup table built from the silver layer.
3. Two queries run every 30 seconds:
   - `matches`: every matching change, appended to Parquet;
   - `window_counts`: changes, distinct editors and bytes changed per IMDb entity and per 5-minute window.

**Lookup table.** It holds 196,068 keys:

| Key type | Entity | Keys |
|---|---|---:|
| film (page title "X (film)" or "X (2010 film)") | title | 101,068 |
| series (page title "X (TV series)") | title | 25,449 |
| person | person | 64,316 |
| any (bare page title "X") | title | 5,235 |

**Volume.**
- 3,452 Wikipedia events were read from Kafka, about 2.3 events per second.
- **77 changes matched an IMDb entity** (2.2 % of the events): 28 changes on 15 titles (18 on movies, 10 on series) and 49 changes on 32 people.
- All 77 are edits (no page creation matched), and 2 were made by bots.

| Most edited entities | Type | Changes | Editors |
|---|---|---:|---:|
| Joseph Maher | person | 10 | 1 |
| Wildwood (2026) | movie | 7 | 2 |
| Ryan Day | person | 6 | 3 |
| Players (2024) | movie | 4 | 1 |
| Joely Collins | person | 3 | 1 |
| Tulsa King | tvSeries | 3 | 1 |

| 5-minute window (UTC) | Changes | Entities |
|---|---:|---:|
| 17:50 - 17:55 | 1 | 1 |
| 17:55 - 18:00 | 18 | 10 |
| 18:00 - 18:05 | 14 | 11 |
| 18:05 - 18:10 | 18 | 15 |
| 18:10 - 18:15 | 12 | 7 |
| 18:15 - 18:20 | 14 | 13 |

The first window only contains the first minute of the test. The windows after 18:10 were still open when the queries stopped: their values are the last update written, not a final value.

Every complete 5-minute window contains at least 12 matching changes, so the filtering is broad enough to process multiple matching events within the test window, as required.

**Performance** (51 micro-batches per query):

| Metric | `matches` | `window_counts` |
|---|---:|---:|
| Input rate (events/s, mean) | 2.25 | 2.25 |
| Processing rate (rows/s, mean) | 17.8 | 20.4 |
| Batch duration, median / max (ms) | 3,842 / 5,218 | 3,386 / 5,118 |
| State rows (max) | 1,990 | 2,025 |
| Rows dropped by the watermark | 49 | 49 |

A batch takes about 4 seconds, against a 30-second trigger: the pipeline keeps up with the stream with a wide margin, and no backlog builds up. The state stays small (about 2,000 rows) because the watermark lets Spark purge old windows and old event ids.

**Matching quality.**
- The keys are normalized (lower case, letters and digits only), and the qualifier in parentheses of the Wikipedia title gives the kind of entity and sometimes the year, which separates remakes such as *Dune (1984 film)* and *Dune (2021 film)*.
- When several IMDb entities share a key, the most voted one is kept.
- A manual check of the 47 matched entities shows that most are correct, but at least two are wrong:
  - *John Madden* is the American football coach on Wikipedia but the film director on IMDb;
  - *Are You Being Served? (Australian TV series)* was matched to the British series, because a series qualifier without a year falls back on the most voted title.
- *Ryan Day* (6 changes) is probably the football coach as well.
- People are matched on their name alone, so homonyms are the main source of error. The vote thresholds (20,000 votes on a credited title for people, 50,000 for bare page titles) were chosen to limit these errors.

### Handling of late data

**Event time.** The windows use the time of the change on Wikipedia (`timestamp` of the event), not the time the message reached Kafka, so that a change is counted in the window where it really happened. The natural delay between the change and its arrival in Kafka is short. On the 75 matched events that were not delayed on purpose:
- median 3 s, mean 3.8 s;
- maximum 13 s.

**Watermark of 10 minutes.** An event is accepted as long as its event time is less than 10 minutes behind the latest event time seen. After that, its window is considered complete and its state is purged.

**Test.** To check this behaviour, the producer holds back 3 % of the events for 12 minutes, which is longer than the watermark, and marks them with `simulated_delay_s`. The results match what we expected:
- The first rows dropped by the watermark appear in batch 25, at about 18:06, which is 12 to 13 minutes after the start, when the first held-back events arrived. In total, **49 late events were dropped**.
- When the producer stopped, it sent the events it was still holding. Some of them had only waited a short time. Two of these were IMDb matches, with delays of 56 s and 412 s, below 10 minutes: they were accepted and counted in their windows.
- The 49 events are dropped by the deduplication step, before the join with IMDb. Most of them were therefore not IMDb pages: with a 2.2 % match rate, we expect about one matching change among them.

**Why 10 minutes.** The natural delay is a few seconds, so 10 minutes is far more than needed in normal operation. It covers a producer or network interruption of several minutes without losing data. The cost is acceptable:
- the state only holds about 2,000 rows;
- a window becomes final 10 minutes after its end. Thanks to the `update` output mode, intermediate values are still available at every batch.

A shorter watermark (1 minute) would give faster final results, but a short interruption of the producer would then lose data. A longer one (1 hour) would keep much more state, for a delay we never observed.

**Duplicates.** Kafka and the producer guarantee "at least once" delivery, so a message can be received twice. The pipeline removes duplicates on the Wikimedia event id with `dropDuplicatesWithinWatermark`: an id is remembered for as long as the watermark allows, then forgotten.

**Limits.** An event later than the watermark is lost for both outputs. We only count it in the metrics (`numRowsDroppedByWatermark`). If these events mattered, they could be written to a separate output and merged into the windows later, in batch.

### Methodological explanation

**Why Kafka between Wikipedia and Spark.** The Wikimedia stream is a live HTTP connection that cannot be replayed. Kafka keeps the events, so Spark can restart from its checkpoint (`startingOffsets = earliest`, offsets saved in the checkpoint) without losing any. The producer and the consumer also run independently: the producer on the host, as in lab 5, and Spark in Docker.

**Filtering strategy.** The stream is reduced in two steps:
1. **Cheap filters first:** the English Wikipedia (where IMDb titles have their pages), edits and page creations only, and articles only (no talk, user or template pages).
2. **The IMDb join:** a stream-static join on a lookup table of about 196,000 keys. The table is small enough to be broadcast to every task, so joining a micro-batch costs no shuffle.

The lookup table only contains titles and people with enough votes (1,000 votes for films and series, 50,000 for bare page titles, 20,000 on a credited title for people). Without these thresholds, common words and names ("Paris", "Home", "John Smith") would match thousands of obscure IMDb entries, which would mostly give false positives. With them, 77 changes matched in 25 minutes, which is enough to show the pipeline working while keeping most matches correct.

**Matching keys.** A Wikipedia title and an IMDb name only match after normalization, so both are turned into the same key: lower case, letters and digits, single spaces. The qualifier in parentheses is used when it exists:
- "film" or "TV series" with a year: the key includes the year;
- a person qualifier ("actor", "director"): the key points to a person;
- another qualifier ("band", "album"): the page is ignored.

A bare title is tried both as a very popular title and as a person.

**Two outputs.**
- `matches` uses the `append` mode: each change is written once, to Parquet.
- `window_counts` uses the `update` mode with `foreachBatch`: each micro-batch writes the windows that changed, together with the batch id, and the final value of a window is its version from the latest batch. This shows the evolution of each window while keeping the final result easy to get. The `append` mode would only write a window after the watermark has passed it, so nothing would be visible during the first 15 minutes of the test.

**Settings.** The trigger is 30 seconds and Spark uses 4 shuffle partitions. The stream is small (2 to 3 events per second), so more partitions would only add scheduling overhead. The metrics of every batch (`recentProgress`) are saved to `results/streaming/progress.csv`.

## 5. Open question

### Question, why it is interesting, additional data

**Do feature-length films with a repeated actor-director collaboration have higher IMDb ratings or more votes than films containing only first observed collaborations? Does the difference remain when comparing similar release years and genres, or the same duo over time?**

I wanted to look at the team behind a film, rather than only the individual careers studied in the exploration section. Working together again could be associated with different results, but successful teams may also be more likely to reunite. The analysis therefore compares observed groups without treating repeat collaboration as a cause of success.

I used five silver tables: `title.basics` for film type, duration, year and genres; `title.principals` for actor/actress credits; `title.crew` for directors; `title.ratings` for ratings and votes; and `name.basics` to label the examples. No external dataset is needed for this question. This also keeps the comparison independent of Wikipedia coverage.

### Results

Notebook 05 was executed from top to bottom on the full local silver snapshot downloaded on 15 November 2026. The six code cells completed without errors and produced eight CSV tables.

| Cohort step | Films |
|---|---:|
| Feature-length films released in 1980–2025 | 362,667 |
| Excluded: no usable non-self actor-director pair | 93,482 |
| Films with an observed actor-director pair | 269,185 |
| Among these, no IMDb rating | 67,058 |
| Main comparison: at least 100 votes | 105,065 |

The primary comparison counts each film once. A film belongs to the repeated group if at least one of its actor-director pairs worked together in an earlier release year.

| At least 100 votes | First-only films | Films with at least one repeated pair |
|---|---:|---:|
| Films | 65,895 | 39,170 |
| Mean rating | 5.712 | 5.743 |
| Median rating | 5.9 | 5.9 |
| Mean votes | 9,999 | 13,036 |
| Median votes | 508 | 557 |

The overall mean-rating gap is small: **+0.031 point** for films with a repeated pair. Their average vote count is higher, but the median difference is much smaller than the mean difference. Very popular films therefore influence the vote averages.

| Comparison | Rating difference | Population |
|---|---:|---|
| Film-level, repeated minus first-only | +0.031 | 105,065 films, at least 100 votes |
| Within release-year/genre groups | +0.079 | 892 groups with at least five films on each side |
| Within the same duo, later minus first-year films | −0.266 | 51,521 comparable duos |

The year/genre result is a weighted average of within-group differences. It uses 131,373 first-only and 80,463 repeated film–genre memberships; these are not distinct-film counts. The corresponding difference in mean `log(1 + votes)` is +0.059.

For the within-duo comparison, the median rating difference is −0.200, and 35.9% of comparable duos have a higher mean rating on their later films. The mean difference in `log(1 + votes)` is −0.219. The positive overall association does not carry over to this different comparison within continuing teams. The populations and weights differ, so these values should not be read as a sequence of causal adjustments.

I also checked whether the raw film-level rating difference changes with the vote threshold:

| Minimum votes | First-only films | Repeated-group films | First-only mean rating | Repeated mean rating | Difference |
|---|---:|---:|---:|---:|---:|
| 100 | 65,895 | 39,170 | 5.712 | 5.743 | +0.031 |
| 1,000 | 23,587 | 14,687 | 6.040 | 6.178 | +0.137 |
| 10,000 | 6,816 | 4,109 | 6.402 | 6.584 | +0.182 |

The difference is larger among higher-vote films, but raising the threshold also changes which films enter the analysis. It does not prove that repeating a collaboration improves a film.

The complete tables are in [results/open_question](results/open_question/), especially [film_summary.csv](results/open_question/film_summary.csv), [year_genre_adjusted.csv](results/open_question/year_genre_adjusted.csv) and [paired_duo_summary.csv](results/open_question/paired_duo_summary.csv). The named examples contain the 100 duos with the most observed eligible films, rather than the 100 largest positive differences.

### Methodological explanation

I used the shared `is_feature_film` flag, which means an IMDb movie lasting more than 40 minutes. The outcome cohort covers 1980–2025, inclusive. Collaboration history includes all dated feature-length films through 2025, including films before 1980 and films without ratings. Otherwise, an unrated film or an older collaboration could be incorrectly ignored when deciding whether a duo is new.

I joined actor/actress principal credits to the directors in `title.crew`, removed duplicate film-person pairs, and excluded cases where the actor and director are the same person. A Spark window counts films in strictly earlier years for each duo. IMDb only provides the release year here, so two films in the same year are not assigned an invented order. “First” means first observed in this data, not a verified first collaboration in the person's whole career.

For the main result, I aggregated those pairs back to one row per film. This avoids giving films with larger casts or several directors more weight simply because they contain more pairs. Missing credits and ratings are counted explicitly; I did not replace missing ratings with an average. The default threshold is 100 votes, with 1,000 and 10,000 tested as alternatives.

For the year/genre comparison, I kept groups with at least five films from each side. I weighted a group's difference by `n_first * n_repeat / (n_first + n_repeat)`, so very small groups have less influence. A multi-genre film can appear in several groups, and groups without both comparison categories are excluded. This result describes the retained film–genre memberships, not the entire original cohort.

For the within-duo comparison, I calculated the difference between the duo's mean rating on later films and its mean rating on first-year films. Both sides must contain at least one 1980–2025 film meeting the vote threshold. Each comparable duo then receives equal weight. This offers a different view from comparing unrelated teams, but it selects duos that continued working together, and several duos can share the same film.

I considered using a pair-level average as the main result, but that would count some films many times. I also considered vote-weighting the ratings, which would give the largest IMDb audiences most of the influence. I kept an equal-film mean, medians and vote-threshold sensitivity tables instead. For votes, I report both raw summaries and `log(1 + votes)` to reduce the influence of extreme values in the comparisons.

The main limits are incomplete principal credits, missing release dates and credits, and the absence of budget, country, franchise and career-stage controls. Films with larger credited casts or more directors also have more opportunities to contain a repeated pair; the analysis does not adjust for this. Current ratings and vote totals are not measurements taken at release, and votes are not box-office revenue. These comparisons are descriptive: they do not establish statistical independence or show that collaborating again caused the observed differences.

# IMDb project report (group gr-02)

> Each section is written by its owner (see CONTRIBUTING.md). Results tables come from the notebooks. The use of AI tools for this report is declared in PROJECT.md.

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

### 2.1 Feature-length movies with an unusual runtime for their genre

### 2.2 Top three genres per year (1980-2025)

### 2.3 Top three genres compared to the other genres

### 2.4 Directors with exactly one movie rated >= 8.0 and other movies averaging <= 6.0

### 2.5 TV series whose worst episode is in the last season and best episode in the first two

### 2.6 Actors and actresses successful in several languages

### 2.7 Actors and actresses whose popularity peaked early

### 2.8 Multi-talented film professionals

### Methodological explanation

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

### Results

### Methodological explanation

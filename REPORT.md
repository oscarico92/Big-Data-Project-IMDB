# IMDb project report (group gr-02)

> Sections follow the team responsibilities in CONTRIBUTING.md. Result tables come from the notebooks. AI assistance is disclosed in PROJECT.md.

## 1. Data preparation

### 1.1 Percentage of null, missing or empty values per column

### 1.2 Five columns with the highest percentage of nulls

### 1.3 Other data quality issues

### 1.4 Handling of these values

### Methodological explanation

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

I selected the ten most-voted feature-length films for each genre and release year from 1980 to 2025. The full local run contains **7,526 distinct films** and **10,543 film–genre–year memberships**. A film belonging to several genres appears in each relevant ranking, but its text is collected once per source page.

| Coverage on distinct selected films | Films |
|---|---:|
| Selected films | 7,526 |
| With a verified Wikipedia introduction used as a synopsis | 6,340 |
| With at least three distinct sourced principal biographies | 6,671 |
| With fewer than three sourced principal biographies | 855 |
| With both a synopsis and at least three biographies | 6,179 |

| Reason for the biography shortfall (Spark counts) | Films |
|---|---:|
| Fewer than three distinct principals in silver | 167 |
| Enough credited principals, but fewer than three verified English biographies | 688 |

Missing information is retained in the output with a code-generated note. A missing source is not replaced by an invented synopsis or biography. The following table describes all film and person targets considered during collection, including principal candidates who were not ultimately selected for the three biography slots:

| Source status | Target entities |
|---|---:|
| `Wikipedia introduction; whitespace normalized` | 37,769 |
| `ambiguous_imdb_id` | 98 |
| `no_english_article` | 12,731 |
| `no_nonempty_verified_article_extract` | 303 |
| `no_wikidata_match` | 25,232 |

The detailed [film coverage table](results/enrichment/film_coverage.csv) records the number of sourced principals for each film and whether it satisfies both requirements. [Coverage by year and genre](results/enrichment/coverage_by_year_genre.csv) includes zero-coverage combinations. The [selected films](results/enrichment/selected_films.csv) retain the ranking and IMDb identifiers, and the [lineage sample](results/enrichment/lineage_sample.csv) makes source matching inspectable.

The full local CSV exports are `film_synopses.csv`, `principal_biographies.csv` and `enriched_film_genres.csv` in `results/enrichment/`. They are excluded from Git because they contain the complete external texts. Compact result tables, 20 sourced synopsis examples, 60 sourced biography examples and executed notebook outputs are versioned. Raw API responses and full Spark tables remain under ignored `data/enrichment/` paths.

### Methodological explanation

I used the shared silver `is_feature_film` flag: an IMDb movie lasting more than 40 minutes. Release years are inclusive. I ranked each year/genre group by current `numVotes`, then by `averageRating`, then by IMDb ID to make ties deterministic. Films without a rating remain eligible but rank last. This measures present-day IMDb attention to films from a given release year, not their popularity at the time of release. A group with fewer than ten eligible films is kept as it is.

I used Wikipedia introductions as short film summaries and biographies. These are existing encyclopedia texts, not generated descriptions. An introduction is not necessarily a complete plot synopsis. Wikipedia is the human-edited source chosen for this project; I did not independently audit the authorship of every article edit.

Identity matching starts with the exact IMDb identifier in Wikidata's `P345` property. If more than one Wikidata entity has the same IMDb ID, the match is rejected. I then use the entity's English Wikipedia sitelink and verify that the returned page's `wikibase_item` property points to the same entity. Disambiguation pages and empty extracts are excluded. A matching title or person name alone is never enough.

For biographies, I consider distinct people in `title.principals`, giving actor, actress and director credits priority, followed by the other principal categories. Sourced candidates come before candidates without a usable biography; within those groups, role priority, IMDb `ordering` and person ID make the selection deterministic. This allows another credited person to replace a missing biography instead of checking only the first three names. If two sourced IMDb IDs point to the same Wikidata person, they count as one biography; an audit found one such film/person group in the input candidates. The final output keeps at most three distinct principals per film. Films with no credits, fewer than three credited people or insufficient source coverage remain in the film-level coverage table.

Every retained text includes a source URL in `lineage`, language, retrieval timestamp, revision URL, match evidence and license/attribution information. The article-history link identifies the Wikipedia contributors, following the [Wikipedia text-reuse guidance](https://en.wikipedia.org/wiki/Wikipedia:Copyrights#Re-use_of_text). The text exports identify the CC BY-SA 4.0 license and link to it; article-specific terms must also be respected. Whitespace is normalized in Spark, but the texts are not paraphrased or completed by a language model.

Only API collection happens outside Spark. The notebook reads the IMDb tables with `read_silver()`, applies explicit schemas to the JSON responses, removes duplicates, checks identities, cleans text, joins films and people, and computes coverage in PySpark. The driver receives only the selected cohort's identifiers and page titles, with an explicit size bound. Spark uses two cores and a 2 GB driver, and intermediate tables are written to Parquet to keep the jobs manageable.

The collector sends sequential Wikidata requests in batches of 100 IDs and Wikipedia requests in batches of at most 20 extracts, as documented by [TextExtracts](https://www.mediawiki.org/wiki/Extension:TextExtracts). Request starts are spaced by at least 1.5 seconds. It uses an explicit User-Agent, `maxlag=5` for Wikipedia, bounded retries, backoff and `Retry-After`. Successful responses are cached atomically using a hash of the request URL. A failed request stops the run rather than being counted as an absent biography. A rerun reuses completed requests.

I considered taking the full Plot section, but this would require more page-specific requests and would not solve missing articles. I kept introductions so the same collection method works for films and people. A second language or source could improve coverage, but would add matching and language-consistency issues; the remaining gaps are therefore measured explicitly. I also avoided approximate title/name matching because homonyms and remakes could produce convincing but incorrect enrichments.

New Wikidata requests explicitly start from the supplied ID list before joining properties and sitelinks. This query-plan change was checked against an already successful batch and returned the same bindings. Earlier successful cached responses remain usable.

The code uses configurable year bounds, ranking size and batch sizes. It ran on the complete selected cohort rather than a hand-picked sample. Checks verify unique memberships and principals, preserved film counts, source lineage for every retained text, and the three-biography requirement. Source coverage, English-language selection and the use of introductions remain limitations of the enrichment.

## 4. Streaming

### Results and streaming metrics

### Handling of late data

### Methodological explanation

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

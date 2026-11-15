# IMDb project report (group gr-02)

> Sections follow the team responsibilities in CONTRIBUTING.md. Result tables come from the notebooks. AI assistance is disclosed in PROJECT.md.

## 1. Data preparation

### 1.1 Percentage of null, missing or empty values per column

### 1.2 Five columns with the highest percentage of nulls

### 1.3 Other data quality issues

### 1.4 Handling of these values

### Methodological explanation

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
- The five entries with the most votes on their qualifying high-rated film are James McTeigue (*V for Vendetta*), Richard Marquand (*Return of the Jedi*), M. Night Shyamalan (*The Sixth Sense*), Richard Kelly (*Donnie Darko*) and Frank Miller (*Sin City*).

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
- The five largest early-minus-later mean-rating differences in the selected group are Saroj Khanal (4.18), Oya Aydogan (3.44), Mahesh (2.99), Jean-Claude La Marre (2.82) and Kristine DeBell (2.77). This ranking is within the selected group. In a separate local IMDb snapshot, 4,629 of 28,491 careers meeting the 20-year/15-film eligibility rule were selected (16.25%). The published CSV selects 4,638 people; its exact eligible-career denominator is not available in the versioned outputs, so the local percentage is indicative rather than an exact percentage for the published snapshot.

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

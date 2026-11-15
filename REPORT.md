# IMDb project report (group gr-02)

> Structure only. Each section is written by its owner (see CONTRIBUTING.md). Results tables come from the notebooks; the methodological explanations are written by us, without AI tools.

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

The main limits are incomplete principal credits, missing release dates and credits, and the absence of budget, country, franchise and career-stage controls. Current ratings and vote totals are not measurements taken at release, and votes are not box-office revenue. These comparisons are descriptive: they do not establish statistical independence or show that collaborating again caused the observed differences.

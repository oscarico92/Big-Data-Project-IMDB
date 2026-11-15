# IMDb project report (group gr-02)

> Structure only. Each section is written by its owner (see CONTRIBUTING.md). Results tables come from the notebooks; the methodological explanations are written by us, without AI tools.

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

### 2.3 Top three genres compared to the other genres

| 2025 film group | Films | Share of films | Share of votes |
|---|---:|---:|---:|
| At least one top-three genre | 9,751 | 45.30% | 74.46% |
| Other listed genres only | 10,496 | 48.76% | 24.92% |
| Unknown genre | 1,278 | 5.94% | 0.62% |

[Disjoint film comparison](results/exploration/q3_disjoint_movie_comparison.csv); [genre-membership comparison](results/exploration/q3_genre_comparison.csv).

### 2.4 Directors with exactly one movie rated >= 8.0 and other movies averaging <= 6.0

- 183 directors in the result.
- Example: James McTeigue — *V for Vendetta* rated 8.1; other eligible rated films average 5.975.
- [Director table](results/exploration/q4_directors.csv).

### 2.5 TV series whose worst episode is in the last season and best episode in the first two

- 412 qualifying series.
- Example: *Two and a Half Men* has 12 full seasons in the result, with best eligible episode rating 8.7 and worst 3.6.
- [Series table](results/exploration/q5_series.csv); [episode evidence](results/exploration/q5_episode_evidence.csv).

### 2.6 Actors and actresses successful in several languages

- 14,185 films meet the success threshold; 12,412 (87.50%) have a language estimate.
- 4,623 candidates have successful films in at least two estimated languages; 867 have at least three.
- [Coverage](results/exploration/q6_language_coverage.csv); [two-language candidates](results/exploration/q6_candidates_two_or_more_languages.csv); [three-language candidates](results/exploration/q6_candidates_three_or_more_languages.csv); [film estimates](results/exploration/q6_movie_language_estimates.csv); [evidence](results/exploration/q6_language_evidence.csv).

### 2.7 Actors and actresses whose popularity peaked early

- 4,638 selected actors and actresses; median early-minus-later mean-rating difference 0.66 point within this group.
- [Career table](results/exploration/q7_early_peak_actors.csv); [peak-film evidence](results/exploration/q7_peak_movies.csv).

### 2.8 Multi-talented film professionals

- 59,577 professionals have rated films in both the single-role and multiple-role groups.
- Mean person-level rating difference (multiple minus single): +0.059 point; median: +0.033 point.
- [Paired differences](results/exploration/q8_paired_differences.csv); [overall summary](results/exploration/q8_overall_comparison.csv).

### Methodological explanation

To complete personally: explain the cohort and thresholds for each question, why these measures were chosen, alternatives considered and their trade-offs, and the limits of the Q6 language and Q7 popularity proxies.

## 3. Data enrichment

### Results

### Methodological explanation

## 4. Streaming

### Results and streaming metrics

### Handling of late data

### Methodological explanation

## 5. Open question

### Question, why it is interesting, additional data

### Results

### Methodological explanation

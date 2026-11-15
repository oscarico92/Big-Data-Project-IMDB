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

I used the cleaned silver tables through `jobs/common.py`, joined records by IMDb IDs, and kept names only for display. Missing ratings were not imputed. The thresholds are parameters in notebook 02; they make each result reproducible on a new IMDb snapshot, although changing a threshold will change the cohort. The choices and alternatives for each question are as follows.

| Question | Choice and reason | Alternative and trade-off |
|---|---|---|
| Q1 — unusual runtime | I compared feature-length films with their genre mean and population standard deviation, requiring at least 30 reference films and an absolute z-score of at least 2. I excluded runtimes flagged as suspicious from both the reference and results. | A median and interquartile-range rule would resist extreme runtimes better, but its cutoff would have a different meaning across genres. The z-score is easy to compare, while remaining sensitive to the shape of each genre's runtime distribution. |
| Q2 — popular genres | I summed the current vote counts of films in each genre and release year from 1980 to 2025. I exported a separate film-count ranking to show how production volume differs from the chosen popularity measure. | Mean rating would measure average reception rather than the size of the observed audience; film count would measure output. Vote totals favour older films that have had more time to accumulate votes, so they do not reconstruct historical popularity in each year. |
| Q3 — top three versus the rest | I placed each film in one disjoint group according to whether any of its genres was in that year's vote-based top three, with a separate unknown-genre group. This counts each film and its votes once. | Comparing film–genre memberships preserves genre detail but counts multi-genre films in several totals. I exported both views and kept their percentages separate because they have different denominators. |
| Q4 — directors | I used director IDs in `title.crew`, required one film rated at least 8.0 with 100 or more votes, and required at least two other eligible films whose unweighted mean rating is at most 6.0. Each eligible film has the same weight. | A vote-weighted mean would let the most widely rated film dominate a director's average. Including very low-vote films would increase coverage but make a single small rating sample more influential; missing ratings cannot establish an additional hit. |
| Q5 — television series | I counted numbered episodes before filtering ratings, accepted series with at least three seasons of ten or more episodes, and compared episode extrema with at least 20 votes. Tied extrema qualify when one best episode is in seasons 1–2 and one worst episode is in the latest numbered season. | Requiring every season to have ten episodes would exclude otherwise eligible series with a short final season. Using every episode rating would increase coverage but give very small vote samples equal influence; ignoring season 0 and unknown seasons retains series while leaving some episodes out of the comparison. |
| Q6 — languages | I defined a successful film as rated at least 7.0 with 1,000 or more votes. I estimated its language from AKA titles matching `originalTitle`, preferring an explicit AKA language and otherwise using a limited region mapping; the most-supported candidate wins. | An external catalogue of original spoken languages could validate the result but would require another source, identity matching and coverage checks. IMDb AKA language concerns title presentation, so the current labels are estimates rather than confirmed spoken languages. Films without an estimate cannot contribute to the multi-language candidate counts. |
| Q7 — early peak | I required at least 20 observed career years and 15 dated films, split the observed span after its first quarter, and required at least three films with 100 or more votes on each side. Both the early maximum and early mean rating had to exceed the later values. | A vote-count comparison would be closer to audience reach, but votes accumulate over time and are strongly affected by film exposure. Ratings follow the question's highest-rated-film example, though they measure reception rather than fame; incomplete principal credits can also shift the observed career span. |
| Q8 — multiple roles | I combined actor/actress, director and writer film credits, deduplicated person–film–role entries, and compared each person's rated single-role and multiple-role films. The overall difference gives one weight to each person with both kinds of film. | A pooled film comparison would give prolific people more weight and mix differences between people with differences between projects. The paired view reduces that problem, but it selects only people with both project types and does not control for film budgets, genres or career stage. |

These are descriptive comparisons. Current IMDb votes and ratings, incomplete credits, missing genres and dates, and differences in rating coverage limit what can be inferred across questions. I checked the complete notebook run for errors and reconciled the year coverage, season thresholds, language coverage and Q8 paired mean with the exported CSVs.

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

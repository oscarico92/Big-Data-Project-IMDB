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

### Results

### Methodological explanation

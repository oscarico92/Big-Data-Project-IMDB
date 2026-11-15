# IMDb project report (group gr-02)

> Each section is maintained by its owner (see CONTRIBUTING.md). Figures below come from the saved notebook results.

## 1. Data preparation

### 1.1 Percentage of null, missing or empty values per column

### 1.2 Five columns with the highest percentage of nulls

### 1.3 Other data quality issues

### 1.4 Handling of these values

### Methodological explanation

## 2. Data exploration

The figures in this section come from the full IMDb silver-layer run saved with [notebook 02](notebooks/02_data_exploration.ipynb). IMDb ratings and vote counts describe the downloaded snapshot; they are not historical measurements taken in each release year. Unless stated otherwise, the analyses exclude titles marked as unreleased and do not fill missing ratings.

### 2.1 Feature-length movies with an unusual runtime for their genre

The analysis found **30,232 film–genre rows**, representing **20,873 distinct films** across 26 genres ([full result](results/exploration/q1_unusual_runtimes.csv)). Of those rows, 25,945 are longer and 4,287 are shorter than their genre reference by at least two standard deviations. A film can appear more than once when it has multiple genres, so the row count is not a count of unique films.

I compared each feature-length film with the mean and population standard deviation of its genre across the available years. Genres needed at least 30 reference films and nonzero variance. I removed runtimes flagged as suspicious from both the reference and the returned films. The resulting `z_runtime` measures an unusual duration within this snapshot; it does not show that a runtime is erroneous or that film lengths follow a normal distribution.

### 2.2 Top three genres per year (1980-2025)

Both rankings cover all **46 years** from 1980 through 2025 and return three genres per year. Popularity is measured by the sum of current IMDb votes, while the second ranking counts films. The distinction matters: in 2025, Documentary ranks second by film count but does not enter the top three by votes ([votes ranking](results/exploration/q2_top_three_by_votes.csv), [film-count ranking](results/exploration/q2_top_three_by_movie_count.csv), [all genres](results/exploration/q2_all_genres.csv)).

| Release year | Top three by votes | Top three by film count |
|---|---|---|
| 1980 | Drama, Adventure, Horror | Drama, Comedy, Action |
| 2025 | Drama, Action, Comedy | Drama, Documentary, Comedy |

Each film contributes once to each of its listed genres. A film without a rating still contributes to the production count but has no recorded votes. These votes were observed in the current snapshot, so the 1980 ranking does not represent what audiences preferred in 1980 itself.

### 2.3 Top three genres compared to the other genres

For the 2025 vote ranking, films with at least one top-three genre account for **9,751 films (45.30%)** and **74.46% of observed votes**. Films with only other listed genres account for 10,496 films (48.76%) and 24.92% of votes; 1,278 films (5.94%) have no listed genre and account for the remaining 0.62% of votes ([disjoint film comparison](results/exploration/q3_disjoint_movie_comparison.csv)). The top-three genres are Drama, Action and Comedy in this year.

I used disjoint groups for the film comparison: a film enters the top-three group if any of its genres is in that year's top three, and its votes are counted once. The separate [genre-membership comparison](results/exploration/q3_genre_comparison.csv) counts each film–genre membership. Its percentages answer a different question because a multi-genre film can contribute to several genre totals; for 2025 the top-three memberships have 39.33% of the summed genre votes. Neither comparison adjusts for changes in the age of films or the amount of time available to accumulate votes.

### 2.4 Directors with exactly one movie rated >= 8.0 and other movies averaging <= 6.0

**183 directors** satisfy the criteria in the snapshot ([director table](results/exploration/q4_directors.csv)). For example, James McTeigue has one eligible film rated at least 8.0, *V for Vendetta* (8.1), while his other eligible rated films average 5.975. This is an example of the rule, not evidence that his other work is uniformly rated below 6.0.

Director identities come from `title.crew`. I required exactly one film rated at least 8.0 with at least 100 votes, at least two other films meeting the 100-vote threshold, and an unweighted mean rating of at most 6.0 for those other eligible films. Unrated films and films with fewer votes remain in the observed film counts but cannot establish an additional high-rated hit. The vote threshold reduces the influence of very small rating samples, while the arithmetic mean gives each eligible film equal weight.

### 2.5 TV series whose worst episode is in the last season and best episode in the first two

**412 series** have at least three seasons containing ten or more episodes and meet the rating-position condition ([series table](results/exploration/q5_series.csv), [episode evidence](results/exploration/q5_episode_evidence.csv)). *Two and a Half Men*, for example, has 12 qualifying full seasons in this result; its best eligible episode rating is 8.7 and its worst is 3.6.

I counted numbered episodes per season before looking at ratings. At least three seasons must have ten episodes each, but other seasons may be shorter, including the final one. Season 0 and episodes without a positive season number are ignored rather than disqualifying a series. Episode maxima and minima use ratings with at least 20 votes. Ties are retained: at least one best-rated episode must be in seasons 1–2 and at least one worst-rated episode in the latest numbered season. The latest season may still be ongoing, and episode rating coverage varies by series, so the result is sensitive to missing or low-vote episode ratings.

### 2.6 Actors and actresses successful in several languages

Among **14,185** films rated at least 7.0 with at least 1,000 votes, **12,412 (87.50%)** received an original-language estimate ([coverage](results/exploration/q6_language_coverage.csv), [film estimates](results/exploration/q6_movie_language_estimates.csv)). The analysis identifies **4,623** actors or actresses with successful films in at least two estimated languages, including **867** with at least three ([two-language candidates](results/exploration/q6_candidates_two_or_more_languages.csv), [three-language candidates](results/exploration/q6_candidates_three_or_more_languages.csv), [film-level evidence](results/exploration/q6_language_evidence.csv)).

IMDb's AKA language describes the language of a title, not necessarily the spoken language of a film. I therefore treated these as **estimates**: a non-original AKA title had to match the film's `originalTitle`; I used its explicit language when available and otherwise a limited region-to-language mapping. The most frequently supported language was selected, with an alphabetical tie-break. Distribution practices, unchanged titles abroad and multilingual regions can bias this inference. The 12.50% of successful films without an estimate are excluded from the actor-language comparison. The candidate lists should not be presented as confirmed multilingual filmographies without an independent spoken-language source.

### 2.7 Actors and actresses whose popularity peaked early

The selection returns **4,638 actors and actresses** ([career table](results/exploration/q7_early_peak_actors.csv), [peak-film evidence](results/exploration/q7_peak_movies.csv)). Within this selected group, the median difference between early and later mean ratings is **0.66 rating point**. This is a description of the selected careers, not an estimate of the typical career pattern for all actors.

I used the first and last dated films in the available principal credits to define an observed career. It needed to span at least 20 years and include at least 15 dated films. The early period is its first quarter. Each side needed at least three films rated with 100 or more votes, and both the maximum and mean early ratings had to exceed their later counterparts. The question uses “popularity,” but the measured outcome here is IMDb **rating**, not vote volume, box-office revenue or fame. Missing principal credits, release years and ratings can move a person's observed career boundaries or change the comparison.

### 2.8 Multi-talented film professionals

For the **59,577** professionals who have rated films in both the single-role and multiple-role groups, the mean person-level rating difference (multiple minus single) is **+0.059 point** and the median difference is **+0.033 point** ([paired differences](results/exploration/q8_paired_differences.csv), [overall summary](results/exploration/q8_overall_comparison.csv)). The small positive average does not show that taking multiple roles improves a film's rating.

I combined actor/actress, director and writer film credits, using `title.crew` as well as principal credits, and removed duplicate person–film–role entries. A professional has multiple career roles if at least two distinct roles appear across observed films; a multiple-role project requires at least two roles on that particular film. I compared each person's rated films with one role to their rated films with simultaneous roles, then averaged differences across people who have both kinds of film. This gives each comparable person equal weight, but the films and career stages in the two groups can differ. The complete large project-level tables remain in local Parquet outputs; the versioned CSVs contain the paired and overall summaries.

### Methodological explanation

All eight analyses read the cleaned silver tables through `jobs/common.py` and use PySpark joins, grouping and window operations. I kept IMDb IDs as join keys and used names only as labels. Fixed-name CSVs hold the versioned result tables; the full Parquet outputs stay outside Git. Numeric thresholds are parameters in notebook 02, so the classifications can be rerun on another IMDb snapshot.

The main limitations are incomplete credits and metadata, different vote coverage across films and episodes, and the fact that IMDb ratings and vote totals change over time. The language and career questions rely on explicitly described proxies. Counts from different questions are not interchangeable because they use different cohorts, time windows, vote thresholds and units of observation. I checked the full run for execution errors and cross-checked year coverage, season thresholds, language-estimate coverage, and the paired Q8 summary against its detailed CSV.

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

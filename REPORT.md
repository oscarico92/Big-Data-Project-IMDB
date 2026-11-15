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

### Results

### Methodological explanation

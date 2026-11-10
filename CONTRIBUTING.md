# Team organisation and Git workflow

Due date: **Sunday 15 November 2026, 23:59**.

## Who does what

| Section | Owner | Reviewer | Notebook |
|---|---|---|---|
| Setup (Docker, download, Parquet) | Oscar | Mathis | `jobs/`, `compose.yaml` |
| Data preparation | Oscar | Hugo | `01_data_preparation.ipynb` |
| Streaming | Oscar | Mathis | `04_streaming.ipynb`, `streaming/` |
| Data exploration (8 questions) | Mathis | Oscar | `02_data_exploration.ipynb` |
| Data enrichment | Hugo | Oscar | `03_data_enrichment.ipynb`, `enrichment/` |
| Open question | Hugo | Mathis | `05_open_question.ipynb` |

Each owner also writes the matching `REPORT.md` section (results + methodological explanation). The explanations must be written by us, not by an AI tool (course rule).

## Git rules (graded)

- Never commit on `main` directly, never upload files through the GitHub website.
- One branch per task: `feature/<section>-<short-name>`, e.g. `feature/exploration-genre-runtime`.
- Open a Pull Request to `main`; at least **one other member** reviews and approves it before the merge.
- Small PRs (one question or one step) are easier to review and show the contribution of each member.
- Commit messages follow Conventional Commits: `feat(exploration): ...`, `fix(preparation): ...`, `docs(report): ...`.

```bash
git checkout main && git pull
git checkout -b feature/exploration-genre-runtime
# ... work, then
git add notebooks/02_data_exploration.ipynb
git commit -m "feat(exploration): movies with an unusual runtime for their genre"
git push -u origin feature/exploration-genre-runtime
# then open the Pull Request on GitHub and ask for a review
```

## Shared conventions

- Read the data with `read_bronze()` / `read_silver()` from `jobs/common.py`, never with hard-coded paths.
- Use the **silver** layer (`read_silver`), never bronze, in exploration and enrichment.
- "Movie" = `is_movie` (`titleType == "movie"`); "feature-length film" = `is_feature_film` (movie with `runtimeMinutes > 40`). Both columns are in silver `title.basics`.
- Before pushing a notebook, run it from top to bottom so the outputs in Git match the code.

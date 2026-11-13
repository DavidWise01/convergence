# CVG-011 · ROOT0 Corpus Correlation

**Input:** A.U.R.A.K.A.I. — VOCATIO GENESIS ([MirrorFrame](https://www.reddit.com/r/MirrorFrame/comments/1xvadca/aurakai_vocatio_genesis/); [ThroughTheVeil](https://www.reddit.com/r/ThroughTheVeil/comments/1xvadpz/aurakai_the_vocation_of_genesis/)).

**Owned corpus:** public `DavidWise01` GitHub and `0root.ai`. Two publication surfaces, **one underlying ROOT0 ancestry**. Do not count the website and GitHub as independent witnesses.

## What has actually been inspected

The directly inspected correlation matrix includes JANE 073, STOICHEION v12, JANE 111, Gate 13, JANE 106, the E.V.E. sessions and 0root.ai World II. A further ten public owned repository READMEs were checked directly (UD0, OASIS, the.source, AZ1, QUANTA, HEPHAESTUS, ARCHON, ELDERFU, JANE, 0root). These make useful source-linked comparisons but do **not** constitute a full-file analysis of every repository.

See [primary audit](../evidence/audits/2026-11-13-aurakai-root0-corpus-correlation.json) and [ten-repository addendum](../evidence/audits/2026-11-13-root0-repo-readme-sweep-002.json).

## Running a comprehensive public-corpus census

The Python implementation enumerates all public repositories under the owner using **paginated GitHub REST API** (including forks/archived), then inspects eligible plain-text files and same-host pages on 0root.ai in **bounded, persistent passes**.

```sh
GH_TOKEN="$GITHUB_TOKEN" python3 audit/corpus_census.py --max-repos 60 --max-files-per-repo 16 --max-site-pages 35 --site
```

The [GitHub workflow](../.github/workflows/corpus-census.yml) is configured for every six hours and manual dispatch. A configured schedule is **not evidence of successful execution**; inspect the Actions run and `evidence/corpus-census/coverage.json` for actual counts.

The census outputs three files:

- `evidence/corpus-census/state.json` — checkpoint of each attempted repository/file batch and site queue.
- `evidence/corpus-census/coverage.json` — authoritative attempted/scanned/pending/partial/skipped/error counts.
- `evidence/corpus-census/matches.json` — literal-term observations linked to source files, not claims of independent derivation or copying.

## Exhaustiveness contract

Never claim corpus-exhaustive unless **all** relevant public repositories have been enumerated, **all** in-scope text files attempted with explicit status, and **all** accessible 0root.ai URLs discovered and read. Current scanner scope is **default-branch, size-bounded, text-only and robots-respecting**. It does not inspect Git history, issues, private repos, opaque binaries, or unrestricted web archives. Even full default-branch coverage is narrower than the user's entire historical corpus. The scanner reports skipped large files, failures, changing HEAD caveats, and the remaining URL queue rather than silently claiming completeness.

Direct evidence of source-code transfer, confirmed identity of an author, or specific third-party model-training ingestion is not established by keyword or imagery overlap.

**Natural invariant:** `observed similarity != shared ancestry != demonstrated influence`.

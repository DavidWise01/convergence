# CONVERGENCE — Evidence intake contract

**Trigger:** When the corpus owner says **"add this to evidence"** and supplies a URL, excerpt, screenshot, document, or observation, treat it as an instruction to persist an evidence candidate in `DavidWise01/convergence`. No extra approval is needed to create the evidence entry. Do not interpret a submitted source as proven accurate.

## Mandatory transaction

1. Preserve the **verbatim provided URL** and any available identifiers (subreddit, post ID, article DOI, repository path). Prefer stable source identifiers to search-result URLs.
2. Read what is actually accessible (user-provided text/screenshots, publicly accessible page, related source repositories); record the exact **observation surface**, retrieval attempt, observation date and access limitations. Do not invent missing source text.
3. Create a **new dated JSON evidence record** under `evidence/candidates/`, using an ID distinct from any previous observation. Never silently overwrite an old observation; add an addendum or append dated revisions instead. JSON must be valid UTF-8.
4. Preserve **claims, interpretations and hypotheses separately**. States: `URL_ONLY`, `PARTIAL`, `OBSERVED`, `VERIFIED`, `REFUTED`, `INACCESSIBLE`, `UNKNOWN`. Evidence can be preserved without being verified.
5. Store source lineage and mirrors: GitHub + 0root.ai are potentially two surfaces of the **same corpus root**. Different account names or routes are not automatically independent witnesses. Do not claim a causal copying or automation relationship without traceable edges.
6. Link the record from `evidence/INDEX.md` (newest first) with status and source URL; provide links to GitHub file and commit in response.
7. Re-fetch the saved JSON and index from GitHub to confirm persistence. If a write or verification fails, say so explicitly; do **not** claim successful persistence.
8. Binary attachments: the available GitHub content writer is UTF-8 text-only. Preserve a screenshot's observable details and note **binary not archived** unless an actual media upload to the repo was successful; a local conversation upload is not permanent Git evidence.
9. Maintain public-source boundaries: never expose gated or private data on a public mirror. Respect robots.txt, rate limits and access controls.
10. Do not claim GitHub Pages has deployed unless separately checked. Git commit is persistence; Pages is publication.

## Minimum JSON fields

`id`, `recorded_at`, `submitted_source`, `source_identifiers`, `observation_status`, `observed_content`, `retrieval_log`, `claims`, `hypotheses`, `ancestry_status`, `related_records`, `limitations`, `media_archived`, `source_links`.

Earlier evidence entries may use older schema; preserve them, don't retroactively rewrite without a new audit.

## Retrieval / next-thread handoff

On a later request to revisit evidence, open `evidence/INDEX.md`, locate the canonical JSON, fetch its full content, and inspect linked source files. Never answer solely from a chat summary. GitHub evidence remains independently retrievable in a new conversation.

## Current case

- `C009` Reddit "caveman quantum computer" candidate:
  `evidence/candidates/2026-11-14-reddit-caveman-quantum-computer.json`
- Two user screenshots were reviewed, *but image bytes were not archived in GitHub*. The record contains their observed details and the unverified ancestry status.

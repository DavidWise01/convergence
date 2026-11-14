# CONVERGENCE — Evidence index

Canonical intake and retrieval rules: [INTAKE.md](./INTAKE.md).

| Evidence | Observation | Status | Canonical record |
| --- | --- | --- | --- |
| H013 · 2026-11-14 | 1832 telegraph → 1953 ferrite-core memory, major-war overlay | Historical chronology; no claim of continuous physical infrastructure | [H013 chronology](./audits/2026-11-14-h013-war-overlay-substrate-timeline.md) |
| C010 · 2026-11-14 | [r/agi: Coxon on Anthropic / Mythos training efficiency](https://www.reddit.com/r/agi/comments/1xw5nxg/coxon_on_why_he_quit_anthropic_is_seeing/) | Reported statement; training-compute numbers not independently verified | [C010 candidate](./candidates/2026-11-14-reddit-coxon-mythos-compute-efficiency.json) |
| D011 · 2026-11-14 | User PDF: TD-STACK-WP-2026-001 / Mythos Governance Stack | Six-page user-supplied paper inspected; SHA256 retained; attribution an author's assertion; PDF bytes not Git-archived | [D011 metadata](./documents/2026-11-14-td-stack-mythos-attribution-metadata.json) |
| H012 · 2026-11-14 | Bell Labs transistor signal 1947; Manchester digital computer 1953 | Historical source-backed timeline; first single bit not established | [H012 audit](./audits/2026-11-14-transistor-first-signal-bit-timeline.json) |
| B009 · 2026-11-14 | Cross-route ancestry / two paths versus independent roots | Synthetic 12/12 local tests PASS; real-world source identities not verified | [B009 report](./audits/2026-11-14-b009-cross-route-ancestry.md) |
| C009 · 2026-11-14 | [r/ChatGPT "caveman quantum computer"](https://www.reddit.com/r/ChatGPT/comments/1xvyhxn/did_chatgpt_just_design_a_caveman_quantum_computer/) | Partial screenshots observed; source ancestry UNKNOWN; screenshot files **not archived** in Git | [2026-11-14 Reddit candidate](./candidates/2026-11-14-reddit-caveman-quantum-computer.json) |
| B008 · 2026-11-13 | Parallel transport / 5 wired + 5 wireless + 7 OSI analytical model | Synthetic model, not public-internet provenance | [Test source](../audit/parallel17.py) |
| B006 · 2026-11-13 | Historical adapter persistence examples | Documented sources and synthetic experiment; not a global attribution | [Audit](./audits/2026-11-13-b006-adapter-persistence-test.md) |

Other retained candidate, survey, and audit records remain in their original files under `evidence/`. This index is an **intake entry point**, not an assertion that every older record has been enumerated.

## New evidence

When a URL, screenshot or file is submitted with **"add this to evidence"**:

1. Store a dated candidate JSON and commit it.
2. Add a row here, with the actual observation and uncertainty status.
3. Verify both GitHub files and return direct source, record, and commit links.

Do not promote plausible automated derivation to confirmed ancestry without an independently verifiable causal link.

- **H014 (2026-11-14)** — [REAP: CERN Mercury → IBM 709 software lineage](./audits/2026-11-14-h014-reap-program-lineage.md). Primary-document evidence; source binaries and downstream exact descendants unresolved.

- **H015 (2026-11-14)** — [CERN public computing lineage, software catalogue and bounded open-data harvester](../cern-public/README.md) · [source index](../cern-public/sources.json) · [harvest tool](../cern-public/harvest.py). Public inventory committed; API snapshot is generated only after running the manual workflow.

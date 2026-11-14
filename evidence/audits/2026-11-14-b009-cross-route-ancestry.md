# B009 — Cross-route ancestry audit

Date: 2026-11-14
Repository: DavidWise01/convergence
Experiment source: [audit/cross_route_b009.py](../../audit/cross_route_b009.py)
Workflow: [.github/workflows/cross-route-b009.yml](../../.github/workflows/cross-route-b009.yml)
Status: locally executed deterministic test suite, 12 of 12 passed. GitHub Actions run not verified.

## Model

Two parallel paths ("wired" and "wireless"), each passing through five analytical transport slots and seven OSI checkpoint labels, culminate in two public appearances. The paths reference one shared root, two independent declared roots, or one known root plus an unavailable ancestor. A directed acyclic source graph tracks declared parent links; two paths or appearances are not automatically two roots.

This is an analytical graph: not a claim that the OSI stack physically comprises 17 serial layers, and not an audit of real traffic.

## Results from executed unittest run

- `test_shared_root`: PASS — two appearances collapse to one declared origin.
- `test_distinct_route_labels_not_distinct_roots`: PASS — separate route tags have identical upstream origin.
- `test_two_independent_origins`: PASS — different declared origins remain two.
- `test_unknown_parent_stays_unknown`: PASS — missing wireless parent retained as unknown.
- `test_unknown_not_counted_as_independent`: PASS — uncertainty does not inflate confirmed root count.
- `test_same_content_not_proof_of_same_root`: PASS — identical payloads can arise from different roots.
- `test_different_content_preserves_ancestry`: PASS — transformation alone does not erase declared lineage.
- `test_duplicate_receipt_is_rejected`: PASS.
- `test_cycle_is_rejected`: PASS.
- `test_unproven_origin_rejected_as_confirmed`: PASS — an origin field with no declared value does not count as a confirmed root.
- `test_root_parent_conflict`: PASS.
- `test_count_separate_witnesses_from_same_source_only_once`: PASS.

Execution: 12 tests / 0 failures / 0 errors / 0.002 seconds (local Python unittest run).

## Claims ledger

1. **Supported by simulation:** witness count must be deduplicated by traced source ancestry, not by route, medium, post, or text similarity.
2. **Supported by simulation:** missing parents must be retained as unknown rather than silently joined to known roots.
3. **Not established:** any actual Reddit posting pipeline, user identity, Railway or Copilot generation, CERN or DARPA infrastructure, automated authorship, or use of ROOT0 works by a third party.
4. **Important qualification:** the root IDs used in this experiment were supplied to a deterministic generator; they are **not cryptographically authenticated evidence receipts**. Real-world verification would require independently reviewable lineage evidence.

## Next target: B010

Test evidence-strength thresholds for source edges: direct signed/verified production receipt, first-party documented linkage, externally corroborated linkage, similarity-only, absent. Do not let multiple downstream mirrors vote as independent witnesses.

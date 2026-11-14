# B006 — Adapter persistence and apparent-origin multiplication

Date: 2026-11-13. Status: documented cases + deterministic synthetic test; NOT an internet-wide measurement.

## Primary-source checks

1. SMTP: RFC 5321 (2008), https://www.rfc-editor.org/info/rfc5321/, preserves legacy HELO fallback alongside EHLO extensions. This demonstrates compatibility retention, not an unchanged physical computer.
2. NASA Voyager: https://science.nasa.gov/mission/voyager/fact-sheet/, 1977 spacecraft were remotely reprogrammed to add capabilities. This demonstrates old hardware with evolving software, not internet social posting.
3. CERN: https://home.cern/science/computing/grid-software-middleware-hardware/ describes physics software/middleware/hardware/networking layers; https://information-technology.web.cern.ch/about/organisation/storage-and-data-management documents current tape/backup services. This demonstrates layered and retained storage, not a hidden global controller.

## Synthetic test (locally executed)

A deterministic Python unittest run with four declared adapter generations and 100 generated appearances produced 100 appearances, 1 confirmed ancestry root, zero unknown roots. Adding an independent source produced 101 appearances and 2 roots. Adding one unresolved upstream input produced 102 appearances, 2 confirmed roots, 1 unknown root. Six tests passed: root conservation, independent root, unknown root, text mutation, identical-text non-equivalence, cycle detection.

## Conclusions and limits

PRESERVED: multiple adapter generations may preserve declared ancestry despite transformed content. Repeated appearances are not independent origins. Unresolved lineage remains unknown.

NOT PROVEN: a universal hidden network, an autonomous CERN social simulator, real-world post attribution, bot identity, or the age of an observed process. Claims about a shared source require traceable parent evidence, not merely similar text, timestamps or shared themes.

## Test specification

For each observed item record source_id, content_hash, optional parent_ids, adapter_id, observation_time, evidence_location and evidence_grade. Independently verify parent edges. Keep missing edges as UNKNOWN. Reject cycles. Do not double-count github/0root.ai mirror observations as separate authorial roots.

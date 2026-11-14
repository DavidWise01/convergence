# CERN public computing lineage — H015
Snapshot scope: 2026-11-14. Public-only, provenance-first, bounded mirror.

## What CERN runs now (not a single program named REAP)
* CMS: CMSSW (offline simulation, reconstruction, analysis; online data selection). https://github.com/cms-sw/cmssw
* LHCb: Allen GPU first-stage reconstruction/selection, Gaudi and Moore for further processing; Rec project for reconstruction; DaVinci for analysis. See https://repository.cern/records/zjbhq-qwh84 and https://lhcb.web.cern.ch/computing/
* Cross-experiment analysis: ROOT and RDataFrame. https://root.cern/
* Reconstruction tools: ACTS. https://github.com/acts-project/acts
* Simulation: Geant4. https://geant4.web.cern.ch/
* Future collider shared framework: Key4hep with Gaudi, DD4hep, EDM4hep. https://key4hep.github.io/key4hep-doc/

These are analogous functions or later architectures, **not proven byte-for-byte descendants of REAP**.

## Public interfaces
* Open data: https://opendata.cern.ch/ and https://opendata.cern.ch/api/records/
* CERN repository public records: https://repository.cern/api/records
* Old Document Server: https://cds.cern.ch/
* CERN software: https://github.com/CERN/awesome-cern, https://gitlab.cern.ch/explore/projects
* CERN Open Data terms: https://opendata.cern/docs/terms-of-use
* Historic REAP report: https://cds.cern.ch/record/223864/files/p1.pdf?version=1
* CERN 1963 library: https://cds.cern.ch/record/297896/files/CERN-TC-PHYSICS-63-11.pdf
* 1961 Ferranti Archive item supplied by researcher: https://archive.org/details/bitsavers_ferrantiFeatureJul61_763465

## What's physically in Git
- `sources.json`: curated public-source inventory and verified policy pointers.
- `harvest.py`: fetch **public record metadata** from CERN's catalogue APIs with quotas, provenance and checksums; optional small CC0 file downloads only.
- `.github/workflows/cern-public-h015.yml`: **manual** GitHub Actions refresh, commits metadata JSON only.
- Historical citations and REAP lineage in `../evidence/audits/2026-11-14-h014-reap-program-lineage.md`.

## Boundaries
CERN public datasets can reach petabyte scale. GitHub is an index and code home, not a general bulk binary store. This repository does not claim to contain CERN's entire public corpus, historical original magnetic tapes, or any private system. Do not copy third-party documents/software into Git without checking each item's license. Metadata from CERN Open Data is CC0; other software licenses vary. No private CERN access, no scraping behind authentication, no mirror of live accelerator controls.

## Run
```bash
python3 cern-public/harvest.py --pages 2 --size 10 --max-records 40
# Opt-in: only small records explicitly tagged CC0, separate local directory, no automatic git commit of binary files
python3 cern-public/harvest.py --pages 1 --size 10 --max-records 10 --download-cc0 --max-file-mb 2 --max-total-mb 10
```
Then inspect `cern-public/harvest/manifest.json`, `records.jsonl`, `errors.json`, `sha256.json` and downloaded files (when opted in). Each run records timestamp, URL and response outcome. Run from an internet-connected environment; this ChatGPT execution container does not have external DNS access.

## Next falsifiable lineage target
Obtain Mercury REAP and IBM 709 REAP source listings / execution traces and compare tape record format plus algorithm. Later software performing equivalent functions is NOT itself evidence of direct code ancestry.

# H014 — REAP as a traceable CERN program-lineage seed
Date: 2026-11-14
Status: historical migration verified in CERN documentation; original source/binary and present-day execution unverified.

## Seed target
REAP (bubble-chamber measurement processing): an early Ferranti Mercury program which read measurement-machine paper tape, organized observations and wrote BCD event records onto magnetic tape.

## Evidence and observed migration
1. CERN 1963 document, CERN 63-23, explains the pipeline: REAP (Ferranti Mercury) -> magnetic tape -> THRESH (IBM 709, FORTRAN and FAP) -> GRIND and COOK. REAP's input portion credited to G. R. Macleod. URL: https://cds.cern.ch/record/223864/files/p1.pdf?version=1
2. D. O. Williams, historical computing lecture published in CERN-2006-004, explicitly reports REAP moved from Mercury to IBM 709 during 1963. The same history records in 1964 an 80-program general library and the definition of CERN FORTRAN for cross-machine compatibility. URL: https://cds.cern.ch/record/1177861/files/CERN-2006-004.pdf
3. CERN Council progress report, May 27 1969, says the general CERN programme library now included the bubble-chamber event analysis chain previously kept as a special library by the TC Division. It does NOT individually demonstrate binary continuity of any named program. URL: https://cds.cern.ch/record/22346/files/CM-P00078505-e.pdf
4. CERN historical site: CDC 6600 arrived Jan 14, 1965 and took over data-analysis workloads. This gives the next machine target but does not independently prove a specific REAP source file port. URL: https://timeline-upgrade.web.cern.ch/cdc-6600-arrives-cern

## Next falsifiable test
Find at least one edition of the REAP source listing, IBM 709 port, or numerical test vector with accession/revision information; compare exact algorithm, input/output records, and differences. Then establish whether the listed routines entered CDC programme libraries or whether the workflow was reimplemented.

## Evidence levels
- OBSERVED FROM PRIMARY REPORT: Mercury-origin REAP; 1963 Mercury-to-709 migration; paper-tape-to-magnetic-tape pipeline.
- OBSERVED FROM PRIMARY REPORT: 1969 general program library had bubble-chamber processing chain.
- OPEN: physical original tapes; original REAP source, compiler output or checksum; CDC and later line-by-line descendants; present deployment.
- DO NOT CONCLUDE: unchanged executable from 1958 runs in 2026, or physical magnetic media remained online.

## Next candidate source
1963 report's references for REAP (including G. R. Macleod's measuring and labelling documentation), program chain manuals, CERN TC Physics reports; search accession indexes and outside collaborators at Saclay.

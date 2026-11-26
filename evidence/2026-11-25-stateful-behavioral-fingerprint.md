# CONVERGENCE-016 — Stateful behavioral fingerprint

Phase II 6/8. Synthetic reference model derived from supplied EVE transcript requirements. Nested interruptions, explicit checkpoints and verification-before-close are proposed test extensions, not historical claims. No actual Gemini or Claude Code execution. Twelve authored stateful fixtures and deterministic replay checks, all passed in this reference model. Tests are specification checks, not independent evidence of copying or originality. Context contamination represented as a rejected event, not real language-model isolation. P3 EVE conceptual lineage; P2 external general architecture; P1 specific /btw origin, provisional. No transmission established. Next: compare external documented semantics against fixtures and identify discriminating differences.

## Executed fixtures

```json
[
  {
    "id": "S01",
    "events": [
      "tangent",
      "advance"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S02",
    "events": [
      "tangent",
      "contaminate"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S03",
    "events": [
      "feedback",
      "execute",
      "advance"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S04",
    "events": [
      "authorize",
      "execute",
      "advance"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S05",
    "events": [
      "tangent",
      "close"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S06",
    "events": [
      "tangent",
      "verify_side",
      "close"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S07",
    "events": [
      "lattice",
      "verify_side",
      "close"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S08",
    "events": [
      "tangent",
      "lattice",
      "verify_side",
      "close"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S09",
    "events": [
      "tangent",
      "lattice",
      "verify_side",
      "close",
      "verify_side",
      "close"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S10",
    "events": [
      "tangent",
      "authorize",
      "execute"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S11",
    "events": [
      "authorize",
      "execute",
      "verify_delivery",
      "advance"
    ],
    "pass": true,
    "replay": true
  },
  {
    "id": "S12",
    "events": [
      "authorize",
      "execute",
      "verify_delivery",
      "advance",
      "advance"
    ],
    "pass": true,
    "replay": true
  }
]
```

.dlw

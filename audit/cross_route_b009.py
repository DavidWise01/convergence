"""B009: Cross-route ancestry, evidence receipts, and independence audit.

This is a synthetic model. Separate network routes are NOT independent source
roots. A signed receipt is not simulated: receipts are declared observations
that can be checked for internal consistency, not proof of real-world origin.
"""
from dataclasses import dataclass
from collections import defaultdict
import unittest

@dataclass(frozen=True)
class Receipt:
    item: str
    parent: str | None
    root: str | None
    surface: str
    route: str
    fingerprint: str

def audit(receipts, endpoints):
    by_item = {}
    for record in receipts:
        if record.item in by_item:
            raise ValueError("duplicate item: " + record.item)
        by_item[record.item] = record
    visiting = set()
    cache = {}
    def trace(key):
        if key in cache:
            return cache[key]
        if key in visiting:
            raise ValueError("cycle")
        if key not in by_item:
            return frozenset(), frozenset((key,)), frozenset()
        r = by_item[key]
        if r.root and r.parent:
            raise ValueError("declared root also has parent")
        visiting.add(key)
        if r.root:
            answer = (frozenset((r.root,)), frozenset(), frozenset((key,)))
        elif r.parent is not None:
            roots, unknown, path = trace(r.parent)
            answer = (roots, unknown, path | frozenset((key,)))
        else:
            answer = (frozenset(), frozenset((key,)), frozenset((key,)))
        visiting.remove(key)
        cache[key] = answer
        return answer
    results = {key: trace(key) for key in endpoints}
    all_roots = frozenset().union(*(v[0] for v in results.values()))
    unknown = frozenset().union(*(v[1] for v in results.values()))
    groups = defaultdict(list)
    for key, (roots, missing, _) in results.items():
        if len(roots) == 1 and not missing:
            groups[next(iter(roots))].append(key)
    return {"roots": all_roots, "unknown": unknown, "by_endpoint": results,
            "witness_groups": dict(groups), "independent_confirmed": len(all_roots),
            "uncertainty_present": bool(unknown)}

def network(root_b=False, orphan=False, mirror=False, transform=False):
    root_a = Receipt("root-A", None, "A", "GitHub", "source", "original")
    rows = [root_a]
    if root_b:
        rows.append(Receipt("root-B", None, "B", "independent-origin", "source", "new"))
    for route in ("wired", "wireless"):
        parent = "root-A"
        if route == "wireless":
            if root_b:
                parent = "root-B"
            elif orphan:
                parent = "unavailable"
        # Five transport positions + seven OSI checkpoints per path.
        for i in range(5):
            key = f"{route}:transport:{i+1}"
            rows.append(Receipt(key, parent, None, route, route, f"transport-{i}"))
            parent = key
        for i, label in enumerate(("physical","data-link","network","transport","session","presentation","application")):
            key = f"{route}:osi:{label}"
            rows.append(Receipt(key, parent, None, route, route,
                                ("transformed" if transform else "original") if i == 6 else label))
            parent = key
        rows.append(Receipt(route + ":post", parent, None, "Reddit" if route == "wireless" else "site", route, "same-content" if mirror else route))
    return rows, ("wired:post", "wireless:post")

class CrossRouteAudit(unittest.TestCase):
    def test_shared_root(self):
        r, ends = network()
        result = audit(r, ends)
        self.assertEqual(result["roots"], frozenset(("A",)))
        self.assertEqual(result["independent_confirmed"], 1)
    def test_distinct_route_labels_not_distinct_roots(self):
        r, ends = network()
        self.assertEqual(len({r[-1].route, r[-14].route}), 2)
        self.assertEqual(len(audit(r, ends)["witness_groups"]["A"]), 2)
    def test_two_independent_origins(self):
        r, ends = network(root_b=True)
        self.assertEqual(audit(r, ends)["roots"], frozenset(("A", "B")))
    def test_unknown_parent_stays_unknown(self):
        r, ends = network(orphan=True)
        a = audit(r, ends)
        self.assertEqual(a["roots"], frozenset(("A",)))
        self.assertEqual(a["unknown"], frozenset(("unavailable",)))
    def test_unknown_not_counted_as_independent(self):
        r, ends = network(orphan=True)
        self.assertEqual(audit(r, ends)["independent_confirmed"], 1)
    def test_same_content_not_proof_of_same_root(self):
        r, ends = network(root_b=True, mirror=True)
        self.assertEqual(audit(r, ends)["independent_confirmed"], 2)
    def test_different_content_preserves_ancestry(self):
        r, ends = network(transform=True)
        self.assertEqual(audit(r, ends)["independent_confirmed"], 1)
    def test_duplicate_receipt_is_rejected(self):
        r, ends = network()
        with self.assertRaises(ValueError):
            audit(r + [r[0]], ends)
    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            audit([Receipt("a", "b", None, "s", "r", ""),
                   Receipt("b", "a", None, "s", "r", "")], ("a",))
    def test_unproven_origin_rejected_as_confirmed(self):
        r, ends = network()
        r = [Receipt(x.item, x.parent, None, x.surface, x.route, x.fingerprint) if x.item == "root-A" else x for x in r]
        a = audit(r, ends)
        self.assertEqual(a["independent_confirmed"], 0)
        self.assertEqual(a["unknown"], frozenset(("root-A",)))
    def test_root_parent_conflict(self):
        with self.assertRaises(ValueError):
            audit([Receipt("a", "b", "A", "s", "r", "")], ("a",))
    def test_count_separate_witnesses_from_same_source_only_once(self):
        r, ends = network()
        a = audit(r, ends)
        self.assertEqual(len(ends), 2)
        self.assertEqual(a["independent_confirmed"], 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)

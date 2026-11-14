"""B007: 17-position analytic overlay, not a literal 17-layer network stack."""
from dataclasses import dataclass
from hashlib import sha256
import unittest

WIRED = tuple(f"wired:{i}" for i in range(1, 6))
WIRELESS = tuple(f"wireless:{i}" for i in range(1, 6))
OSI = ("physical", "data_link", "network", "transport", "session", "presentation", "application")
POSITIONS = WIRED + WIRELESS + tuple("osi:" + s for s in OSI)

@dataclass(frozen=True)
class Appearance:
    appearance_id: str
    parent_id: str | None
    origin_id: str | None
    position: str
    content: str

def roots(items):
    byid = {x.appearance_id: x for x in items}
    if len(byid) != len(items):
        raise ValueError("duplicate appearance_id")
    found, unknown = set(), set()
    for item in items:
        visiting = set()
        node = item
        while True:
            if node.appearance_id in visiting:
                raise ValueError("lineage cycle")
            visiting.add(node.appearance_id)
            if node.origin_id:
                found.add(node.origin_id)
                break
            if node.parent_id is None or node.parent_id not in byid:
                unknown.add(item.appearance_id)
                break
            node = byid[node.parent_id]
    return found, unknown

def generate_chain():
    out = [Appearance("root", None, "source-A", "origin", "A")]
    parent = "root"
    for i, position in enumerate(POSITIONS, 1):
        name = f"appearance-{i}"
        out.append(Appearance(name, parent, None, position, sha256((position+parent).encode()).hexdigest()))
        parent = name
    return out

class TestModel(unittest.TestCase):
    def test_17_distinct_positions(self):
        self.assertEqual(len(POSITIONS), 17)
        self.assertEqual(len(set(POSITIONS)), 17)
    def test_5_5_7(self):
        self.assertEqual((len(WIRED), len(WIRELESS), len(OSI)), (5, 5, 7))
    def test_ancestry_conserved(self):
        items = generate_chain()
        self.assertEqual(len(items), 18)
        self.assertEqual(roots(items), ({"source-A"}, set()))
    def test_content_mutation_does_not_create_root(self):
        self.assertEqual(len({x.content for x in generate_chain()}), 18)
        self.assertEqual(len(roots(generate_chain())[0]), 1)
    def test_independent_origin_is_counted(self):
        items = generate_chain() + [Appearance("other", None, "source-B", "origin", "B")]
        self.assertEqual(roots(items)[0], {"source-A", "source-B"})
    def test_unresolved_origin_not_assumed(self):
        items = generate_chain() + [Appearance("mystery", "missing", None, "wired:1", "?")]
        self.assertEqual(roots(items)[1], {"mystery"})
    def test_repeated_text_is_not_same_origin(self):
        items = [Appearance("a", None, "source-A", "origin", "same"),
                 Appearance("b", None, "source-B", "origin", "same")]
        self.assertEqual(len(roots(items)[0]), 2)
    def test_cycles_rejected(self):
        with self.assertRaises(ValueError):
            roots([Appearance("a", "b", None, "wired:1", "a"),
                   Appearance("b", "a", None, "wireless:1", "b")])

if __name__ == "__main__":
    unittest.main(verbosity=2)

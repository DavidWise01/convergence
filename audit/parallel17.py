"""B008 — parallel transport paths and OSI provenance.
Analytical 5+5+7 overlay; wired/wireless are paths, not ten extra OSI layers.
No assertion that the public internet uses a 17-layer protocol stack.
"""
from dataclasses import dataclass
import unittest

OSI = ("physical", "data_link", "network", "transport", "session", "presentation", "application")
ROUTES = ("wired", "wireless")
HOPS = 5

@dataclass(frozen=True)
class Node:
    name: str
    parents: tuple[str, ...] = ()
    origin: str | None = None

def build_graph(wireless_parent_override=None):
    graph = {"root": Node("root", origin="corpus-root-A")}
    ends = []
    for route in ROUTES:
        prev = "root"
        for i in range(1, HOPS + 1):
            name = f"{route}-hop-{i}"
            parent = wireless_parent_override if route == "wireless" and i == 1 and wireless_parent_override else prev
            graph[name] = Node(name, (parent,))
            prev = name
        for layer in OSI:
            name = f"{route}-osi-{layer}"
            graph[name] = Node(name, (prev,))
            prev = name
        ends.append(prev)
    graph["merge"] = Node("merge", tuple(ends))
    return graph

def inspect(graph, name):
    """Returns (confirmed roots, unknown missing parents, visited nodes).
    An unknown path does not nullify independently verified known paths.
    """
    cache = {}
    visiting = set()
    def walk(key):
        if key in visiting:
            raise ValueError("cycle")
        if key in cache:
            return cache[key]
        if key not in graph:
            return frozenset(), frozenset((key,)), frozenset()
        visiting.add(key)
        node = graph[key]
        if node.origin is not None and node.parents:
            raise ValueError("a declared origin cannot also have upstream parents")
        roots = set((node.origin,)) if node.origin else set()
        unknown = set()
        visited = set((key,))
        if not node.origin and not node.parents:
            unknown.add(key)
        for parent in node.parents:
            r, u, v = walk(parent)
            roots.update(r)
            unknown.update(u)
            visited.update(v)
        visiting.remove(key)
        result = (frozenset(roots), frozenset(unknown), frozenset(visited))
        cache[key] = result
        return result
    return walk(name)

class B008Tests(unittest.TestCase):
    def test_two_routes(self):
        g = build_graph()
        self.assertEqual(sum(k.startswith("wired-") for k in g), 12)
        self.assertEqual(sum(k.startswith("wireless-") for k in g), 12)
    def test_seven_osi_each(self):
        g = build_graph()
        for route in ROUTES:
            self.assertEqual([k for k in g if k.startswith(route + "-osi-")],
                             [route + "-osi-" + x for x in OSI])
    def test_five_transport_hops_each(self):
        g = build_graph()
        for route in ROUTES:
            self.assertEqual(sum(k.startswith(route + "-hop-") for k in g), 5)
    def test_merge_preserves_single_root(self):
        r, u, v = inspect(build_graph(), "merge")
        self.assertEqual((r, u, len(v)), (frozenset({"corpus-root-A"}), frozenset(), 26))
    def test_two_distinct_origins_do_not_collapse(self):
        g = build_graph()
        g["other-root"] = Node("other-root", origin="corpus-root-B")
        g["wireless-hop-1"] = Node("wireless-hop-1", ("other-root",))
        self.assertEqual(inspect(g, "merge")[0], frozenset({"corpus-root-A", "corpus-root-B"}))
    def test_missing_parent_remains_unknown(self):
        g = build_graph("unseen-source")
        roots, unknown, _ = inspect(g, "merge")
        self.assertEqual(roots, frozenset({"corpus-root-A"}))
        self.assertEqual(unknown, frozenset({"unseen-source"}))
    def test_cycle_rejected(self):
        g = build_graph()
        g["root"] = Node("root", ("merge",))
        with self.assertRaises(ValueError):
            inspect(g, "merge")
    def test_no_origin_parent_conflict(self):
        g = build_graph()
        g["root"] = Node("root", ("wired-hop-2",), "corpus-root-A")
        with self.assertRaises(ValueError):
            inspect(g, "merge")
    def test_route_redundancy_not_independent_witness(self):
        g = build_graph()
        a = inspect(g, "wired-osi-application")[0]
        b = inspect(g, "wireless-osi-application")[0]
        self.assertEqual(a, b)
        self.assertEqual(len(a | b), 1)
    def test_unresolved_does_not_erase_known(self):
        r, u, _ = inspect(build_graph("unknown"), "merge")
        self.assertEqual((len(r), len(u)), (1, 1))

if __name__ == "__main__":
    unittest.main(verbosity=2)

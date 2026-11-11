"""Part A - Greedy: Kruskal's Minimum Spanning Tree over skills.

Graph: nodes = skills, edges = available resources (weight = hours).

Suggested approach
------------------
1. Drop resources with unavailable == True.
2. Sort edges by (hours ASC, -combined relevance of both endpoints)
   -> satisfies the tie-break rule in the proposal.
3. Run Kruskal with Union-Find (path compression + union by rank).
4. Keep only the MST component(s) that contain the student's current skills.
   Tip: merge all current skills into one set first (union them with each
   other at cost 0) so "reachable" = everything in that set at the end.
5. Skills never joined to that set are reported as unreachable.

Complexity to state in the report: O(E log E) for the sort + ~O(E α(V)) for DSU.
"""
from dataclasses import dataclass, field

from .models import Dataset, Resource


class DisjointSet:
    """Union-Find. TODO: implement find (with path compression) and union (by rank)."""

    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x):
        raise NotImplementedError

    def union(self, a, b) -> bool:
        """Merge the sets of a and b. Return False if already in the same set."""
        raise NotImplementedError


@dataclass
class PartAResult:
    chosen_resources: list[Resource] = field(default_factory=list)
    total_hours: int = 0
    reachable_skills: set[str] = field(default_factory=set)
    unreachable_skills: set[str] = field(default_factory=set)


def run_part_a(data: Dataset) -> PartAResult:
    # TODO: implement the steps in the module docstring.
    raise NotImplementedError

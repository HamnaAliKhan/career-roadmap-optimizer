"""Part A - Greedy: Kruskal's Minimum Spanning Tree over skills.

Graph: nodes = skills, edges = available learning resources (weight = hours).

Steps
-----
1. Drop resources marked unavailable.
2. Sort edges by hours ascending. Ties: the resource linking higher-relevance
   skills (sum of both endpoints' relevance) comes first; if relevance is also
   equal, the one linking higher-demand skills (sum of demand); finally
   resource_id so the result is deterministic.
3. Put all of the student's current skills into one set (they are already
   known, so connecting them costs 0 hours).
4. Kruskal: take each edge in order; keep it if it joins two different sets
   (Union-Find), otherwise it would form a cycle and is skipped.
5. Reachable skills = every skill in the student's set at the end.
   Chosen resources = kept edges inside that set (a minimum spanning tree of
   the reachable part). All other skills are unreachable.

Complexity: sorting O(E log E); Union-Find operations O(E * alpha(V)), so
O(E log E) overall, with E = resources and V = skills.
"""
from dataclasses import dataclass, field

from .models import Dataset, Resource


class DisjointSet:
    """Union-Find with path compression and union by rank."""

    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b) -> bool:
        """Merge the sets of a and b. Return False if they were already in the same set."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:      # union by rank
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


@dataclass
class PartAResult:
    chosen_resources: list[Resource] = field(default_factory=list)
    total_hours: int = 0
    reachable_skills: set[str] = field(default_factory=set)
    unreachable_skills: set[str] = field(default_factory=set)
    skipped_unavailable: list[Resource] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)  # step-by-step log for the report/demo


def sort_key(data: Dataset):
    """Hours ascending; equal hours -> higher combined relevance first;
    still equal -> higher combined demand first; then id (deterministic)."""
    def key(r: Resource):
        a, b = data.skills[r.skill_a], data.skills[r.skill_b]
        return (r.hours, -(a.relevance + b.relevance), -(a.demand + b.demand), r.resource_id)
    return key


def run_part_a(data: Dataset) -> PartAResult:
    result = PartAResult()
    available = [r for r in data.resources if not r.unavailable]
    result.skipped_unavailable = [r for r in data.resources if r.unavailable]

    edges = sorted(available, key=sort_key(data))
    dsu = DisjointSet(data.skills.keys())

    start = sorted(data.student_skills)
    for sid in start[1:]:
        dsu.union(start[0], sid)

    accepted: list[Resource] = []
    for r in edges:
        if dsu.union(r.skill_a, r.skill_b):
            accepted.append(r)
            result.trace.append(f"take {r.resource_id} ({r.skill_a}-{r.skill_b}, {r.hours}h)")
        else:
            result.trace.append(f"skip {r.resource_id} ({r.skill_a}-{r.skill_b}, {r.hours}h): cycle")

    if start:
        root = dsu.find(start[0])
        result.reachable_skills = {s for s in data.skills if dsu.find(s) == root}
    result.unreachable_skills = set(data.skills) - result.reachable_skills
    result.chosen_resources = [r for r in accepted if r.skill_a in result.reachable_skills]
    result.total_hours = sum(r.hours for r in result.chosen_resources)
    return result

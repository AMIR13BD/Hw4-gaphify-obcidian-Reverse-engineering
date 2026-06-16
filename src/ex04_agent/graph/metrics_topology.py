"""Topology helpers for graph metrics."""

from __future__ import annotations

from collections import deque
from typing import Any

from ex04_agent.graph.indexer import GraphIndexer


def percentile_90(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, int(0.9 * (len(ordered) - 1)))
    return ordered[index]


def connected_components(adjacency: dict[str, set[str]], node_ids: list[str]) -> dict[str, Any]:
    visited: set[str] = set()
    components: list[list[str]] = []
    for node_id in node_ids:
        if node_id in visited:
            continue
        queue: deque[str] = deque([node_id])
        component: list[str] = []
        visited.add(node_id)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in adjacency.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    sizes = [len(component) for component in components]
    return {
        "count": len(components),
        "sizes": sizes,
        "largest_size": max(sizes) if sizes else 0,
        "components": components,
    }


def bridging_scores(indexer: GraphIndexer, node_ids: list[str]) -> dict[str, float]:
    adjacency = indexer.undirected_adjacency
    scores = dict.fromkeys(node_ids, 0.0)
    for node_id in node_ids:
        neighbors = sorted(adjacency.get(node_id, set()))
        if len(neighbors) < 2:
            continue
        for left in range(len(neighbors)):
            for right in range(left + 1, len(neighbors)):
                if not has_alt_path(adjacency, neighbors[left], neighbors[right], node_id):
                    scores[node_id] += 1.0
    return scores


def has_alt_path(adjacency: dict[str, set[str]], start: str, end: str, blocked: str) -> bool:
    if start == end:
        return True
    queue: deque[str] = deque([start])
    visited = {start}
    while queue:
        current = queue.popleft()
        for neighbor in adjacency.get(current, set()):
            if neighbor == blocked or neighbor in visited:
                continue
            if neighbor == end:
                return True
            visited.add(neighbor)
            queue.append(neighbor)
    return False

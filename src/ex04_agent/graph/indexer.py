"""Graph indexes for fast lookup and metrics."""

from __future__ import annotations

from collections import defaultdict

from ex04_agent.graph.models import GraphDocument, GraphLink, GraphNode


class GraphIndexer:
    """Build lookup indexes from a parsed graph document."""

    def __init__(self, document: GraphDocument) -> None:
        self._document = document
        self._nodes_by_id: dict[str, GraphNode] = {}
        self._outgoing: dict[str, list[GraphLink]] = defaultdict(list)
        self._incoming: dict[str, list[GraphLink]] = defaultdict(list)
        self._links_by_source_file: dict[str, list[GraphLink]] = defaultdict(list)
        self._nodes_by_source_file: dict[str, list[GraphNode]] = defaultdict(list)
        self._undirected_adjacency: dict[str, set[str]] = defaultdict(set)
        self._build()

    @property
    def document(self) -> GraphDocument:
        return self._document

    @property
    def nodes_by_id(self) -> dict[str, GraphNode]:
        return self._nodes_by_id

    @property
    def outgoing_by_source(self) -> dict[str, list[GraphLink]]:
        return dict(self._outgoing)

    @property
    def incoming_by_target(self) -> dict[str, list[GraphLink]]:
        return dict(self._incoming)

    @property
    def links_by_source_file(self) -> dict[str, list[GraphLink]]:
        return dict(self._links_by_source_file)

    @property
    def nodes_by_source_file(self) -> dict[str, list[GraphNode]]:
        return dict(self._nodes_by_source_file)

    @property
    def undirected_adjacency(self) -> dict[str, set[str]]:
        return {node_id: set(neighbors) for node_id, neighbors in self._undirected_adjacency.items()}

    def _build(self) -> None:
        for node in self._document.nodes:
            self._nodes_by_id[node.id] = node
            self._undirected_adjacency.setdefault(node.id, set())
            if node.source_file:
                self._nodes_by_source_file[node.source_file].append(node)

        for link in self._document.links:
            self._outgoing[link.source].append(link)
            self._incoming[link.target].append(link)
            if link.source_file:
                self._links_by_source_file[link.source_file].append(link)
            self._undirected_adjacency[link.source].add(link.target)
            self._undirected_adjacency[link.target].add(link.source)
            self._undirected_adjacency.setdefault(link.source, set())
            self._undirected_adjacency.setdefault(link.target, set())

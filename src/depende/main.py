from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DependsInfo:
    dependency: Callable[..., Any] | None = None
    use_cache: bool = True
    scope: str | None = None


def Depends(
    dependency: Callable[..., Any] | None = None,
    *,
    use_cache: bool = True,
    scope: str | None = None,
) -> DependsInfo:
    return DependsInfo(dependency=dependency, use_cache=use_cache, scope=scope)


def get_dependency_graph(root: DependsInfo) -> list[DependsInfo]:
    visited: set[int] = set()
    result: list[DependsInfo] = []

    def _walk(node: DependsInfo) -> None:
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)
        result.append(node)
        if isinstance(node.scope, DependsInfo):
            _walk(node.scope)

    _walk(root)
    return result


def detect_cycles(root: DependsInfo) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[int, int] = {}

    def _dfs(node: DependsInfo) -> bool:
        node_id = id(node)
        color[node_id] = GRAY
        if isinstance(node.scope, DependsInfo):
            scope_id = id(node.scope)
            if color.get(scope_id, WHITE) == GRAY:
                return True
            if color.get(scope_id, WHITE) == WHITE and _dfs(node.scope):
                return True
        color[node_id] = BLACK
        return False

    return _dfs(root)


def solve_dependencies(root: DependsInfo) -> list[DependsInfo]:
    graph = get_dependency_graph(root)
    if not graph:
        return []

    adj: dict[int, list[int]] = {id(n): [] for n in graph}
    in_degree: dict[int, int] = {id(n): 0 for n in graph}
    node_map: dict[int, DependsInfo] = {id(n): n for n in graph}

    for node in graph:
        if isinstance(node.scope, DependsInfo):
            scope_id = id(node.scope)
            if scope_id in adj:
                adj[scope_id].append(id(node))
                in_degree[id(node)] += 1

    queue: deque[int] = deque(
        nid for nid, deg in in_degree.items() if deg == 0
    )
    result: list[DependsInfo] = []

    while queue:
        nid = queue.popleft()
        result.append(node_map[nid])
        for neighbor in adj[nid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result

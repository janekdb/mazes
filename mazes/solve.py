# Recommendation: BFS with parent pointers
#
#   It's the canonical "shortest path on an unweighted graph" algorithm, and the
#   parent-dict pattern for reconstructing the path is genuinely worth knowing
#   — it shows up everywhere from Dijkstra to git's commit graph.
#
#   Concepts on the way:
#
#   - collections.deque — popleft() is O(1); doing the same with list.pop(0) would be O(n) per step, which is the textbook gotcha.
#   - parents: dict[Cell, Cell] — this dict does double duty: "have I visited this cell?" and "how did I get here?" That's the load-bearing idea — most BFS bugs come from tracking those separately.
#   - Reconstructing a path by walking parent pointers backward then reversing — appears in Dijkstra, A*, version control, dependency resolvers.
#   - frozenset unpacks positionally just like a tuple when you know its size.

from mazes.maze import Cell, Maze
from collections import defaultdict, deque
from collections.abc import Iterator

def adjacency(maze: Maze) -> dict[Cell, set[Cell]]:
    """One-pass index from the edge set O(E) build, O(1) neighbour lookup"""
    adj: defaultdict[Cell, set[Cell]] = defaultdict(set)
    for edge in maze.edges:
        a, b = edge
        adj[a].add(b)
        adj[b].add(a)
    return dict(adj)  # Don't grow the dict on lookups on missing keys


def solve(maze: Maze, start: Cell, goal: Cell) -> list[Cell]:
    """Return the final path."""
    adj = adjacency(maze)
    parents: dict[Cell, Cell] = {start: start}  # start is its own parent
    frontier: deque[Cell] = deque([start])
    while frontier:
        cell = frontier.popleft()
        if cell == goal:
            return _reconstruct(parents, goal)
        for neighbour in adj[cell]:
            if neighbour not in parents:
                parents[neighbour] = cell
                frontier.append(neighbour)

    raise ValueError(f"No path from {start} to {goal}")


def solve_steps(
    maze: Maze, start: Cell, goal: Cell
) -> Iterator[tuple[set[Cell], set[Cell], Cell]]:
    """Yield (visited, frontier, current) per BFS step; return the final path."""
    adj = adjacency(maze)
    parents: dict[Cell, Cell] = {start: start}  # start is it's own parent
    frontier: deque[Cell] = deque([start])
    while frontier:
        cell = frontier.popleft()
        yield (
            set(parents),
            set(frontier),
            cell,
        )  # snapshot copies to avoid aliases to a mutating data structure
        if cell == goal:
            return _reconstruct(parents, goal)
        for neighbour in adj[cell]:
            if neighbour not in parents:
                parents[neighbour] = cell
                frontier.append(neighbour)

    raise ValueError(f"No path from {start} to {goal}")


def _reconstruct(parents: dict[Cell, Cell], goal: Cell) -> list[Cell]:
    path = [goal]
    while parents[path[-1]] != path[-1]:
        path.append(parents[path[-1]])
    path.reverse()
    return path

# Solve using A*
import heapq
from itertools import count

def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_astar_steps(maze, start, goal):
    adj = adjacency(maze)
    parents = {start: start}
    g = {start: 0} # cost so-far dict
    tie = count() # stable tie-breaker - see note
    frontier = [(_manhattan(start, goal), next(tie), start)]
    seen = {start}
    while frontier:
        _, _, cell = heapq.heappop(frontier)
        yield set(seen), {c for _, _, c in frontier}, cell
        if cell == goal:
            return _reconstruct(parents, goal)
        for nb in adj[cell]:
            if nb not in seen:
                seen.add(nb)
                parents[nb] = cell
                g[nb] = g[cell] + 1  # ← real steps, not geometry
                # g = _manhattan(start, nb)
                f = g[nb] + _manhattan(nb, goal)
                heapq.heappush(frontier, (f, next(tie), nb))
    raise ValueError(f"No path from {start} to {goal}")
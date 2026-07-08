from mazes.maze import Cell, Maze
from mazes.solve import adjacency, solve
from mazes.solve import solve_steps
from mazes.solve import solve_astar_steps


def test_adjacency():
    m = Maze(3)
    m.link_cells((0, 0), (0, 1))
    m.link_cells((0, 0), (1, 0))
    adj: dict[Cell, set[Cell]] = adjacency(m)

    expected = {(0, 0): {(0, 1), (1, 0)}, (0, 1): {(0, 0)}, (1, 0): {(0, 0)}}

    assert adj == expected


def test_solve():
    m = Maze(3)
    m.link_cells((0, 0), (0, 1))
    m.link_cells((0, 1), (0, 2))
    m.link_cells((0, 2), (1, 2))
    m.link_cells((1, 2), (2, 2))

    path = solve(m, (0, 0), (2, 2))

    expected = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]

    assert path == expected


def _drive(gen):
    """Exhaust a generator, returning (list_of_yields, return_value)."""
    states = []
    try:
        while True:
            states.append(next(gen))
    except StopIteration as stop:
        return states, stop.value


def test_solve_steps_path_matches_solve():
    m = Maze(3)
    m.link_cells((0, 0), (0, 1))
    m.link_cells((0, 1), (0, 2))
    m.link_cells((0, 2), (1, 2))
    m.link_cells((1, 2), (2, 2))

    states, path = _drive(solve_steps(m, (0, 0), (2, 2)))

    # The streamed solver returns the same answer as the batch one.
    assert path == solve(m, (0, 0), (2, 2))
    assert path == [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]

    # First step: only the start is visited, it is the current cell.
    visited, frontier, current = states[0]
    assert visited == {(0, 0)}
    assert current == (0, 0)

    # Invariant across the whole search: visited never shrinks,
    # and the current cell is always already visited.
    seen_counts = [len(v) for v, _, _ in states]
    assert seen_counts == sorted(seen_counts)
    assert all(current in visited for visited, _, current in states)

def test_solve_astart_steps_path_matches_solve():
    m = Maze(3)
    m.link_cells((0, 0), (0, 1))
    m.link_cells((0, 1), (0, 2))
    m.link_cells((0, 2), (1, 2))
    m.link_cells((1, 2), (2, 2))

    states, path = _drive(solve_astar_steps(m, (0, 0), (2, 2)))

    # The streamed solver returns the same answer as the batch one.
    assert path == solve(m, (0, 0), (2, 2))
    assert path == [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]

    # First step: only the start is visited, it is the current cell.
    visited, frontier, current = states[0]
    assert visited == {(0, 0)}
    assert current == (0, 0)

    # Invariant across the whole search: visited never shrinks,
    # and the current cell is always already visited.
    seen_counts = [len(v) for v, _, _ in states]
    assert seen_counts == sorted(seen_counts)
    assert all(current in visited for visited, _, current in states)
import pytest
from mazes.maze import Maze, generate_kruskal
from mazes.solve import adjacency


def test_allows_valid_edges():
    m = Maze(4)
    m.link_cells((0, 0), (1, 0))


def test_self_link_rejected():
    m = Maze(4)
    with pytest.raises(ValueError):
        m.link_cells((2, 1), (2, 1))


def test_non_adjacent_cells_link_rejected():
    m = Maze(4)
    with pytest.raises(ValueError):
        m.link_cells((0, 0), (2, 2))


# def test_get_linked_cells_delete_me():
#     m = Maze(4)
#     m.link_cells((0, 0), (1, 0))
#     m.link_cells((1, 0), (1, 1))
#     expected = {((0, 0), (1, 0)), ((1, 0), (1, 1))}
#     actual = m.get_linked_cells()
#
#     assert actual == expected, f"Expected {expected}, got {actual}"


def test_get_linked_cells():
    m = Maze(4)
    m.link_cells((0, 0), (1, 0))
    m.link_cells((1, 0), (1, 1))
    expected = {frozenset({(0, 0), (1, 0)}), frozenset({(1, 0), (1, 1)})}
    actual = m.get_linked_cells()

    assert actual == expected, f"Expected {expected}, got {actual}"

# Verify it's actually a perfect maze
#
# A nice differential test using what you already have: a perfect maze on N² cells has
# exactly N²−1 open walls and is fully connected.

def _reachable(adj, start):
    seen, stack = {start}, [start]
    while stack:
        for nb in adj.get(stack.pop(), ()):
            if nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return seen

def test_kruskal_is_spanning_tree():
    m, _ = list(generate_kruskal(5))[-1] # exhaust generator, take final maze
    cells = {(r,c) for r in range(5) for c in range(5)}
    adj = adjacency(m)
    assert _reachable(adj, (0, 0)) == cells # Connected: reaches all 25
    assert len(m.edges) == 24 # exactly V-1 edge

# # test_matrix.py
# import pytest
# from your_module import create_matrix, set_cell
#
# def test_matrix_dimensions():
#     m = create_matrix(3, 4)
#     assert len(m) == 3
#     assert all(len(row) == 4 for row in m)
#
# def test_matrix_default_false():
#     m = create_matrix(2, 2)
#     assert all(cell is False for row in m for cell in row)
#
# def test_set_cell():
#     m = create_matrix(2, 2)
#     set_cell(m, 0, 1, True)
#     assert m[0][1] is True
#     assert m[0][0] is False  # neighbours untouched
#
# def test_rows_are_independent():
#     m = create_matrix(3, 3)
#     m[0][0] = True
#     assert m[1][0] is False  # proves rows aren't aliased

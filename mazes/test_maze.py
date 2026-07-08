import pytest
from mazes.maze import Maze


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

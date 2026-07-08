from mazes.maze import Maze
from mazes.render import iter_walls


def test_iter_walls_includes_exterior_walls():
    m = Maze(2)
    walls = set(iter_walls(m, cell_size=5))
    for wall in walls:
        print(wall)

    assert (0, 0, 10, 0) in walls
    assert (0, 0, 0, 10) in walls
    assert (0, 10, 10, 10) in walls
    assert (10, 0, 10, 10) in walls

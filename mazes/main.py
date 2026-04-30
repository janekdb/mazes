from maze import Maze, generate, render

if False:
    m = Maze(5)

    m.link_cells((0, 0), (0, 1))
    m.link_cells((0, 1), (0, 2))
    m.link_cells((0, 2), (0, 3))
    m.link_cells((0, 3), (1, 3))
    m.link_cells((1, 3), (2, 3))
    m.link_cells((2, 3), (3, 3))
    m.link_cells((3, 3), (3, 4))
    m.link_cells((3, 4), (4, 4))

    render(m)

    m.link_cells((0, 1), (1, 1))
    m.link_cells((1, 1), (2, 1))
    m.link_cells((2, 1), (3, 1))
    m.link_cells((3, 1), (3, 0))

    render(m)

m = generate(5)
render(m)

# for t in range(1000):
#     print(f'Maze #{t+1}')
#     m = generate(6)
#     render(m)
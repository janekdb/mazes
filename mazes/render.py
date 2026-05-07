def _p(s):
    print(s, end='')

def _print_corner():
    _p('+')

def _print_horiz_wall():
    _p('---')

def _print_missing_horiz_wall():
    _p('   ')

def _print_vert_wall():
    _p('|')

def _print_missing_vert_wall():
    _p(' ')

def _print_cell():
    _p('   ')

def render(maze):
    links = maze.get_linked_cells()
    links = {frozenset(link) for link in links}

    size = maze.size
    horizontal = '+---' * size + '+'
    print(horizontal)
    for row in range(size):
        if row > 0:
            for col in range(size):
                # Add a horizontal wall unless this cell links to the cell below
                _print_corner()
                cell = (row, col)
                above_cell = (row - 1, col)
                link = {cell, above_cell}
                if frozenset(link) in links:
                    _print_missing_horiz_wall()
                else:
                    _print_horiz_wall()
            _print_corner()
            print()
        _print_vert_wall()
        for col in range(size):
            # Add a vertical wall unless this cell links to the cell to the right
            _print_cell()
            cell = (row, col)
            right_cell = (row, col + 1)
            link = {cell, right_cell}
            if frozenset(link) in links:
                _print_missing_vert_wall()
            else:
                _print_vert_wall()
        print()

    print(horizontal)

def render_svg(maze):
    """Create an SVG representation of the maze"""
    cell_size = 20
    size = maze.size
    extent = cell_size * size
    links = {frozenset(link) for link in maze.get_linked_cells()}

    walls = []
    walls.append((0, 0, extent, 0))
    walls.append((0, extent, extent, extent))
    walls.append((0, 0, 0, extent))
    walls.append((extent, 0, extent, extent))

    # Interior horizontal walls between (row - 1, col) and (row, col)
    for row in range(1, size):
        for col in range(size):
            if frozenset({(row, col), (row - 1, col)}) not in links:
                x = col * cell_size
                y = row * cell_size
                walls.append((x, y, x + cell_size, y))

    # Interior vertical walls between (row, col) and (row, col + 1)
    for row in range(size):
        for col in range(size - 1):
            if frozenset({(row, col), (row, col + 1)}) not in links:
                x = (col + 1) * cell_size
                y = row * cell_size
                walls.append((x, y, x, y + cell_size))

    doc = []
    doc.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {extent} {extent}">')
    doc.append(f'  <rect width="{extent}" height="{extent}" fill="lightyellow"/>')
    doc.append(f'  <g stroke="green" stroke-width="2" stroke-linecap="square">')
    for x1, y1, x2, y2 in walls:
        doc.append(f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    doc.append(f'  </g>')
    doc.append('</svg>')
    return '\n'.join(doc)
import colorsys
from dataclasses import dataclass
from itertools import pairwise
from PIL import Image, ImageDraw


def _p(s):
    print(s, end="")


def _print_corner():
    _p("+")


def _print_horiz_wall():
    _p("---")


def _print_missing_horiz_wall():
    _p("   ")


def _print_vert_wall():
    _p("|")


def _print_missing_vert_wall():
    _p(" ")


def _print_cell():
    _p("   ")


def render(maze):
    links = maze.get_linked_cells()

    size = maze.size
    horizontal = "+---" * size + "+"
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


def iter_walls(maze, cell_size):
    """Yield (x1, y1, x2, y2) for every wall segment in the maze."""
    size = maze.size
    extent = cell_size * size

    yield 0, 0, extent, 0
    yield 0, extent, extent, extent
    yield 0, 0, 0, extent
    yield extent, 0, extent, extent

    links = maze.get_linked_cells()

    # Interior horizontal walls between (row - 1, col) and (row, col)
    for row in range(1, size):
        for col in range(size):
            if frozenset({(row, col), (row - 1, col)}) not in links:
                x = col * cell_size
                y = row * cell_size
                yield x, y, x + cell_size, y

    # Interior vertical walls between (row, col) and (row, col + 1)
    for row in range(size):
        for col in range(size - 1):
            if frozenset({(row, col), (row, col + 1)}) not in links:
                x = (col + 1) * cell_size
                y = row * cell_size
                yield x, y, x, y + cell_size


def render_svg(maze):
    """Create an SVG representation of the maze"""
    cell_size = 10
    size = maze.size
    extent = cell_size * size
    walls = iter_walls(maze, cell_size)
    doc = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {extent} {extent}">',
        f'  <rect width="{extent}" height="{extent}" fill="lightyellow"/>',
        '  <g stroke="green" stroke-width="2" stroke-linecap="square">',
    ]
    for x1, y1, x2, y2 in walls:
        doc.append(f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    doc.append("  </g>")
    doc.append("</svg>")
    return "\n".join(doc)


def _cell_centre(cell, cell_size):
    r, c = cell
    return (c + 0.5) * cell_size, (r + 0.5) * cell_size

def _path_segments(path, cell_size):

    for a, b in pairwise(path):
        yield *_cell_centre(a, cell_size), *_cell_centre(b, cell_size)

def _fill_cell(draw, cell, cell_size, colour):
    r, c = cell
    x0, y0 = c * cell_size, r * cell_size
    draw.rectangle((x0, y0, x0 + cell_size, y0 + cell_size), fill=colour)

def _endcap(draw, cell, cell_size, colour, radius):
    cx, cy = _cell_centre(cell, cell_size)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=colour)

# To make a component's colour stable across its whole life, key the palette on the root's original
# grid index rather than assigning colours in encounter order (which would shift as merges happen):
# Since a surviving root never changes identity, its hue is fixed for its lifetime — no flicker.
# Teaches: colorsys and generating N perceptually-spread colours from the HSV wheel.

def _hue_for(root, size):
    idx = root[0] * size + root[1]
    r, g, b = colorsys.hsv_to_rgb(idx/(size * size), 0.55, 0.90)
    return int(r * 255), int(g * 255), int(b * 255)

@dataclass(frozen=True)
class RenderStyle:
    cell_size: int = 20
    width: int = 2
    bg: str = "lightyellow"
    stroke: str = "green"
    path_stroke: str = "red"
    visited_fill: str = "lightblue"
    frontier_fill: str = "deepskyblue"
    current_fill: str = "orange"

def render_frame(
    maze,
    style = RenderStyle(),
    *,
    path=None,
    visited=None,
    frontier=None,
    current=None,
    # An optional dict from cell to the cell which is the identity of the component the cell is in.
    # Present when Kruskal is generating the maze.
    cell_set_lookup=None
):
    size = maze.size
    extent = style.cell_size * size
    img = Image.new("RGB", (extent + style.width, extent + style.width), style.bg)
    draw = ImageDraw.Draw(img)
    for cell in visited or ():
        _fill_cell(draw, cell, style.cell_size, style.visited_fill)
    for cell in frontier or ():
        _fill_cell(draw, cell, style.cell_size, style.frontier_fill)
    if current is not None:
        _fill_cell(draw, current, style.cell_size, style.current_fill)

    if cell_set_lookup:
        cells = [(row, col) for row in range(size) for col in range(size)]
        for cell in cells:
            component = cell_set_lookup[cell]
            colour = _hue_for(component, size)
            _fill_cell(draw, cell, style.cell_size, colour)

    for seg in iter_walls(maze, style.cell_size):
        draw.line(seg, fill=style.stroke, width=style.width)

    if path:
        # points = [_cell_centre(cell, cell_size) for cell in path]
        # draw.line(points, fill=path_stroke, width=width, joint="curve")
        points = [_cell_centre(cell, style.cell_size) for cell in path]
        draw.line(points, fill=style.path_stroke, width=style.width) #, joint="curve")

        # for seg in _path_segments(path, style.cell_size):
        #     draw.line(seg, fill=style.path_stroke, width=style.width)
        radius = 2 # style.cell_size * 0.3
        _endcap(draw, path[0], style.cell_size, style.path_stroke, radius)  # start
        _endcap(draw, path[-1], style.cell_size, style.path_stroke, radius)  # goal

    return img

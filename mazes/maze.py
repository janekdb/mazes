import random


class Maze:
    """A maze is represented by a graph where edges can exist between adjacent nodes
    A node is adjacent to another node when the nodes are arranged on a rectangular grid.
    Connected nodes can be moved between. Disconnected nodes are separated by a maze wall.
    """
    def __init__(self, size):
        if not size >= 1:
            raise ValueError(f'Maze size must be >= 1: {size}')
        self.size = size
        # Start with a fully disconnected graph represented by an adjacency matrix
        cells_count = size ** 2
        self.adjacency = [[False] * cells_count for _ in range(cells_count)]

    def validate_range(self, cell):
        row, col = cell
        if not (0 <= row < self.size):
            raise ValueError(f'Cell row out of range: {cell}')
        if not (0 <= col < self.size):
            raise ValueError(f'Cell col out of range: {cell}')

    def cell_index(self, cell):
        row, col = cell
        return row * self.size + col

    def cell_from_index(self, index):
        row = index // self.size
        col = index % self.size
        return row, col

    def link_cells(self, cell_1, cell_2):
        """Add a traversable path between two cells. The first component is the zero based row index, the second
        component is the zero based column index. This order takes inspiration from linear algebra."""
        if cell_1 == cell_2:
            raise ValueError(f'Cannot link a cell to itself: {cell_1}')
        row_1, col_1 = cell_1
        row_2, col_2 = cell_2

        self.validate_range(cell_1)
        self.validate_range(cell_2)

        manhattan_distance = abs(row_1 - row_2) + abs(col_1 - col_2)
        if manhattan_distance != 1:
            raise ValueError(f'Cells were not adjacent to each other: {cell_1}, {cell_2}')

        index_1 = self.cell_index(cell_1)
        index_2 = self.cell_index(cell_2)

        self.adjacency[index_1][index_2] = True
        self.adjacency[index_2][index_1] = True

    def get_linked_cells(self):
        links = set()
        for row_ix in range(0, len(self.adjacency)):
            row = self.adjacency[row_ix]
            for col_ix in range(row_ix, len(row)):
                linked = row[col_ix]
                if linked:
                    cell_1 = self.cell_from_index(row_ix)
                    cell_2 = self.cell_from_index(col_ix)
                    links.add((cell_1, cell_2))

        return links

def print_corner():
    print('+', end='')

def _print_horiz_wall():
    print('---', end='')

def _print_missing_horiz_wall():
    print('   ', end='')

def _print_vert_wall():
    print('|', end='')

def _print_missing_vert_wall():
    print(' ', end='')

def _print_cell():
    print('   ', end='')

# class MazeRenderer:
#
#     @staticmethod
def render(maze):
    links = maze.get_linked_cells()
    links = [set(link) for link in links]
    # for link in links:
    #     print(link)

    size = maze.size
    horizontal = '+---' * size + '+'
    vertical = '|   ' * size + '|'
    print(horizontal)
    for row in range(size):
        if row > 0:
            for col in range(size):
                # Add a horizontal wall unless this cell links to the cell below
                print_corner()
                cell = (row, col)
                above_cell = (row - 1, col)
                link = {cell, above_cell}
                # print(f'Testing {link} -> {link in links}')
                if link in links:
                    _print_missing_horiz_wall()
                else:
                    _print_horiz_wall()
            print_corner()
            print()
        _print_vert_wall()
        for col in range(size):
            # Add a vertical wall unless this cell links to the cell to the right
            _print_cell()
            cell = (row, col)
            right_cell = (row, col + 1)
            link = {cell, right_cell}
            if link in links:
                _print_missing_vert_wall()
            else:
                _print_vert_wall()
        print()

    print(horizontal)

def _shuffled_directions():
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    return directions

def _in_range(cell, size):
    ps = list(cell)
    for p in ps:
        if p < 0 or p >= size:
            return False
    return True

# TODO: Avoid cells previously visited to improve snakiness of route
def generate(size):
    """Generate a maze from a random walk"""
    m = Maze(size)
    sentinel = (size - 1, size - 1)
    current = (0, 0)
    visited = {current}
    trail = [current]
    backtracks = 0
    # while current != sentinel:
    while len(visited) != size * size:
        (r, c) = current
        # (rd, cd) = _random_direction()
        directions = _shuffled_directions()
        # print(f'current: {current}')
        found = False
        next_cell = None
        for direction in directions:
            (rd, cd) = direction
            candidate = (r + rd, c + cd)
            # print(f'candidate: {candidate}')
            if _in_range(candidate, size) and not candidate in visited:
                found = True
                next_cell = candidate
        if found:
          # print(f'current: {current}, next_cell: {next_cell}')
          m.link_cells(current, next_cell)
          current = next_cell
          visited.add(current)
          trail.append(current)
        elif len(trail) == 1:
          render(m)
          print(f'current: {current}')
          raise RuntimeError(f"Failed to find a path from {current}")
        else:
            # Backtrack
            trail.pop()
            failed_cell = current
            current = trail[-1]
            backtracks += 1
            # print(f'Backtracked from {failed_cell} to {current}')

    print(f'backtracks: {backtracks}')
    return m

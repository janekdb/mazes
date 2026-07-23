import random

Cell = tuple[int, int]


class Maze:
    """A maze is represented by a graph where edges can exist between adjacent nodes
    A node is adjacent to another node when the nodes are arranged on a rectangular grid.
    Connected nodes can be moved between. Disconnected nodes are separated by a maze wall.
    """

    def __init__(self, size):
        if size < 1:
            raise ValueError(f"Maze size must be >= 1: {size}")
        self.size = size
        # Start with a fully disconnected graph represented by an edge list
        self.edges: set[frozenset[Cell]] = set()

    def validate_range(self, cell):
        row, col = cell
        if not (0 <= row < self.size):
            raise ValueError(f"Cell row out of range: {cell}")
        if not (0 <= col < self.size):
            raise ValueError(f"Cell col out of range: {cell}")

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
            raise ValueError(f"Cannot link a cell to itself: {cell_1}")
        row_1, col_1 = cell_1
        row_2, col_2 = cell_2

        self.validate_range(cell_1)
        self.validate_range(cell_2)

        manhattan_distance = abs(row_1 - row_2) + abs(col_1 - col_2)
        if manhattan_distance != 1:
            raise ValueError(
                f"Cells were not adjacent to each other: {cell_1}, {cell_2}"
            )

        self.edges.add(frozenset({cell_1, cell_2}))

        # index_1 = self.cell_index(cell_1)
        # index_2 = self.cell_index(cell_2)
        #
        # self.adjacency[index_1][index_2] = True
        # self.adjacency[index_2][index_1] = True

    def get_linked_cells(self):
        return self.edges
        # links = set()
        # for row_ix in range(len(self.adjacency)):
        #     row = self.adjacency[row_ix]
        #     for col_ix in range(row_ix, len(row)):
        #         linked = row[col_ix]
        #         if linked:
        #             cell_1 = self.cell_from_index(row_ix)
        #             cell_2 = self.cell_from_index(col_ix)
        #             links.add((cell_1, cell_2))
        #
        # return links


def _shuffled_directions():
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    return directions


def _shuffled_directions_biased(last_followed_direction):
    """Prefer the last followed direction"""
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    # A higher chance of continuing the same direction
    directions.append(last_followed_direction)
    random.shuffle(directions)
    # != to prefer previous direction
    # == to avoid previous direction
    # directions.sort(key=lambda d: d == last_followed_direction)
    return directions


def _in_range(cell, size):
    return all(0 <= p < size for p in cell)


def generate(size):
    """Generate a maze from a random walk"""
    m = Maze(size)
    yield m, None
    current = (0, 0)
    visited = {current}
    trail = [current]
    backtracks = 0
    # last_followed_direction = None
    while len(visited) != size * size:
        r, c = current
        # directions = _shuffled_directions_biased(last_followed_direction)
        directions = _shuffled_directions()
        # print(f'current: {current}')
        found = False
        next_cell = None
        for direction in directions:
            rd, cd = direction
            candidate = r + rd, c + cd
            # print(f'candidate: {candidate}')
            if _in_range(candidate, size) and candidate not in visited:
                found = True
                next_cell = candidate
                # last_followed_direction = direction
                break
        if found:
            # print(f'current: {current}, next_cell: {next_cell}')
            m.link_cells(current, next_cell)
            current = next_cell
            visited.add(current)
            trail.append(current)
            yield m, None
        elif len(trail) == 1:
            # render(m)
            print(f"current: {current}")
            raise RuntimeError(f"Failed to find a path from {current}")
        else:
            # Backtrack
            trail.pop()
            # failed_cell = current
            current = trail[-1]
            backtracks += 1
            # print(f'Backtracked from {failed_cell} to {current}')

    # print(f'backtracks: {backtracks}')
    # return m

def _all_walls(size):
    """Every adjacent cell pair, each one (east + south neighbours)"""
    for r in range(size):
        for c in range(size):
            if c + 1 < size:
                yield (r, c), (r, c + 1)
            if r + 1 < size:
                yield (r, c), (r + 1, c)

def generate_kruskal(size):
    """Kruskal assembled:
       Kruskal's insight: shuffle all possible walls, and open each one only if its two cells are in different regions
       (opening it would connect them without making a loop).
       Stop when everything's one region — that's a spanning tree, i.e. a perfect maze.
       Union by rank/size — track each root's tree size and always attach the smaller under the larger.
       Combined with path compression it gives the optimal α(n) bound. A good "make it textbook-optimal" second pass.
    """

    parent = {(r, c): (r, c) for r in range(size) for c in range(size)}
    tree_size = {(r, c): 1 for r in range(size) for c in range(size)}

    def find(cell):
        """Identify the set this cell belong to"""
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]] # path compression by path halving
            cell = parent[cell]
        return cell

    def roots():
        """Snapshot cell -> current root for the whole grid"""
        return {cell: find(cell) for cell in parent}

    m = Maze(size)
    yield m, roots()

    walls = list(_all_walls(size))
    random.shuffle(walls)
    for a, b in walls:
        ra, rb = find(a), find(b)
        if ra != rb: # different region → safe to open as no cycle will be created
            if tree_size[ra] > tree_size[rb]:
                ra, rb = rb, ra # make ra the smaller root
            parent[ra] = rb # union by attaching smaller under larger
            tree_size[rb] += tree_size[ra] # rb's tree grew by ra's cells
            m.link_cells(a, b)
            yield m, roots() # snapshot for the animation

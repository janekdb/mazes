import random
from dataclasses import dataclass
from collections.abc import Mapping
from itertools import pairwise

Cell = tuple[int, int]

@dataclass(frozen=True)
class GenStep:
    maze: Maze
    # backtracker fields
    visited: frozenset[Cell] | None = None
    current: Cell | None = None
    stack: tuple[Cell, ...] | None = None
    doomed: frozenset[Cell] | None = None  # cells about to be backtracked
    junction: Cell | None = None # cell where backtracking stops & carving resumes
    phase: str | None = None # "advance" | "dead_end" | "backtrack"
    # kruskal field
    cell_set_lookup: Mapping[Cell, Cell] | None = None
    # Wilson field: corridor to flash on commit
    carved: frozenset[Cell] | None = None

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

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # E, S, W, N

def _shuffled_directions():
    directions = list(DIRECTIONS)
    random.shuffle(directions)
    return directions


def _shuffled_directions_biased(last_followed_direction):
    """Prefer the last followed direction"""
    directions = list(DIRECTIONS)
    # A higher chance of continuing the same direction
    directions.append(last_followed_direction)
    random.shuffle(directions)
    # != to prefer previous direction
    # == to avoid previous direction
    # directions.sort(key=lambda d: d == last_followed_direction)
    return directions


def _in_range(cell, size):
    return all(0 <= p < size for p in cell)

def _has_unvisited_neighbour(cell, visited, size):
    """True if any orthogonal neighbour of `cell` is not yet visited."""
    r, c = cell
    return any(
        _in_range((r + dr, c + dc), size) and (r + dr, c + dc) not in visited
        for dr, dc in DIRECTIONS
    )

def _doomed_segment(trail, visited, size):
    """Cells abandoned on backtracking: the dead-end run from trail[-1] down to
    (but not including) the nearest cell that still has an unvisited neighbour.
    Returned dead-end-first, i.e. in pop order."""
    segment = [trail[-1]]
    for cell in reversed(trail[:-1]):
        if _has_unvisited_neighbour(cell, visited, size):
            break
        segment.append(cell)
    return segment

def generate_backtracker(size):
    """Generate a maze from a random walk"""
    m = Maze(size)
    yield GenStep(m)
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

        # TODO: Use this idiom
        # next_cell = next(
        #     (cand for dr, dc in directions
        #      if _in_range((cand := (r + dr, c + dc)), size) and cand not in visited),
        #     None,
        # )
        # if next_cell is not None:
        #     m.link_cells(current, next_cell)

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
            yield GenStep(m, visited=frozenset(visited), current=current, stack=tuple(trail), phase="advance")

        elif len(trail) == 1:
            # render(m)
            print(f"current: {current}")
            raise RuntimeError(f"Failed to find a path from {current}")
        else:
            # Backtrack
            # Dead end: trail[-1] has no unvisited neighbour.
            doomed = _doomed_segment(trail, visited, size)
            # the cell _doomed_segment stopped at: one below the doomed run
            junction = trail[-(len(doomed) + 1)] if len(doomed) < len(trail) else None

            # (1) flash: whole doomed corridor, head still on the dead end
            yield GenStep(m, visited=frozenset(visited), current=current,
                          stack=tuple(trail), doomed=frozenset(doomed),
                          junction=junction, phase="dead_end")

            # (2) retreat: pop the doomed cells one at a time, highlight shrinking
            for i in range(len(doomed)):
                trail.pop()
                backtracks += 1
                if not trail: # popped past the origin
                    raise RuntimeError(f"Backtracked past origin from {current}")
                current = trail[-1]
                yield GenStep(m, visited=frozenset(visited), current=current,
                    stack=tuple(trail), doomed=frozenset(doomed[i + 1:]),
                    junction=junction, phase="backtrack")

            # Why the pieces are where they are

            # doomed[i + 1:] is the key line. After popping index i (which removed the cell at the top),
            # the still-to-be-popped doomed cells are exactly the suffix doomed[i+1:]. So the highlight
            # recedes in lockstep with the head: at the last iteration it's doomed[len:] = empty, and
            # current has landed on the surviving junction. That's the "corridor peels away as the head
            # retreats" effect, and it's driven entirely by the slice — no separate mutable "remaining"
            # set to keep in sync.

            # The flash frame (1) is the only one with current on the dead end. From iteration i=0 onward
            # the head has already moved down. So (1) is what gives the viewer the beat of "recognized the
            # dead end" before the retreat starts. If you'd rather skip the flash (Option B, persistent tint
            # with no separate recognition beat), drop block (1) and start straight into the loop — the
            # doomed set still shrinks correctly.

            # Draw-order note for render_step: in the flash frame the dead-end cell is both current and in
            # doomed. Fill doomed cells first, then the current head on top, so the head color wins on that
            # overlap — otherwise the dead end reads as doomed rather than as the active cell.

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

    def find(cell: Cell) -> Cell:
        """Identify the set this cell belong to"""
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]] # path compression by path halving
            cell = parent[cell]
        return cell

    def roots():
        """Snapshot cell -> current root for the whole grid"""
        return {cell: find(cell) for cell in parent}

    m = Maze(size)
    yield GenStep(m, cell_set_lookup=roots())

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
            # yield m, roots() # snapshot for the animation
            yield GenStep(m, cell_set_lookup=roots()) # snapshot for the animation

def generate_binary_tree(size):
    """For each cell, carve north or east - whichever exists"""
    m = Maze(size)
    yield m, None
    for r in range(size):
        for c in range(size):
            neighbours = []
            if r > 0:
                neighbours.append((r - 1, c)) # north
            if c < size - 1:
                neighbours.append((r, c + 1)) # east
            if neighbours:
                m.link_cells((r, c), random.choice(neighbours))
                yield m, None

def _walk_path(direction_from, start, head):
    path = [start]
    c = start
    while c != head and c in direction_from: # stop AT head - not just "no pointer"
        dr, dc = direction_from[c]
        c = (c[0] + dr, c[1] + dc)
        path.append(c)
    return path

def generate_wilson(size):
    m = Maze(size)
    yield GenStep(m)

    cells = [(r, c) for r in range(size) for c in range(size)]
    in_tree = {random.choice(cells)} # seed the tree with one cell

    while len(in_tree) < size * size:
        # any cell outside the tree. Randomised for visual appeal.
        start = random.choice([c for c in cells if c not in in_tree])
        # start = next(c for c in cells if c not in in_tree)
        direction_from = {} # the loop-erasure trick

        # --- random walk until we hit the tree ---
        cell = start
        while cell not in in_tree:
            yield GenStep(
                m,
                visited=frozenset(in_tree),
                stack=tuple(_walk_path(direction_from, start, cell)),
                current=cell,
                phase="walk"
            )
            dr, dc = random.choice([
                (dr, dc) for dr, dc in DIRECTIONS
                if _in_range((cell[0] + dr, cell[1] + dc), size)
            ])
            direction_from[cell] = (dr, dc)  # overwrite — last exit wins
            cell = (cell[0] + dr, cell[1] + dc)

        # --- commit: carve the whole loop-erased path, then flash it ---
        path = _walk_path(direction_from, start, cell)   # start → tree-contact
        for a, b in pairwise(path):
            m.link_cells(a, b)
            in_tree.add(a)
        # one bright beat on the freshly carved corridor
        yield GenStep(
            m,
            visited=frozenset(in_tree),
            stack=tuple(path),
            carved=frozenset(path),
            phase="commit",
        )
        #
        # # --- commit: carve the loop-erased path into the tree, one edge per frame ---
        # path = _walk_path(direction_from, start, cell)   # start → tree-contact cell
        # for a, b in pairwise(path):
        #     m.link_cells(a, b)
        #     in_tree.add(a)
        #     yield GenStep(
        #         m,
        #         visited=frozenset(in_tree),
        #         current=b,
        #         stack=tuple(path),          # whole committed corridor, highlighted
        #         phase="commit",
        #     )
        #
        # # --- retrace the loop-erased path and carve it ---
        # cell = start
        # while cell not in in_tree:
        #     dr, dc = direction_from[cell]
        #     nxt = (cell[0] + dr, cell[1] + dc)
        #     m.link_cells(cell, nxt)
        #     in_tree.add(cell)
        #     cell = nxt

    yield GenStep(m)  # placeholder: one final frame; real animation comes in stage 2

# A maze is rendered as a grid of cells. Each cell has four sides (N, E, S, W).
# A cell has one, two or three walls which cannot be passed through. Cells with no
# walls or four walls are invalid.
#
# The NW cell is distinguished as the maze entrance, the SE as the exit. The entrance
# cell has the N wall open and the W wall closed. The exit has the S wall open and the
# W wall closed.

from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    """Each cell wall can be open or closed which corresponds to true or false. True means the edge is open."""
    north: bool
    east: bool
    south: bool
    west: bool


class Maze:
    def _row(self, index):
        """Return the cells from the row at the given index."""
        offset = index * self.size
        return self.cells[offset : offset + self.size]

    def _col(self, index):
        """Return the cells from the column at the given index."""
        return self.cells[index :: self.size]

    def _validate_top_row(self, row):
        top_edges = [cell.north for cell in row]
        if not top_edges[0]:
            raise ValueError("The North West entrance was closed")
        del top_edges[0]
        for edge in top_edges:
            if edge:
                raise ValueError("Unexpected open wall in top row")

    def _validate_bottom_row(self, row):
        bottom_edges = [cell.south for cell in row]
        if not bottom_edges[self.size - 1]:
            raise ValueError("The South East entrance was closed")
        del bottom_edges[self.size - 1]
        for edge in bottom_edges:
            if edge:
                raise ValueError("Unexpected open wall in bottom row")

    def _validate_left_col(self, col):
        left_edges = [cell.west for cell in col]
        for edge in left_edges:
            if edge:
                raise ValueError("Unexpected open wall in left col")

    def _validate_right_col(self, col):
        right_edges = [cell.east for cell in col]
        for edge in right_edges:
            if edge:
                raise ValueError("Unexpected open wall in right col")

    def _validate_perimeter(self):
        # The top row should have north = False with the exception of the first cell
        # The bottom row should have south = False with the exception of the last cell
        # The left column should have west = True
        # The right column should have east = True
        top_row = self._row(0)
        self._validate_top_row(top_row)
        bottom_row = self._row(self.size - 1)
        self._validate_bottom_row(bottom_row)
        left_col = self._col(0)
        self._validate_left_col(left_col)
        right_col = self._col(self.size - 1)
        self._validate_right_col(right_col)

    def __init__(self, size, cells):
        self.size = size
        self.cells = cells[:]

        if not size > 0:
            raise ValueError(f"size must be > 0: {size}")

        if not len(cells) == size**2:
            raise ValueError(
                f"cell count did not match grid size: size: {size}, cells: {len(cells)}"
            )

        self._validate_perimeter()

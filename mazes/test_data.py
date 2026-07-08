from mazes.maze_cell_based import Cell

cell_closed = Cell(False, False, False, False)
cells_four_closed = [cell_closed, cell_closed, cell_closed, cell_closed]
cell_closed_north = Cell(False, True, True, True)
cell_nw = Cell(True, True, True, False)
valid_top_row = [cell_nw, cell_closed_north, cell_closed_north, cell_closed_north]
cell_closed_south = Cell(True, True, False, True)
cell_closed_sw = Cell(True, True, False, False)
cell_se = Cell(True, False, True, True)
valid_bottom_row = [cell_closed_sw, cell_closed_south, cell_closed_south, cell_se]

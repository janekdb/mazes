from pathlib import Path
import sys
import time
from mazes.maze import generate, generate_kruskal
from mazes.render import render, render_frame, render_svg
from mazes.solve import solve
from mazes.solve import solve_steps
from mazes.solve import solve_astar_steps

def main():
    render_mode = "gif"
    generate_mode = "kruskal"
    size = 10

    if generate_mode == "kruskal":
        snapshots = generate_kruskal(size)
    elif generate_mode == "backtracker":
        snapshots = generate(20)

    if render_mode == "svg":
        frames_dir = Path("frames")
        frames_dir.mkdir(exist_ok=True)
        for old in frames_dir.glob("maze-*.svg"):
            old.unlink()
        for i, snapshot in enumerate(snapshots):
            svg = render_svg(snapshot)
            Path(f"frames/maze-{i:04d}.svg").write_text(svg)

    elif render_mode == "text":
        # CLEAR = '\033[2J\033[H'  # clear screen + home cursor
        CLEAR = "\033[2J\033[H"  # clear screen + home cursor
        for snapshot in snapshots:
            sys.stdout.write(CLEAR)
            render(snapshot)
            time.sleep(0.05)

    elif render_mode == "gif":
        out = Path("maze.gif")
        out.unlink(missing_ok=True)
        # frames = [render_frame(snap) for snap in snapshots]
        frames = []
        for snap, cell_set_lookup in snapshots:
            frames.append(render_frame(snap, cell_set_lookup=cell_set_lookup))
        maze_build_frames_len = len(frames)
        maze = snap  # after the loop, snap is the fully-generated maze

        # gen = solve_steps(maze, (0, 0), (maze.size - 1, maze.size - 1))
        gen = solve_astar_steps(maze, (0, 0), (maze.size - 1, maze.size - 1))
        try:
            while True:
                visited, frontier, current = next(gen)
                frames.append(
                    render_frame(maze, visited=visited, frontier=frontier, current=current)
                )
        except StopIteration as stop:
            path = stop.value
        maze_search_frames_len = len(frames) - maze_build_frames_len

        # path = solve(maze, (0, 0), (maze.size - 1, maze.size - 1))
        frames += [render_frame(maze, path=path[:i]) for i in range(2, len(path) + 1)]
        maze_solve_frames = len(frames) - maze_build_frames_len - maze_search_frames_len

        durations = [
            5000,
            *[2] * (maze_build_frames_len - 2),
            2000,
            *[40] * (maze_search_frames_len - 1),
            2000,
            *[120] * (maze_solve_frames - 1),
            5000,
        ]

        assert len(durations) == len(frames)

        frames[0].save(
            out,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True,
        )

    # Pre-flood fill
    if False and render_mode == "gif":
        out = Path("maze.gif")
        out.unlink(missing_ok=True)
        # frames = [render_frame(snap) for snap in snapshots]
        frames = []
        for snap in snapshots:
            frames.append(render_frame(snap))
        maze_build_frames = len(frames)
        maze = snap  # after the loop, snap is the fully-generated maze

        path = solve(maze, (0, 0), (maze.size - 1, maze.size - 1))
        frames += [render_frame(maze, path=path[:i]) for i in range(2, len(path) + 1)]
        maze_solve_frames = len(frames) - maze_build_frames

        durations = [
            5000,
            *[20] * (maze_build_frames - 2),
            2000,
            *[80] * (maze_solve_frames - 1),
            5000,
        ]

        assert len(durations) == len(frames)

        frames[0].save(
            out,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True,
        )

if __name__ == "__main__":
    main()
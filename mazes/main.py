from pathlib import Path
import sys
import time
from dataclasses import replace
from PIL import Image
from mazes.maze import generate_backtracker
from mazes.maze import generate_binary_tree
from mazes.maze import generate_kruskal
from mazes.maze import GenStep
from mazes.render import render, render_frame, render_svg, RenderStyle
from mazes.solve import solve
from mazes.solve import solve_steps
from mazes.solve import solve_astar_steps

def _render_step(step: GenStep) -> Image.Image:
    """Adapt a GenStep to render_frame, choosing colours from the phase."""
    if step.phase == "dead_end":
        # brighter flash the instant the dead end is recognised
        style = replace(RenderStyle(), current_fill="red", doomed_fill="orchid")
    elif step.phase == "backtrack":
        style = replace(RenderStyle(), current_fill="black") # deepskyblue
    else:
        style = RenderStyle() # default: orange head
    return render_frame(
        step.maze,
        style,
        visited=step.visited,
        current=step.current,
        path=step.stack,
        doomed=step.doomed,
        cell_set_lookup=step.cell_set_lookup,
    )

def main():
    render_mode = "gif"
    generate_mode = "backtracker"
    solve_mode = "astar"
    size = 30

    maze_name = f"maze-{generate_mode}-{solve_mode}-{size}x{size}"

    if generate_mode == "kruskal":
        snapshots = generate_kruskal(size)
    elif generate_mode == "backtracker":
        snapshots = generate_backtracker(size)
    elif generate_mode == "binary_tree":
        snapshots = generate_binary_tree(size)

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
        out = Path(f"{maze_name}.gif")
        out.unlink(missing_ok=True)
        # frames = [render_frame(snap) for snap in snapshots]
        frames = []
        for step in snapshots:
            frame = _render_step(step)
            frames.append(frame)
            # frames.append(
            #     render_frame(
            #         step.maze,
            #         visited=step.visited,
            #         current=step.current,
            #         path=step.stack,
            #         cell_set_lookup=step.cell_set_lookup,
            #     )
            # )
        maze_build_frames_len = len(frames)
        maze = step.maze  # after the loop, step.maze is the fully-generated maze

        # gen = solve_steps(maze, (0, 0), (maze.size - 1, maze.size - 1))
        if solve_mode == "astar":
            gen = solve_astar_steps(maze, (0, 0), (maze.size - 1, maze.size - 1))
        else:
            raise ValueError(f"Unknown solve_mode: {solve_mode}")

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
            # GIF delays are stored in centiseconds (10ms units); anything
            # below 10ms rounds to 0, which decoders treat as "undefined" and
            # replace with their own default (ffmpeg carries the previous delay
            # forward — here the 5000ms intro — bloating the video). 20ms (2cs)
            # is the practical floor and matches ffmpeg's default min_delay.
            *[200] * (maze_build_frames_len - 2),  # 40
            2000,
            *[40] * (maze_search_frames_len - 1),
            2000,
            *[120] * (maze_solve_frames - 1),
            5000,
        ]

        print(f"Durations length: {len(durations)}")
        print(f"Frames length: {len(frames)}")

        assert len(durations) == len(frames)

        # for duration in durations:
        #     print(duration)

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
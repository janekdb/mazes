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
        style = replace(RenderStyle(), current_fill="magenta", doomed_fill="magenta") # doomed_fill="orchid"
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
        junction = step.junction,
        cell_set_lookup=step.cell_set_lookup,
    )

# durations in ms, keyed by the frame's kind
BUILD_PHASE_MS = {
    "advance":  80,
    "dead_end": 1000,   # full-second flash on dead-end recognition
    "backtrack": 40,
}
INTRO_MS = 5000
PRE_SOLVE_MS = 2000
SEARCH_MS = 40
SOLVE_MS = 40
FINAL_MS = 5000

def main():
    render_mode = "gif"
    generate_mode = "backtracker"
    solve_mode = "astar"
    size = 20

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

        timeline = []  # list of (frame, ms)

        # build phase - duration comes straight from the phase
        for step in snapshots:
            frame = _render_step(step)
            duration = BUILD_PHASE_MS.get(step.phase)
            timeline.append((frame, duration))
        timeline[0] = (timeline[0][0], INTRO_MS) # hold the opening frame
        timeline[-1] = (timeline[-1][0], PRE_SOLVE_MS) # pause before search begins

        maze = step.maze  # after the loop, step.maze is the fully-generated maze

        # gen = solve_steps(maze, (0, 0), (maze.size - 1, maze.size - 1))
        if solve_mode == "astar":
            gen = solve_astar_steps(maze, (0, 0), (maze.size - 1, maze.size - 1))
        else:
            raise ValueError(f"Unknown solve_mode: {solve_mode}")

        try:
            while True:
                visited, frontier, current = next(gen)
                frame = render_frame(maze, visited=visited, frontier=frontier, current=current)
                timeline.append((frame, SEARCH_MS))
        except StopIteration as stop:
            path = stop.value
        timeline[-1] = (timeline[-1][0], PRE_SOLVE_MS)  # pause before the solution draws

        # solve phase
        for i in range(2, len(path) + 1):
            frame = render_frame(maze, path=path[:i])
            timeline.append((frame, SOLVE_MS))
        timeline[-1] = (timeline[-1][0], FINAL_MS)  # hold the finished maze

        # GIF delays are stored in centiseconds (10ms units); anything
        # below 10ms rounds to 0, which decoders treat as "undefined" and
        # replace with their own default (ffmpeg carries the previous delay
        # forward — here the 5000ms intro — bloating the video). 20ms (2cs)
        # is the practical floor and matches ffmpeg's default min_delay.

        durations = [d for _, d in timeline]
        frames = [f for f, _ in timeline]

        print(f"Durations length: {len(durations)}")
        print(f"Frames length: {len(frames)}")

        assert len(durations) == len(frames)

        frames[0].save(
            out,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True,
        )

    print(maze_name)

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
from pathlib import Path
import sys
import time
from dataclasses import replace
from PIL import Image
from mazes.maze import generate_backtracker
from mazes.maze import generate_binary_tree
from mazes.maze import generate_kruskal
from mazes.maze import generate_wilson
from mazes.maze import GenStep
from mazes.render import render, render_frame, render_svg, RenderStyle
from mazes.solve import solve
from mazes.solve import solve_steps
from mazes.solve import solve_astar_steps


def _render_step(step: GenStep) -> list[Image.Image]:
    """Adapt a GenStep to render_frame, choosing colours from the phase."""
    if step.phase == "dead_end":
        # brighter flash the instant the dead end is recognised

        # Current highlighted, doomed not highlighted, junction not highlighted
        style = replace(RenderStyle(), current_fill="magenta") # doomed_fill="orchid"
        f1 = render_frame(
            step.maze,
            style,
            visited=step.visited,
            current=step.current,
            path=step.stack,
            # doomed=step.doomed,
            # junction = step.junction,
            # cell_set_lookup=step.cell_set_lookup,
        )

        # Go black
        style = replace(RenderStyle(), current_fill="black")  # doomed_fill="orchid" / magenta
        f2 = render_frame(
            step.maze,
            style,
            visited=step.visited,
            current=step.current,
            path=step.stack,
            # doomed=step.doomed,
            # junction = step.junction,
            # cell_set_lookup=step.cell_set_lookup,
        )

        # Highlight
        style = replace(RenderStyle(), current_fill="magenta") # doomed_fill="orchid"
        f3 = render_frame(
            step.maze,
            style,
            visited=step.visited,
            current=step.current,
            path=step.stack,
            # doomed=step.doomed,
            # junction = step.junction,
            # cell_set_lookup=step.cell_set_lookup,
        )

        # Show doomed and junction
        style = replace(RenderStyle(), current_fill="magenta", doomed_fill="magenta")  # doomed_fill="orchid"
        f4 = render_frame(
            step.maze,
            style,
            visited=step.visited,
            current=step.current,
            path=step.stack,
            doomed=step.doomed,
            junction = step.junction,
            # cell_set_lookup=step.cell_set_lookup,
        )

        return [f1, f2, f3, f4]

    elif step.phase == "backtrack":
        style = replace(RenderStyle(), current_fill="black") # deepskyblue
    # elif step.phase == "walk":
    #     style = replace(RenderStyle(), current_fill="purple")
    elif step.phase == "commit":
         style = replace(RenderStyle(), current_fill="limegreen")
    else:
        style = RenderStyle() # default: orange head

    frame = render_frame(
        step.maze,
        style,
        visited=step.visited,
        current=step.current,
        path=step.stack,
        doomed=step.doomed,
        junction = step.junction,
        cell_set_lookup=step.cell_set_lookup,
        carved=step.carved,
    )

    return [frame]

# durations in ms, keyed by the frame's kind
# BUILD_PHASE_MS = {
#     "advance":  80,
#     "dead_end": 250,   # full-second flash on dead-end recognition
#     "backtrack": 40,
# }
INTRO_MS = 5000
PRE_SOLVE_MS = 2000
SEARCH_MS = 40
SOLVE_MS = 40
FINAL_MS = 5000

# TODO: flash commits for short carved very quickly
# TODO: flash the loop-to-be-erased

# durations in ms, keyed by the frame's kind
def _build_phase_ms(size):
    # When the size is 10 this is 80
    # When the size is 20 this is 40
    # When the size is 40 this is 20
    # Above that it is 20
    advance = max(20, 80 * 10 // size)
    # full-second flash on dead-end recognition when the size is 10
    dead_end = 250 + 10 - size * 2
    # Backtrack at twice the pace
    backtrack = max(20, advance // 2)
    # When the size is 10 this is 60
    # When the size is 20 this is 30
    # Above that it is 20
    walk = max(20, 60 * 10 // size)
    return {
            "advance":  advance,
            "dead_end": dead_end,
            "backtrack": backtrack,
            "walk": walk,
            "commit": 1000
        }

def _search_ms(size):
    return max(20, SEARCH_MS * 10 // size)

def _solve_ms(size):
    return max(20, SOLVE_MS * 10 // size)

def main():
    render_mode = "gif"
    generate_mode = "wilson"
    solve_mode = "astar"
    size = 25

    build_phase_ms = _build_phase_ms(size)
    search_ms = _search_ms(size)
    solve_ms = _solve_ms(size)

    print('build_phase_ms')
    for key, value in build_phase_ms.items():
        print(f'{key}: {value}')

    maze_name = f"maze-{generate_mode}-{solve_mode}-{size}x{size}"

    if generate_mode == "kruskal":
        snapshots = generate_kruskal(size)
    elif generate_mode == "backtracker":
        snapshots = generate_backtracker(size)
    elif generate_mode == "binary_tree":
        snapshots = generate_binary_tree(size)
    elif generate_mode == "wilson":
        snapshots = generate_wilson(size)

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

        # step_idx = 0
        # build phase - duration comes straight from the phase
        for step in snapshots:
            frames = _render_step(step)
            # print(f"step: {step_idx}: frames: {len(frames)}")
            # step_idx += 1
            # print(f"phase: {step.phase}")
            duration = build_phase_ms.get(step.phase)
            # Reduce time for short carved corridor as Wilson generates many of these after
            # the initial longer carves
            if step.phase == "commit":
                duration = min(duration, 50 * len(step.carved))

            for frame in frames:
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
                timeline.append((frame, search_ms))
        except StopIteration as stop:
            path = stop.value
        timeline[-1] = (timeline[-1][0], PRE_SOLVE_MS)  # pause before the solution draws

        # solve phase
        for i in range(2, len(path) + 1):
            frame = render_frame(maze, path=path[:i])
            timeline.append((frame, solve_ms))
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
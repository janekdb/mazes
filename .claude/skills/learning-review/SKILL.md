---
name: learning-review
description: Review code in a personal learning project (not production). Use when the user asks for review of code they're writing to explore a language or ecosystem — small experimental repos, often with unfinished sub-modules, commented-out alternatives, and minimal dependencies. Differs from production review by prioritising suggestions that expose new language concepts, treating half-finished code as work-in-progress rather than bugs, and ordering work by learning payoff over feature completeness.
---

# Learning review

Use this skill when reviewing code in a personal learning project — a sandbox where the user is exploring a language or ecosystem rather than shipping a product. The goal is to help them grow as a programmer in that language, not to harden their code for production.

## When to invoke

Invoke when one or more of these holds:

- The user explicitly asks to "review" or "look over" a file in a project they've described as personal, learning, exploratory, a playground, a sandbox, or "just to learn X."
- An auto-memory or CLAUDE.md describes the project as a learning playground.
- The repository has strong hallmarks of a learning project: small scope (a few files), no or minimal third-party dependencies, commented-out experiments, multiple alternative implementations of the same idea side by side, no CI configuration, no deployment artefacts.

If the project is production code (deployed, generates revenue, has users, has a CI pipeline, has open PRs from a team), prefer the built-in `/review` instead. When in doubt, ask the user one question: "Is this a learning project or production code?"

## How it differs from production review

|                       | Production review                | Learning review                                                              |
| --------------------- | -------------------------------- | ---------------------------------------------------------------------------- |
| Refactor suggestions  | Justified by maintainability     | Justified by what *language/ecosystem concept* they expose                   |
| Commented-out code    | Flag as dead code to remove      | Treat as work-in-progress unless the user asks for cleanup                   |
| Half-finished modules | Flag as bugs                     | Note as parallel experiments; don't pressure to finish                       |
| Dead variables        | Always flag                      | Flag, but tag as low-priority                                                |
| Style nits            | Flag all relevant                | Flag a few representative ones; don't enumerate exhaustively                 |
| Magic numbers         | Suggest named constants          | Suggest keyword-only args or a dataclass (exposes language concepts instead) |
| Recommended order     | Bug → polish → tests             | Bug → highest-learning-payoff enrichment                                     |
| Test coverage         | Always suggest broadening        | Suggest only when it teaches a new tool (e.g. hypothesis, parametrisation)   |

## Output structure

1. **Where you are** — one short paragraph summarising the file's current state, especially if reviewing the same file again (mention what landed since last time).
2. **Bugs / correctness** — real defects only. One per bullet, with `file:line` citations. Skip this section if there are none.
3. **Style / language idioms** — a handful of items. For each, name the concept it would teach if changed. Don't enumerate exhaustively; pick the highest-signal three or four.
4. **Refactor opportunity** — at most one named opportunity, with the language concept it exposes (generators, Protocol, dataclass, etc.) and a concrete code sketch.
5. **Recommended next move** — one sentence. Bug fix first if there is one; otherwise the change with the highest learning payoff.

Keep each section terse. The review should be readable in under a minute, not an essay.

## The "concept lens"

Every refactor suggestion must answer the question *what would the user learn from doing this?* If the only answer is "cleaner code" or "more maintainable," demote or omit the suggestion.

Good concept-lens framings:
- "Extract this duplicated traversal into a generator" → teaches `yield`, the iterator protocol, multiple-consumer pattern.
- "Use a `frozenset` so the lookup container can itself be a set" → teaches `frozenset` and hashable collection types.
- "Promote magic numbers to keyword-only args" → teaches `*,` in function signatures.
- "Replace the for-each-then-string-join with a generator expression" → teaches generator expressions vs list comprehensions.
- "Add type hints and run mypy" → teaches the type-checker ecosystem.
- "Add `@dataclass(frozen=True)` to this tuple-of-tuples model" → teaches dataclasses and immutability.

Weak framings (avoid):
- "Rename `x` to `value`" — no concept exposed.
- "Add docstrings" — unless the user is exploring documentation tooling.
- "Use `enumerate` here" — fine to mention once if the user clearly hasn't seen it, but don't churn on basics they already use elsewhere in the file.

If the user's memory or CLAUDE.md indicates which concepts they've already covered, prefer suggestions that introduce *new* ones over repeating familiar ground.

## What to skip

Don't suggest things that only make sense for production:

- Error monitoring, retry logic, structured logging.
- Dependency pinning beyond what the project's package manager already provides.
- Deployment, CI configuration, secrets management.
- Performance optimisations that don't expose a profiling or measurement tool. Don't suggest `lru_cache` for a 5×5 loop unless the user is learning `functools`.
- Test coverage targets, mutation testing, fuzz coverage — unless the *tool* is the lesson (e.g. introducing `hypothesis`).
- Renaming things to be "more descriptive" unless the current name is genuinely misleading or shadows a builtin.

## Tone

Match the user's exploring, low-stakes energy. The review is collaborative, not gatekeeping. Phrase enrichments as "you could try X, which would expose you to Y," not "you should X." Save imperatives for actual bugs. When you point out a bug, say so plainly; when you suggest a refactor, frame it as an option with a learning payoff.

## Example (anchor)

A canonical output, condensed:

> ## Where you are
> The iterator refactor landed cleanly — `iter_walls` is now the shared model and both renderers consume it. The GIF pipeline works end-to-end.
>
> ## Bugs / correctness
> - **`generate` walks deterministically, not randomly** (`maze.py:95-102`). The direction loop is missing `break` after `found = True`, so it overwrites `next_cell` with whichever valid direction happens to be last in the shuffled list. One-line fix.
>
> ## Style / language idioms
> - Mid-file `from PIL import` at `render.py:128` — convention is top-of-module.
> - Commented-out blocks at `render.py:91-114`: git remembers; clear them.
> - Coordinate parity mismatch: `render_frame` adds `+ width` to the canvas, `render_svg` doesn't. Pick one strategy. *Teaches: thinking about coordinate-system conventions in graphics code.*
>
> ## Refactor opportunity
> Add a `bfs(maze, start, goal)` solver returning the path, then a second `render_*` pass that overlays the solution in another colour. *Teaches: `collections.deque`, BFS, and the "multiple consumers of one model" pattern you've already started with `iter_walls`.*
>
> ## Recommended next move
> Fix the missing `break` first as a one-line commit; then the BFS solver gives the biggest visual payoff per line of code.

# TODO

DONE: Implement A. Solve the maze
When using Kruskal's algorithm for maze construction colour each disjoint set
  differently. This will show smaller tree being added under larger.
When solving, a frontier cell which is entirely enclosed by visited cells
  does not need to be extends as there is no path to the goal. Implement this.

# Details 
Three candidate next directions                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                    
  A. Solve the maze (highest visual payoff)                                                                                                                                                                                                         
                  
  Add bfs(maze, start, goal) returning the path, then a second renderer pass that draws the solution in a different colour. Natural follow-up: a Dijkstra/BFS colour gradient where each cell is tinted by its distance from the start — produces   
  those beautiful heatmap-style mazes you see in tutorials.
                                                                                                                                                                                                                                                    
  Python concepts exposed: collections.deque for BFS, dict paths, optional heapq if you go A*. The colouring step exposes HSL-to-RGB conversion (Pillow's ImageColor.getrgb).                                                                       
   
  B. A second generation algorithm (architectural)                                                                                                                                                                                                  
                  
  Drop in Wilson's, Hunt-and-Kill, or Kruskal's alongside the recursive backtracker. The visible textures differ dramatically (Wilson's is unbiased and snaky; Kruskal's looks "shattered"). Forces you to factor a MazeGenerator Protocol or       
  strategy interface.
                                                                                                                                                                                                                                                    
  Python concepts exposed: typing.Protocol, structural subtyping, possibly abc.ABC. Less visual surprise than A but better grounding in Python's type system.                                                                                       
   
  C. Property-based testing with Hypothesis                                                                                                                                                                                                         
                  
  uv add hypothesis, write properties like "every generated maze has exactly size² - 1 links" (it's a spanning tree), "every cell is reachable from (0,0)", "no link list contains duplicates". Hypothesis will hammer the generator with random    
  sizes and shrink failures to minimal counter-examples — and it'll find the directions-loop bug above without being told.
                                                                                                                                                                                                                                                    
  Python concepts exposed: hypothesis strategies, shrinking, the BFS reachability check (small overlap with A).                                                                                                                                     
   
  Recommendation                                                                                                                                                                                                                                    
                  
  A first. It has the strongest visual reward — the GIF you've built becomes a stage for showing solutions/distances, not just construction — and the BFS step is small (~20 lines) and self-contained. After that, C is the highest-ROI follow-up: 
  with a solver in hand, "every cell is reachable" becomes a real, easily-checkable invariant, and Hypothesis will catch the generate bug as a bonus side-effect. B is the right move when you're tired of visuals and want to dig into the type
  system; I'd save it for a third iteration.                                                                                                                                                                                                        

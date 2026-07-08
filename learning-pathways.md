 Here are directions ordered by learning density per line of code:                                                                                                                                              
   
  Language features                                                                                                                                                                                              
  - Add full type hints (tuple[int, int], Self, Iterator[...]); run mypy --strict or pyright to learn the gaps. Try a Cell = NamedTuple to replace bare tuples.
  - Use match/case on direction tuples and on cell-position validation — natural fit for structural patterns.                                                                                                    
  - Convert get_linked_cells and _shuffled_directions to generators; make generate yield intermediate states so render can animate progress.                                                                     
  - PEP 695 generics (type Grid[T] = list[list[T]]) — new in 3.12+, perfect tiny playground.                                                                                                                     
                                                                                                                                                                                                                 
  Algorithms (each teaches a different idiom)                                                                                                                                                                    
  - Implement Wilson's, Aldous-Broder, Kruskal's, Prim's, Sidewinder. Kruskal's invites a union-find class; Prim's a heapq; Wilson's loop-erased random walks.                                                   
  - Add a BFS/Dijkstra solver returning the path — exposes collections.deque, heapq, dict-as-graph.                                                                                                              
  - Refactor algorithms behind a Protocol (PEP 544) — compare to abc.ABC.                                                                                                                                        
                                                                                                                                                                                                                 
  Testing & correctness                                                                                                                                                                                          
  - hypothesis property tests: "spanning tree has exactly n²−1 edges", "every cell reachable from (0,0)", "no link crosses a wall". Property-based testing is uniquely well-suited here.                         
  - pytest.mark.parametrize across algorithms and sizes; pytest-benchmark to compare them.                                                                                                                       
                  
  Performance & tooling                                                                                                                                                                                          
  - Profile with cProfile/timeit; swap the O(n²) adjacency matrix for a dict-of-sets or bitarray and measure. Try numpy for the matrix variant.
  - Parallelize "generate 1000 mazes" with concurrent.futures.ProcessPoolExecutor.                                                                                                                               
                                                                                  
  Packaging & CLI                                                                                                                                                                                                
  - Add __main__.py, a typer or argparse CLI (mazes gen --size 10 --algo wilson --format svg), entry point in pyproject.toml, install via uv.                                                                    
                                                                                                                                                                                                                 
  Output                                                                                                                                                                                                         
  - SVG renderer (pure-stdlib string templating) → PNG via Pillow → live rich terminal animation. Each tier teaches different stdlib/3rd-party APIs.
  - 
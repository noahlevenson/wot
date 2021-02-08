# Open questions

0. There's a bug where sometimes we use makeg to create a strongly connected graph, but some peers don't wind up in the strong set... I know why this happens: if randint picks ourself as a signing buddy, we just skip that signature... when you fix this, we should enforce the interval too...

1. Given several strongly connected components in the graph, how do we determine which is the real strong set? Would we just look for a sentinel, or "genesis" vertex? Does PGP just look for the largest strongly connected subgraph, and if so, how do they prevent abuse if identitiy creation is free?

2. When we calculate shortest paths for each vertex using BFS, do we calculate it over only the strong set, or over the entire graph,
but only w.r.t each vertex in the strong set? Similarly, how should we do it when calculating AMSD?

3. How do we prevent an attack where an adversary creates more signatures for a pubkey than the system can compute?

4. What's the right data structure strategy for representing signatures? It seems that PGP implementations keep signatures with the signee rather than
the signer - why?

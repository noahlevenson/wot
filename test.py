#!/usr/bin/env python3

import wot

# The 6-vertex graph from: https://www.analyticsvidhya.com/blog/2020/04/community-detection-graphs-networks/
g = [wot.Pubkey(label=i) for i in range(6)]
g[0].sign(1) # outedge from A to B
g[0].sign(3) # outedge from A to D

g[1].sign(0) # outedge from B to A
g[1].sign(2) # outedge from B to C
g[1].sign(4) # outedge from B to E

g[2].sign(1) # outedge from C to B
g[2].sign(5) # outedge from C to F

g[3].sign(0) # outedge from D to A
g[3].sign(4) # outedge from D to E

g[4].sign(3) # outedge from E to D
g[4].sign(1) # outedge from E to B
g[4].sign(5) # outedge from E to F

g[5].sign(2) # outedge from F to C
g[5].sign(4) # outedge from F to E

print(*g, sep="\n")

pg = wot.bfs(g, g[0])

print(*pg, sep="\n")

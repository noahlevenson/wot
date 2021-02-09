#!/usr/bin/env python3

import wot

# Below, we simulate a Sybil attack scenario in which an adversary (Peer 17) creates a strongly
# connected disconnected subgraph consisting of sock accounts, then tricks one non-adversarial
# peer into recirpocally signing him into the network. The result is that Peer 17 winds up
# with top 10% global MSD network-wide.

# Note that after Peer 17 tricks one non-adversarial peer into reciprocally signing him into the
# network, all of his sock accounts become identifiable by their articulation points -- but
# after tricking a second non-adversarial peer, articulation points cannot be detected in this manner.

# Make a network of 10 peers (all are part of the strong set)
g1 = wot.makeg(10)
print(*wot.scc(g1), sep="\n")
print(f"(Network size: {len(g1)} AMSD: {wot.amsd(g1, wot.scc(g1)[0])})")

msds = [(i, wot.msd(g1, i)) for i in wot.scc(g1)[0]]
msds.sort(key=lambda x: x[1])

print("STRONG SET:")

for m in msds:
    print(f"peer: {m[0]} msd: {m[1]:.1f} art points: {wot.ss_artic(g1, m[0])}")

print("\n\n")

# Add 20 new peers to the network, all of whom are part of their own strongly connected disconnected subgraph
# controlled by Peer 17
g2 = wot.makeg(20, sig_range=(5, 10))
g1 = wot.addg(g1, g2)
print(*wot.scc(g1), sep="\n")
print(f"(Network size: {len(g1)} AMSD: {wot.amsd(g1, wot.scc(g1)[0])})")

msds = [(i, wot.msd(g1, i)) for i in wot.scc(g1)[0]]
msds.sort(key=lambda x: x[1])

print("STRONG SET:")

for m in msds:
    print(f"peer: {m[0]} msd: {m[1]:.1f} art points: {wot.ss_artic(g1, m[0])}")

print("\n\n")

# Peer 17 tricks peer 2 into reciprocally signing him into the strong set
g1[17].sign(2)
g1[2].sign(17)
print(*wot.scc(g1), sep="\n")
print(f"(Network size: {len(g1)} AMSD: {wot.amsd(g1, wot.scc(g1)[0])})")

msds = [(i, wot.msd(g1, i)) for i in wot.scc(g1)[0]]
msds.sort(key=lambda x: x[1])

print("STRONG SET:")

for m in msds:
    print(f"peer: {m[0]} msd: {m[1]:.1f} art points: {wot.ss_artic(g1, m[0])}")

print("\n\n")

# Peer 17 uses his sock identity, Peer 29, to trick peer 4 into reciprocally signing him into the strong set
g1[29].sign(4)
g1[4].sign(29)
print(*wot.scc(g1), sep="\n")
print(f"(Network size: {len(g1)} AMSD: {wot.amsd(g1, wot.scc(g1)[0])})")

msds = [(i, wot.msd(g1, i)) for i in wot.scc(g1)[0]]
msds.sort(key=lambda x: x[1])

print("STRONG SET:")

for m in msds:
    print(f"peer: {m[0]} msd: {m[1]:.1f} art points: {wot.ss_artic(g1, m[0])}")

print("\n\n")

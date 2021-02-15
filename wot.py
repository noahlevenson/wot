import copy
import uuid
import random
from enum import IntEnum

# A web of trust network can be represented as a directed graph:
# each vertex is a public key belonging to a peer, and each
# outedge is a signature

# We represent a directed graph as an adjacency list:
# Each element of the list is a vertex represented as a Pubkey object
# and each vertex keeps a list of its outedges (as indices into the list)
# in its 'signed' property

# A public key belonging to a simulated peer
# a public key has a label which should probably correspond to its index 
# as a vertex in an adjacency list, a UUID, and a list of labels of 
# the peer keys it has signed
class Pubkey():
    def __init__(self, label):
        self.label = label
        self.id = uuid.uuid4()
        self.signed = []
    
    def __str__(self):
        labels = ", ".join([str(i) for i in self.signed])
        return (f"PEER: {self.label}\nnum sigs: {len(self.signed)}\n{labels}\n\n")
        
    def sign(self, idx):
        self.signed.append(idx)

# Construct a graph of n_peers, each reciprocally signing sig_range peers
def makeg(n_peers, sig_range=(1, 3)):
    g = []

    for i in range(n_peers):
        g.append(Pubkey(label=i))   
    
    for pubkey in g:
        # TODO: get fancier and actually enforce the interval
        for j in range(random.randint(*sig_range)): 
            buddy_idx = random.randint(0, n_peers - 1)
            
            if buddy_idx != pubkey.label and pubkey.label not in g[buddy_idx].signed:
                g[buddy_idx].sign(pubkey.label)
                pubkey.sign(buddy_idx)

    return g

# Concatenate graph g2 with graph g1, updating its indices appropriately
def addg(g1, g2):
    offset = len(g1)

    for pubkey in g2:
        pubkey.label += offset
        pubkey.signed = [label + offset for label in pubkey.signed]
    
    return g1 + g2

# Return a copy of graph g with vertex label 'l' disconnected, updating all signatures appropriately
def dcon(g, l):
    h = copy.deepcopy(g)
    h[l].signed = []

    for pubkey in h:
        if l in pubkey.signed:
            pubkey.signed.remove(l)

    return h

# Discovery colors for graph search algos
class COLOR(IntEnum):
    WHITE = 0
    GREY = 1
    BLACK = 2

# A vertex property
class Vertex_prop:
    def __init__(self, color, d, f, pi, label):
        self.color = color
        self.d = d
        self.f = f
        self.pi = pi
        self.label = label

    def __str__(self):
        return f"Vertex_prop(color: {self.color}, d: {self.d}, f: {self.f}, pi: {None if self.pi == None else self.pi.label}, label: {self.label})"

# Breadth first search - returns the predecessor subgraph (as vertex properties) for graph g w.r.t source vertex s   
# and the number of shortest paths to each vertex w.r.t source vertex s
def bfs(g, s):
    vprops = []
    
    paths = [0 for _ in g]
    paths[g.index(s)] = 1

    for i in range(len(g)):
        if (g[i] == s): 
            vprops.append(None) # Don't include props for the source vertex
            continue

        vprops.append(Vertex_prop(COLOR.WHITE, float("inf"), None, None, i))
    
    sp = Vertex_prop(COLOR.GREY, 0, None, None, g.index(s)) # Here's props for the source vertex
    q = [] 
    q.append(sp)

    while len(q) != 0:
        u = q.pop(0)
        
        # For every Pubkey that this Pubkey has signed
        for v in g[u.label].signed:
            vp = vprops[v] if vprops[v] != None else sp 
            
            # The CLRS discussion of BFS doesn't ever consider counting shortest paths,
            # so I hacked this in from https://www.baeldung.com/cs/graph-number-of-shortest-paths
            # TODO: we should prob give it a rigorous unit test
            if vp.d > u.d + 1:
                paths[vp.label] = paths[u.label]
            elif vp.d == u.d + 1:
                paths[vp.label] = paths[vp.label] + paths[u.label]

            if vp.color == COLOR.WHITE:
                vp.color = COLOR.GREY
                vp.d = u.d + 1
                vp.pi = u
                q.append(vp)

        u.color = COLOR.BLACK

    vprops[sp.label] = sp
    return ([vp for vp in vprops if vp.pi != None or vp == sp], paths)

# Compute the edge scores for a graph g, w.r.t a single vertex, from a predecessor subgraph and
# number of shortest paths as computed by BFS above
# TODO: this is an inefficient naive implementation which is excessively complicated because we support directed graphs
# and we represent our graphs as adjacency lists... since a node's edges do not indicate bidirectional relationships,
# we can't determine all of a node's parents by looking at its edges -- instead, we have to search the graph for all
# of the nodes who have outedges to the present node. The predecessor subgraph created during BFS does not capture
# all parent-child relationships, because it ignores edges that would create cycles...
# There might be a way to capture the cyclic edges during BFS... or we might research whether it's possible to 
# enforce a "reciprocal signatures only" policy such that un-reciprocated signatures are not even considered, effectively
# giving us undirected graphs...
# ALSO TODO: the output is transposed - ie, scores[i][j] is the score for the outedge from vertex j to vertex i
def _get_edge_scores(g, pg, paths):
    z = list(zip(pg, paths))
    z.sort(key=lambda x: x[0].d, reverse=True)
    
    # Our intermediate representation is a list of dictionaries, where list[i] is a dictionary mapping
    # outedges (as vertex numbers) to scores - it's ordered by label (ie default order of the predecessor subgraph)
    scores = [{} for _ in pg]
   
    # Since we sorted our predecessor subgraph by distance descending above, we're climbing from leaf to root:
    for i, zipped in enumerate(z):
        vprop = zipped[0]
        n_paths = zipped[1]

        # We need to calculate edge scores for every node with a smaller distance than vprop which has an outedge to vprop, so...
        # TODO: you could do this faster by only considering nodes ahead of our current pointer in z
        for pubkey in g:
            if pg[pubkey.label].d < vprop.d and vprop.label in pubkey.signed:
                # Collect any accumulated predecessor flow...
                f = 0

                # ...which we do by looping through the graph and grabbing all nodes with a larger distance than vprop
                # which vprop has an outedge to
                for child in g[vprop.label].signed:
                    if pg[child].d > vprop.d:
                        f += scores[child][vprop.label]

                scores[vprop.label][pubkey.label] = ((paths[pubkey.label] if i == 0 else 1) + f) / n_paths
    
    return scores

# Compute the edge betweenness centrality for graph g
def ebc(g, digraph=True):
    scores = []

    for v in g:
        pg, paths = bfs(g, v)
        scores.append(_get_edge_scores(g, pg, paths))
    
    # TODO: this is a naive method to sum over all the scores
    final = [{} for _ in g]
    
    for score_wrt_source in scores:
        for i, score_dict in enumerate(score_wrt_source):
            for k in score_dict.keys():
                final[i][k] = final[i].get(k, 0) + score_dict[k]

    return final

# Get the top n EBC scores from the result of a call to ebc above
# Returns a sorted list of [u-v, score] lists
def top_ebc(scores, n=10):
    # TODO: rewrite this as a list comprehension
    res = []

    for i, score_dict in enumerate(scores):
        for k in score_dict:
            res.append([f"{i}-{k}", score_dict[k]])
    
    res.sort(key=lambda x: x[1], reverse=True)
    return res[:n]

# Depth first search - returns vertex properties created for graph g
def dfs(g, visit_order=None):
    vprops = []

    for i in range(len(g)):
        vprops.append(Vertex_prop(COLOR.WHITE, None, None, None, i))
        
    time = 0
    
    if visit_order == None:
        visit_order = range(len(vprops))
    
    for i in visit_order:
        if vprops[i].color == COLOR.WHITE:
            time = _dfs_visit(g, vprops, vprops[i].label, time)

    return vprops

def _dfs_visit(g, vprops, label, time):
    time += 1
    vprops[label].d = time
    vprops[label].color = COLOR.GREY
    
    # For every Pubkey that this Pubkey has signed...
    for v in g[label].signed:
        vp = vprops[v]

        if vp.color == COLOR.WHITE:
            vp.pi = vprops[label]
            time = _dfs_visit(g, vprops, v, time)

    vprops[label].color = COLOR.BLACK
    time += 1
    vprops[label].f = time
    return time

# Compute the transpose of graph g
# Notable: if we only allow reciprocal signatures, there's no need to calculate the transpose
def graph_transpose(g):
    gt = [Pubkey(label=i) for i in range(len(g))]
    
    for i in range(len(g)):
        for j in g[i].signed:
            gt[j].sign(i)
    
    return gt

# Compute the strongly connected components of graph g
# If decompose = True, it will return SCCs as a list of lists of indices
# otherwise it will return a depth first forest as Vertex_prop objects
def scc(g, decompose=True):
    vprops = dfs(g)
    gt = graph_transpose(g)
    vprops_sorted = sorted(vprops, reverse=True, key=lambda vprop: vprop.f)
    sort_order = [vprops.index(vprop) for vprop in vprops_sorted]
    dff = dfs(gt, visit_order=sort_order)
    
    if not decompose:
        return dff
    
    # Sort the forest by finishing time, descending - any vertex in the list with a
    # pi of None is a root, all vertices that follow with a non-None pi are part of its SCC
    dff.sort(key=lambda x: x.f, reverse=True)
    scc = []

    for vprop in dff:
        if vprop.pi == None:
            scc.append([vprop.label])
        else:
            scc[-1].append(vprop.label)

    return scc

# Compute the mean shortest distance for a vertex with label 'l' in graph g
def msd(g, l):
    pg = bfs(g, g[l])[0]
    return sum([vprop.d for vprop in pg]) / len(pg)

# Experimental idea:
# Compute dearticulated MSD for a vertex with label 'l' in graph g
# in DMSD, vertices for whom vertex l is an articulation point are 
# disincluded from the set over which the mean is calculated
# TODO: this metric is so far pretty useless - maybe we should weight
# the final calculation by the cardinality of the set after dearticulation?
def dmsd(g, l):
    h = dcon(g, l)
    
    # TODO: this assumes that the 0th list returned by SCC is the strong set
    # we need a strongset function which identifies the canonical strong set
    dscc = scc(h)
    pg = bfs(g, g[l])[0]
    connected = [vprop for vprop in pg if vprop.label in dscc[0]]
    return sum([vprop.d for vprop in connected]) / len(connected) 

# Compute the average mean shortest distance over a graph g and subset of peers s
def amsd(g, s):
    msds = [msd(g, i) for i in s]
    return sum(msds) / len(s)

# Compute the articulation points which would disconnect a vertex with 
# label 'l' from the canonical strong set over graph g
# If l is not in the canonical strong set over g, the result is undefined
def ss_artic(g, l):
    # Brute force approach
    ap = []

    for pubkey in g:
        h = dcon(g, pubkey.label)
        dscc = scc(h)
        
        # TODO: this assumes that the 0th list returned by SCC is the strong set
        # we need a strongset function which identifies the canonical strong set
        if l not in dscc[0] and pubkey.label != l:
            ap.append(pubkey.label)

    return ap

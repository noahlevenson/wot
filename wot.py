#!/usr/bin/env python3

import uuid
import random

class Pubkey():
    def __init__(self):
        self.id = uuid.uuid4()
        self.signed = []
    
    def __str__(self):
        ids = ", ".join([str(peer.id) for peer in self.signed])
        return (f"PEER: {self.id}\nSigs: {len(self.signed)}\n{ids}\n\n")
        
    def sign(self, ref):
        self.signed.append(ref)

def makeg(n_peers, sig_range=(1, 3)):
    g = []

    for i in range(n_peers):
        g.append(Pubkey())   
    
    for i in g:
        for j in range(random.randint(*sig_range)):
            buddy = random.randint(0, n_peers - 1)
            
            if g[buddy] != i and i not in g[buddy].signed:
                g[buddy].sign(i)
                i.sign(g[buddy])

    return g

g = makeg(10)
print(*g, sep="\n")

#!/usr/bin/env python3

import random
import hashlib

KEY_LEN = 1024 # In bits

# h is integral hash value, n is number of bits of leading zeros, b is the number of bits in your hash
def check_leading_zeros(h, n, b=160):
    mask = 2 ** n - 1
   
    # The right shift is only required if you want to match a nonzero value
    if (h & (mask << (b - n))) >> (b - n) == 0:
        return True
    
    return False

class Cert:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.pubkey = random.getrandbits(KEY_LEN) 
        self.counter = 0

    def __str__(self):
        return f"name: {self.name}\naddress: {self.address}\npubkey: {self.pubkey}\n counter: {self.counter}"

plr = Cert("Pizzeria La Rosa", "12 Russell Ave. New Rochelle NY 10803")

while not check_leading_zeros(int(hashlib.sha1(str.encode(str(plr))).hexdigest(), 16), 20):
    plr.counter += 1

print(plr)
print(hashlib.sha1(str.encode(str(plr))).hexdigest())

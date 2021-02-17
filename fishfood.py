#!/usr/bin/env python3

import random
import csv

KEY_LEN = 1024 # In bits
DICT_WIDTH = 12 # In bits
DICT_MASK = 2 ** DICT_WIDTH - 1

with open("./adj_28480.txt", "r") as fd:
    reader = csv.reader(fd)
    x = [row[0] for row in reader]

with open("./noun_5449.txt", "r") as fd:
    reader = csv.reader(fd)
    y = [row[0] for row in reader]

def get_index(pubkey, offset=0):
    return (pubkey & (DICT_MASK << (offset * DICT_WIDTH))) >> (offset * DICT_WIDTH)

pubkey = random.getrandbits(KEY_LEN)
print(f"pubkey: {pubkey:x}\n")

a = get_index(pubkey)
b = get_index(pubkey, 1)
c = get_index(pubkey, 2)

print(f"{a}, {b}, {c}")
print(f"{x[a]} {x[b]} {y[c]}")

#!/usr/bin/python
###########################################################################
# consecucheck.py
# (c) Rose Midford 2025, see LICENSE for details
###########################################################################
# This script will check that digital camera filenames in a given
# directory will have consecutive file numbering. Might be useful if
# you're drunk and use rm instead of ls while file import is underway and
# have to see that you restored everything from backup correctly. It's a
# thing that could happen. Don't ask.
#
# Doesn't use anything beside Python standard library
# Usage: python consecucheck.py [directory]

import os, sys, re
from pathlib import Path

try:
    path = sys.argv[1]
    dir = Path(path)
except IndexError:
    dir = Path.cwd()
pattern = r"DSC_(\d{4}).DNG"

try:
    allfiles = os.listdir(dir.absolute())
except FileNotFoundError:
    print(f"Directory {dir.absolute()} not found.")
    sys.exit(1)

matches = {}

for f in allfiles:
    match = re.match(pattern,f)
    if match:
        matches[int(match.group(1))] = f

r = sorted(matches.keys())
try:
    start = r[0]
    end = r[-1]
except IndexError:
    print("No filenames match.")
    sys.exit(0)

print(f"First found: {start}, last found: {end}")

sequences = []
seq_start = start

for x in range(start,end):
    if x not in matches:
        if seq_start is not None:
            seq = (seq_start,x)
            sequences.append(seq)
            seq_start = None
    else:
        if seq_start is None:
            seq_start = x
if seq_start is not None:
    seq = (seq_start,end)
    sequences.append(seq)

print("Sequences:")
for s in sequences:
    print(f" - {s[0]}-{s[1]}")


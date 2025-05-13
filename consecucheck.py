#!/usr/bin/python
###########################################################################
# consecucheck.py
# (c) Rose Midford 2025, see LICENSE for details
###########################################################################
# This script will check that digital camera filenames in a given
# directory will have consecutive file numbering. It will report the
# number ranges of images it finds.
#
# This script might be useful if you're drunk and use rm instead of ls
# while a massive file import is underway, and have to ensure that you
# restored everything from backup correctly, while still drunk. It's a
# thing that could happen. Hypothetically. Don't ask.
#
# Doesn't use anything beside Python standard library
# Usage: python consecucheck.py [directory]
###########################################################################

import os, sys, re
from pathlib import Path

###########################################################################

# Default path is current working directory, but you can specify
# alternate path on command line.
try:
    path = sys.argv[1]
    dir = Path(path)
except IndexError:
    dir = Path.cwd()
# The file name pattern we're trying to match against.
# TODO: Make this configurable or something?
pattern = r"DSC_(\d{4}).DNG"

# Get the files from that directory
try:
    allfiles = os.listdir(dir.absolute())
except FileNotFoundError:
    print(f"Directory {dir.absolute()} not found.")
    sys.exit(1)

# This is actually a sparse array, integer-keyed dict,
# call it what you want
matches = {}

# Go through all the files and put the matches in the
# dict
for f in allfiles:
    match = re.match(pattern,f)
    if match:
        matches[int(match.group(1))] = f

# Grab the matched file numbers. As they are sorted,
# the first and last will provide a range for us to
# work on. If we don't match 'em, well, guess there's
# no files.
r = sorted(matches.keys())
try:
    start = r[0]
    end = r[-1]
except IndexError:
    print("No filenames match.")
    sys.exit(0)

print(f"First found: {start}, last found: {end}")

# This will be a list of tuples in form of (start,end)
sequences = []
# Temp for the start of the current sequence
seq_start = start

# Go through the range and pick up the start and end
# of each sequence. If an end of the sequence is detected,
# stick it in the sequences list.
for x in range(start,end):
    if x not in matches:
        if seq_start is not None:
            seq = (seq_start,x)
            sequences.append(seq)
            seq_start = None
    else:
        if seq_start is None:
            seq_start = x
# The loop done, handle the last sequence if we were
# in middle of one when the list ended (we probably
# are)
if seq_start is not None:
    seq = (seq_start,end)
    sequences.append(seq)

# Finally, print out the sequences!
print("Sequences:")
for s in sequences:
    print(f" - {s[0]}-{s[1]}")


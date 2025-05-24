#!/usr/bin/python
# Moves files into day-based subfolders based on modification timestamp.

import os, shutil
from datetime import date
from pathlib import Path

infiles = os.listdir(Path.cwd())

for i in infiles:
    infile = Path(i)
    targetdir = Path(date.fromtimestamp(os.path.getmtime(infile)).strftime('%Y-%m-%d'))
    if not os.path.exists(targetdir):
        os.mkdir(targetdir)
    destination = shutil.move(infile,targetdir)
    print(f"{infile} => {destination}")

#!/usr/bin/python
# Renames video files from HDV_0001.MP4 to HDV_0001_yyyymmdd_hhmmss.mp4

import os, shutil, glob
from datetime import datetime
from pathlib import Path

# File types we want to handle
globs = ['*.MP4','*.MOV','*.avi']

infiles = []
for g in globs:
    infiles.extend(glob.glob(pathname=g,root_dir=Path.cwd()))

for i in infiles:
    infile = Path(i)
    infile_date = datetime.fromtimestamp(os.path.getmtime(infile))
    datestamp = Path(infile_date.strftime('%Y%m%d_%H%M%S'))
    outfile = Path(f"{infile.stem}_{datestamp}{infile.suffix}")
    print(f"{infile} => {outfile}")
    shutil.move(infile,outfile)

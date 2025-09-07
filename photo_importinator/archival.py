#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

# standard library
import os
from pathlib import Path
import logging
# PyPI
import py7zr
# Local
from dazzle import *

logger = logging.getLogger(__name__)

def archive(source:Path, target:Path):
    """Archive all files under `source` to 7-Zip file `target`.

    TODO: This should probably be a bit more elegant. Yet, since this
    part of the process can't really be parallelised, expressing these
    as photo_processing.Task isn't really feasible. So this is
    really just a helper function at this point.
    """
    backup_source_files = enumerate_source(source)
    total_size = total_source_size(backup_source_files)
    bytes_so_far = 0
    progressbar_widgets=[
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        ' (', progressbar.DataSize(), ' / ', human_size(total_size), ') ',
        ' (', progressbar.ETA(), ') ',
    ]
    logger.info(f"Backing up {source} to {target}.")
    with py7zr.SevenZipFile(target, 'w') as archive, \
        progressbar.ProgressBar(max_value=total_size, \
                                widgets=progressbar_widgets) as bar:
        for file, size in backup_source_files:
            rel_file = file.relative_to(source)
            logger.info(f"Backup: {rel_file}")
            logger.debug(f"Full path {file}, size {size} bytes")
            archive.write(file,rel_file)
            bytes_so_far += size
            bar.update(bytes_so_far)
    arc_size = os.path.getsize(target)
    ratio = (arc_size / total_size) * 100
    logger.info("Archival complete. "+ \
          f"{len(backup_source_files)} files, " + \
          f"{human_size(total_size)} bytes, " + \
          f"{human_size(arc_size)} compressed ({ratio:.2f}% of original))")
    print(f"{ICON_DONE} Archival complete. " + \
          f"{len(backup_source_files)} files, " + \
          f"{human_size(total_size)} bytes, " + \
          f"{human_size(arc_size)} compressed ({ratio:.2f}% of original)")

def total_source_size(sources:list) -> int:
    """Given a source file list of (Path,int) tuples (path and file size),
    return total file size"""
    total_size = 0
    for _,size in sources:
        total_size += size
    return total_size

def enumerate_source(source:Path) -> list:
    """Find all regular files in the source path.

    Returns a list of (Path,int) tuples with file path and file size.

    Will throw exception if running into a file that is not readable.

    TODO: We should probably do the whole enumeration of sources and what will
    happen to those files first so we don't need to do that again when we import
    stuff.
    """
    source_files = []
    for root, _, files in os.walk(source):
        for file in files:
            file = Path(root) / file
            if not os.path.isfile(file):
                next
            if not os.access(file,os.R_OK):
                logger.error(f"Backup: File {file} isn't readable.")
                raise IOError(f"File {file} isn't readable")
            f_info = (file,os.path.getsize(file))
            source_files.append(f_info)
    return source_files

def human_size(size:int) -> str:
    """Return `size` byte count as a human-friendly value.
    
    FIXME: There's python_utils.converters.scale_1024() too? (python_utils is an
    indirect pypi requirement from progressbar2)"""
    if size > 1024*1024*1024:
        c = size / (1024*1024*1024)
        return f"{c:.1f} GiB"
    elif size > 1024*1024:
        c = size / (1024*1024)
        return f"{c:.1f} MiB"
    elif size > 1024:
        c = size / (1024)
        return f"{c:.1f} KiB"
    else:
        return f"{size} Bytes"
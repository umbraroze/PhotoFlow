#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2025,2026 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import os
from pathlib import Path
import logging
from zipfile import ZipFile

import py7zr
from dazzle import *
from rich import print
from rich.progress import Progress, SpinnerColumn, FileSizeColumn, TotalFileSizeColumn
from configuration import Configuration

logger = logging.getLogger(__name__)

###### Creating backup archives ##########################################

def archive(source:Path, target:Path):
    """Archive all files under `source` to 7-Zip file `target`.

    TODO: This should probably be a bit more elegant. Yet, since this
    part of the process can't really be made parallel, expressing these
    as photo_processing.Task isn't really feasible. So this is
    really just a helper function at this point.
    """
    backup_source_files = enumerate_source(source)
    total_size = total_source_size(backup_source_files)
    logger.info(f"Backing up {source} to {target}.")
    with py7zr.SevenZipFile(target, 'w') as output_archive, \
        Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            ' | ',
            FileSizeColumn(),
            '/',
            TotalFileSizeColumn()
        ) as bar:
        bar_task = bar.add_task("[yellow]Backing up...", total=total_size)
        for file, size in backup_source_files:
            rel_file = file.relative_to(source)
            logger.info(f"Backing up: {rel_file}")
            logger.debug(f"Full path {file}, size {size} bytes")
            print(f"Backing up: {rel_file}")
            output_archive.write(file, rel_file)
            bar.update(bar_task,advance=size)
    arc_size = os.path.getsize(target)
    ratio = (arc_size / total_size) * 100
    report = f"{len(backup_source_files)} files, " + \
          f"{human_size(total_size)} bytes, " + \
          f"{human_size(arc_size)} compressed ({ratio:.2f}% of original))"
    logger.info(f"Archival complete. {report}")
    success(f"Archival complete. {report}")

###### Unarchiving task ##################################################

def unpack_all(configuration:Configuration):
    """Unarchive all .zip and .7z archives in the target card, per given configuration."""

    # Total count of unpacked files
    total_count = 0

    # Sanity checks before proceeding
    if not configuration.is_cloud_source():
        logger.error(f"Unpack all: {configuration.camera} is not a cloud source")
        die(f"{configuration.camera} is not a cloud source")

    # Print the configuration
    print_boxed_text("UNPACK")
    print(f" - Camera: {configuration.camera}")
    print(f" - Cloud drive: :cloud: {configuration.card}")
    if configuration.dry_run:
        print(" - Dry run")
    if configuration.leave_originals:
        print(" - Leave originals")
    if configuration.overwrite_target:
        print(" - Overwrite target files")
    print()

    # Go over each source folder
    for source in configuration.get_source_folders():
        print(f"Source folder: {source}")
        if not source.is_dir():
            logger.error(f"Unarchive all in {source} failed: not a directory")
            die(f"Unarchive all in {source} failed: not a directory")
        for file in source.iterdir():
            if not file.suffix in ['.7z','.zip']:
                continue
            if file.suffix == '.7z':
                die("7-zip files unpacking is unimplemented")
            print(f"Unarchive file: {file}")
            with (ZipFile(file,'r') as archive_file,
                  Progress(SpinnerColumn(),*Progress.get_default_columns()) as bar):
                bar_task = bar.add_task("[white]Unpacking...",
                                        total=len(archive_file.filelist))
                for entry in archive_file.filelist:
                    # The target path. NB: only the filename is used, the preceding path
                    # in the original archive file's path is ignored.
                    out_path = source / Path(entry.filename)
                    # Skip if the target file exists
                    if out_path.exists():
                        skip_warn(f"Target file {out_path} already exists")
                        logger.warning(f"Target file {out_path} already exists, skipped")
                        bar.update(bar_task, advance=1)
                        continue
                    if not configuration.dry_run:
                        archive_file.extract(entry, source)
                        print(f":white_check_mark-emoji: Extracted {out_path}")
                        logger.debug(f"Unpacked {out_path}")
                        total_count = total_count + 1
                    else:
                        print(f":cross_mark_button-emoji: [yellow]Skipped: {out_path}[/yellow] (Dry run)")
                        logger.debug(f"Dry run: would have unpacked {out_path}")
                    bar.update(bar_task,advance=1)
            if not (configuration.leave_originals or configuration.dry_run):
                os.unlink(file)
                logger.info(f"Deleted successfully unpacked file {file}")
            else:
                logger.debug(f"Didn't delete the original")
    if total_count > 0:
        success(f"{total_count} files unpacked in total")
        logger.info(f"{total_count} files unpacked in total")

###### Archival-related utility functions ################################

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

    Will throw exception if running into a file that is not readable."""

    # TODO: We should probably do the whole enumeration of sources and what will
    # happen to those files first so we don't need to do that again when we import
    # stuff.

    source_files = []
    for root, _, files in os.walk(source):
        for file in files:
            file = Path(root) / file
            if not os.path.isfile(file):
                continue
            if not os.access(file,os.R_OK):
                logger.error(f"Backup: File {file} isn't readable.")
                raise IOError(f"File {file} isn't readable")
            f_info = (file,os.path.getsize(file))
            source_files.append(f_info)
    return source_files

def human_size(size:int) -> str:
    """Return `size` byte count as a human-friendly value."""
    
    # TODO: There's python_utils.converters.scale_1024() too?
    # (Might need to add python_utils as an explicit requirement though)
    if size > 1024*1024*1024:
        c = size / (1024*1024*1024)
        return f"{c:.1f} GiB"
    elif size > 1024*1024:
        c = size / (1024*1024)
        return f"{c:.1f} MiB"
    elif size > 1024:
        c = size / 1024
        return f"{c:.1f} KiB"
    else:
        return f"{size} Bytes"
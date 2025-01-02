#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import os, sys
import datetime
from pathlib import Path
import exiv2
from dazzle import *
from configuration import Configuration
from dataclasses import dataclass
import time
from enum import Enum
import logging
import subprocess
import shutil

logger = logging.getLogger(__name__)

###### Photo processing task #############################################

@dataclass
class Task:
    class Status(Enum):
        UNKNOWN = 0
        READY = 1
        RUNNING = 2
        DONE = 3
        SKIPPED = 4
        FAILURE = 5
    status:Status = Status.UNKNOWN
    start_time:time = None
    end_time:time = None
    total_time:float = None
    def _execute(self):
        raise RuntimeError("This task needs to be subclassed.") # More elegant way of handling this?
    def execute(self):
        """Perform the task. Will perform the timekeeping for the task and
        call the _execute method in subclass for the """
        self.start_time = time.time()
        self._execute()
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time

# TODO: Ideally, the backup task should use the appropriate 7zip library (py7zr) for this task.
@dataclass
class BackupTask(Task):
    source: Path = None
    target: Path = None
    sevenzip_path: Path = None
    dry_run:bool = False
    def __init__(self,configuration:Configuration):
        self.dry_run = configuration.dry_run
        if configuration.skip_backup:
            self.dry_run = True
        self.target = configuration.backup_path / Path(f"{configuration.camera}_{configuration.date_to_filename()}.7z")
        self.source = configuration.source_path
        self.sevenzip_path = configuration.sevenzip_path
    def _execute(self):
        if not self.dry_run:
            logger.info(f"Start backup: {self.source} to {self.target}")
            subprocess.run([self.sevenzip_path,'a','-t7z', '-r', self.target, self.source])
            # TODO: Error checking and status fudging.
            self.status = Task.Status.DONE
        else:
            logger.info(f"Backup skipped (would have archived {self.source} to {self.target})")
            print(f"{ICON_SKIP} Backup skipped.")
            self.status = Task.Status.SKIPPED

@dataclass
class MoveTask(Task):
    """Task representing image moving or conversion. Keeps track of the
    state of the process and stats."""

    source_file:Path = None
    target_file:Path = None
    file_type:str = None
    convert:bool = False
    dry_run:bool = False
    skip_import:bool = False
    leave_originals:bool = False
    dnglab_path:Path = None
    dnglab_flags:list = None
    def __init__(self,configuration:Configuration,source_file:Path,target_file:Path):
        # Note: configuration is only read, not stored.
        # TODO: Is it really such a bad thing not to store the configuration locally?
        self.source_file = source_file
        self.target_file = target_file
        self.file_type = identify_file(source_file)
        self.convert = configuration.is_converson_needed(source_file)
        self.skip_import = configuration.skip_import
        self.dry_run = configuration.dry_run
        self.leave_originals = configuration.leave_originals
        if self.convert:
            self.target_file = dng_suffix_for(self.target_file)
        self.status = Task.Status.READY
        self.dnglab_path = configuration.dnglab_path
        self.dnglab_flags = configuration.dnglab_flags

    def _move(self):
        """Will either move the file to target folder, or copy it,
        depending on whether we want to leave the originals."""
        # TODO: Error checking?
        if self.leave_originals:                
            shutil.copy(self.source_file,self.target_file)
            logger.info(f"Copied: {self.source_file} to {self.target_file}")
        else:
            shutil.move(self.source_file,self.target_file)
            logger.info(f"Moved: {self.source_file} to {self.target_file}")
        print(f"{self.source_file} {ICON_TO}  {self.target_file}")
        self.status = Task.Status.DONE

    def _convert(self):
        """Convert the raw file using dnglab and remove the original
        (if desired)."""
        print(f"Convert: {self.source_file} {ICON_TO}  {self.target_file}")
        logger.info(f"Converting: {self.source_file} to {self.target_file}")
        self.status = Task.Status.RUNNING

        if self.target_file.exists():
            logger.info(f"{self.source_file} skipped, {self.target_file} exists.")
            print(f"{ICON_SKIP}  {self.source_file}: Target file {self.target_file} exists. Skipped.")
            self.status = Task.Status.SKIPPED
            return

        if self.dnglab_flags is not None:
            cmd = [self.dnglab_path,'convert']
            cmd.extend(self.dnglab_flags)
            cmd.append(self.source_file)
            cmd.append(self.target_file)
        else:
            cmd = [self.dnglab_path,'convert',self.source_file,self.target_file]
        logger.info(f"Convert job: {cmd}")
        try:
            result = subprocess.run(cmd,capture_output=True,check=True)
            try:
                str(result.stdout).index("Converted 1/1 files")
                run_successfully = True
            except ValueError:
                logger.error(f"Conversion failed, dnglab reported no conversion, "+
                             f"return code {result.returncode} - "+
                             f"stdout: {result.stdout} stderr: {result.stderr}")
                print(f"{ICON_WARN}  dnglab reported no conversion took place.")
                run_successfully = False
                self.status = Task.Status.FAILURE
        except subprocess.CalledProcessError:
            logger.error(f"Conversion failed with return code {result.returncode} - "+
                         f"stdout: {result.stdout} stderr: {result.stderr}")
            print(f"{ICON_WARN} Error {result.returncode} with conversion.")
            run_successfully = False
            self.status = Task.Status.FAILURE
        # If we failed to convert, delete the target file.
        if not run_successfully:
            os.unlink(self.target_file)
        # Delete source file if we were successful and we actually want it
        if run_successfully and not self.leave_originals:
            os.unlink(self.source_file)
        if self.status == Task.Status.RUNNING:
            self.status = Task.Status.DONE

    def _execute(self):
        if self.skip_import or self.dry_run:
            logger.info(f"Skipped: {self.source_file} to {self.target_file}")
            print(f"{ICON_SKIP} Skipped: {self.source_file} to {self.target_file}")
            self.status = Task.Status.SKIPPED
            return
        # Create target folder if it doesn't exist
        if not self.target_file.parent.exists():
            self.target_file.parent.mkdir(parents=True,exist_ok=True)
            logger.info(f"Created directory {self.target_file.parent}")
        # We handle the file. Finally.
        if not self.convert:
            # Move or copy the file.
            self._move()
        else:
            self._convert()
        # TODO: Further error checking/reporting here?
    def print_status(self):
        print(f"{self.source_file}\n  Format: {self.file_type} * Convert: {self.convert} * Dry run: {self.dry_run}\n  {ICON_TO}  {self.target_file}")

def dng_suffix_for(file:Path) -> Path:
        return file.parent / Path(file.stem + ".DNG")

def identify_file(file:Path) -> str:
    """Returns a normalised file identification."""
    s = file.suffix[1:].upper()
    match s:
        case 'JPG' | 'JPEG' | 'JFIF':
            return 'JPEG'
        case _:
            return s

def read_date(file:Path) -> datetime.datetime:
    """Reads the date for the specified image file. Will try to grab the
    original date from EXIF, or failing that, file modification time."""
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file))
    try:
        img = exiv2.ImageFactory.open(str(file))
    except exiv2.Exiv2Error:
        return None
    img.readMetadata()
    img_data = img.exifData()
    date_raw = img_data["Exif.Photo.DateTimeOriginal"].getValue()
    if date_raw is None:
        date = mtime
    else:
        try:
            date = datetime.datetime.strptime(str(date_raw),'%Y:%m:%d %H:%M:%S')
        except ValueError:
            date = mtime
    return date

class ImportQueue:
    """The main photo import queue."""
    _config:Configuration = None
    _jobs:list = []
    _target_directories:dict = {}

    def __init__(self,configuration:Configuration):
        """Create the import queue."""
        self._config = configuration

    def populate(self):
        """Populates the job queue. Will walk the source folder, create tasks, and add them to the queue."""
        source_dirs = self._config.get_source_folders()
        for source_path in source_dirs:
            print(f"Processing source path: {source_path}")
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    # Get the file's full name
                    fqfile = Path(root) / file
                    # Skip non-files
                    if not os.path.isfile(fqfile):
                        continue
                    # Is this one of the files we want to ignore?
                    if self._config.ignore is not None:
                        ign = False
                        for ignored in self._config.ignore:
                            if str(file) == ignored:
                                ign = True
                        if ign == True:
                            logger.info(f"{fqfile} ignored")
                            print(f"{ICON_SKIP} {fqfile} ignored")
                            continue
                    # OK, we're cool, continuing
                    date = read_date(fqfile)
                    if date is None:
                        logger.warning(f"File {file} cannot be read by Exiv2. Skipping.")
                        print(f"{ICON_SKIP} Date for {file} cannot be read. Skipping.")
                        continue
                    datef = date.strftime("%Y-%m-%d")
                    target_dir = self._config.target_path / self._config.date_to_path(date)
                    target_file = target_dir / file
                    if datef not in self._target_directories:
                        self._target_directories[datef] = {
                            'directory': target_dir,
                            'count': 0
                        }
                    else:
                        self._target_directories[datef]['count'] += 1
                    task = MoveTask(self._config,fqfile,target_file)
                    #task.print_status() # DEBUG
                    self._jobs.append(task)

    def print_status(self):
        """Print out the current status of job queue and statistics."""
        job_cnt = len(self._jobs)
        status_cnt = {}
        for job in self._jobs:
            if job.status in status_cnt:
                status_cnt[job.status] += 1
            else:
                status_cnt[job.status] = 1
        print(f"{job_cnt} jobs queued.")
        print("Statuses:")
        for s in status_cnt.keys():
            print(f" - {s}: {status_cnt[s]}")
        print("Day summary:")
        for d in self._target_directories.keys():
            print(f" - {d}, {self._target_directories[d]['count']} images")

    def run(self):
        """Run all of the tasks in the queue."""
        for job in self._jobs:
            job.execute()

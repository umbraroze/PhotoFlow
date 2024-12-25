import os, sys
import datetime
from pathlib import Path
import exiv2
from dazzle import *
from configuration import Configuration

###### Photo processing task #############################################

class Task:
    """Task representing image moving or conversion. Keeps track of the
    state of the process and stats."""
    source_file:Path = None
    target_file:Path = None
    def __init__(self,source_file:Path,target_file:Path):
        self.source_file = source_file
        self.target_file = target_file

def read_date(file:Path) -> datetime.datetime:
    """Reads the date for the specified image file. Will try to grab the
    original date from EXIF, or failing that, file modification time."""
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file))
    try:
        img = exiv2.ImageFactory.open(str(file))
    except exiv2.Exiv2Error:
        print(f"File {file} cannot be read by Exiv2. Skipping.")
        sys.exit(1)
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
                    # OK, we're cool, continuing
                    date = read_date(fqfile)
                    datef = date.strftime("%Y-%m-%d")
                    target_dir = self._config.target_path / self._config.date_to_path(date)
                    # TODO: Check file conversion here
                    target_file = target_dir / file
                    if datef not in self._target_directories:
                        self._target_directories[datef] = {
                            'directory': target_dir,
                            'count': 0
                        }
                    else:
                        self._target_directories[datef]['count'] += 1
                    print(f"{fqfile}\n  ({datef})\n  {ICON_TO}  {target_file}")

    def print_status(self):
        """Print out the current status of job queue and statistics."""
        job_cnt = len(self._jobs)
        pending_cnt = 0
        done_cnt = 0
        print(f"Import queue status: {job_cnt} jobs queued, {pending_cnt} pending, {done_cnt} done.")
        print("Day summary:")
        for d in self._target_directories.keys():
            print(f" - {d}, {self._target_directories[d]['count']} images")


#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import os, sys, platform
import re
import argparse
import datetime
import tomllib
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
import logging
from dazzle import *

logger = logging.getLogger(__name__)

###### Configuration #####################################################

# TODO: Allow pulling logfile path from an environment variable.
# TODO: Or, just use tempfile library's NamedTempfile.
#       https://docs.python.org/3/library/tempfile.html
# TODO: Maybe default to home directory?
def logfile_path() -> Path:
    return Path('photo_importinator.log')

@dataclass
class Configuration:
    """Photo Importinator's configuration."""

    class Action(Enum):
        IMPORT = 0
        LIST_CAMERAS_AND_TARGETS = 1
        LIST_RUNNING_STATS = 2
        PURGE_LOG_FILE = 3
        PURGE_RUNNING_STATS = 4

    action: Action = Action.IMPORT
    _config: dict = None
    configuration_file: Path = None
    target: str = None
    card: str = None
    card_label: str = None
    date: datetime = None
    skip_import: bool = False
    skip_backup: bool = False
    dry_run: bool = False
    leave_originals: bool = False
    overwrite_target: bool = False
    camera: str = None
    source_path: Path = None
    target_path: Path = None
    folder_structure: str = None
    ignore: list[str] = None
    convert_raw: list[str] = None
    backup_path: Path = None
    dnglab_path: Path = None
    dnglab_flags: list = None

    def is_valid_config(self) -> bool:
        """Returns true if the current configuration contains no problematic
        settings."""
        # TODO: Other conditions here
        if self.camera is None:
            return False
        if self.source_path is None:
            return False
        if self.target_path is None:
            return False
        if self.folder_structure is None:
            return False
        if self.backup_path is None:
            return False
        return True

    @staticmethod
    def default_configuration_path_for(file:Path) -> Path:
        """Returns the path for a specified file in the default configuration directory."""
        if platform.system() == 'Windows':
            return Path.home() / 'AppData/Local/photo_importinator' / file
        else:
            try:
                return Path(os.environ['XDG_CONFIG_HOME']) / "photo_importinator" / file
            except KeyError:
                return Path.home() / '.config/photo_importinator' / file
    
    @staticmethod
    def default_configuration_path() -> Path:
        """Returns the default configuration file location."""
        return Configuration.default_configuration_path_for('photo_importinator_config.toml')
    
    @staticmethod
    def default_running_stats_path() -> Path:
        """Returns the default running stats storage location."""
        return Configuration.default_configuration_path_for('photo_importinator_running_stats.db')

    def running_stats_path(self) -> Path:
        # TODO: Make this customisable in the settings.
        return Configuration.default_running_stats_path()

    def date_to_filename(self) -> str:
        """Returns the desired datestamp in ISO format suitable for file names."""
        return self.date.strftime('%Y%m%d')
    def date_to_str(self) -> str:
        """Returns the desired datestamp in ISO format."""
        return self.date.strftime('%Y-%m-%d')
    def date_to_path(self,date:datetime) -> Path:
        """Returns the directory structure for the given day."""
        d = date.date()
        return Path(self.folder_structure.format(year=d.year,month=d.month,day=d.day))
    def date_to_path_demo(self) -> Path:
        """Returns the target path, with date fields substituted with
        YYYY-MM-DD for demonstration purposes."""
        # Chop off the f-string formatting directives, just leaving the variable names
        m = re.sub(pattern=r'\{(.*?):(.*?)\}',repl=r'{\1}', string=self.folder_structure)
        return self.target_path / Path(m.format(year='YYYY',month='MM',day='DD'))

    def parse_command_line(self):
        """Parses script command line arguments for Photo Importinator."""
        parser = argparse.ArgumentParser(
            prog='photo_importinator',
            description='Move or convert photos from SD card or cloud to your photo server.')        
        subparsers = parser.add_subparsers(dest='command')

        # Global arguments.
        parser.add_argument('-C','--configuration-file',default=Configuration.default_configuration_path(),
                            help=f"specify configuration file (default: {Configuration.default_configuration_path()})")

        # Import subcommand and its arguments
        parser_import_cmd = subparsers.add_parser('import',aliases=['i'],help='import from the specified camera.')

        # Target and destination specifications
        parser_import_cmd.add_argument('-T','--target',default=None,help="specify target device (default: as set in config)")
        parser_import_cmd.add_argument('-c','--card',default=None,help='card path/device (default: as per camera settings in config)')
        parser_import_cmd.add_argument('--date',
                                       type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(),
                                       default=datetime.date.today(),
                                       help="archive date stamp, YYYY-mm-dd (default: current date)")
        # Skipping switches
        parser_import_cmd.add_argument('--skip-backup',action='store_true',help="skip backup phase")
        parser_import_cmd.add_argument('--skip-import',action='store_true',help="skip the final import phase")
        parser_import_cmd.add_argument('--dry-run',action='store_true',help="do nothing, except explain what would be done")
        parser_import_cmd.add_argument('--leave-originals',action='store_true',help="leave original files intact")
        parser_import_cmd.add_argument('--overwrite-target',action='store_true',help="overwrite target files if found (default: just skip)")
        
        # Camera name as the last positional argument for the import command.
        parser_import_cmd.add_argument('camera',default=None,nargs='?',help="camera name.")

        # Camera/target list subcommand and its arguments
        parser_list_cmd = subparsers.add_parser('list',help='list cameras and targets.')

        # Running stats subcommand and its arguments
        parser_runningstats_cmd = subparsers.add_parser('runningstats',help='list running statistics of previous imports.')

        # Purge command
        purge_cmd = subparsers.add_parser('purge',help='Delete log file or running stats.')
        purge_cmd.add_argument('to_be_purged',default=None,nargs='?',help="'log' or 'runningstats'")

        # Done with the setup! Parse the arguments!
        args = parser.parse_args()

        # Populate the configuration object with parsed values
        self.configuration_file=args.configuration_file

        # Find out what our subcommand is, set the relevant arguments.
        if args.command in ['import','i']:
            self.action = Configuration.Action.IMPORT
            self.target=args.target
            self.card=args.card
            self.date=args.date
            self.skip_backup=args.skip_backup
            self.skip_import=args.skip_import
            self.dry_run=args.dry_run
            self.leave_originals=args.leave_originals
            self.camera=args.camera
        elif args.command in ['list']:
            self.action = Configuration.Action.LIST_CAMERAS_AND_TARGETS
        elif args.command in ['runningstats']:
            self.action = Configuration.Action.LIST_RUNNING_STATS
        elif args.command in ['purge']:
            if args.to_be_purged is None:
                die("Unspecified purge target (must be 'log' or 'runningstats')")
            elif args.to_be_purged == 'log':
                self.action = Configuration.Action.PURGE_LOG_FILE
            elif args.to_be_purged == 'runningstats':
                self.action = Configuration.Action.PURGE_RUNNING_STATS
            else:
                die(f"Unknown purge target {args.to_be_purged}")
        else:
            die(f"Unknown command {args.command}")

    def read_configuration(self) -> dict:
        if not os.path.exists(self.configuration_file):
            logger.error("Configuration file {self.configuration_file} does not exist.")
            die(f"Configuration file {self.configuration_file} does not exist.")
        logger.info(f"Parsing configuration file {self.configuration_file}")
        with open(self.configuration_file,'rb') as f:
            self._config = tomllib.load(f)

    def parse_configuration(self):
        """Parses the configuration file, setting the relevant
        fields. Will not overwrite the values if specified on command line.
        Must only be called after command line arguments are parsed and configuration file is read."""
        
        # No target? Then figure out the default target
        if self.target is None:
            try:
                self.target = self._config['Target']['default']
                if self.target == 'None':
                    self.target = None
            except KeyError:
                logger.error("Target not specified.")
                die("Target was not specified on the command line, and no default target is set in the configuration file.")
        # Do we still not know where the target is?
        if self.target is None:
            logger.error("Target isn't known.")
            die("Target isn't known.")
        # OK, we have a target - is that valid?
        if self.target not in self._config['Target']:
            logger.error(f"Target {self.target} unknown.")
            die(f"Target {self.target} not specified in the configuration file.")
        try:
            self.target_path = Path(self._config['Target'][self.target]['path'])
        except KeyError:
            logger.error(f"Target {self.target}: No path")
            die(f"Target {self.target} doesn't specify the destination path.")
        try:
            self.folder_structure = self._config['Target'][self.target]['folder_structure']
        except KeyError:
            logger.error(f"Target {self.target}: No folder_structure.")
            die(f"Target {self.target} doesn't specify folder structure.")
        if self.camera is None and ('default' not in self._config['Cameras'] or self._config['Cameras']['default'] == 'None'):
            logger.error("Camera unspecified.")
            die("Camera was not specified on the command line, and no default camera is set in the configuration file.")
        if self.camera not in self._config['Cameras']:
            logger.error("Camera {self.camera} unknown.")
            die(f"Camera {self.camera} not specified in the configuration file.")
        camera_details = self._config['Cameras'][self.camera]
        if self.card is None and 'card' in camera_details:
            self.card = camera_details['card']
        if self.card is None:
            logger.error("Camera {self.camera}: No card.")
            die(f"Camera {self.camera} has no default card and no card has been specified.")
        if 'card_label' in camera_details:
            self.card_label = camera_details['card_label']
        if 'ignore' in camera_details:
            self.ignore = camera_details['ignore']
        if 'convert_raw' in camera_details:
            self.convert_raw = camera_details['convert_raw']
        # The directory where backups are stored
        try:
            self.backup_path = Path(self._config['Target'][self.target]['backup_path'])
        except KeyError:
            logger.error("Target {self.target}: No backup_path.")
            die("Backup path not specified for target {self.target} in the configuration file.")
        # Location of dnglab executable and the command line parameters
        try:
            self.dnglab_path = Path(self._config['Conversion']['dnglab_path'])
        except KeyError:
            self.dnglab_path = 'dnglab'
        try:
            self.dnglab_flags = self._config['Conversion']['convert_flags']
        except KeyError:
            self.dnglab_flags = None

    def find_source_path_card(self):
        # TODO: first check that the card is inserted (needs OS trickery?)
        self.source_path = Path(self.card) / '/DCIM'
        if not self.source_path.exists():
            logger.error(f"Source card {self.card} does not have a DCIM folder")
            die(f"Source card {self.card} does not have a DCIM folder.")

    def find_source_path_cloud(self):
        cloud_path = Path(self._config['Cloud'][self.card])
        # Is it a path relative to home?
        if os.path.exists(Path.home() / cloud_path):
            self.source_path = Path.home() / cloud_path
        # Maybe it's an absolute path or relative to working directory?
        elif os.path.exists(cloud_path):
            self.source_path = cloud_path
        # Otherwise, I don't know what it is
        else:
            logger.error("Cloud source {self.card} folder {cloud_path} doesn't exist.")
            die(f"The local sync folder of cloud service {self.card}, located at {cloud_path}, cannot be found.")

    def is_cloud_source(self):
        """Return True if the source is a cloud drive (i.e. found in Cloud
        section of sources)"""
        return (self.card in self._config['Cloud'])

    def find_source_path(self):
        """Find and set the source path based on selected source type."""
        if self.is_cloud_source():
            self.find_source_path_cloud()    
        else:
            self.find_source_path_card()

    def get_source_folders(self) -> list:
        if self.is_cloud_source():
            return [self.source_path]
        else:
            # Get all subdirectories of .source_path and prepend the actual source path.
            # Because os.listdir() doesn't return the prefixes.
            # TODO: Does this need more filtering? (Doesn't seem to be picking . and .. etc)
            return map(lambda x: self.source_path / x, os.listdir(self.source_path))

    def parse(self):
        """Read configuration. Do all of the relevant steps to ensure
        configuration is set correctly for the actual processing."""
        self.parse_command_line()
        self.read_configuration()
        if self.action == Configuration.Action.IMPORT:
            self.parse_configuration()
            self.find_source_path()

    def validate(self):
        if not self.is_valid_config():
            logger.error("Configuration is not valid (something slipped through?)")
            die("Configuration is not valid")

    def is_converson_needed(self,path:Path) -> bool:
        """Will check if conversion is needed for a given file. Will return
        True if the file suffix matches any of the suffixes given in
        chosen camera's convert_raw list."""
        if self.convert_raw is None or len(self.convert_raw) < 1:
            return False
        suffix = path.suffix.upper()
        for s in self.convert_raw:
            if s == suffix:
                return True
        return False

    def list_cameras_and_targets(self):
        """Prints out valid cameras and targets. Only requres configuration
        file to be parsed."""
        try:
            default_camera = self._config['Cameras']['default']
        except KeyError:
            default_camera = 'None'
        try:
            default_target = self._config['Target']['default']
        except KeyError:
            default_target = 'None'
        print("\nCameras:")
        for c in self._config['Cameras']:
            if c != 'default':
                if c == default_camera:
                    print(f" - {c} (default)")
                else:
                    print(f" - {c}")
        if default_camera == 'None':
            print("   No default camera specified.")
        print("\nTargets:")
        for t in self._config['Target']:
            if t != 'default':
                if t == default_target:
                    print(f" - {t} (default)")
                else:
                    print(f" - {t}")
        if default_target == 'None':
            print("   No default target specified.")
        logger.info("List of cameras and targets requested. Exiting.")

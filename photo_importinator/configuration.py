
import os, sys, platform
import re
import argparse
import datetime
import tomllib
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

###### Configuration #####################################################

@dataclass
class Configuration:
    """Photo Importinator's configuration."""

    class Action(Enum):
        IMPORT = 0
        LIST_CAMERAS_AND_TARGETS = 1

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
    camera: str = None
    source_path: Path = None
    target_path: Path = None
    folder_structure: str = None
    ignore: list[str] = None
    convert_raw: list[str] = None
    backup_path: Path = None

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
    def default_configuration_path() -> Path:
        """Returns the default configuration file location."""
        if platform.system() == 'Windows':
            return Path.home() / 'AppData/Local/photo_importinator/photo_importinator_config.toml'
        else:
            try:
                return Path(os.environ['XDG_CONFIG_HOME']) / "photo_importinator/photo_importinator_config.toml"
            except KeyError:
                return Path.home() / '.config/photo_importinator/photo_importinator_config.toml'

    def date_to_str(self) -> str:
        return self.date.date.strftime('%Y-%m-%d')
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
        parser.add_argument('-C','--configuration-file',default=Configuration.default_configuration_path(),
                            help=f"specify configuration file (default: {Configuration.default_configuration_path()})")
        # Target and destination specifications
        parser.add_argument('-T','--target',default=None,help="specify target device (default: as set in config)")
        parser.add_argument('-c','--card',default=None,help='card path/device (default: as per camera settings in config)')
        parser.add_argument('--date',
                            type=lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(),
                            default=datetime.date.today(),
                            help="archive date stamp, YYYY-mm-dd (default: current date)")
        # Skipping switches
        parser.add_argument('--skip-backup',action='store_true',help="skip backup phase")
        parser.add_argument('--skip-import',action='store_true',help="skip the final import phase")
        parser.add_argument('--dry-run',action='store_true',help="do nothing, except explain what would be done")
        parser.add_argument('--leave-originals',action='store_true',help="leave original files intact")
        # Camera
        parser.add_argument('camera',default=None,nargs='?',help="camera name.")
        # Done with setup, parse the arguments.
        args = parser.parse_args()
        # Populate the configuration object with parsed values
        self.configuration_file=args.configuration_file
        self.target=args.target
        self.card=args.card
        self.date=args.date
        self.skip_backup=args.skip_backup
        self.skip_import=args.skip_import
        self.dry_run=args.dry_run
        self.leave_originals=args.leave_originals
        self.camera=args.camera
        if args.camera is not None and args.camera.lower() == 'list':
            self.action = Configuration.Action.LIST_CAMERAS_AND_TARGETS

    def parse_config_file(self):
        """Reads and parses the configuration file, setting the relevant
        fields. Will not overwrite the values if specified on command line.
        Must only be called after command line arguments are parsed."""
        if not os.path.exists(self.configuration_file):
            sys.exit(f"Configuration file {self.configuration_file} does not exist.")
        with open(self.configuration_file,'rb') as f:
            self._config = tomllib.load(f)
        if self.action == Configuration.Action.LIST_CAMERAS_AND_TARGETS:
            self.list_cameras_and_targets()
            sys.exit(0)
        if self.target is None:
            try:
                self.target = self._config['Target']['default']
                if self.target == 'None':
                    self.target = None
            except KeyError:
                sys.exit("Target was not specified on the command line, and no default target is set in the configuration file.")
        if self.target is None:
            sys.exit("Target isn't known.")
        if self.target not in self._config['Target']:
            sys.exit(f"Target {self.target} not specified in the configuration file.")
        try:
            self.target_path = Path(self._config['Target'][self.target]['path'])
        except KeyError:
            sys.exit(f"Target {self.target} doesn't specify the destination path.")
        try:
            self.folder_structure = self._config['Target'][self.target]['folder_structure']
        except KeyError:
            sys.exit(f"Target {self.target} doesn't specify folder structure.")
        if self.camera is None and ('default' not in self._config['Cameras'] or self._config['Cameras']['default'] == 'None'):
            sys.exit("Camera was not specified on the command line, and no default camera is set in the configuration file.")
        if self.camera not in self._config['Cameras']:
            sys.exit(f"Camera {self.camera} not specified in the configuration file.")
        camera_details = self._config['Cameras'][self.camera]
        if self.card is None and 'card' in camera_details:
            self.card = camera_details['card']
        if self.card is None:
            sys.exit(f"Camera {self.camera} has no default card and no card has been specified.")
        if 'card_label' in camera_details:
            self.card_label = camera_details['card_label']
        if 'ignore' in camera_details:
            self.ignore = camera_details['ignore']
        if 'convert_raw' in camera_details:
            self.convert_raw = camera_details['convert_raw']
        try:
            self.backup_path = Path(self._config['Target'][self.target]['backup_path'])
        except KeyError:
            sys.exit("Backup path not specified for target {self.target} in the configuration file.")

    def find_source_path_card(self):
        raise RuntimeError("Unimplemented")

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
            print(f"The local sync folder of cloud service {self.card}, located at {cloud_path}, cannot be found.")
            sys.exit(1)

    def is_cloud_source(self):
        return (self.card in self._config['Cloud'])

    def find_source_path(self):
        if self.is_cloud_source():
            self.find_source_path_cloud()    
        else:
            self.find_source_path_card()

    def get_source_folders(self) -> list:
        if self.is_cloud_source():
            src = [self.source_path]
        else:
            print("get_source_folders unimplemented for cards")
            sys.exit(1)
        return src

    def parse(self):
        """Read configuration. Do all of the relevant steps to ensure
        configuration is set correctly for the actual processing."""
        self.parse_command_line()
        self.parse_config_file()
        self.find_source_path()

    def validate(self):
        if not self.is_valid_config():
            sys.exit("Configuration is not valid")

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


# https://docs.python.org/3/library/pathlib.html
import pathlib
import os, sys
import platform
import datetime
# https://docs.python.org/3/library/tomllib.html
import tomllib
# https://docs.python.org/3/library/argparse.html
import argparse
from dataclasses import dataclass

###### Configuration #####################################################

@dataclass
class Configuration:
    """Photo Importinator's configuration."""

    configuration_file: pathlib.Path = None
    target: str = None
    card: str = None
    card_label: str = None
    date: datetime = None
    skip_import: bool = False
    skip_backup: bool = False
    dry_run: bool = False
    camera: str = None
    target_path: pathlib.Path = None
    folder_structure: str = None
    ignore: list[str] = None
    convert_raw: list[str] = None

    def is_valid_config(self) -> bool:
        """Returns true if the current configuration contains no problematic
        settings."""
        # TODO: Other conditions here
        if self.camera == None:
            return False
        if self.target_path == None:
            return False
        if self.folder_structure == None:
            return False
        return True

    @staticmethod
    def default_configuration_path() -> pathlib.Path:
        """Returns the default configuration file location."""
        if platform.system() == 'Windows':
            return pathlib.Path.home() / 'AppData/Local/photo_importinator/photo_importinator_config.toml'
        else:
            try:
                return pathlib.Path(os.environ['XDG_CONFIG_HOME']) / "photo_importinator/photo_importinator_config.toml"
            except KeyError:
                return pathlib.Path.home() / '.config/photo_importinator/photo_importinator_config.toml'

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
        self.camera=args.camera

    def parse_config_file(self):
        """Reads and parses the configuration file, setting the relevant
        fields. Will not overwrite the values if specified on command line.
        Must only be called after command line arguments are parsed."""
        if not os.path.exists(self.configuration_file):
            sys.exit(f"Configuration file {self.configuration_file} does not exist.")
        with open(self.configuration_file,'rb') as f:
            conf_file = tomllib.load(f)
        if self.target == None:
            self.target = conf_file['Target']['default']
        if self.target == None:
            sys.exit("Target isn't known.")
        if self.target not in conf_file['Target']:
            sys.exit(f"Target {self.target} not specified in the configuration file.")
        self.target_path = pathlib.Path(conf_file['Target'][self.target]['path'])
        self.folder_structure = conf_file['Target'][self.target]['folder_structure']
        if self.camera == None and ('default' not in conf_file['Cameras'] or conf_file['Cameras']['default'] == 'None'):
            sys.exit("Camera was not specified on the command line, and no default camera is set configuration file.")
        if self.camera not in conf_file['Cameras']:
            sys.exit(f"Camera {self.camera} not specified in the configuration file.")
        camera_details = conf_file['Cameras'][self.camera]
        if self.card == None and 'card' in camera_details:
            self.card = camera_details['card']
        if 'card_label' in camera_details:
            self.card_label = camera_details['card_label']
        if 'ignore' in camera_details:
            self.ignore = camera_details['ignore']
        if 'convert_raw' in camera_details:
            self.convert_raw = camera_details['convert_raw']

    def parse(self):
        """Read configuration. Do all of the relevant steps to ensure
        configuration is set correctly for the actual processing."""
        self.parse_command_line()
        self.parse_config_file()

    def validate(self):
        if not self.is_valid_config():
            sys.exit("Configuration is not valid")

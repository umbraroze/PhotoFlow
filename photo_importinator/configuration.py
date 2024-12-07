
# https://docs.python.org/3/library/pathlib.html
import pathlib
import os
import platform
import datetime
# https://docs.python.org/3/library/tomllib.html
import tomllib
# https://docs.python.org/3/library/argparse.html
import argparse
from dataclasses import dataclass

###### Configuration #####################################################

class CLIOptions:
    """Parses script command line arguments for Photo Importinator."""
    @staticmethod
    def getopt():
        parser = argparse.ArgumentParser(
            prog='photo_importinator',
            description='Move or convert photos from SD card or cloud to your photo server.')
        parser.add_argument('-C','--configuration-file',default=Configuration.default_configuration_path(),
                            help=f"specify configuration file (default: {Configuration.default_configuration_path()})")
        # Target and destination specifications
        parser.add_argument('-T','--target',default=None,help="specify target device (default: as set in config)")
        parser.add_argument('-c','--card',help='card path/device (default: as per camera settings in config)')
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
        args = parser.parse_args()
        return args

class Configuration:
    """Photo Importinator's configuration."""

    @staticmethod
    def default_configuration_path() -> pathlib.Path:
        if platform.system() == 'Windows':
            return pathlib.Path.home() / 'AppData/Local/photo_importinator/photo_importinator_config.toml'
        else:
            try:
                return pathlib.Path(os.environ['XDG_CONFIG_HOME']) / "photo_importinator/photo_importinator_config.toml"
            except KeyError:
                return pathlib.Path.home() / '.config/photo_importinator/photo_importinator_config.toml'


    @dataclass
    class Camera:
        """Configuration for camera specific details."""
        card: str
        card_label: str
        ignore: list[str]
        convert_raw: list[str]


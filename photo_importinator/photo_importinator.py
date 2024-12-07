#!/usr/bin/python
#
# Photo Importinator III: This Time It's Python For Some Reason
#

# https://pypi.org/project/colorama/
import colorama

from configuration import Configuration

###### Main program ######################################################

configuration: Configuration = None

def main() -> int:
    """Photo Importinator main program."""
    global configuration
    
    # Initialise Colorama
    colorama.just_fix_windows_console()
    
    # Parse command line options and configuration file, do all of the
    # necessary sanity checks as you go.
    configuration = Configuration()
    configuration.parse()
    configuration.validate()

    # So here we are now.
    print(configuration)

    print(f"Settings file: {configuration.configuration_file}")
    print("Settings:")
    print(f"Camera:        {configuration.camera}")
    print(f"Card:          {configuration.card}")
    print(f"Backup folder: {configuration.backup_path}")
    print(f"Destination:   {configuration.date_to_path_demo()}")

    return 0

if __name__ == '__main__':
    main()

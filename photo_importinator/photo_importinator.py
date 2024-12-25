#!/usr/bin/python
#
# Photo Importinator III: This Time It's Python For Some Reason
#

import colorama

from configuration import Configuration
from dazzle import *
from photo_processing import *

###### Main program ######################################################

def main() -> int:
    """Photo Importinator main program."""
    
    # Initialise Colorama
    colorama.just_fix_windows_console()
    
    # Parse command line options and configuration file, do all of the
    # necessary sanity checks as you go.
    configuration = Configuration()
    configuration.parse()
    configuration.validate()

    # Print the banner and relevant settings
    print_boxed_text("PHOTO IMPORTINATOR")

    print_separator_line()
    print(f"Settings file: {configuration.configuration_file}")
    print(colorama.Style.BRIGHT+"Settings:"+colorama.Style.RESET_ALL)
    print(f"Camera:        {configuration.camera}")
    print(f"Card:          {configuration.card}")
    print(f"Backup folder: {configuration.backup_path}")
    print(f"Destination:   {configuration.date_to_path_demo()}")
    print_separator_line()

    # Wait for user confirmation
    try:
        print("If information isn't correct, press Ctrl+C to abort.")
        input("Press Return to continue: ")
    except KeyboardInterrupt:
        print("\nImport cancelled.")
        return 1

    print(f"File A {ICON_TO}  File B. {ICON_SKIP}  Skipped. {ICON_WARN}  Warning. {ICON_CLOUD}  Cloud.")

    queue = ImportQueue(configuration)
    queue.populate()
    queue.print_status()

    return 0

if __name__ == '__main__':
    main()

#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import colorama

from configuration import Configuration
from dazzle import *
from photo_processing import *


# TODO: More extensive use of logging facility.
# https://docs.python.org/3/library/logging.html
import logging
logger = logging.getLogger(__name__)

###### Main program ######################################################

def main() -> int:
    """Photo Importinator main program."""

    logging.basicConfig(filename='photo_importinator.log', level=logging.INFO)
    logger.info('Photo Importinator started.')

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
    print_separator_line()
    print(colorama.Style.BRIGHT+"Settings:"+colorama.Style.RESET_ALL)
    print(f"Camera:        {configuration.camera}")
    if configuration.is_cloud_source():
        print(f"Cloud drive:   {ICON_CLOUD} {configuration.card}")
    else:
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

    backuptask = BackupTask(configuration)
    backuptask.execute()

    queue = ImportQueue(configuration)
    queue.populate()
    queue.run()

    queue.print_status()

    logger.info('Photo Importinator finished normally.')

    return 0

if __name__ == '__main__':
    main()

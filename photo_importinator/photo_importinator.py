#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import colorama

from configuration import Configuration
from running_stats import RunningStats
from dazzle import *
from photo_processing import *


# TODO: More extensive use of logging facility.
# https://docs.python.org/3/library/logging.html
import logging
logger = logging.getLogger(__name__)

###### The import job ###################################################

def importinate(config:Configuration):
    # Print the banner and relevant settings
    print_boxed_text("PHOTO IMPORTINATOR")

    print_separator_line()
    print(f"Settings file: {config.configuration_file}")
    print_separator_line()
    print(colorama.Style.BRIGHT+"Settings:"+colorama.Style.RESET_ALL)
    print(f"Camera:        {config.camera}")
    if config.is_cloud_source():
        print(f"Cloud drive:   {ICON_CLOUD} {config.card}")
    else:
        print(f"Card:          {config.card}")
    print(f"Backup folder: {config.backup_path}")
    print(f"Destination:   {config.date_to_path_demo()}")
    print_separator_line()

    # Wait for user confirmation
    try:
        print("If information isn't correct, press Ctrl+C to abort.")
        input("Press Return to continue: ")
    except KeyboardInterrupt:
        print("\nImport cancelled.")
        return 1

    # Create and run the backup task.
    backuptask = BackupTask(config)
    backuptask.execute()

    # Create and run the import queue.
    queue = ImportQueue(config)
    queue.populate()
    queue.run()

    # Print out some final stats.
    queue.print_status()
    logger.debug('Import finished normally.')

###### Main program ######################################################

def main() -> int:
    """Photo Importinator main program."""

    logging.basicConfig(filename='photo_importinator.log', level=logging.INFO)
    logger.info('Photo Importinator started.')

    # Initialise Colorama
    colorama.just_fix_windows_console()
    
    # Parse command line options and configuration file, do all of the
    # necessary sanity checks as you go.
    config = Configuration()
    config.parse()
    # Handle subcommands. Depending on what we do we need to either have
    # a valid configuration or we must not actually validate the configuration.
    if config.action == Configuration.Action.IMPORT:
        # NOTE: NEED to validate config
        config.validate()
        importinate(config)
    elif config.action == Configuration.Action.LIST_CAMERAS_AND_TARGETS:
        # NOTE: MUST NOT validate config, actually.
        config.list_cameras_and_targets()
        sys.exit(0)
    elif config.action == Configuration.Action.LIST_RUNNING_STATS:
        running_stats = RunningStats(config)
        running_stats.list_all()
        sys.exit(0)

    return 0

if __name__ == '__main__':
    main()

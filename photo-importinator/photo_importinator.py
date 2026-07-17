#!/usr/bin/python
##########################################################################
# Photo Importinator III: This Time It's Python For Some Reason
##########################################################################
# (c) 2024,2025,2026 Rose Midford.
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.

import os, sys, time, datetime
from typing import Annotated
import typer
from pathlib import Path
from configuration import Configuration, logfile_path
from running_stats import RunningStats
from dazzle import *
from rich import print
from rich.table import Table
from photo_processing import *

import logging
logger = logging.getLogger(__name__)

###### LOG SETTINGS #####################################################

# Useful values: logging.INFO or logging.DEBUG
log_level = logging.INFO
delete_old_log = True

###### APPLICATION ######################################################

# TODO: Stuff from configuration.parse_command_line() should go here.

app = typer.Typer(name="photo_importinator",
                  help="Move or convert photos from SD card or cloud to your photo server.",
                  no_args_is_help=True)
config = Configuration()

@app.command(name="import",
             help="Import from the specified camera.")
def command_import(
    camera:
        Annotated[str,
            typer.Argument(help="Camera name.")],
    configuration_file:
        Annotated[Path,
            typer.Option("--configuration-file","-C",
                help="Configuration file.")] =
            Configuration.default_configuration_path(),
    target:
        Annotated[str,
            typer.Option("--target","-T",
                help="Target to import to. Default specified in configuration file.")]
            = None,
    card:
        Annotated[str,
            typer.Option("--card","-c",
                help="Card to import from. Default specified in configuration file.")]
            = None,
    date:
        Annotated[datetime.datetime,
            typer.Option(formats=['%Y-%m-%d'],
                help="Date for the backup file name. (Time portion is ignored.)")]
            = str(datetime.date.today()),
    skip_backup:
        Annotated[bool,
            typer.Option(help="Skip the backup phase.")]
            = False,
    skip_import:
        Annotated[bool,
            typer.Option(help="Skip the import phase.")]
            = False,
    dry_run: Annotated[bool,
            typer.Option(help="Explain what would be done, but do nothing.")]
            = False,
    leave_originals:
        Annotated[bool,
            typer.Option(help="Leave original files on the card.")]
            = False,
    overwrite_target:
        Annotated[bool,
            typer.Option(help="If target files exist, overwrite them instead of skipping.")]
            = False):
    # Configuration
    config.action = Configuration.Action.IMPORT
    config.configuration_file = configuration_file
    config.target = target
    config.card = card
    config.date = date
    config.skip_backup = skip_backup
    config.skip_import = skip_import
    config.dry_run = dry_run
    config.leave_originals = leave_originals
    config.overwrite_target = overwrite_target
    config.camera = camera
    logger.info('ACTION: Import')
    config.read_configuration()
    config.parse_configuration()
    config.find_source_path()
    config.validate()
    # Time for action

    start_time = time.time()

    # Print the banner and relevant settings
    print_boxed_text("PHOTO IMPORTINATOR")

    table = Table(title='Settings',show_header=False,show_edge=False)
    table.add_column('',style='bright_white',no_wrap=True)
    table.add_column('', style='white')
    # Settings file section
    table.add_section()
    table.add_row('Settings file',str(config.configuration_file))
    # Settings section
    table.add_section()
    table.add_row('Camera',config.camera)
    if config.is_cloud_source():
        table.add_row('Cloud drive', f":cloud-emoji:  {config.card}")
    else:
        table.add_row('Card',config.card)
    table.add_row('Backup folder',str(config.backup_path))
    table.add_row('Destination', str(config.date_to_path_demo()))
    flags = []
    if config.dry_run:
        flags.append("Dry run.")
    if config.skip_backup:
        flags.append("Skipping backup.")
    if config.skip_import:
        flags.append("Skipping import.")
    if config.leave_originals:
        flags.append("Leaving original files.")
    if config.overwrite_target:
        flags.append("Overwriting existing target files.")
    if len(flags) > 0:
        flags_txt = ''
        for f in flags:
            flags_txt += f"- {f}\n"
        flags_txt = flags_txt.rstrip()
        table.add_section()
        table.add_row('Flags:',flags_txt)
    print(table)

    # Wait for user confirmation
    try:
        print("If information isn't correct, press Ctrl+C to abort.")
        input("Press Return to continue: ")
    except KeyboardInterrupt:
        print("\nImport cancelled.")
        sys.exit(0)

    # Create and run the backup task.
    backup_task = BackupTask(config)
    backup_task.execute()

    # Create and run the import queue.
    queue = ImportQueue(config)
    queue.populate()
    queue.run()

    # Print out some final stats.
    queue.print_status()

    end_time = time.time()
    total_time = str(datetime.timedelta(seconds=int(end_time - start_time)))

    print(f"\nTotal time: {total_time}")
    logger.info(f'Import finished, total time: {total_time}')

    sys.exit(0)

@app.command(name="list",
             help="List cameras and targets.")
def command_list_cameras_and_targets(
    configuration_file:
        Annotated[Path,
        typer.Option("--configuration-file", "-C",
                     help="Configuration file.")] =
        Configuration.default_configuration_path()):
    # Configuration
    config.action = Configuration.Action.LIST_CAMERAS_AND_TARGETS
    config.configuration_file = configuration_file
    logger.info('ACTION: List Cameras and Targets')
    config.read_configuration()
    # NOTE: MUST NOT validate config. We rely entirely on config file, not CLI.
    # Time for action
    config.list_cameras_and_targets()
    sys.exit(0)

@app.command(name="stats",
             help="List running statistics of previous imports.")
def command_running_stats(
    configuration_file:
        Annotated[Path,
            typer.Option("--configuration-file", "-C",
                         help="Configuration file.")] =
            Configuration.default_configuration_path()):
    # Configuration
    config.action = Configuration.Action.LIST_RUNNING_STATS
    config.configuration_file = configuration_file
    logger.info('ACTION: List running stats')
    config.read_configuration()
    # NOTE: MUST NOT validate config. We rely entirely on config file, not CLI.
    # Time for action
    running_stats = RunningStats(config)
    running_stats.list_all()
    sys.exit(0)

@app.command(name="purge",
             help="Delete log file or running stats.")
def command_purge(
    to_be_purged: # TODO: Should validate if this is 'log' or 'stats'.
        Annotated[str,
            typer.Argument(help="'log' or 'stats'.")]):
    # TODO: if running stats/log file custom paths are ever implemented, this should parse config, I guess.
    if to_be_purged == 'log':
        config.action = Configuration.Action.PURGE_LOG_FILE
        logger.info('ACTION: Purge log files')  # :-(
        logging.shutdown()
        os.unlink(logfile_path())
        print(f"Purged Photo Importinator log file {logfile_path().absolute()}")
    elif to_be_purged == 'stats':
        config.action = Configuration.Action.PURGE_RUNNING_STATS
        logger.info('ACTION: Purge running stats')
        os.unlink(config.running_stats_path())
        print(f"Running stats file {config.running_stats_path()} removed, stats are now reset")
    else:
        logger.error(f'ACTION: Invalid purge target {to_be_purged}')
        print(f"I don't know how to purge {to_be_purged}")
        sys.exit(1)
    sys.exit(0)

@app.command(name="scan",
             help="Examine source photos and produce a CSV-formatted import preview.")
def command_scan(
    camera:
        Annotated[str,
            typer.Argument(help="Camera name.")],
    report_output_file:
        Annotated[Path,
            typer.Argument(help="Report CSV output file.")]
            = Path('scan_results.csv'),
    configuration_file:
        Annotated[Path,
            typer.Option("--configuration-file", "-C",
                help="Configuration file.")] =
            Configuration.default_configuration_path(),
    card:
        Annotated[str,
        typer.Option("--card", "-c",
                 help="Card to import from. Default specified in configuration file.")]
            = None):
    logger.info('ACTION: Scan')
    # Configuration
    config.action = Configuration.Action.SCAN
    config.configuration_file = configuration_file
    config.camera = camera
    config.card = card
    config.read_configuration()
    config.parse_configuration()
    config.find_source_path()
    config.validate()
    # Time for action
    die("Unimplemented")
    sys.exit(0)

@app.command(name="unpack",
             help="Unpack all archive files on specified cloud drive.")
def command_unpack(
    camera:
        Annotated[str,
            typer.Argument(help="Camera name.")],
    configuration_file:
        Annotated[Path,
            typer.Option("--configuration-file", "-C",
                 help="Configuration file.")]
        = Configuration.default_configuration_path(),
    card:
        Annotated[str,
        typer.Option("--card", "-c",
                     help="Card to import from. Default specified in configuration file.")]
        = None,
    dry_run:
        Annotated[bool,
            typer.Option(help="Explain what would be done, but do nothing.")]
        = False,
    leave_originals:
        Annotated[bool,
            typer.Option(help="Leave original files on the card.")]
        = False,
    overwrite_target:
        Annotated[bool,
            typer.Option(help="If target files exist, overwrite them instead of skipping.")]
        = False):
    # Configuration
    logger.info('ACTION: Unpack')
    config.action = Configuration.Action.UNPACK
    config.configuration_file = configuration_file
    config.camera = camera
    config.card = card
    config.dry_run = dry_run
    config.leave_originals = leave_originals
    config.overwrite_target = overwrite_target
    config.read_configuration()
    config.parse_configuration()
    config.find_source_path()
    config.validate()
    # Time for action
    archival.unpack_all(config)
    sys.exit(0)

###### Main program ######################################################

def main() -> int:
    """Photo Importinator main program."""

    # Initialise fancypants terminal stuff
    endazzle_terminal()

    # Delete old log if it exists
    if delete_old_log and os.path.exists(logfile_path()):
        os.unlink(logfile_path())
    # Start logging
    logging.basicConfig(level=log_level,filename=logfile_path())
    logger.info('Photo Importinator started.')

    # Parse command line, parse configuration as needed, do our activities.
    app()
    # And we're done!
    return 0

if __name__ == '__main__':
    main()

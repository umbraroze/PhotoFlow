# My photography workflow scripts

This repository contains my photography workflow automation scripts,
written primarily in PowerShell, meant to be used on Windows host.

## Photo Importinator

This script will import images from SD card or Dropbox to a NAS,
creating a backup archive. Requires exiftool and 7-Zip.

## Find Empty Day Folders

This will go through NAS file hierarchy (YYYY/MM/DD) and looks
for empty daily folders, allowing you to delete them.

## Remove internal tags

This will remove caption/category metadata from images to be
published, because in my case it's mostly useful for internal
use anyway.

## Video Rename

A quick and dirty script for adding date and time stamp on
video file names.

## Fix Memorycard Recovery

When doing deep filesystem recovery with Recuva, the software
sometimes spits out cryptic filenames when it can't figure out
the original names. This will try to make the names more
sensible and fix the datestamps based on metadata.

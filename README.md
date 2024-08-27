# My photography workflow scripts

This repository contains my photography workflow automation scripts,
written primarily in PowerShell, meant to be used on Windows host.

## Photo Importinator

This PowerShell script will import images from SD card or locally auto-synced cloud drive
(Dropbox, OneDrive, etc)
to a NAS, and creating a backup archive.

Requires
[exiv2](https://exiv2.org/),
[dnglab](https://github.com/dnglab/dnglab) and
[7-Zip](https://www.7-zip.org/) executables.

## Geoscooper

Python script that will read the geotags from all of the images
in a given directory and will spit out a KML file suitable for
visualising in GIS software of your choice.

Requires `exiv2`, `pykml` and `diskcache` packages via PIP.

## Upcoming

* Maybe need a script for helping sorting through "daily photo challenge"
  stuff.
* Some kind of tool for automatically making calendars of "photos from
  these days have been tagged with locations and put on map"

## Other scripts

* **Find Empty Day Folders**:
  This will go through NAS file hierarchy (YYYY/MM/DD) and looks
  for empty daily folders, allowing you to delete them.
* **Remove internal tags**:
  This will remove caption/category metadata from images to be
  published, because in my case it's mostly useful for internal
  use anyway.
* **Video Rename**:
  A quick and dirty script for adding date and time stamp on
  video file names.
* **Fix Memorycard Recovery**:
  When doing deep filesystem recovery with Recuva, the software
  sometimes spits out cryptic filenames when it can't figure out
  the original names. This will try to make the names more
  sensible and fix the datestamps based on metadata.

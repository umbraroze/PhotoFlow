# My photography workflow scripts

This repository contains my photography workflow automation scripts.

Many of the scripts were written for my personal use and are written
with Windows in mind, but some of them could possibly work on other
OSes.

## Photo Importinator

(See the [`photo_importinator`](photo_importinator/) subdirectory)

This script will import images to a NAS, creating a backup archive.
The aim is to minimise the user hassle: usually, you only need to
specify the camera you're using, and the script will do the rest.

## Geo Scooper

(See the [`geo_scooper`](geo_scooper/) subdirectory)

Python script that will read the geotags from all of the images
in a given directory and will spit out a KML file suitable for
visualising in GIS software of your choice.

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

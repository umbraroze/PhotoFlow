# My photography workflow scripts

This repository contains my photography workflow automation scripts.

Many of the scripts were written for my personal use and are written
with Windows in mind, but some of them could possibly work on other
OSes.

For extensive documentation, please see the
[PhotoFlow website](https://umbraroze.github.io/PhotoFlow/).

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

* **Consecucheck**: Did you take five bazillion images? Did you
  delete a few due to buttery fingers? Was it annoying to
  look at the backup? This script will find out
  if your image file sequence is indeed sequential or not!
  (Yeah, kind of a niche utility tool.)
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

# Further development directions and contributing

I have started to use the
[Issue tracker](https://github.com/umbraroze/PhotoFlow/issues)
to keep track of improvements I'm going to add to the scripts
here. There's also a list of random improvement ideas
from the previous bug tracker that can be found in the Wiki page
[Tasks](https://github.com/umbraroze/PhotoFlow/wiki/Tasks); these
were either done already, or should probably be converted into
Issues whenever I finally get around to do that. 

If you somehow get really bright ideas on how to expand these
humble scripts, or have found a terrifying bug, please feel free
to file an Issue!

If you actually use these scripts for anything worthwhile and
manage to get them running on your own, I first want to thank
you. Secondly, please tell everybody how you use these as part
of your workflow in a blog or like.

I *might* merge in well crafted Pull Requests, but expect me to
*scrutinise* them. ...Nothing malicious, just saying it's probably
going to take a long time.

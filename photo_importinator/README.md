# Photo Importinator

It imports photos!
This is suprisingly tricky and none of the apps I tried did it right!
...So I wrote my own, dang it!

## Overview

The intended audience of this software are people who host their
photographs locally on a NAS and use local digital asset
manager / photo management software (e.g. digiKam, ACDSee, what-have-you)
to access them.

The purpose of this script:

* Import images from SD card or locally auto-synced cloud drive
  (Dropbox, OneDrive, etc) to a NAS.
* During the import, perform conversion from camera-specific
  raw formats to DNG.
* Automatically create backup file of the original files (in case
  you ever need them again).

The aim is to minimise the user hassle: usually, you only need to
specify the camera you're using (and perhaps card drive letter, in case
Windows does funny things), and the script will do the rest.

The script allows for flexible configuration of the whole process
and different settings for different cameras.

Why does this script exist? Despite this being such a necessary and
ubiquitous part of photography workflow, and the fact that this feature
also exists on many DAMs too, *it might not work the way you expect it to.*
It's *surprisingly* easy to mess things up.

## Requirements

This is a [Python](https://www.python.org/) script, and it should work
on a reasonably recent version of Python 3.

For Python modules, see the file
[`requirements.txt`](requirements.txt) for a list of what's needed.
You can install them with `pip install -r requirements.txt`.

Some external software is needed to be installed - you need to
specify the path to the executables in the configuration file.

* [dnglab](https://github.com/dnglab/dnglab) (`dnglab`)
* [7-Zip](https://www.7-zip.org/) (`7za`)

## Configuration

Example file is provided in
[`photo_importinator_config.example.toml`](photo_importinator_config.example.toml).

Copy the file as `photo_importinator_config.toml` and place it in
configuration directory
(`~\AppData\Local\photo_importinator\` in Windows,
`~/.config/photo_importinator/` in POSIXy-land;
you should create the folder in case it doesn't exist, and why would
it, if you haven't used the app before - that'd be quite weird,
right?)

Then edit the file as desired. (Clearer instructions forthcoming as
situation develops. ...I hope.)

## History

This is the *third* iteration of the same idea.

I originally had a Microsoft Power Automate script. It worked.
It was a bit janky, though not because of Power Automate.
I mostly used it because Adobe DNG Converter couldn't be scripted
otherwise. Then stuff broke for good. `#JustAdobeThings`

The second iteration was a PowerShell script. It worked
reliably, and was not janky at all, actually. Especially when I
decided to first convert the raw files to DNG manually, and
later found `dnglab` which does the job considerably more
batch-processing-friendly than the Adobe tool.

Just that at some point the script grew to the point that I really
needed to throw some actual software organisation at it. While
PowerShell can ostensibly do some fancy complicated organisation
of code, that's not really what I use PowerShell for.

Decided to rewrite it in Python. So now we're here.

# Photo Importinator

*It imports photos!  
This is suprisingly tricky and none of the apps I tried did it right!  
...So I wrote my own, dang it!*

## Overview

The intended audience of this software are people who host their
photographs locally on a NAS and use local digital asset
manager / photo management software (e.g. digiKam, ACDSee, what-have-you)
to access them.

The script imports images from SD card or synchronised cloud folder,
converts raw to DNG, and creates a backup file of the originals.

The aim is to minimise the user hassle: usually, you only need to
specify the camera you're using, and the script will do the rest.

The script allows for flexible configuration of the whole process
and different settings for different cameras.

For a more thorough discussion, please see the
[Photo Importinator home page](https://umbraroze.github.io/PhotoFlow/photo_importinator/).

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

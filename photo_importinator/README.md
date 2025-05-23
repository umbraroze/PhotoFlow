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

You also need [dnglab](https://github.com/dnglab/dnglab) and usually need to
specify its location in the configuration file.

## Configuration

Example file is provided in
[`photo_importinator_config.example.toml`](photo_importinator_config.example.toml).

Copy the file as `photo_importinator_config.toml` and place it in
configuration directory
(`~\AppData\Local\photo_importinator\` in Windows,
`~/.config/photo_importinator/` in POSIXy-land).
Edit the file as desired.

More information is found in the
[usage section](https://umbraroze.github.io/PhotoFlow/photo_importinator/usage.html)
in the home page.

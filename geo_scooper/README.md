# Photo Geo Scooper

Ever fancied seeing *exactly where* you have been strolling
while taking photographs? Using *real* software?

This script will take all of the photographs in specified
directory or folder, grab the photo metadata, and spit out
a KML file containing coordinates of all photos you've taken.
You can then stick this KML file in any map visualisation tool
you like.

## Requirements

This is a [Python](https://www.python.org/) script, and it should work
on a reasonably recent version of Python 3.

Easiest way to run the program is by using the
[uv](https://docs.astral.sh/uv/) project manager
to handle virtual environment and PyPi dependency
fetching. To install all required packages,
just do:

```console
> uv sync
```

## Usage

Nothing too complicated, I hope:

```console
> uv run geo_scooper.py --input INPUTDIR --output outputfile.kml --verbose
```

(or `-i`, `-o`, `-v`) Input directory and the output file are required,
of course.

You may also specify the cache location via `--cache` or `-c`, e.g.
`--cache my_funny_scoop`. If left unspecified, caching will not be
used. The cache will store the pertinent metadata so that the
tags will only need to be re-read when the file has been changed.
This will speed up the process a great deal when there's a lot
of files and you're running the script repeatedly.

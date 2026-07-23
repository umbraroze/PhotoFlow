#!/usr/bin/python3
##########################################################################
# Photo Geo Scooper
##########################################################################
# (c) Rose Midford 2023,2024,2026
# Distributed under the MIT license. See the LICENSE file in parent folder
# for the full license terms.
##########################################################################

import os
import sys
import re
import datetime
import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import Annotated

import exiv2
from lxml import etree
from pykml.factory import KML_ElementMaker
from pykml.factory import GX_ElementMaker
from diskcache import Cache
import typer
from rich import print

app = typer.Typer()

##########################################################################

def make_extended_data(values: dict):
    """Creates a KML ExtendedData tag structure from the dict of given values."""
    # FIXME: Return type???
    ed = KML_ElementMaker.ExtendedData()
    for k in values.keys():
        d = KML_ElementMaker.Data(name=k)
        v = KML_ElementMaker.value(values[k])
        d.append(v)
        ed.append(d)
    return ed


def make_geo_timestamp(time: str, lat: float|int, lon: float|int):
    """Creates a KML camera data time stamp with latitude and longitude."""
    # FIXME: Return type???
    return KML_ElementMaker.Camera(
        GX_ElementMaker.TimeStamp(KML_ElementMaker.when(time)),
        KML_ElementMaker.latitude(lat),
        KML_ElementMaker.longitude(lon)
    )


def parse_exif_date(date: str) -> datetime.datetime | None:
    """Parses Exif datestamp string into a datetime structure.
    Will return None if date cannot be parsed."""
    try:
        return datetime.datetime.strptime(str(date), '%Y:%m:%d %H:%M:%S')
    except ValueError:
        return None


def parse_exif_rational(frac: str) -> float | int:
    """Parses a fraction given as a string and returns it as a float."""
    [(x, y)] = re.findall(r"(\d+)/(\d+)", frac)
    a, b = float(x), float(y)
    if b == 0:
        raise ZeroDivisionError(f"Exif coordinate fraction {frac} has 0 as a denominator")
    if a == 0:
        return 0.0
    return float(a / b)


def parse_exif_coords(lat: str, lon: str, lat_ref: str, lon_ref: str) -> tuple[float, float]:
    """Parses Exif coordinates.
    
    In Exif data, both latitude and longitude are given as string with
    three fractional values separated by spaces, representing
    degrees, minutes and seconds. (e.g. "123/456 123/456 123/456")
    Reference is given as a single character ('N','E','S','W').

    This function will parse the fractional values and converts them
    to a pair of signed float values, as used in KML files to
    represent coordinates."""

    # Parse latitude into fractions
    [(lat_deg_frac, lat_min_frac, lat_sec_frac)] = \
        re.findall(r"(\d+/\d+)\s+(\d+/\d+)\s+(\d+/\d+)", str(lat))
    # Convert fractions into floats
    lat_deg, lat_min, lat_sec = \
        parse_exif_rational(lat_deg_frac), \
            parse_exif_rational(lat_min_frac), \
            parse_exif_rational(lat_sec_frac)
    # Parse longitude into fractions
    [(lon_deg_frac, lon_min_frac, lon_sec_frac)] = \
        re.findall(r"(\d+/\d+)\s+(\d+/\d+)\s+(\d+/\d+)", str(lon))
    # Convert fractions into floats
    lon_deg, lon_min, lon_sec = \
        parse_exif_rational(lon_deg_frac), \
            parse_exif_rational(lon_min_frac), \
            parse_exif_rational(lon_sec_frac)

    # Convert latitude from degrees/minutes/seconds into a float.
    lat_d = float(lat_deg) + \
            (float(lat_min) * (1 / 60)) + \
            (float(lat_sec) * (1 / 60) * (1 / 60))
    # If we're on the Southern Hemisphere, flip the sign
    if str(lat_ref) == 'S':
        lat_d = -lat_d
    # Sanity check.
    if str(lat_ref) != 'N':
        raise ValueError(f"Latitude reference {str(lat_ref)} is neither N or S")
    # Convert longitude from degrees/minutes/seconds into a float.
    lon_d = float(lon_deg) + \
            (float(lon_min) * (1 / 60)) + \
            (float(lon_sec) * (1 / 60) * (1 / 60))
    # If we're on the Western Hemisphere, flip the sign
    if str(lon_ref) == 'W':
        lon_d = -lon_d
    # Sanity check.
    if str(lon_ref) != 'E':
        raise ValueError(f"Longitude reference {str(lon_ref)} is neither W or E")
    # And we have our values now!
    return lat_d, lon_d


class SkippedFileException(Exception):
    pass


# Read the image EXIF data
def read_exif(file) -> tuple[datetime.datetime, float, float]:
    try:
        img = exiv2.ImageFactory.open(file)
    except exiv2.Exiv2Error:
        raise SkippedFileException("File can't be read by exiv2")
    img.readMetadata()
    data = img.exifData()
    date_raw = data["Exif.Photo.DateTimeOriginal"].getValue()
    if date_raw is None:
        raise SkippedFileException("No date found")
    date = parse_exif_date(str(date_raw))
    if date is None:
        raise SkippedFileException("Date unparseable")

    # Read the GPS coordinates and convert them to KML style decimal coordinates
    # FIXME later: ok, so value() works, but what the heck was up with getValue() above???
    try:
        lat, lon, lat_ref, lon_ref = \
            str(data['Exif.GPSInfo.GPSLatitude'].value()), \
                str(data['Exif.GPSInfo.GPSLongitude'].value()), \
                str(data['Exif.GPSInfo.GPSLatitudeRef'].value()), \
                str(data['Exif.GPSInfo.GPSLongitudeRef'].value())
        kml_lat, kml_lon = parse_exif_coords(lat, lon, lat_ref, lon_ref)
    except exiv2.Exiv2Error:
        raise SkippedFileException("No coordinates found")

    return date, kml_lat, kml_lon


def read_exif_from_cache(fq_file: Path, cache: Cache) -> tuple[datetime.datetime, float, float]:
    # Get the file's last modified time
    mtime = os.path.getmtime(fq_file)
    try:
        cdata: dict | None = pickle.loads(cache[str(fq_file)])
    except KeyError:
        cdata = None
    if cdata is None or mtime > cdata['mtime']:
        # Cache doesn't exist or is too old.
        # Come up with the new data and cache it.
        try:
            date, kml_lat, kml_lon = read_exif(fq_file)
        except SkippedFileException:
            # If no sufficient data, save anyway
            cdata: dict = dict()
            cdata['mtime'] = mtime
            cdata['date'] = None
            cdata['kml_lat'] = None
            cdata['kml_lon'] = None
            cache[str(fq_file)] = pickle.dumps(cdata)
            # And off we go to the next file then. Signal the
            # caller that we skipped the file.
            raise
        # OK, here's the regular data
        cdata: dict = dict()
        cdata['mtime'] = mtime
        cdata['date'] = date
        cdata['kml_lat'] = kml_lat
        cdata['kml_lon'] = kml_lon
        cache[str(fq_file)] = pickle.dumps(cdata)
        return date, kml_lat, kml_lon
    else:
        # Cache is valid-ish, retrieve cached values
        date: datetime.datetime | None = cdata['date']
        kml_lat = cdata['kml_lat']
        kml_lon = cdata['kml_lon']
        if date is None:
            # Well there's no data for this then
            raise SkippedFileException("No coordinates found")
        return date, kml_lat, kml_lon

##########################################################################

@app.command()
def main(input_dir: Annotated[Path, typer.Option(help="Input directory.")] = Path("."),
         output_file:Annotated[Path, typer.Option(help="Output file.")] = Path("output.kml"),
         cache_dir: Annotated[Path | None, typer.Option(help="Cache directory location. If unspecified, caching is disabled.")] = None,
         verbose:Annotated[bool, typer.Option(help="Verbose mode.")] = False):
    # Print out our settings.
    if verbose:
        print(f"Input dir: {input_dir}")
        print(f"Output file: {output_file}")
        if cache_dir is not None:
            print(f"Cache location: {cache_dir}")
        else:
            print("Caching disabled")

    # Set up cache
    if cache_dir is not None:
        cache = Cache(str(cache_dir))
    else:
        cache = None

    # New KML document
    kml = KML_ElementMaker.kml(KML_ElementMaker.Document())

    # Walk the input directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # Get the file's full name
            fq_file = Path(root) / file
            # Skip non-files
            if not fq_file.is_file():
                continue
            # OK, we're cool, continuing
            if verbose:
                print(f"Processing {fq_file}")

            # Read the exif data (via cache possibly)
            try:
                if cache is not None:
                    date, kml_lat, kml_lon = read_exif_from_cache(fq_file, cache)
                else:
                    date, kml_lat, kml_lon = read_exif(fq_file)
            except SkippedFileException:
                # Print skip reason
                if verbose and (sys.exception() is not None):
                    print(sys.exception())
                continue

            # At this point, we have data, kml_lat and kml_lon
            if verbose:
                print(f" - Coordinates: {kml_lat},{kml_lon}")
            # ...but wait! Did we somehow get pointed to the Null Island?
            if kml_lat == 0.0 and kml_lon == 0.0:
                if verbose:
                    print(" - Coordinates are probably bogus, skipping this one")
                continue
            # Right! With that out of the way, we can be reasonably sure we indeed have
            # what we need: File name, date stamp, and coordinates.

            # Construct the KML data
            ed = {
                "Path": fq_file,
                "Date": date.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            place_mark = KML_ElementMaker.Placemark(
                KML_ElementMaker.name(file),
                make_geo_timestamp(date.strftime("%Y-%m-%dT%H:%M:%S"), kml_lat, kml_lon),
                make_extended_data(ed)
            )
            # ...and put it on the file!
            kml.Document.append(place_mark)

    # Write the KML document to file.
    f = open(output_file, "wb")
    f.write(etree.tostring(kml, pretty_print=True))
    f.close()

if __name__ == '__main__':
    app()

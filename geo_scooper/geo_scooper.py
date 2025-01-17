#!/usr/bin/python3
##########################################################################
#
# Photo Geo Scooper
# (c) Rose Midford 2023,2024
# See LICENSE for terms of distribution
#
##########################################################################

# builtins
import os, sys
import re
import getopt
import datetime
import pickle

# via PIP
import exiv2
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from diskcache import Cache

##########################################################################

def make_extended_data(values):
    ed = KML.ExtendedData()
    for k in values.keys():
        d = KML.Data(name=k)
        v = KML.value(values[k])
        d.append(v)
        ed.append(d)
    return ed

def make_geo_timestamp(time,lat,lon):
    return KML.Camera(
        GX.TimeStamp(KML.when(time)),
        KML.latitude(lat),
        KML.longitude(lon)
    )

def parse_exif_date(date):
    try:
        return datetime.datetime.strptime(str(date),'%Y:%m:%d %H:%M:%S')
    except ValueError:
        return None

def parse_exif_rational(frac):
    [(a,b)] = re.findall(r"(\d+)/(\d+)",frac)
    if a == "0" or b == "0":
        return 0.0
    return float(a)/float(b)

def parse_exif_coords(lat,lon,lat_ref,lon_ref):
    [(lat_deg_frac,lat_min_frac,lat_sec_frac)] = \
        re.findall(r"(\d+/\d+)\s+(\d+/\d+)\s+(\d+/\d+)",str(lat))
    lat_deg, lat_min, lat_sec = \
        parse_exif_rational(lat_deg_frac), \
        parse_exif_rational(lat_min_frac), \
        parse_exif_rational(lat_sec_frac)
    [(lon_deg_frac,lon_min_frac,lon_sec_frac)] = \
        re.findall(r"(\d+/\d+)\s+(\d+/\d+)\s+(\d+/\d+)",str(lon))
    lon_deg, lon_min, lon_sec = \
        parse_exif_rational(lon_deg_frac), \
        parse_exif_rational(lon_min_frac), \
        parse_exif_rational(lon_sec_frac)

    lat_d = float(lat_deg) + \
        (float(lat_min)*(1/60)) + \
        (float(lat_sec)*(1/60)*(1/60))
    if str(lat_ref) == 'S':
        lat_d = -lat_d
    lon_d = float(lon_deg) + \
        (float(lon_min)*(1/60)) + \
        (float(lon_sec)*(1/60)*(1/60))
    if str(lon_ref) == 'W':
        lon_d = -lon_d
    return (lat_d,lon_d)

class SkippedFileException(Exception):
    pass

# Read the image EXIF data
def read_exif(file):
    global verbose_mode
    try:
        img = exiv2.ImageFactory.open(file)
    except exiv2.Exiv2Error:
        if verbose_mode:
            print(" - This file can't be read by Exiv2. Skipping.")
        raise SkippedFileException
    img.readMetadata()
    data = img.exifData()
    #for k in data:
    #    print(k)
    date_raw = data["Exif.Photo.DateTimeOriginal"].getValue()
    if date_raw is None:
        if verbose_mode:
            print(" - No date found, skipping")
        raise SkippedFileException
    date = parse_exif_date(str(date_raw))
    if date is None:
        if verbose_mode:
            print(" - Date unparseable, skipping")
        raise SkippedFileException
    if verbose_mode:
        print(f" - Date: {date}")

    # Read the GPS coordinates and convert them to KML style decimal coordinates
    # FIXME later: ok, so value() works, but what the heck was up with getValue() above???
    try:
        lat, lon, lat_ref, lon_ref = \
            data['Exif.GPSInfo.GPSLatitude'].value(), \
            data['Exif.GPSInfo.GPSLongitude'].value(), \
            data['Exif.GPSInfo.GPSLatitudeRef'].value(), \
            data['Exif.GPSInfo.GPSLongitudeRef'].value()
        kml_lat, kml_lon = parse_exif_coords(lat, lon, lat_ref, lon_ref)
    except exiv2.Exiv2Error:
        if verbose_mode:
            print(" - No coordinates found, skipping")
        raise SkippedFileException

    return (date,kml_lat,kml_lon)

##########################################################################

# Command line parameters parsing
# TODO: Convert this to use argparse instead of getopt

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:o:c:v", ["input=", "output=","cache=","verbose"])
except getopt.GetoptError as err:
    print(err)
    print("Usage: photo_geo_scooper [-i inputdir] [-o output.kml] [-v]")
    sys.exit(2)
verbose_mode = False
input_dir = "."
output_file = "output.kml"
cache_file = None
caching = False
for o, a in opts:
    if o in ("-i", "--input"):
        input_dir = a
    elif o in ("-o", "--output"):
        output_file = a
    elif o in ("-c", "--cache"):
        cache_file = a
        caching = True
    elif o == "-v":
        verbose_mode = True
if verbose_mode:
    print(f"Input dir: {input_dir}")
    print(f"Output file: {output_file}")
    if cache_file is not None:
        print(f"Cache file: {cache_file}")
    else:
        print("Caching disabled")

# Set up cache
cache = None
if caching:
    cache = Cache(cache_file)

# New KML document
kml = KML.kml(KML.Document())

# Walk the input directory
for root, dirs, files in os.walk(input_dir):
    path = root.split(os.sep)
    for file in files:
        # Get the file's full name
        fqfile = os.sep.join(path)+os.sep+file
        # Skip non-files
        if not os.path.isfile(fqfile):
            continue
        # OK, we're cool, continuing
        if verbose_mode:
            print(f"Processing {fqfile}")
        
        # Get the file's last modified time
        mtime = os.path.getmtime(fqfile)

        # Read the exif data (via cache possibly)
        if caching:
            # Yes we do caching and yes this gets complicated
            try:
                cdata = pickle.loads(cache[fqfile])
            except KeyError:
                cdata = None
            if cdata is None or mtime > cdata['mtime']:
                # Cache doesn't exist or is too old.
                # Come up with brand new data and cache it.
                try:
                    date, kml_lat, kml_lon = read_exif(fqfile)
                except SkippedFileException:
                    # If no sufficient data, save anyway
                    cdata = dict()
                    cdata['mtime'] = mtime
                    cdata['date'] = None
                    cdata['kml_lat'] = None
                    cdata['kml_lon'] = None
                    cache[fqfile] = pickle.dumps(cdata)
                    # And off we go to the next file then
                    continue
                # OK, here's the regular data
                cdata = dict()
                cdata['mtime'] = mtime
                cdata['date'] = date
                cdata['kml_lat'] = kml_lat
                cdata['kml_lon'] = kml_lon
                cache[fqfile] = pickle.dumps(cdata)
            else:
                # Cache is valid
                # Retrieve cached values
                if verbose_mode:
                    print(" - File unmodified, cached values used")
                date = cdata['date']
                kml_lat = cdata['kml_lat']
                kml_lon = cdata['kml_lon']
                if date is None:
                    # Well there's no data for this then
                    if verbose_mode:
                        print(" - No coordinates found, skipping")
                    continue

        else:
            # No caching magic, just read the damn thing
            try:
                date, kml_lat, kml_lon = read_exif(fqfile)
            except SkippedFileException:
                continue

        if verbose_mode:
            print(f" - Coordinates: {kml_lat},{kml_lon}")
        # ...but wait! Did we somehow get pointed to the Null Island?
        if kml_lat == 0.0 and kml_lon == 0.0:
            if verbose_mode:
                print(" - Coordinates are probably bogus, skipping this one")
            continue
        # Right! With that out of the way, we can be reasonably sure we indeed have
        # what we need: File name, date stamp, and coordinates.

        # Construct the KML data
        ed = {
            "Path": fqfile,
            "Date": date.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        place_mark = KML.Placemark( 
            KML.name(file),
            make_geo_timestamp(date.strftime("%Y-%m-%dT%H:%M:%S"),kml_lat,kml_lon),
            make_extended_data(ed)
        )
        # ...and put it on the file!
        kml.Document.append(place_mark)

# Write the KML document to file.
f = open(output_file,"wb")
f.write(etree.tostring(kml,pretty_print=True))
f.close()

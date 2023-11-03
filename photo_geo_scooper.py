#!/usr/bin/python3
##########################################################################
#
# Photo Geo Scooper
# (c) Rose Midford 2023
# See LICENSE for terms of distribution
#
# This will walk your photo directory, grab photo metadata, and spit out
# a KML file containing coordinates of all photos you've taken. You can
# then stick this KML file in any map visualisation tool you like.
#
# To install the required libraries:
#
#   $ pip install exiv2 pykml
#
##########################################################################

import os, sys
import re
import getopt
import datetime

import exiv2
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

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
    return datetime.datetime.strptime(str(date),'%Y:%m:%d %H:%M:%S')

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

##########################################################################

# Command line parameters parsing

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:o:v", ["input=", "output=","verbose"])
except getopt.GetoptError as err:
    print(err)
    print("Usage: photo_geo_scooper [-i inputdir] [-o output.kml] [-v]")
    sys.exit(2)
verbose_mode = False
input_dir = "."
output_file = "output.kml"
for o, a in opts:
    if o in ("-i", "--input"):
        input_dir = a
    elif o in ("-o", "--output"):
        output_file = a
    elif o == "-v":
        verbose_mode = True
if verbose_mode:
    print(f"Input dir: {input_dir}")
    print(f"Output file: {output_file}")


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
        # Read the image EXIF data
        try:
            img = exiv2.ImageFactory.open(fqfile)
        except exiv2.Exiv2Error:
            if verbose_mode:
                print(" - This file can't be read by Exiv2. Skipping.")
            continue
        img.readMetadata()
        data = img.exifData()
        #for k in data:
        #    print(k)
        date_raw = data["Exif.Photo.DateTimeOriginal"].getValue()
        if date_raw == None:
            if verbose_mode:
                print(" - No date found, skipping")
            continue
        date = parse_exif_date(str(date_raw))
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

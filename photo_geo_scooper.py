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

def parse_exif_coords(lat,lon):
    # there's probably a library for this, but what the heck...
    # Note: this probably only works in North/East quadrant of the world 
    # (lat and lon positive). Haven't got a clue what goes in the EXIF
    # in other regions. Sorry for an Eurocentrist quick hack.
    [(lat_deg,lat_min,lat_sec)] = re.findall(r"(\d+)deg\s+(\d+)'\s+(\d+)\"",lat)
    [(lon_deg,lon_min,lon_sec)] = re.findall(r"(\d+)deg\s+(\d+)'\s+(\d+)\"",lon)
    lat_d = float(lat_deg) + (float(lat_min)*(1/60)) + (float(lat_sec)*(1/60)*(1/60))
    lon_d = float(lon_deg) + (float(lon_min)*(1/60)) + (float(lon_sec)*(1/60)*(1/60))
    return (lat_d,lon_d)

##########################################################################

# Command line parameters parsing

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:o:v", ["input=", "output=","verbose"])
except getopt.GetoptError as err:
    print(err)
    print("Usage: photo_geo_scooper [-i inputdir] [-o outputdir] [-v]")
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
        if(verbose_mode):
            print(f"Processing {fqfile}")
        # Read the image EXIF data
        img = exiv2.ImageFactory.open(fqfile)
        img.readMetadata()
        data = img.exifData()
        #for k in data:
        #    print(k)
        date = parse_exif_date(str(data["Exif.Photo.DateTimeOriginal"].getValue()))
        if verbose_mode:
            print(f" - Date: {date}")

        # Read the GPS coordinates and convert them to KML style decimal coordinates
        try:
            lat, lon = data['Exif.GPSInfo.GPSLatitude'], data['Exif.GPSInfo.GPSLongitude']
            kml_lat, kml_lon = parse_exif_coords(str(lat), str(lon))
        except exiv2.Exiv2Error:
            if verbose_mode:
                print(" - No coordinates found")
            continue

        if verbose_mode:
            print(f" - Coordinates: {kml_lat},{kml_lon}")

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

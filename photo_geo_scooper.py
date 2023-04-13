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

import exiv2
import pykml
import os, sys
import getopt
import datetime

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
    KML.Camera(
        GX.TimeStamp(KML.when("2023-04-13T17:55:00+02:00")),
        KML.latitude("-0.0"),
        KML.longitude("0.0")
    )

def parse_exif_date(date):
    print(date)
    datetime.datetime.strptime(str(date),'%Y:%m:%d %H:%M:%S')

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
        fqfile = os.sep.join(path)+os.sep+file
        if not os.path.isfile(fqfile):
            continue
        img = exiv2.ImageFactory.open(fqfile)
        img.readMetadata()
        data = img.exifData()
        # for k in data:
        #    print k
        date = parse_exif_date(data["Exif.Photo.DateTimeOriginal"].getValue())
        print(date)
        sys.exit(0)

sys.exit(0)


ed = {
    "Path": "Full file path",
    "Date": "Datestamp",
    "Camera": "Camera and lens details"
}
place_mark = KML.Placemark(
    KML.name("File basename"),
    make_geo_timestamp("2023-04-13T17:55:00+02:00","-0.0","0.0"),
    make_extended_data(ed)
)

kml.Document.append(place_mark)

print(etree.tostring(kml))
#print(etree.tostring(doc,pretty_print=True))
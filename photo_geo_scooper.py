#!/usr/bin/python3

import exiv2
import pykml

from lxml import etree
from pykml.factory import KML_ElementMaker as KML

kml = KML.kml(KML.Document())

place_mark = KML.Placemark(
    KML.name("Hello World!"),
    KML.description("Description goes here"),
    KML.Point(
        KML.coordinates("-0.0,0.0")
    )
)

kml.Document.append(place_mark)

#print(etree.tostring(kml))
#print(etree.tostring(doc,pretty_print=True))
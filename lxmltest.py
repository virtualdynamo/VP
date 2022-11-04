from dotenv import load_dotenv
import os

#from xml.etree import ElementTree
import lxml.etree as ElementTree
#from lxml import etree

from pathlib import Path

load_dotenv()
data_folder = Path(os.getenv('DATA_FOLDER'))
TCX_full = data_folder / "Poudre_Up.tcx"
dom = ElementTree.parse(TCX_full)
trackpoints = dom.findall('{*}Courses/{*}Course/{*}Track/{*}Trackpoint')

i=0
for t in trackpoints:
    lat = float(t.find('{*}Position/{*}LatitudeDegrees').text)
    long = float(t.find('{*}Position/{*}LongitudeDegrees').text)
    alt = float(t.find('{*}AltitudeMeters').text)
    dist_meters = float(t.find('{*}DistanceMeters').text)
    print('%5d %10.6f %10.6f %6.1f %8.2f' % (i, lat, long, alt, dist_meters))
    i += 1
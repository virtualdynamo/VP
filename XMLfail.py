from dotenv import load_dotenv
import os

from xml.etree import ElementTree

from pathlib import Path

def _register_namespaces(self):
    self.namespaces = {node[0]: node[1] for _, node in ET.iterparse(self.filepath, events=['start-ns'])}
    for key, value in self.namespaces.items():
        ElementTree.register_namespace(key, value)
    self.default_ns = "{" + self.namespaces[""] + "}"

def load_tcx(self, filepath):
    tree = self._load_file(filepath, ".tcx")
    if not tree:
        return
    else:
        self._register_namespaces()
        self.tree = tree
        self.activity = self.tree.getroot()
        self._get_laps()

load_dotenv()
data_folder = Path(os.getenv('DATA_FOLDER'))
TCX_full = data_folder / "Poudre_Up.tcx"
#dom = ElementTree.parse(TCX_full)
dom = load_tcx(str(data_folder) + "Poudre_Up.tcx")
trackpoints = dom.findall('{*}Courses/{*}Course/{*}Track/{*}Trackpoint')

i=0
for t in trackpoints:
    lat = float(t.find('{*}Position/{*}LatitudeDegrees').text)
    long = float(t.find('{*}Position/{*}LongitudeDegrees').text)
    alt = float(t.find('{*}AltitudeMeters').text)
    dist_meters = float(t.find('{*}DistanceMeters').text)
    print('%5d %10.6f %10.6f %6.1f %8.2f' % (i, lat, long, alt, dist_meters))
    i += 1
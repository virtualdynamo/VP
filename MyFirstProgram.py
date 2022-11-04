# python.exe -m pip install --upgrade pip
# pip install python-dotenv
from dotenv import load_dotenv
import os

import csv
import copy

from xml.etree import ElementTree

from pathlib import Path
# pip install haversine
from haversine import haversine
from maps import *

# variable names: lower_score

load_dotenv()
data_folder = Path(os.getenv('DATA_FOLDER'))
#CSV_file_root = "2016JUL11"
#CSV_file_root = "2016JUL14"
CSV_file_root = "2022SEP17_UP"
#CSV_file_root = "2022SEP17_DOWN"

print(CSV_file_root, data_folder)

Garmin_full = data_folder / (CSV_file_root+"_data.csv")
output_full = data_folder / (CSV_file_root+"_output.csv")
TCX_full = data_folder / "Poudre_Up.tcx"

print(Garmin_full)

#Read in Garmin file that has been converted from FIT to CSV by C:\Users\toigo\Downloads\FitSDKRelease_21.67.00\java\FITTOCSV-record.BAT
Garmin_list = []
Garmin_node = node()

with open(Garmin_full) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        Garmin_node.lat = float(row['record.position_lat[semicircles]']) * FIT2DD
        Garmin_node.long = float(row['record.position_long[semicircles]']) * FIT2DD
        Garmin_node.alt = float(row['record.altitude[m]'])
        Garmin_list.append(copy.deepcopy(Garmin_node))

#Read in Plotaroute TCX file. Remember to delete everything after the TrainingCenterDatabase tag in the second line of the TCX file.

route_list = []
route_node = new_node()

dom = ElementTree.parse(TCX_full)
trackpoints = dom.findall('{*}Courses/{*}Course/{*}Track/{*}Trackpoint')

i=0
for t in trackpoints:
    route_node.lat = float(t.find('{*}Position/{*}LatitudeDegrees').text)
    route_node.long = float(t.find('{*}Position/{*}LongitudeDegrees').text)
    route_node.alt = float(t.find('{*}AltitudeMeters').text)
    route_node.dist_meters = float(t.find('{*}DistanceMeters').text)
    route_node.dist = 40000.0
    for g in Garmin_list:
        haversine_dist = haversine((route_node.lat,route_node.long),(g.lat,g.long))
        if haversine_dist < route_node.dist:
            route_node.dist = haversine_dist
            route_node.corr_alt = g.alt
    print(i, route_node.lat, route_node.long, route_node.alt, route_node.dist_meters, route_node.dist, route_node.corr_alt)
    route_list.append(copy.deepcopy(route_node))
    i += 1
    if i >= 10:
        break
    
fixpoint_start = route_list[0].alt - route_list[0].corr_alt
fixpoint_end = route_list[-1].alt - route_list[-1].corr_alt
route_length = route_list[-1].dist_meters

i = 0
with open(output_full, 'w') as f:
    header = "Row,Latitude,Longitude,Input altitude,Course dist,Dist to correction,Corrected altitude,Interpolated altitude\n"
    f.write(header)
    for p in route_list:
        p.inter_alt = (p.dist_meters / route_length) * (fixpoint_end - fixpoint_start) + fixpoint_start + p.corr_alt
        row = str(i)+","+str(p.lat)+","+str(p.long)+","+str(p.alt)+","+str(p.dist_meters)+","+str(p.dist)+","+str(p.corr_alt)+","+str(p.inter_alt)+"\n"
        f.write(row)
        i += 1
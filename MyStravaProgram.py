from configparser import Interpolation
from re import I, X
from dotenv import load_dotenv
import os

from datetime import datetime, timedelta
from time import strptime

import csv
import copy
from ctypes.wintypes import PINT

from xml.etree import ElementTree

from pathlib import Path
from haversine import haversine
from maps import *

# variable names: lower_score

"""
Wmax	253.2671006	W
Winter	14	m/s
m	90	kg
CdA	0.35	m^2
rho	1.2	kg/m^3
Crr	0.005	
g	9.81	m/s^2
"""

power_max = 253.2671006
power_x_intercept = 14.0
mass = 90.0
CdA = 0.35
rho = 1.2
Crr = 0.005
g = 9.81

dv_dt_max = 10.5
dt_max = 1.0


load_dotenv()
data_folder = Path(os.getenv('DATA_FOLDER'))
#data_folder = Path("C:/Users/toigo/Documents/Bike/GPS Files/OSM/")

TCX_file_root = "Poudre Down"
#TCX_full = data_folder / "Poudre Strava_1.tcx"
TCX_input_full = data_folder / (TCX_file_root+".tcx")
TCX_output_full = data_folder / (TCX_file_root+"_output.tcx")

#Read in Strava TCX file. Remember to delete everything after the TrainingCenterDatabase tag in the second line of the TCX file.

Strava_list = []
Strava_node = TCX_node()
last_VP = virtual_partner()
next_VP = virtual_partner()

dom = ElementTree.parse(TCX_input_full)
trackpoints = dom.findall('{*}Courses/{*}Course/{*}Track/{*}Trackpoint')

start_run = datetime.now()

#one_day = timedelta(days=1)

i=0
for t in trackpoints:
    Strava_node.time  = (t.find('{*}Time')).text
    Strava_node.lat = float(t.find('{*}Position/{*}LatitudeDegrees').text)
    Strava_node.long = float(t.find('{*}Position/{*}LongitudeDegrees').text)
    Strava_node.alt = float(t.find('{*}AltitudeMeters').text)
    Strava_node.dist_meters = float(t.find('{*}DistanceMeters').text)
#    print(Strava_node.time)
    Strava_datetime = datetime.strptime(Strava_node.time[0:19], '%Y-%m-%dT%H:%M:%S')
    if i == 0:
        start_time = Strava_datetime
        last_alt = Strava_node.alt
        last_dist_meters = Strava_node.dist_meters
        last_VP.t = 0.0
        last_VP.v = 0.1 * power_x_intercept
        last_VP.x = 0.0
    elif Strava_node.dist_meters > last_dist_meters:
        slope = (last_alt - Strava_node.alt)/(last_dist_meters - Strava_node.dist_meters)
#        print(slope)
        j = 0
        while last_VP.x < Strava_node.dist_meters and j < 30:
            last_VP.power = power_max * (1.0-last_VP.v/power_x_intercept)
            last_VP.accel = last_VP.power/(mass*last_VP.v) - g*(Crr+slope) - CdA*rho*last_VP.v**2.0/(2.0*mass)
            if last_VP.accel > dv_dt_max / dt_max:
                dt = last_VP.accel / dv_dt_max
            else:
                dt = dt_max
            next_VP.t = last_VP.t + dt
            next_VP.v = last_VP.v + last_VP.accel * dt
            next_VP.x = last_VP.x + last_VP.v * dt + last_VP.accel*dt**2/2.0
#            print("%d %2d %6.2f %6.3f %8.1f %6.2f %6.3f" % (i, j, last_VP.t, last_VP.v, last_VP.x, last_VP.power, last_VP.accel))
            if next_VP.x >= Strava_node.dist_meters:
                last_alt = Strava_node.alt
                last_dist_meters = Strava_node.dist_meters
                inter = (Strava_node.dist_meters - last_VP.x) / (next_VP.x - last_VP.x)
                next_VP.t = last_VP.t + inter*(next_VP.t-last_VP.t)
                next_VP.v = last_VP.v + inter*(next_VP.v-last_VP.v)
                next_VP.x = Strava_node.dist_meters
                next_time = start_run + timedelta(seconds = next_VP.t)
                str_next_time = next_time.strftime('%Y-%m-%d'+'T'+next_time.strftime('%H:%M:%S')+'+00:00')
                print('%5d %6.3f %6.4f %8.2f %6.3f %s %s' % (i, slope, inter, next_VP.t, next_VP.v,str(next_time), str_next_time))
            last_VP = copy.deepcopy(next_VP)
            j += 1
#    print(Strava_datetime)
#    print(Strava_datetime-start_time)
    i += 1
#    if i >= 200:
#        break   
from cgitb import text
import string


FIT2DD = (360/2**32)

class node:
    def __init__(self):
        self.lat: float
        self.long: float
        self.alt: float

class new_node:
    def __init__(self):
        node()
        self.dist_meters: float
        self.dist: float
        self.corr_alt: float
        self.inter_alt: float

class TCX_node:
    def __init__(self):
        node()
        self.dist_meters: float
        self.time: string

class virtual_partner:
    def __init__(self):
        self.t: float
        self.v: float
        self.x: float
        self.power: float
        self.accel: float

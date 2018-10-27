
import sys
import time
import datetime
from math import *

import ephem

class Tracker():

    
    def __init__(self,satellite, groundstation):
        self.groundstation = ephem.Observer()
        self.groundstation.lat = groundstation[0]
        self.groundstation.lon = groundstation[1]
        self.groundstation.elevation = int(groundstation[2])

        self.satellite = ephem.readtle(satellite["name"], satellite["tle1"], satellite["tle2"])

    
    def set_epoch(self, epoch=time.time()):
        ''' sets epoch when parameters are observed '''

        self.groundstation.date = datetime.datetime.utcfromtimestamp(epoch)

        print (self.groundstation.date)
        self.satellite.compute(self.groundstation)

    def azimuth(self):
        ''' returns satellite azimuth in degrees '''
        return degrees(self.satellite.az)

    def elevation(self):
        ''' returns satellite elevation in degrees '''
        return degrees(self.satellite.alt)

    def latitude(self):
        ''' returns satellite latitude in degrees '''
        return degrees(self.satellite.sublat)

    def longitude(self):
        ''' returns satellite longitude in degrees '''
        return degrees(self.satellite.sublong)

    def range(self):
        ''' returns satellite range in meters '''
        return self.satellite.range

    def doppler(self, frequency_hz=437505000):
        ''' returns doppler shift in hertz '''
        return -self.satellite.range_velocity / 299792458. * frequency_hz

    def ecef_coordinates(self):
        ''' returns satellite earth centered cartesian coordinates
            https://en.wikipedia.org/wiki/ECEF
        '''
        x, y, z = self._aer2ecef(self.azimuth(), self.elevation(), self.range(), float(self.groundstation.lat), float(self.groundstation.lon), self.groundstation.elevation)
        return x, y, z

    def _aer2ecef(self, azimuthDeg, elevationDeg, slantRange, obs_lat, obs_long, obs_alt):

        #site ecef in meters
        sitex, sitey, sitez = llh2ecef(obs_lat,obs_long,obs_alt)

        #some needed calculations
        slat = sin(radians(obs_lat))
        slon = sin(radians(obs_long))
        clat = cos(radians(obs_lat))
        clon = cos(radians(obs_long))

        azRad = radians(azimuthDeg)
        elRad = radians(elevationDeg)

        # az,el,range to sez convertion
        south  = -slantRange * cos(elRad) * cos(azRad)
        east   =  slantRange * cos(elRad) * sin(azRad)
        zenith =  slantRange * sin(elRad)

        x = ( slat * clon * south) + (-slon * east) + (clat * clon * zenith) + sitex
        y = ( slat * slon * south) + ( clon * east) + (clat * slon * zenith) + sitey
        z = (-clat *        south) + ( slat * zenith) + sitez

        return x, y, z

    """

"""
if __name__ == "__main__":
    # taken from: http://celestrak.com/NORAD/elements/cubesat.txt
    ec1_tle = { "name": "XW-2F", \
                "tle1": "1 40910U 15049M   18224.56523641  .00000684  00000-0  38306-4 0  9994", \
                "tle2": "2 40910  97.4583 228.1371 0014927 181.0455 179.0750 15.16647843160127"}

    # http://www.gpscoordinates.eu/show-gps-coordinates.php
    bolzano = ("46.583333", "11.2", "300")

    tracker = Tracker(satellite=ec1_tle, groundstation=bolzano)
    
    satf = 435340000

    while 1:
        tracker.set_epoch(time.time())


        print (tracker.groundstation.next_pass(tracker.satellite))

        print ("----")
        print ("az         : {0:.1f}".format(tracker.azimuth()))
        print ("ele        : {0:.1f}".format(tracker.elevation()))
        print ("range      : {0:.1f} km".format((tracker.range()/1000)))
        print ("range rate : {0:.1f} km/s".format((tracker.satellite.range_velocity/1000)))
        print ("doppler    : {0} Hz".format((tracker.doppler(satf))))
        print ("freq   : {0} Hz".format(int(satf - tracker.doppler(satf))))

        time.sleep(0.5)


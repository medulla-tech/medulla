# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.


import os
import sys
#import math
from math import cos
from math import sin
from math import acos
from math import asin
from math import atan2
from math import degrees
from math import radians
from math import sqrt 

rt = 6371  # rayon terrestre moyen en km
### on considere laltitude a rt quelque soit le point.
import GeoIP


class Point:
        def __init__(self, lat1, lon1):
            self.lat=radians(lat1)
            self.lon=radians(lon1)

        def afficher(self):
            print "lat=%f"%degrees(self.lat)
            print "long=%f"%degrees(self.lon)

class Localisation:
    def __init__(self):
        self.gi = GeoIP.open("/usr/share/GeoIP/GeoLiteCity.dat", GeoIP.GEOIP_STANDARD)
    def geodataip(self,ip):
        return self.gi.record_by_addr(ip)

    def geodatadnsname(self,dnsname):
        return self.gi.record_by_name(dnsname)

    def determinationbylongitudeandip(self, lat1, long1 , ip2):
        point1 = Point(lat1, long1 )
        gir2 = self.gi.record_by_addr(ip2)
        if gir2 != None:
            point2 = Point(gir2['latitude'],gir2['longitude'])
            if str(point1.lat)==str(point2.lat) and str(point1.lon)==str(point2.lon):
                self.distance = 0
            else:
                self.distance = self.distHaversine( point1,point2)
        else:
            self.distance = None
        return int(self.distance)

    def determinationbyip(self, ip1, ip2):
        gir1 = self.gi.record_by_addr(ip1)
        gir2 = self.gi.record_by_addr(ip2)
        if gir1 != None and  gir2 != None:
            self.point1 = Point(gir1['latitude'],gir1['longitude'])
            self.point2 = Point(gir2['latitude'],gir2['longitude'])
            self.distance = self.distHaversine( self.point1,self.point2)
        else:
            self.distance = None
        return self.distance

    def distHaversine(self, p1, p2):
        """
        #  Calcul de la distance (en km) entre 2 points specifies par leurs
        #  latitude/longitude avec la formule de Haversine
        # 
        #   de : Haversine formula - R. W. Sinnott, "Virtues of the Haversine",
        #        Sky and Telescope, vol 68, no 2, 1984
        #        http://www.census.gov/cgi-bin/geo/gisfaq?Q5.1
        #  
        """
        dLat  = p2.lat - p1.lat
        dLong = p2.lon - p1.lon
        a = sin(dLat/2) * sin(dLat/2) + cos(p1.lat) * cos(p2.lat) * sin(dLong/2) * sin(dLong/2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = rt * c
        return  d

    def distCosineLaw(self,p1, p2):
        """
            # Calcul de la distance (en km) entre 2 points specifies par leurs
            # latitude/longitude en utilisant les fonctions trigonometriques
            #
        """
        d = acos(sin(p1.lat)*sin(p2.lat) + cos(p1.lat)*cos(p2.lat)*cos(p2.lon-p1.lon)) * rt
        return d



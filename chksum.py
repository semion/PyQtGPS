import string
import math

class NMEA:
#    def __init__(self):
#        self.prn = range(12)
#        self.elevation = range(12)
#        self.azimuth = range(12)
#        self.ss = range(12)
#        self.zs = range(12)
#        self.zv = range(12)
#        self.time = '?'
#        self.mode = 0
#        self.lat = 0.0
#        self.lon = 0.0
#        self.altitude = 0.0
#        self.track = 0.0
#        self.speed = 0.0
#        self.in_view = 0
#        self.SAT = 0
#        self.ZCH = 0
#        self.ZCHseen = 0
#        self.LATLON = 0

    def add_checksum(self,sentence):
        csum = 0
        for c in sentence:
            csum = csum ^ ord(c)
        print "%02X ADD" %csum
        return sentence + "%02X" % csum + "\r\n"

    def checksum(self,sentence, cksum):
        csum = 0
        for c in sentence:
            csum = csum ^ ord(c)
        print "%02X" %csum
        return ("%02X" % csum) == cksum

#    def update(self, lval, value, category):
#        if lval != value:
#            return (value, 1)
#        else:
#            return (lval, category)
#
#
#
#    def  do_lat_lon(self, words):
#        if words[0][-1] == 'N':
#            words[0] = words[0][:-1]
#            words[1] = 'N'
#        if words[0][-1] == 'S':
#            words[0] = words[0][:-1]
#            words[1] = 'S'
#        if words[2][-1] == 'E':
#            words[2] = words[2][:-1]
#            words[3] = 'E'
#        if words[2][-1] == 'W':
#            words[2] = words[2][:-1]
#            words[3] = 'W'
#        if len(words[0]):
#            lat = string.atof(words[0])
#            frac, intpart = math.modf(lat / 100.0)
#            lat = intpart + frac * 100.0 / 60.0
#            if words[1] == 'S':
#                lat = -lat
#            (self.lat, self.LATLON) = self.update(self.lat, lat, self.LATLON)
#        if len(words[2]):
#            lon = string.atof(words[2])
#            frac, intpart = math.modf(lon / 100.0)
#            lon = intpart + frac * 100.0 / 60.0
#            if words[3] == 'W':
#                lon = -lon
#            (self.lon, self.LATLON) = self.update(self.lon, lon, self.LATLON)

#$GPRMC,024932.992,V,4443.7944,N,07456.7103,W,,,270402,,*05
#$GPGGA,024933.992,4443.7944,N,07456.7103,W,0,00,50.0,192.5,M,,,,0000*27
#$GPGSA,A,1,,,,,,,,,,,,,50.0,50.0,50.0*05
#$GPGSV,3,1,09,14,77,023,,21,67,178,,29,64,307,,30,42,095,*7E
#$GPGSV,3,2,09,05,29,057,,11,15,292,,18,08,150,,23,08,143,*7A
#$GPGSV,3,3,09,09,05,052,*4B
#$GPRMC,024933.992,V,4443.7944,N,07456.7103,W,,,270402,,*04
#$GPGGA,024934.991,4443.7944,N,07456.7103,W,0,00,50.0,192.5,M,,,,0000*23
#$GPGSA,A,1,,,,,,,,,,,,,50.0,50.0,50.0*05

#        RMC - Recommended minimum specific GPS/Transit data
#        RMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68
#           225446       Time of fix 22:54:46 UTC
#           A            Navigation receiver warning A = OK, V = warning
#           4916.45,N    Latitude 49 deg. 16.45 min North
#           12311.12,W   Longitude 123 deg. 11.12 min West
#           000.5        Speed over ground, Knots
#           054.7        Course Made Good, True
#           191194       Date of fix  19 November 1994
#           020.3,E      Magnetic variation 20.3 deg East
#           *68          mandatory checksum
#    def processGPRMC(self, words):
#        global seconds
#        # the Navman sleeve's GPS firmware sometimes puts the direction in the wrongw ord.
#        day = string.atoi(words[8][0:2])
#        month = string.atoi(words[8][2:4])
#        year = 2000 + string.atoi(words[8][4:6])
#        hours = string.atoi(words[0][0:2])
#        minutes = string.atoi(words[0][2:4])
#        seconds = string.atoi(words[0][4:6])
#        if words[1] == "V" or words[1] == "A":
#            self.time = ("%02d/%02d/%04d %02d:%02d:%02d" %
#                (day, month, year, hours, minutes, seconds))
#            if words[6]: self.speed = string.atof(words[6])
#            if words[7]: self.track = string.atof(words[7])
#
#            self.do_lat_lon(words[2:])
#
##        GGA - Global Positioning System Fix Data
##        GGA,123519,4807.038,N,01131.324,E,1,08,0.9,545.4,M,46.9,M, , *42
##           123519       Fix taken at 12:35:19 UTC
##           4807.038,N   Latitude 48 deg 07.038' N
##           01131.324,E  Longitude 11 deg 31.324' E
##           1            Fix quality: 0 = invalid
##                                     1 = GPS fix
##                                     2 = DGPS fix
##           08           Number of satellites being tracked
##           0.9          Horizontal dilution of position
##           545.4,M      Altitude, Metres, above mean sea level
##           46.9,M       Height of geoid (mean sea level) above WGS84
##                        ellipsoid
##           (empty field) time in seconds since last DGPS update
##           (empty field) DGPS station ID number
#
#    def processGPGGA(self,words):
#        self.do_lat_lon(words[1:])
#
## sometimes I get the following, which of course produces an error when parsing the status:
##$GPGGA,051122.091,0000.0000,N,00000.0000,E0,,00,50.0,0.0,M,,,,0000*36
#        self.status = string.atoi(words[5])
#        self.satellites = string.atoi(words[6])
#        self.altitude = string.atof(words[8])
#
##        GSA - GPS DOP and active satellites
##        GSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
##           A            Auto selection of 2D or 3D fix (M = manual)
##           3            3D fix
##           04,05...     PRNs of satellites used for fix (space for 12)
##           2.5          PDOP (dilution of precision)
##           1.3          Horizontal dilution of precision (HDOP)
##           2.1          Vertical dilution of precision (VDOP)
##             DOP is an indication of the effect of satellite geometry on
##             the accuracy of the fix.
#    def processGPGSA(self,words):
#        (self.mode, self.LATLON) = self.update(self.mode, string.atof(words[1]), self.LATLON)
#        self.pdop = string.atof(words[14])
#        self.hdop = string.atof(words[15])
#        self.vdop = string.atof(words[16])
#
##        GSV - Satellites in view
##        GSV,2,1,08,01,40,083,46,02,17,308,41,12,07,344,39,14,22,228,45*75
##           2            Number of sentences for full data
##           1            sentence 1 of 2
##           08           Number of satellites in view
##           01           Satellite PRN number
##           40           Elevation, degrees
##           083          Azimuth, degrees
##           46           Signal strength - higher is better
##           <repeat for up to 4 satellites per sentence>
##                There my be up to three GSV sentences in a data packet
#    def processGPGSV(self,words):
#        n = string.atoi(words[1])
#        in_view = string.atoi(words[2])
#        (self.in_view, self.SAT) = self.update(self.in_view, in_view, self.SAT)
#
#        f = 3
#        n = (n - 1) * 4;
#        m = n + 4;
#
#        while n < in_view and n < m:
#            if words[f+0]:
#                (self.prn[n], self.SAT) = self.update(self.prn[n], string.atoi(words[f+0]), self.SAT)
#            if words[f+1]:
#                (self.elevation[n], self.SAT) = self.update(self.elevation[n], string.atoi(words[f+1]), self.SAT)
#            (self.azimuth[n], self.SAT) = self.update(self.azimuth[n],  string.atoi(words[f+2]), self.SAT)
#            if f + 3 < len(words) and words[f+3]:
#                (self.ss[n], self.SAT) = self.update(self.ss[n], string.atoi(words[f+3]), self.SAT)
#            f = f + 4
#            n = n + 1
#
##PRWIZCH - Rockwell Zodiac Proprietary
##Channel Information
##$PRWIZCH ,00,0,03,7,31,7,15,7,19,7,01,7,22,2,27,2,13,0,11,7,08,0,02,0*4C
##SATELLITE
##IDENTIFICATION NUMBER - 0-31
##SIGNAL QUALITY - 0 low quality - 7 high quality Repeats 12 tims.
#    def processPRWIZCH(self,words):
#        for i in range(12):
#            (self.zs[i], self.ZCH) = self.update(self.zs[i], string.atoi(words[2*i+0]), self.ZCH)
#            (self.zv[i], self.ZCH) = self.update(self.zv[i], string.atoi(words[2*i+1]), self.ZCH)
#        self.ZCHseen = 1;

    def handle_line(self, line):
        if line[0] == '$':
            line = string.split(line[1:], '*')
            if len(line) != 2: return
            print line
            return self.checksum(line[0], line[1])
#            if not self.checksum(line[0], line[1]):
            
#               print "BAD"
#               return "Bad checksum"
#            words = string.split(line[0], ',')
#            if NMEA.__dict__.has_key('process'+words[0]):
#                NMEA.__dict__['process'+words[0]](self, words[1:])
#            else:
#                return "Unknown sentence"
        else:
            return "Not NMEA"

#    def get_status(self,satellite):
#        if self.ZCHseen:
#            for i in range(12):
#                if satellite == self.zs[i]:
#                    return (self.zv[i] & 7) | 8
#            return 0
#        else:
#            for i in range(12):
#                if satellite == self.prn[i]:
#                    s = self.ss[i] / 6
#                    return min(s, 7)
#            return 0

nmea = NMEA()
#lines = [
#    "$GPGGA,000033.997,0000.0000,N,00000.0000,E,0,00,50.0,0.0,M,,,,0000*3C\n",
#    "$GPRMC,024932.992,V,4443.7944,N,07456.7103,W,,,270402,,*05\n",
#    "$GPGSA,A,1,,,,,,,,,,,,,50.0,50.0,50.0*05\n",
#    "$GPGSV,3,1,09,14,77,023,,21,67,178,,29,64,307,,30,42,095,*7E\n",
#    "$GPGSV,3,2,09,05,29,057,,11,15,292,,18,08,150,,23,08,143,*7A\n",
#    "$GPGSV,3,3,09,09,05,052,*4B\n",
#]
line = "$GPRMC,100643.000,A,5522.9036,N,03710.1282,E,0.16,119.11,200507,,*0D"
l1 = "$GPRMC,163032.000,A,3246.5298,N,03501.6924,E,0.09,6.14,200509,,*09"
l2 = "$GPRMC,163003.745,A,3246.5261,N,03501.6911,E,0.03,349.76,200509,,*0B"
l3 = "$GPRMC,163532.000,A,3246.3374,N,03502.5305,E,27.68,84.52,200509,,*0A"
if nmea.handle_line(l3):
    print "True"
else:
    print "False"
#print nmea.__dict__



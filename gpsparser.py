#!/usr/bin/env python

__version__ = '$Revision: 4799 $'.split()[1]
__date__ = '$Date: 2008-11-20 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__author__ = 'Val Schmidt'
__doc__ = '''
GPSparser, a Python GPS NMEA String parsing module. 

This module provides GPS NMEA string parsing through the GPSString
class. A GPSstring is an object whose I{msg} is any ASCII text string
containing a NMEA GPS string somewhere within it. NMEA strings
characteristicly start with the leading "$" and end with the *hh where
hh is the two character checksum. All of the following examples are fine:

    - C{$GPGGA,154809.00,4305.52462642,N,07051.89568468,W,1,3,4.1,48.971,M,-32.985,M,,*54}
    - C{RTK1_GPS         DATA    2008-11-21T15:48:10.510017      $GPGGA,154809.00,4305.52462642,N,07051.89568468,W,1,3,4.1,48.971,M,-32.985,M,,*5}
    - C{09/12/2003,04:01:46.666,$GPGGA,040145.871,7117.3458,N,15700.3788,W,1,06,1.4,014.6,M,-000.4,M,,*50}
    - C{posnav  2008:226:18:31:34.1365  $INGGA,183133.898,7120.91996,N,15651.72629,W,1,11,0.8,-1.06,M,,,,*19}

GPSparser provides methods for extracting the NMEA string from the
larger set of ASCII characters, verifying its checksum and parsing the
string's fields. The fields may then be accessed as attributes of GPSString
(i.e. C{GPSString.latitude}). The complete set of attributes available
after a string has been parsed can be found in the attribute list
C{GPSString.fieldnames}. Some fields are not returned, such as those that
provide units which, by standard or convention, never seem to change. 

GPSparser is designed for follow-on processing and plotting of values,
and therefore every effort is made to convert all fields to
meaningful, numeric values (objects of the Decimal Class). For example, Latitude and
Longitude are converted to decimal degrees to 10 digits past the
decimal point. Similarly, GPS fix type in RMC strings are indicated by an "A"
when the GPS has a fix and a "V" when it does not. These values are
reported by GPSParser as 1 and 0, respectively. 

Time in GPS strings are converted to datetime objects (see the
datetime module). Many NMEA strings contain time-of-day, but not date
(GGA for example). GPSparser will, by default, convert these strings
to datetime.time objects. However if the GPSString.date attribute is
set with a datetime.date object prior to calling the parse() method, a
full datetime.datetime object will be returned combining the supplied
date and time parsed from the string. This is a handy way to produce
full date-time stamps for each string.

A common thing to overlook, however, when parsing a file of strings
from a parent script, in which the times rotate over a UTC day, one
must be sure to also rotate the value used to set the GPSString.date
attribute.

When the module is called as a script, it will parse a file for a
single string type, which must be specified on the command-line (see
C{gpsparser.py -h}). The fields are written in tab-delimited format to
standard-out. Date-time stamps are written as tab-delimited vectors
(C{YYYY MM DD HH MM SS}). This format makes reading parsed data files
into Octave or MATLAB trivial ( C{load('datafile')} ), with the notable
exception of GSV strings which have variable numbers of fields
depending on the number of satellites tracked.

@author: U{'''+__author__+'''<http://aliceandval.com/valswork>}
@organization: Center for Coastal and Ocean Mapping, University of New Hampshire 
@version: ''' + __version__ +'''
@copyright: 2008
@status: under development
@license: GPL

@bug: I've tried to handle several fields gracefully when they are commonly missing, but an empty line with a proper checksum, such as is common before a GPS has a fix will surely cause the code to fail. 

@todo: Unit tests. There are none so far and there needs to be. 

'''

import os
import sys
import datetime
import re
import string
import decimal as dec
import pdb
from operator import xor
import exceptions 

class GPSString(object):
    '''
    A GPSString is any string that contains a complete NMEA string someplace 
    within it. The string must start with the leading $ and end with the *hh 
    where hh is the checksum. 
    '''
    GPS_IDs = { \
        'GGA' : 1, \
            'ZDA' : 2, \
            'RMC' : 3, \
            'GST' : 4, \
            'GSV' : 5, \
            'VTG' : 6, \
            'HDT' : 7 ,\
            'PASHR' : 8}


    def __init__(self,msg):
        '''
        Initializes the class with any string containing a single NMEA data string.

        @param msg: The ASCII string containing the NMEA data string.

        '''
        self.msg = msg
        'The message containing the gps string.'
        self.debug = False
        'A flag for writing debugging information'

    def identify(self):
        '''
        This method identifies the string within gps_string, returning an ID index
        which is required to parse the string. 
        
        Currently the following message types are supported:
        GGA, ZDA, RMC, GST, GSV, VTG, HDT, PASHR
        '''
        'A dictionary of supported strings and their numeric indentifiers'

        for key in self.GPS_IDs.keys():
            if re.search( key, self.msg):
                self.id = self.GPS_IDs[key]
                return self.GPS_IDs[key]

        raise NotImplementedError, ("This string is not recognized: " + self.msg)

    def parse(self):
        '''
        This method pareses a GPSString, defining a set of attributes for the class 
        with the parsing results. How each string is parsed is dependent on the
        type of string. In any case, the fields returned are defined in
        "self.fieldnames".

        Before parsing the string's checksum if verified. The GPSString.FailedChecksum 
        exception is raised if the checksum fails. [NOTE: The checksum verification
        may cause problems for some gps systems which do not calculate the checksum
        on the proper portion of the string. The NMEA standard specifies calculation 
        on the portions of the string  __between__ the leading "$" and "*", but 
        not to include either. ]

        A few general rules are in order. Time stamps are converted to datetime
        objects. Several GPS strings contain only time fields with no year, month,
        or day. If gps_string.date is defined with a datetime.date object (i.e.
        mygpsstring.date = datetime.date(2008,12,1) ) prior to calling the 
        parse() method, the final datetime object will combine the pre-set 
        date with the gps parsed time value. If gps_string.date is not defined
        the returned datetime object returned from the parse() method will 
        reflect the gps time as a datetime.time() object.

        Latitude and Longitude are converted to decimal degrees with negative 
        values for the Southern and Western hemispheres. They are reported to 8
        decimal places which equates to just over 1 mm precision.

        Some fields are not parsed because they do not typically change. The 
        units fields of meters for geoid separation in the GGA string is a classic
        example.

        '''

        ' Verify Checksum'
        if not self.checksum(True):
            raise self.FailedChecksum, ("Checksum: " + str(self.checksum()))


        ' If the string is already identified (self.id is set) go on, '
        ' if not, then identify it. This prevents the user from having to '
        ' identify it manually. '
        try:
            tmp = self.id
        except:
            self.identify()

        ' Parse the code'
        if self.id == 1:
            'GGA'
            exp = '(?P<match>\$..GGA.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                
                'Handle GGA Fields'
                self.handlegpstime(fields[1])                
                self.handle_lat( fields[2], fields[3] )
                self.handle_lon ( fields[4], fields[5] )
                self.quality = dec.Decimal( fields[6] )
                self.svs = dec.Decimal( fields[7] )
                self.hdop = dec.Decimal( fields[8]) 
                self.fixstatus = self.hdop <= 6
                self.antennaheightMSL = dec.Decimal(fields[9])
                try:
                    self.geoid = dec.Decimal(fields[11])
                except dec.InvalidOperation:
                    if self.debug:
                        print "The field GEOID Height may not be present."
                        print fields[11]
                        self.geoid = dec.Decimal('NaN')
                try:
                    self.dgpsage = dec.Decimal(fields[13])
                except dec.InvalidOperation:
                    if self.debug: 
                        print "The field DGPS Age may not be present."
                        print fields[13]
                        self.dgpspage = dec.Decimal('NaN')
                try:
                    self.stationid = dec.Decimal(fields[14] )
                except dec.InvalidOperation:
                    if self.debug: 
                        print "The field DGPS Station ID may not be present."
                        print fields[14]
                        self.stationid = dec.Decimal('NaN')
        elif self.id == 2:
            'ZDA'
            exp = '(?P<match>\$..ZDA.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                'Handle ZDA Fields'
                self.datetime = datetime.date(int( fields[4]), \
                                                  int(fields[3]), \
                                                  int(fields[2]))
                self.handlegpstime(fields[1])
                try:
                    self.tzoffsethours = dec.Decimal( fields[5] )
                except dec.InvalidOperation:
                    if self.debug:
                        print "Thef ield Local TZ Offset Hours may not be present."
                        print fields[5]
                        self.tzoffsethours = dec.Decimal('NaN')

                try:
                    self.tzoffsetminutes = dec.Decimal( fields[6] )
                except dec.InvalidOperation:
                    if self.debug: 
                        print "The field Local TZ Offset Minutes may not be present."
                        print fields[6]
                        self.tzoffsetminutes = dec.Decimal('NaN')


        elif self.id == 3:
            'RMC' 
            exp = '(?P<match>\$..RMC.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                chk_extract = m.group('chksum')
                #print self.msg
                #print gps_extract
                #print chk_extract
                fields = gps_extract.split(',')
                'Handle RMC Fields'
                'Getting the date first ensure handlegpstime will return a full'
                'datetime object'                
#                self.date = datetime.date(int(fields[9][4:6])+2000,
#                                   int(fields[9][2:4]),
#                                   int(fields[10][0:2]))
                self.handlegpstime(fields[1])
                if fields[2] == 'A':
                    self.fixstatus = 1
                else:
                    self.fixstatus = 0
                self.handle_lat(fields[3], fields[4])
                self.handle_lon(fields[5], fields[6])
                self.knots = dec.Decimal(fields[7])
                self.kmph = self.knots * dec.Decimal('1.85200')
                self.cog = fields[8]

        elif self.id == 4:
            'GST'
            exp = '(?P<match>\$..GST.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                'Handle GST Fields'
                self.handlegpstime(fields[1])
                self.residualrms = dec.Decimal(fields[2])
                self.semimajor = dec.Decimal(fields[3])
                self.semiminor = dec.Decimal(fields[4])
                self.orientation = dec.Decimal(fields[5])
                self.lat1sigma = dec.Decimal(fields[6])
                self.lon1sigma = dec.Decimal(fields[7])
                self.height1sigma = dec.Decimal(fields[8])

        elif self.id == 5:
            'GSV'
            exp = '(?P<match>\$..GSV.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                'Handle GSV Fields'
                self.messages = dec.Decimal( fields[1] )
                self.messagenum = dec.Decimal ( fields[2] )
                self.visibleSVs = dec.Decimal ( fields[3] )
                self.PRN = []
                self.elevation = []
                self.azimuth = []
                self.snr = []
                if self.debug: 
                    print fields
                for idx in range(4,fields.__len__() - 1, 4):
                    self.PRN.append(dec.Decimal(fields[idx]))
                    self.elevation.append(dec.Decimal(fields[idx + 1]))
                    try:
                        self.azimuth.append(dec.Decimal(fields[idx + 2]))
                    except dec.InvalidOperation:
                        self.azimuth.append(dec.Decimal('NaN'))
                        print "The field Satellite Azimuth may be missing."
                        print fields[idx + 3]
                    try:
                        self.snr.append(dec.Decimal(fields[idx + 3]))
                    except dec.InvalidOperation:
                        # The spec says snr should be null when "not tracking"
                        self.snr.append(dec.Decimal('NaN'))

        elif self.id == 6:
            'VTG'
            exp = '(?P<match>\$..VTG.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                'Handle VTG Fields'
                self.cog = dec.Decimal(fields[1])
                self.knots = dec.Decimal(fields[5])
                self.kmph = dec.Decimal(fields[7])
                

        elif self.id == 7:
            'HDT'
            exp = '(?P<match>\$..HDT.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                'Handle HDT Fields'
                self.heading = fields[1]
        elif self.id == 8:
            'PASHR'
            exp = '(?P<match>\$PASHR.*)\*(?P<chksum>..)'
            m = re.search(exp,self.msg)
            if m:
                gps_extract = m.group('match')
                fields = gps_extract.split(',')
                'Handle PASHR Fields'
                self.handlegpstime(fields[1])
                self.heading = dec.Decimal(fields[2])
                self.roll = dec.Decimal(fields[4])
                self.pitch = dec.Decimal(fields[5])
                self.heave = dec.Decimal(fields[6])
                self.rollaccuracy = dec.Decimal(fields[7])
                self.pitchaccuracy = dec.Decimal(fields[8])
                self.headingaccuracy = dec.Decimal(fields[9])
                self.headingalgorithm = dec.Decimal(fields[10])
                self.imustatus = dec.Decimal(fields[11])
        
        # Create a dictionary of the fields parsed.
        keys = self.__dict__.keys()
        keys.remove('debug')
        keys.remove('msg')
        keys.remove('id')
        self.fields = {}
        for item in keys:
            self.fields[item] = self.__getattribute__(item)

    def handlegpstime(self, timestr):
        '''
        An internal method to convert gps time strings to datetime.time objects 
        (default) or datetime.datetime objects when GPSString.date is pre-defined
        with a datetime.date object. 

        @param timestr: A NMEA time string of the form HHMMSS.SSS .

        Since many strings do not contain the date,
        defining the 'date' attribute of GPSString allows one to manually set 
        the date.
        '''
        tmptime = timestr
        hour = dec.Decimal(tmptime[0:2])
        try:
            minute = dec.Decimal(tmptime[2:4])
        except dec.InvalidOperation:
            print timestr
            print tmptime[2:4]
            print self.msg
            sys.exit()
            
        seconds = int(dec.Decimal(tmptime[4:tmptime.__len__()]))
        microseconds = int( (dec.Decimal(tmptime[4:tmptime.__len__()]) - \
                                 dec.Decimal(seconds) ) * 1000000 )

        timeval = datetime.time(hour, minute, seconds, microseconds)

        try:
            self.datetime = datetime.datetime.combine(self.date, timeval)
        except:
            self.datetime = timeval

    def handle_lat(self,lattmp, lathem):
        '''
        Converts latitude strings of arbitrary precision to decimal degrees to
        10 decimal places of precision (about .000001 meters).

        @param lattmp: The NMEA latitude string. (DDMM.MMMM)
        @param lathem: The NMEA latitude hemisphere ('N'/'S')
        '''
        self.latitude = '%.6f' % (dec.Decimal(lattmp[0:2]) + 
                         dec.Decimal(lattmp[2:lattmp.__len__()]) / 60)
        self.latitude = dec.Decimal(self.latitude)
        if lathem == 'S':
            self.latitude = - self.latitude

    def handle_lon(self,lontmp, lonhem):
        '''
        Converts longitude strings of arbitrary precision to decimal degrees to
        10 decimal places of precision (about .000001 meters at the equator).

        @param lontmp: The NMEA longitude string. (DDDMM.MMMM)
        @param lonhem: The NMEA longitude hemisphere ('E'/'W')
        '''
        self.longitude = '%.6f' % (dec.Decimal(lontmp[0:3]) + 
                          dec.Decimal(lontmp[3:lontmp.__len__()]) / 60)
        self.longitude = dec.Decimal(self.longitude)
        if lonhem == 'W':
            self.longitude = - self.longitude

    def stripisotime(self):
        '''
        Strips and ISO 8601 time stamp from the GPSString and returns a datetime
        object.

        For many scientific applications GPS strings are logged with the 
        logging computer's date-time stamp. When these time stamps are in 
        ISO 8601 format, this method will extract and parse them, returning a
        datetime object. 
        '''
        iso_exp = re.compile('(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)T(?P<hour>\d\\d):(?P<minute>\d\d):(?P<seconds>\d\d\.\d+)') 
        m = re.search(iso_exp,self.msg)
        if m:
            year =  int( m.group('year'))
            month = int( m.group('month'))
            day =   int( m.group('day'))
            hour =  int(m.group('hour'))
            minute = int(m.group('minute'))
            seconds = int(float(m.group('seconds')))
            microseconds = int( ( float(m.group('seconds')) - seconds ) * 1000000)
            dts = datetime.datetime(year, month, day, hour, minute, seconds, microseconds)
            return dts

    def datetimevec(self,dts):
        '''
        Converts a datetime stamp in the form of a datetime object to a
        tab-delimited vector of numeric values.

        @param dts: A datetime object.

        For many scientific applications one often desires to import data into MATLAB
        or Octave. A simple way to do that is to produce a tab-delimited date time 
        stamp of the form:

        YYYY    MH    DD    HR    MN    SS

        whiich can be converted to MATLABs internal representation of time with 
        datevec(). This method returns such as time stamp from a datetime object.
        '''
        return "\t".join(map(str,( dts.year, dts.month, dts.day, dts.hour, dts.minute, float(dts.second) + float(dts.microsecond) / 1000000 )))

    def checksum(self, verify = False):
        ''' 
        A function to calculate and return a checksum of a NMEA string.
 
        @param verify: When specified as True, checksum returns True/False
        rather than the acutal checksum value. 

        '''
        exp = '(?P<match>\$.*)\*(?P<chksum>..)'
        m = re.search(exp,self.msg)
        if m:                
            data = m.group('match')
            tmp = map(ord, data[1:])
            checksum = hex(reduce(xor, tmp))
            chk_extract = str(m.group('chksum'))
            #print "extract"+chk_extract
            if len(checksum[2:4].upper()) !=2:
                chk ="0%s"%checksum[2:4].upper()
                #print "BORIS %s"%chk
            else:
                chk = str(checksum[2:4].upper()) 
            #print chk_extract
            #print checksum[2:4].upper()
            #print "Checsum" +chk
            if verify:
                #return checksum[2:4].upper() == m.group('chksum')
                #return "%(#)02X" % checksum[2:4] == m.group('chksum')
                return chk == chk_extract
            else:
                return checksum[2:4].upper()

# I'm keeping this because I once had code that simply returned the checksum for
# a string (that may not be a well-formatted NMEA string) which is required above.
# I'm not convinced this level of generality is necessary or appropriate here just yet.

#        if data.find('*') != -1 :
#            hasstar = True
#            tmp = map(ord, data[1:data.index('*')])
#        else:
#            tmp = map(ord, data)
#            
#        checksum = reduce(xor, tmp)
#        checksum = hex(checksum)
#        return checksum[2:4]

    class FailedChecksum(Warning):
        '''
        A class creating the exception FailedChecksum, which is derived from the 
        standard exception.Warning. This exception is raised when a GPS string's
        checksum is incorrect indicating corruption to the data.  
        '''
        pass

######################################################################################
######################## Module Code Ends Here. ######################################
######################################################################################

#if __name__ == '__main__':
#
#    gpstmp = GPSString('')
#    supportedstrings = gpstmp.GPS_IDs.keys()
#    supportedstrings.sort()
#    supportedstrings = ' '.join(supportedstrings)
#
#    from optparse import OptionParser
#    optionparser = OptionParser(usage="%prog [options]",
#                           version="%prog "+__version__+' ('+__date__+')')
#    optionparser.add_option('-f','--filename', dest='filename',action='store',
#                       help='specify the filename')
#    optionparser.add_option('-s','--stringtype',dest='stringtype',action='store',
#                           type='string', help='specify which string to parse by specifying the three-letter identifier (Currently supported strings: '+ supportedstrings + ' )')
#
#    (options,args) = optionparser.parse_args()
#
#    filename = options.filename
#    stringtype = options.stringtype
#
#    for line in file(filename,'r'):
#        gps = GPSString(line)
#        try:
#            id = gps.identify()
#        except NotImplementedError:
#            sys.stderr.write('Unrecognized NMEA string.\n')
#            continue
#
#        'Only handle string specified'
#        if id != gps.GPS_IDs[stringtype]:
#            continue
#
#        'This will die silently if there is not pc timestamp.'
#        PCtime = gps.stripisotime()
#        
#        if id == 1:
#            try:
#                gps.date = PCtime.date()
#            except:
#                gps.date = datetime.datetime.utcnow().date()
#
#            try: 
#                gps.parse()
#            except gps.FailedChecksum:
#                sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
#                                  " :: " + gps.msg + '\n') 
#                continue
#            
#            fieldstoprint = [gps.datetimevec(PCtime), 
#                             gps.datetimevec(gps.datetime), 
#                             gps.latitude, 
#                             gps.longitude, 
#                             gps.quality,
#                             gps.svs, 
#                             gps.hdop, 
#                             gps.antennaheightMSL,
#                             gps.geoid]
#            print "\t".join(map(str,fieldstoprint)).expandtabs()
#
#        if id == 2:
#            try:
#                gps.date = PCtime.date()
#            except:
#                gps.date = datetime.datetime.utcnow().date()
#
#            try: 
#                gps.parse()
#            except gps.FailedChecksum:
#                sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
#                                  " :: " + gps.msg + '\n') 
#
#                continue
#
#            fieldstoprint = [gps.datetimevec(PCtime),
#                             gps.datetimevec(gps.datetime)]
#
#            print "\t".join(map(str,fieldstoprint)).expandtabs()
#
#        if id == 3:
#            try:
#                gps.date = PCtime.date()
#            except:
#                gps.date = datetime.datetime.utcnow().date()
#            try:
#                gps.parse()
#            except self.FailedChecksum:
#                sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
#                                  " :: " + gps.msg + '\n') 
#                continue
#
#            fieldstoprint = [gps.datetimevec(PCtime),
#                             gps.datetimevec(gps.datetime),
#                             gps.fixstatus,
#                             gps.latitude,
#                             gps.longitude,
#                             gps.knots,
#                             gps.cog]
#            print "\t".join(map(str,fieldstoprint)).expandtabs()
#
#        if id == 4:
#            try:
#                gps.date = PCtime.date()
#            except:
#                gps.date = datetime.datetime.utcnow().date()
#
#            try:
#                gps.parse()
#            except self.FailedChecksum:
#                sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
#                                  " :: " + gps.msg + '\n') 
#                continue
#            
#            fieldstoprint = [gps.datetimevec(PCtime),
#                             gps.datetimevec(gps.datetime),
#                             gps.residualrms,
#                             gps.semimajor,
#                             gps.semiminor,
#                             gps.orientation,
#                             gps.lat1sigma,
#                             gps.lon1sigma,
#                             gps.height1sigma]
#            print "\t".join(map(str,fieldstoprint)).expandtabs()
#                              
#        if id == 5:
#            try:
#                gps.date = PCtime.date()
#            except:
#                gps.date = datetime.datetime.utcnow().date()
#
#            try: 
#                gps.parse()
#            except self.FailedChecksum:
#                sys.stderr.write( "Failed Checksum: " + gps.checksum() + 
#                                  " :: " + gps.msg + '\n') 
#                continue
#
#            fieldstoprint = ([gps.datetimevec(PCtime)] +  
#                             map(str,gps.PRN) +
#                             map(str,gps.elevation) +
#                             map(str,gps.azimuth) +
#                             map(str,gps.snr) )
#            print "\t".join(map(str,fieldstoprint)).expandtabs()
#
#
#        if id == 6:
#            try:
#                gps.parse()
#            except self.FailedChecksum:
#                sys.stderr.write( "Failed Checksum:" + gps.checksum() + 
#                                  "::" + gps.msg + '\n') 
#                continue
#
#
#        
#        if id == 8:
#            try:
#                gps.parse()
#            except self.FailedChecksum:
#                sys.stderr.write( "Failed Checksum:" + gps.checksum() + 
#                                  "::" + gps.msg + '\n') 
#                continue

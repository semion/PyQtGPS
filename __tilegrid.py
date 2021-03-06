#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, math
import decimal as dec
from globalmaptiles import GlobalMercator
from PyQt4 import QtCore, QtGui

class TileGrid(object):
    def __init__(self, parentgeometry, bearing = 0.0, zoomlevel = 17, lat = dec.Decimal('32.330347'), lon = dec.Decimal('34.851395')):
    #def __init__(self, parentgeometry, bearing = 0.0, zoomlevel = 16, lat = dec.Decimal('32.330347'), lon = dec.Decimal('34.851395')):                
    #def __init__(self, parentgeometry, bearing = 0.0, zoomlevel = 16, lat = dec.Decimal('32.809248'), lon = dec.Decimal('35.109293')):            
        #set initial values
        self.bearing = bearing
        self.zoomlevel = zoomlevel
        self.lat = lat
        self.lon = lon
        self.gx, self.gy = None, None
        
        self.destlat = dec.Decimal('32.776250')
        self.destlon = dec.Decimal('35.028946')
        
        self.distance = 0

        self.boundx, self.boundy = parentgeometry.width(), parentgeometry.height()
        
        self.sysPath = os.path.join(sys.path[0], "")      
        
        #make GlobalMercator instance        
        self.mercator = GlobalMercator()       
        self.moveTo(lat, lon)        
        
               
    def setBounds(self, newx, newy):
        self.boundx, self.boundy = newx, newy      
        
    def getOffset(self):
        'get pixel offset of coordinates from 0,0 of tile'
        offpx = int(self.px) - int(self.tx) * self.mercator.tileSize        
        #the y pixel coordinate system begins from top
        offpy = self.mercator.tileSize - ( int(self.py) - int(self.ty) * self.mercator.tileSize )
        return offpx, offpy
    
    def moveTo(self, lat, lon):
        'move position to lat, lon and update all properties'
        #update bearing from previous position        
        self.bearing = math.degrees(math.atan2(lon - self.lon, lat - self.lat))
        if self.bearing < 0:
            self.bearing += 360
        
        self.lat = lat
        self.lon = lon
                
        #get meters from lat/lon
        mx, my = self.mercator.LatLonToMeters( float(self.lat), float(self.lon) )
        
        dx, dy = self.mercator.LatLonToMeters( float(self.destlat), float(self.destlon) )
        
        self.distance = math.sqrt(math.pow(mx-dx, 2) + math.pow(my-dy, 2 ))
               
        #get pixels from meters
        self.px,  self.py = self.mercator.MetersToPixels(mx, my, self.zoomlevel)
        
        #get tile from pixels
        self.tx, self.ty = self.mercator.PixelsToTile( int(self.px), int(self.py) )
        
        #get google tile
        self.gx, self.gy = self.mercator.GoogleTile(self.tx, self.ty, self.zoomlevel)
        
        #update offset of tile
        self.offpx, self.offpy = self.getOffset()

#TODO:  calculate loadRect bounds for peripherial tiles
        
        self.sizex = math.ceil(self.boundx/self.mercator.tileSize)+1
        self.sizey = math.ceil(self.boundy/self.mercator.tileSize)+1
        
        #print "grid size: %ix%i" % (self.sizex, self.sizey)
        
        halfdeltax = int(math.ceil(self.sizex/2))
        halfdeltay = int(math.ceil(self.sizey/2))
        
        self.images = set()
        
        offtilex = halfdeltax * int(self.mercator.tileSize) + int(self.offpx)
        for x in range(self.gx-halfdeltax, self.gx+halfdeltax+1):
            offtiley = halfdeltay * int(self.mercator.tileSize) + int(self.offpy)
            for y in range(self.gy-halfdeltay, self.gy+halfdeltay+1):
                #fname = "D:\israel\streetmap\%i\israel streetmap\gm_%i_%i_%i.png" % (self.zoomlevel, x, y, self.zoomlevel)
                fname = "D:\israel\streetmap\Natanya\%i\Natanya streetmap\gm_%i_%i_%i.png" % (self.zoomlevel, x, y, self.zoomlevel)
                #fname = "d:\PyGps\workspace\PyGPS\src\%i\%i_%i_%i.png" % (self.zoomlevel, self.zoomlevel, x, y)
                #fname = "D:\terraIsrael\15\ISRAEL_TER_15\gt_%i_%i_%i.png" % (x, y, self.zoomlevel)
                #fname = "d:\PyGps\workspace\PyGPS\src\406.png"
                #if not QtCore.QFile.exists(self.sysPath + fname):
                print fname
                if not QtCore.QFile.exists(fname):
                    
                    fname = "404.png"
                  
                
                self.images.add("%i,%i,%s" % (offtilex, offtiley, fname))
                
                offtiley -= self.mercator.tileSize
            offtilex -= self.mercator.tileSize
        
        
    def refresh(self):
        lat, lon = self.lat, self.lon
        self.moveTo(lat, lon)
        
    def setZoom(self, zoom):
        self.zoomlevel = zoom
        self.refresh() 
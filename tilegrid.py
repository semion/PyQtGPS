#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, math, decimal
#import decimal
from globalmaptiles import GlobalMercator
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
class TileGrid(object):
    #def __init__(self, parentgeometry, bearing = 0.0, zoomlevel = 16, lat = dec.Decimal('32.829608'), lon = dec.Decimal('35.080498')):        
    #def __init__(self, parentgeometry, bearing = 0.0, zoomlevel = 16, lat = dec.Decimal('32.330347'), lon = dec.Decimal('34.851395')):
    def __init__(self, bearing = 0.0, zoomlevel = 16, lat = decimal.Decimal('32.018300'), lon = decimal.Decimal('34.898161'), parent = None):                   
        #set initial values
        self.parent = parent
        self.bearingSensitivity = decimal.Decimal('0.00001')
        self.bearing = bearing
        self.zoomlevel = zoomlevel
        self.lat = lat
        self.lon = lon
        self.gx, self.gy = None, None
        self.velocity = 0.0

        self.sysPath = os.path.join(sys.path[0], "")

        self.mapPath = self.sysPath
        self.maxZoomLevel = 16
        
        self.destlat = decimal.Decimal('32.776250')
        self.destlon = decimal.Decimal('35.028946')
        
        self.distance = 0

        self.setBounds(parent.geometry().width(), parent.geometry().height())
              
        self.halfboundx = math.ceil(self.boundx/2)
        self.halfboundy = math.ceil(self.boundy/2)
 
        #make GlobalMercator instance        
        self.mercator = GlobalMercator()
#        create pathways    
        self.refresh()    
    
    def setMapPath(self, path):
        if path != "":
            self.mapPath = path+"/"
        print self.mapPath        
               
    def setBounds(self, newx, newy):
        self.boundx, self.boundy = newx, newy
#        adding 16px to halfbounds height and width to display icons
        self.halfboundx = int(math.ceil(self.boundx/2))+31
        self.halfboundy = int(math.ceil(self.boundy/2))+31      
        
    def getOffset(self):
        'get pixel offset of coordinates from 0,0 of tile'
        offpx = self.px - self.tx * self.mercator.tileSize        
        #the y pixel coordinate system begins from top
        offpy = self.mercator.tileSize - ( self.py - self.ty * self.mercator.tileSize )
        return offpx, offpy
    
    def moveTo(self, lat, lon, calculateBearing = True):
        'move position to lat, lon and update all properties'
        #update bearing from previous position
        if calculateBearing:
            if abs(lon - self.lon) > self.bearingSensitivity \
            or abs(lat - self.lat) > self.bearingSensitivity:        
                self.bearing = math.degrees(math.atan2(lon - self.lon, lat - self.lat))
                if self.bearing < 0:
                    self.bearing += 360
        
        self.lat = lat
        self.lon = lon
                
        #get meters from lat/lon
        mx, my = self.mercator.LatLonToMeters( float(self.lat), float(self.lon) )
        
        #dx, dy = self.mercator.LatLonToMeters( float(self.destlat), float(self.destlon) )
        
        #self.distance = math.sqrt(math.pow(mx-dx, 2) + math.pow(my-dy, 2 ))
               
        #get pixels from meters
        self.px,  self.py = self.mercator.MetersToPixels(mx, my, self.zoomlevel)
        
        #get tile from pixels
        self.tx, self.ty = self.mercator.PixelsToTile( int(self.px), int(self.py) )
        
        #get google tile
        self.gx, self.gy = self.mercator.GoogleTile(self.tx, self.ty, self.zoomlevel)
        
        #update offset of tile
        self.offpx, self.offpy = self.getOffset()

#TODO:  calculate loadRect bounds for peripherial tiles
        
        self.sizex = int(math.ceil(self.boundx/self.mercator.tileSize))+1
        self.sizey = int(math.ceil(self.boundy/self.mercator.tileSize))+1
        
        halfdeltax = int(math.ceil(self.sizex/2))+1
        halfdeltay = int(math.ceil(self.sizey/2))+1
        
        self.images = set()
        
        offtilex = halfdeltax * self.mercator.tileSize + self.offpx
        for x in range(self.gx-halfdeltax, self.gx+halfdeltax+1):
            offtiley = halfdeltay * self.mercator.tileSize + self.offpy
            for y in range(self.gy-halfdeltay, self.gy+halfdeltay+1):
                fname = "%i/gm_%i_%i_%i.png" % (self.zoomlevel, x, y, self.zoomlevel)
                if not QtCore.QFile.exists(self.mapPath+fname):
                    fname = "404.png"                
                self.images.add((QtCore.QPointF(-offtilex, -offtiley), fname))              
                offtiley -= self.mercator.tileSize
            offtilex -= self.mercator.tileSize
#            print fname
            
            
        self.bounds = {'TL':(self.px-self.halfboundx, self.py-self.halfboundy),
                       'TR':(self.px+self.halfboundx, self.py-self.halfboundy),
                       'BR':(self.px+self.halfboundx, self.py+self.halfboundy),
                       'BL':(self.px-self.halfboundx, self.py+self.halfboundy) }

        
        self.pathways = QtGui.QPolygonF()
#        create waypoints icons
        self.visible_waypoints = set()
        for wp in self.waypoints_pixels:
            x = wp[0]-self.px
            y = self.py-wp[1]
            self.pathways.append(QtCore.QPointF(x,y))
            if self.isVisible(wp):
                self.visible_waypoints.add(QtCore.QPointF(x-15,y-32))
            
#        print self.waypoints_pixels
                
        
    def isVisible(self, wp):
        return  wp[0] > self.bounds['TL'][0] and \
                wp[0] < self.bounds['TR'][0] and \
                wp[1] > self.bounds['TL'][1] and \
                wp[1] < self.bounds['BL'][1]        
      
        
    def refresh(self):
        self.waypoints_pixels = set()
        for wp in self.parent.waypoint:
            wpm = self.mercator.LatLonToMeters(wp[0], wp[1])
            wppx = self.mercator.MetersToPixels(wpm[0], wpm[1], self.zoomlevel)
            self.waypoints_pixels.add(wppx)
        self.moveTo(self.lat, self.lon)
        
    def setZoom(self, zoom):
        self.zoomlevel = zoom
        self.refresh()
        
    def zoomIn(self):
        if self.zoomlevel < self.maxZoomLevel:
            self.zoomlevel +=1
            self.refresh()
    
    def zoomOut(self):
        if self.zoomlevel > 0:
            self.zoomlevel -= 1
            self.refresh()
        
    def setBearing(self, bear):
        self.bearing = bear
    
    def setVelocity(self, vel):
        self.velocity = vel 
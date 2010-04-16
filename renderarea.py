#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os
from PyQt4 import QtCore, QtGui
from tilegrid import TileGrid

class RenderArea(QtGui.QWidget):
    #set of points to draw Heading and Bearing arrows
    points = QtGui.QPolygon([
        QtCore.QPoint(0, -15),
        QtCore.QPoint(-15, 15),
        QtCore.QPoint(0, 0),
        QtCore.QPoint(15, 15)
    ])

    
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
       
        self.tilegrid = TileGrid(parent=parent)
        
        self.sysPath = os.path.join(sys.path[0], "")
        
        #load map tile into pixmap
        self.setBackgroundRole(QtGui.QPalette.Base)
    
    def minimumSizeHint(self):
        return QtCore.QSize(256, 256)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def paintEvent(self, event):
        #create instance of QPainter
        painter = QtGui.QPainter() 
 
        #begin paint
        painter.begin(self)        
        
        #set anti-aliasing hint
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.translate(0,0)
#        move coordinates origin to center of renderArea
        painter.translate(self.width()/2, self.height()/2)
        
        for img in self.tilegrid.images:
            p, fname = img    
            image = QtGui.QImage()
            image.load(self.tilegrid.mapPath+fname)
#            draw image with offset
            painter.drawImage(p, image)
            
        painter.setPen(QtGui.QPen(QtCore.Qt.green, 4, QtCore.Qt.DotLine))    
        painter.drawPolyline(self.tilegrid.pathways)
        
        image = QtGui.QImage()
        image.load("./wp.png")
        for wp in self.tilegrid.visible_waypoints:
            painter.drawImage(wp, image)
        
  
        
        #rotate painter coordinates system according to current bearing
        painter.rotate(float(self.tilegrid.bearing))
        
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 2, QtCore.Qt.SolidLine))
        
        #draw bearing arrow from set of points
        painter.drawPolygon(RenderArea.points)
        

        painter.end()
        
#        del painter


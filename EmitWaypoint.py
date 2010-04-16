'''
Created on 07/11/2009

@author: Boris
'''
#from PyQt4.QtCore import  *
from __future__ import division
import sys
import bluetooth
from PyQt4.QtCore import  *
from PyQt4.QtGui import *
from renderarea import RenderArea


class EmitWaypoints(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.wayPointFlag=False
    
    def emitNow(self):
#        self.wayPointFlag=True
        self.emit(SIGNAL('waypointset'),())
#        self.emit(SIGNAL('btn_on'),())
        print "Emitted"

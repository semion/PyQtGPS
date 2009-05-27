#!/usr/bin/python
# -*- coding: UTF-8 -*-

from PyQt4 import QtCore, QtGui
import sys

class Satellites(QtGui.QWidget):
    def __init__(self, parent = None, satellitesList = None):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(0,0,220,220)
        
        
    def paintEvent(self, event):
        
        painter = QtGui.QPainter() 
 
        painter.begin(self)        
        
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        painter.translate(10,10)
        
        painter.drawEllipse(50,50,100,100)
        painter.drawEllipse(0,0,200,200)
        
        painter.end()
        
#    $GPGSV,3,1,10,32,50,300,25,11,50,309,20,19,44,213,19,14,37,042,*70
#    $GPGSV,3,2,10,31,30,120,,20,24,281,25,03,21,191,,22,14,069,*70
#    $GPGSV,3,3,10,06,13,179,,23,11,218,20*7B 

      
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    sats = Satellites()
    sats.show()
    sys.exit(app.exec_())
        
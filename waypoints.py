'''
Created on 30/10/2009

@author: Boris
'''
from __future__ import division
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from PyQt4 import QtSql
from PyQt4 import QtCore,QtGui

import sqlite3
import os, sys
import decimal
import re

ID, port_id, finalLat, finalLng, countryName, country_id = range(6)

class AirPort(QDialog):
    def __init__(self, parent=None):
        
        super(AirPort, self).__init__(parent)
#        self.em = EmitWaypoints()
        self.waypointFlag = False
        
    def startRun(self, way):
        self.setModal(True)
        self.lat=""
        self.lng=""
        
        self.waypoints = way
        self.setWindowTitle("Waypoints")
        self.countryCombo = QComboBox()
        self.portCombo = QComboBox()
        
        self.btnCancel = QPushButton("Cancel")
        self.btnAdd = QPushButton("Add Waypoint")
        self.btnRemove = QPushButton("Remove Waypoint")
        self.btnFinish = QPushButton("Finish")
        
        self.txtLat = QLineEdit()
        self.txtLng = QLineEdit()
        
        self.tblWaypoints = QTableWidget ()
        
        
        
        
        
        self.lblCountry = QLabel("Select your Country destination")
        self.lblCountry.setBuddy(self.countryCombo)
        self.lblPort = QLabel("Select your Air port destination" )
        self.lblPort.setBuddy(self.portCombo)
        self.lblLat = QLabel("Latitude")
        self.lblLat.setBuddy(self.txtLat)
        self.lblLng = QLabel("Longtitude")
        self.lblLng.setBuddy(self.txtLng)
        self.lblWaypoints = QLabel("Waypoints")
        self.lblWaypoints.setBuddy(self.tblWaypoints)
        
        
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.lblCountry)
        vlayout.addWidget(self.countryCombo)
        vlayout.addWidget(self.lblPort)
        vlayout.addWidget(self.portCombo)
        
        self.vgroup = QGroupBox()
        self.vgroup.setLayout(vlayout)
        
        self.latlntgroup = QGroupBox()
        gridLatLon = QGridLayout()
        gridLatLon.addWidget(self.lblLat, 0,0)
        gridLatLon.addWidget(self.lblLng, 0,1)
        gridLatLon.addWidget(self.txtLat, 1,0)
        gridLatLon.addWidget(self.txtLng, 1,1)
        gridLatLon.addWidget(self.btnAdd,1,2)
        self.latlntgroup.setLayout(gridLatLon)
        
        self.tabllayout = QGroupBox()
        gridTable = QVBoxLayout()
        gridTable.addWidget(self.lblWaypoints)
        gridTable.addWidget(self.tblWaypoints)
        gridTable.addWidget(self.btnRemove)
        self.tabllayout.setLayout(gridTable)
        
        self.btnLayout = QGroupBox()
        hBtn = QHBoxLayout()
        hBtn.addWidget(self.btnCancel)
        hBtn.addWidget(self.btnFinish)
        self.btnLayout.setLayout(hBtn)
        
        grid = QGridLayout()
        grid.addWidget(self.vgroup, 0,0)
        grid.addWidget(self.tabllayout, 0,1)
        grid.addWidget(self.latlntgroup, 1,0)
        grid.addWidget(self.btnLayout, 2,0)
        
        self.setLayout(grid)
        
    
        self.setVisible(True)
        
        
        self.model = QSqlRelationalTableModel(self)
        self.model.setTable("country")
        self.model.setRelation(country_id,QSqlRelation("country", "country_id", "country_name"))
        self.model.select()
        
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.mapper.setModel(self.model)
        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))
        relationModel = self.model.relationModel(country_id)
        self.countryCombo.setModel(relationModel)
        self.countryCombo.setModelColumn(relationModel.fieldIndex("country_name"))
        self.mapper.addMapping(self.countryCombo, country_id)
        self.mapper.toFirst()
        
        
        
        self.port()
        
        
        self.connect(self.countryCombo, SIGNAL("currentIndexChanged(int)"), self.port)
        self.connect(self.portCombo, SIGNAL("currentIndexChanged(int)"), self.coordinates)
        self.connect(self.btnAdd, SIGNAL("clicked()"),self.add)
        self.connect(self.btnRemove, SIGNAL("clicked()"),self.removeRow)
        self.connect(self.btnFinish, SIGNAL("clicked()"),self.finish)
        self.connect(self.btnCancel, SIGNAL("clicked()"),self.cancel)
        
    def cancel(self):
        self.waypoints = []
        self.close()              
    
    
    def populateTable(self):
    
        self.tblWaypoints.clear()
        self.tblWaypoints.setSortingEnabled(False)
        self.tblWaypoints.setRowCount(len(self.waypoints))
        self.tblWaypoints.setColumnCount(2)
        headers = ["Latitude","Longtitude"]
        self.tblWaypoints.setHorizontalHeaderLabels(headers)
        self.tblWaypoints.setColumnWidth(320,0)
        self.tblWaypoints.setAlternatingRowColors(True)
        self.tblWaypoints.setSelectionBehavior(QTableWidget.SelectRows)
        self.tblWaypoints.setSelectionMode(QTableWidget.SingleSelection)
        selected = None
        
        for row in range(0,len(self.waypoints)):
            item =QTableWidgetItem(self.waypoints[row][0])
            item.setTextAlignment(Qt.AlignCenter)
            self.tblWaypoints.setItem(row, 0, item)
            item = QTableWidgetItem(self.waypoints[row][1])
            item.setTextAlignment(Qt.AlignCenter)
            self.tblWaypoints.setItem(row, 1, item)
            
        
        
        
        
    def removeRow(self):
        if self.tblWaypoints.currentRow() != -1:
            del self.waypoints[self.tblWaypoints.currentRow()]
        self.populateTable()
    
    
    def add(self):
        re1='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])' 
        lat = self.txtLat.text()
        lng = self.txtLng.text()
        rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
        m = rg.search(lat)
        n = rg.search(lng)
        if m and n:
            tempLat = m.group(1)
            tempLat = decimal.Decimal(str(tempLat))
            tempLng = n.group(1)
            tempLng = decimal.Decimal(str(tempLng))
            if tempLat >= -90 and tempLat <= 90 and tempLng >= -180 and tempLng <= 180 :
                              
                self.waypoints.append((str(tempLat),str(tempLng)))
                self.txtLat.clear()
                self.txtLng.clear()
                self.populateTable()
            else:
                QMessageBox.warning(self, self.trUtf8("Incorrect values"),self.trUtf8(u"Valid values are:\n Latitude: form -90\u00BA to 90\u00BA\n Longtitude: form -180\u00BA to 180\u00BA"))
        else:
            QMessageBox.warning(self, self.trUtf8("Incorrect values"),self.trUtf8(u"Input data are blank or in wrong format! \n Correct input for example is:\n Latitude: 32.546544  Longtitude: 29.987678"))
    def port(self):
        cName = self.countryCombo.currentText()
        self.portCombo.clear()
        query = QSqlQuery()
        query.exec_("SELECT country_id FROM country WHERE (country_name = '%s')" % cName)
        while query.next():
            id = query.value(ID).toInt()[0]
            cn = unicode(query.value(port_id).toString())
#            print id
#            print cn
            subquery = QSqlQuery("SELECT * FROM port " "WHERE country_id = %d" % id)
            
            while subquery.next():
                pn = unicode(subquery.value(2).toString())
                self.portCombo.addItem(pn)
        
                
    
    def coordinates(self):
        coord = self.portCombo.currentText()
        if coord:
            
            query1 = QSqlQuery()
            query1.exec_("SELECT lat, lng FROM port " "WHERE (port_name = '%s')" % coord)
            while query1.next():
                self.lat = query1.value(0).toString()
                self.lng = query1.value(1).toString()
            
        else:
            self.lat=""
            self.lng=""
    def finish(self):
        if self.lat != "" and self.lng != "":
            self.waypoints.append((str(self.lat),str(self.lng)))
            self.waypointFlag = True
            self.emit(SIGNAL('waypointset'),())
#            self.em.emitNow() 
#            return self.waypoints 
#            self.populateTable()
#        return self.waypoints
        else:
            self.waypointFlag = False
        self.close()
#class EmitWaypoint():
#    def __init__(self, parent=None):
#        pass
#    
#    def emitNow(self):
#        self.emit(SIGNAL('waypointset'),())


  
        

#form = AirPort()        
#form.show
##app.exec_()        
#sys.exit(app.exec_())
        
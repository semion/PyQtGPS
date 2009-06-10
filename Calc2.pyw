'''
Created on 02.05.2009

@author: Boris
'''
from __future__ import division
import sys
from math import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Form(QDialog):
    def __init__(self, parent= None):
        super(Form, self).__init__(parent)
        self.btn1 = QPushButton("1")
        self.btn2 = QPushButton("2")
        self.btn3 = QPushButton("3")
        self.btn4 = QPushButton("4")
        self.btn5 = QPushButton("5")
        self.btn6 = QPushButton("6")
        self.btn7 = QPushButton("7")
        self.btn8 = QPushButton("8")
        self.btn9 = QPushButton("9")
        self.btn0 = QPushButton("0")
        self.btnClear = QPushButton("C")
        self.btnDot = QPushButton(".")
        self.btnMul = QPushButton("*")
        self.btnDiv = QPushButton("/")
        self.btnAdd = QPushButton("+")
        self.btnSub = QPushButton("-")
        self.btnEven = QPushButton("=")
        self.btnRp = QPushButton(")")
        self.btnLp = QPushButton("(")
        self.btnSqrt = QPushButton("sqrt")
        self.btnGroup = QGroupBox()
        btnlayout=QGridLayout()
        btnlayout.addWidget(self.btn7, 0, 0)
        btnlayout.addWidget(self.btn8, 0, 1)
        btnlayout.addWidget(self.btn9, 0, 2)
        btnlayout.addWidget(self.btnDiv, 0, 3)
        btnlayout.addWidget(self.btn4, 1, 0)
        btnlayout.addWidget(self.btn5, 1, 1)
        btnlayout.addWidget(self.btn6, 1, 2)
        btnlayout.addWidget(self.btnMul, 1, 3)
        btnlayout.addWidget(self.btn1, 2, 0)
        btnlayout.addWidget(self.btn2, 2, 1)
        btnlayout.addWidget(self.btn3, 2, 2)
        btnlayout.addWidget(self.btnSub, 2, 3)
        btnlayout.addWidget(self.btn0, 3, 1)
        btnlayout.addWidget(self.btnClear, 4, 3)
        btnlayout.addWidget(self.btnDot, 4, 2)
        btnlayout.addWidget(self.btnAdd, 3, 3)
        btnlayout.addWidget(self.btnRp, 3, 2)
        btnlayout.addWidget(self.btnLp, 3, 0)
        btnlayout.addWidget(self.btnSqrt, 4, 1) 
        btnlayout.addWidget(self.btnEven, 4, 0)
        self.btnGroup.setLayout(btnlayout)
               
        self.browser = QTextBrowser()
        self.lineedit = QLineEdit()#"Type an Expression and press Enter")
        self.lineedit.selectAll()
        groupLayout = QGroupBox()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        groupLayout.setLayout(layout)
        
        mlayout = QGridLayout()
        mlayout.addWidget(groupLayout, 0, 0)
        mlayout.addWidget(self.btnGroup, 0, 1)
        
        self.setLayout(mlayout)
        self.lineedit.setFocus()
        self.connect(self.btn0, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn1, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn2, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn3, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn4, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn5, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn6, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn7, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn8, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btn9, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnAdd, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnDiv, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnDot, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnMul, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnSub, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnLp, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnRp, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnSqrt, SIGNAL("clicked()"), self.updateLine)
        self.connect(self.btnClear, SIGNAL("clicked()"), self.lineedit.clear) 
        self.connect(self.btnEven, SIGNAL("clicked()"), self.updateUi)
        self.connect(self.lineedit, SIGNAL("returnPressed()"),self.updateUi)
        self.setWindowTitle("Boris's Calculator")
        
    
    def updateLine(self):
        try:
            button = self.sender()
            if button is None or not isinstance(button, QPushButton):
                return
            ltext=unicode(self.lineedit.text())
            ltext=ltext+ button.text()
            self.lineedit.setText(unicode(ltext))
        except:
            print ltext+"<font color=red><b> ERROR</b></font>"
    
    def updateUi(self):
        try:
            text = unicode(self.lineedit.text())
            self.browser.append("{0} = <b>{1}</b>".format(text,eval(text)))
            self.lineedit.clear()
        except:
            self.browser.append("<font color=red>{0} is invalid!</font>"
                                .format(text))
app=QApplication(sys.argv)
form= Form()
form.show()
app.setStyleSheet(open("./calc2.qss","r").read())
app.exec_()
    
        
        
                     
        
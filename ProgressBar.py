
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore


class ProgressBar(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

#        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Scanning For Devices')

        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        
        self.button = QtGui.QPushButton('Start', self)
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.move(40, 80)
        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.onStart)

#        self.setWindowModality(QtCore.Qt.WindowModal)
        self.timer1 = QtCore.QBasicTimer()
        self.step = 0;
        
#        self.timer1.start(100,self)

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer1.stop()
            return
        self.step = self.step + 1
        self.pbar.setValue(self.step)

    def onStart(self):
        if self.timer1.isActive():
            self.timer1.stop()
            self.button.setText('Start')
        else:
            self.timer1.start(100, self)
            self.button.setText('Stop')

#app = QtGui.QApplication(sys.argv)
#icon = ProgressBar()
#icon.show()
#app.exec_()

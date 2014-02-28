'''
DCCUI - ParamEdit
---------------
A window for editing node parameters. 
'''

from PySide import QtCore, QtGui


class NodeParam(QtGui.QWidget):
    def __init__(self, parent=None):
        super(NodeParam, self).__init__(parent)


class ParamEdit(QtGui.QFrame):
    def __init__(self, parent=None):
        super(ParamEdit, self).__init__(parent)

        #self.scrollArea = QtGui.QScrollArea()
        self.paramVbox = QtGui.QVBoxLayout()
        self.setLayout(self.paramVbox)
        self.dispatcher = None

    def addParam(self, param):
        param.show()
        self.paramVbox.addWidget(param)

    def clearParams(self):
        for i in reversed(range(self.paramVbox.count())):
            print self.paramVbox.itemAt(i)
            self.paramVbox.itemAt(i).widget().hide()
            self.paramVbox.removeItem(self.paramVbox.itemAt(i))


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    pEdit = ParamEdit()
    pEdit.show()
    sys.exit(app.exec_())

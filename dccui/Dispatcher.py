'''
DCCUI - Dispatcher
---------------

'''
import sys
from PySide import QtGui, QtCore
from PySide.QtCore import Slot, Signal


class myQ(object):
    '''
    Handles threading
    '''
    def __init__(self):
        super(myQ, self).__init__()
        self.q = []

    def push(self, task):
        self.q.append(task)

    def update(self):
        print "Updating."
        data = {}
        newData = {}
        for task in self.q:
            newData = task(data)
            data = newData
        self.q = []
        return newData


class Dispatcher(QtCore.QObject):
    '''
    The dispatcher object maintains communication
    between the GUI, the nodegraph, node parameters
    and the framebuffer.
    '''
    sendParams = Signal(QtCore.QObject)

    def __init__(self, parent=None):
        super(Dispatcher, self).__init__(parent)

        #Collect params from nodes.
        self.params = {}
        self.editedParams = []

        #Widget for parameter editing
        self.paramWidget = None

        #Widget for framebuffer
        self.frameBufferWidget = None

    def registerParams(self, node, param):
        self.params[node] = param

    @QtCore.Slot(str)
    def swapParams(self, nodeName):
        if not self.paramWidget:
            return None
        #Toggle node
        if nodeName in self.editedParams:
            self.editedParams.remove(nodeName)
        else:
            self.editedParams.append(nodeName)
        self.paramWidget.clearParams()
        for node in self.editedParams:
            self.paramWidget.addParam(self.params[node])

    @QtCore.Slot(str)
    def initViewer(self, nodeName):
        print nodeName

    @QtCore.Slot(str)
    def updateQ(self, updatedNode):
        print "Updating: " + updatedNode

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWin()

    dispatcher = myDispatcher()
    dispatcher.initViewer(window.res_img)
    dir(dispatcher.sendParams)
    window.params = dispatcher.params
    #dispatcher.sendParams.connect(window.swapParamWidgets)

    @window.clicked.connect
    def swapParamWidgets(name):
        pLayout = window.paramVbox
        print name
        for i in range(pLayout.count()):
            pLayout.itemAt(i).widget().hide()
            pLayout.removeItem(pLayout.itemAt(i))
        for param in window.params[name]:
            print type(param)
            param.show()
            pLayout.addWidget(param)

    window.updateButton.clicked.connect(dispatcher.updateQ)
    dispatcher.updateQ()

    window.show()
    sys.exit(app.exec_())

'''
DCCUI - MainWindow
---------------

The main window provides a nodegraph, framebuffer
and parameter window. It centralizes menu items and keyboard
shortcuts.
'''

from PySide import QtGui, QtCore

from dccui_qtd import *
from MainWindowMenus import *

from stylesheet import *
from stylesheet_rc import *

from NodeGraph import *
from FrameBuffer import *
from ParamEdit import *


class ViewContainer(QtGui.QMainWindow):
    """ This class is a container for a view that allows an initial size
    (specified as a tuple) to be set.
    """
    def __init__(self, size, main_window):
        QtGui.QMainWindow.__init__(self)
        # Save the size and main window.
        self.width, self.height = size
        self.main_window = main_window
        # set a minimum size to quiet Qt
        self.setMinimumSize(100, 100)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Preferred)

    def minimumSizeHint(self):
        try:
            return self.centralWidget().minimumSizeHint()
        except AttributeError:
            return super(ViewContainer, self).minimumSizeHint()

    def sizeHint(self):
        sh = self.centralWidget().sizeHint()
        if self.width > 0:
            if self.width > 1:
                w = self.width
            else:
                w = self.main_window.width() * self.width
            sh.setWidth(int(w))
        if self.height > 0:
            if self.height > 1:
                h = self.height
            else:
                h = self.main_window.height() * self.height
            sh.setHeight(int(h))
        return sh


class DCCUI_MainWindow(DCCUI_MainWindow_Menus):
    def __init__(self):
        super(DCCUI_MainWindow, self).__init__()

        self.ui = Ui_DCCUI()
        self.ui.setupUi(self)

        self.setStyleSheet(STYLESHEET)
        # Set up font:
        #self.fontDB = QtGui.QFontDatabase()
        #self.fontDB.addApplicationFont("resources/nexa_bold.otf")
        #self.setFont(QtGui.QFont("Nexa Bold", 18))

        #Init nodegraph and dispatcher.
        self.ngScene = NodeGraphScene()
        self.ngView = NodeGraphView(self.ngScene)
        self.dispatcher = self.ngScene.dispatcher

        #Init framebuffer
        self.framebuffer = FrameBufferView(self)
        fbDock = self.createDockWidget("Framebuffer", self.framebuffer,
            MW_FB_SIZE)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, fbDock)
        self.dispatcher.frameBufferWidget = self.framebuffer

        #Init paramedit
        self.parameters = ParamEdit()
        paramDock = self.createDockWidget("Parameters", self.parameters,
            MW_PM_SIZE)
        self.dispatcher.paramWidget = self.parameters

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, paramDock)

        self.connectMenuItems()

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.ngView)
        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        #Setup window
        self.setWindowTitle("DCC UI")
        self.resize(MW_WINSIZE[0], MW_WINSIZE[1])

    def createDockWidget(self, name, widget, size):
        dock = QtGui.QDockWidget(name, self)
        vc = ViewContainer(size, self)
        dock.setWidget(vc)
        dock.setObjectName(name)
        self._qt4_adjust_widget_layout(widget)
        dock.widget().setCentralWidget(widget)
        return dock

    def connectMenuItems(self):
        self.ui.actionIgnore_Node.triggered.connect(self.ngScene.ignoreNode)
        self.ui.actionExtract_Node.triggered.connect(self.ngScene.extractNode)
        self.ui.actionEdit_Node.triggered.connect(self.ngScene.editSelNodes)
        self.ui.actionView_Node.triggered.connect(self.ngScene.viewSelNodes)

    @staticmethod
    def _qt4_adjust_widget_layout(w):
        lay = w.layout()
        if lay is not None:
            lay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            lay.setContentsMargins(0, 0, 0, 0)

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    mainWin = DCCUI_MainWindow()
    ngScene = mainWin.ngScene

    node1 = ngScene.addNode((0, 0), name="Test1")
    node2 = ngScene.addNode((-75, 75), name="Test2")
    node3 = ngScene.addNode((75, 150), name="FJEIOSFJESJFESJFEIOSJFEJFSIOSF_____FEDSJIO!@$#@!&%")
    ngScene.addEdge(node1.ports["out"][0], node2.ports["in"][0])
    ngScene.addEdge(node2.ports["out"][0], node3.ports["in"][0])

    mainWin.show()
    sys.exit(app.exec_())

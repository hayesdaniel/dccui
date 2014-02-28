from PySide import QtGui, QtCore


class DCCUI_MainWindow_Menus(QtGui.QMainWindow):

    @QtCore.Slot()
    def on_actionNew_triggered(self):
        self.ui.statusbar.showMessage("New")
        print "testing"

    @QtCore.Slot()
    def on_actionOpen_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionSave_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionSaveAs_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionQuit_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionCut_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionCopy_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionPaste_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionTesting_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionDocs_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionAbout_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionDuplicate_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionSave_Layout_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionTesting_2_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionTesting_Add_Node_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionSelect_All_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionTest_Windows_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionSave_Layout_2_triggered(self):
        print "testing"

    @QtCore.Slot()
    def on_actionTest_Saved_Layouts_triggered(self):
        print "testing"

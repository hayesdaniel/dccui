'''
SlapComp GUI - HUD Panel Widget
~~~~~~~~~~~~


'''

from PySide import QtCore, QtGui

HUD_DEFAULT_SIZE = (0, 0, 300, 75)
HUD_OPACITY = .5
HUD_CORNER_RADIUS = (3, 3)
HUD_BG_COLOR = QtGui.QColor(80, 80, 80, 255)
HUD_TEXT_COLOR = QtGui.QColor(240, 240, 240, 255)
HUD_BORDER_COLOR = QtCore.Qt.black
HUD_BORDER_SIZE = 2
HUD_DEFAULT_TEXT = "Test Message"


class HUDItem(QtGui.QGraphicsWidget):
    def __init__(self, parent=None, label=None):
        super(HUDItem, self).__init__(parent)

        self.opacity = HUD_OPACITY

        self.vertLayout = QtGui.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.setLayout(self.vertLayout)

    def addLabel(self, text):
        proxy = QtGui.QGraphicsProxyWidget()
        textWidget = QtGui.QLabel(text)
        proxy.setWidget(textWidget)
        self.vertLayout.addItem(proxy)

    # def boundingRect(self):
    #     return QtCore.QRectF(QtCore.QRectF(self.size[0],
    #         self.size[1], self.size[2], self.size[3]))

    def paint(self, painter, qstyleoptiongraphicsitem, qwidget):
        painter.setOpacity(self.opacity)
        painter.setPen(QtGui.QPen(HUD_BORDER_COLOR,
            HUD_BORDER_SIZE))
        painter.setBrush(HUD_BG_COLOR)
        painter.drawRoundedRect(self.boundingRect(),
            HUD_CORNER_RADIUS[0], HUD_CORNER_RADIUS[1])

        #textRect = self.boundingRect().adjusted(10, 10, -10, -10)
        #flags = QtCore.Qt.TextWordWrap

        #font = QtGui.QFont()
        #font.setPixelSize(12)
        #painter.setPen(HUD_TEXT_COLOR)
        #painter.setFont(font)
        #painter.drawText(textRect, flags, self.text)

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    testPanel = QtGui.QGraphicsView()
    testScene = QtGui.QGraphicsScene(testPanel)
    testPanel.setScene(testScene)
    testPanel.setRenderHints(QtGui.QPainter.Antialiasing |
                QtGui.QPainter.SmoothPixmapTransform |
                QtGui.QPainter.TextAntialiasing)

    testPanel.setBackgroundBrush(QtGui.QColor(50, 50, 50, 255))

    testHUDitem = HUDItem()
    testHUDitem.addLabel("testing")
    testHUDitem.addLabel("testing")

    testScene.addItem(testHUDitem)

    testHUDitem.grabKeyboard()

    testPanel.setFocus()
    testPanel.show()

    sys.exit(app.exec_())

'''
SlapComp GUI FrameBuffer
~~~~~~~~~~~~

The frameBuffer implements a way to navigate and inspect updates as they are updated.
It also reports back the visible portion of the image as well as a specified ROI.

'''
#import os
import math

from PySide import QtCore, QtGui
from hud_item import *
from pyqtgraph.graphicsItems.ImageItem import ImageItem
#from pyqtgraph.GraphicsView import *
#from pyqtgraph.GraphicsView.ImageItem import *
import numpy as np
import time

#NODEGRAPH GLOBALS
FRAMEBUFFER_BG_COL = QtGui.QColor(50, 50, 50, 255)
FRAMEBUFFER_VIEW_PAD = 50


class FBWidget(QtGui.QWidget):
    '''
    Container widget for the graphicsview image and a header/footer.
    '''
    def __init__(self, parent=None):
        super(FBWidget, self).__init__(parent)

        self.vbox = QtGui.QVBoxLayout()

        self.frameBuffer = FrameBufferView(self)
        self.vbox.addWidget(self.frameBuffer)

        self.setLayout(self.vbox)

# class FrameBufferScene(QtGui.QGraphicsScene):
#     '''
#     Object to store the image widgets.
#     '''

#     def __init__(self, ):
#         super(FrameBufferScene, self).__init__()

class FrameBufferView(QtGui.QGraphicsView):
    '''
    Object to display and update the image.
    '''
    def __init__(self, parent=None, res=(640, 480)):
        super(FrameBufferView, self).__init__(parent)

        #self.enableMouse()
        #self.setAspectLocked(True)

        self.scene = QtGui.QGraphicsScene()
        self.setScene(self.scene)

        self.imgArray = np.zeros(res)
        self.imgBuffer = ImageItem(border='w')
        self.scene.addItem(self.imgBuffer)

        self.fitInView(QtCore.QRectF(0, 0, self.imgArray.shape[1], self.imgArray.shape[1]))

        #TODO - line update Q
        #Fills up when it changes, passes to the dispatcher

    def setResolution(res=(640, 480)):
        '''
        '''
        self.imgArray.resize(res)

    def viewedRect(self):
        '''
        Return the pixel coordinates of the image visible in the viewport.
        '''
        pass

    def updateImage(self, data):
        '''
        Update the image with data.
        '''
        self.imgBuffer.setImage(data)

if __name__ == '__main__':

    import sys
    import platform
    from PIL import Image

    def file2array(file):
        img = Image.open(file)
        # if img.getbands() == ("R", "G", "B"):
        #     img.putalpha(0)
        imgArray = np.array(img, dtype=np.uint16)
        imgArray = np.swapaxes(imgArray, 0, 1)
        return imgArray

    app = QtGui.QApplication(sys.argv)
    fb = FBWidget()
    #fb.resize(800, 600)
    fb.setGeometry(100, 100, 800, 500)

    if platform.system() == 'Darwin':
        img = "/Users/d/Dropbox/Desktops/Car_Desktops/2Rqvw.jpg"
        img2 = "/Users/d/Dropbox/Desktops/Car_Desktops/wallpaper-1011844.jpg"
    elif platform.system() == 'Linux':
        img = '/media/prod/Dropbox/Car_Desktops/2Rqvw.jpg'
        img2 = '/media/prod/Dropbox/Car_Desktops/wallpaper-1011844.jpg'
    else:
        img = "Z:\\Dropbox\\Car_Desktops\\2Rqvw.jpg"
        img2 = "Z:\\Dropbox\\Car_Desktops\\wallpaper-1011844.jpg"

    fb.setWindowTitle("FrameBuffer")

    #fb.frameBuffer.updateImage(data)
    fb.frameBuffer.updateImage(file2array(img))

    #fb.show()
    fb.show()

#    time.sleep(10)

#    fb.frameBuffer.updateImage(file2array(img2))

    sys.exit(app.exec_())

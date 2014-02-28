'''
DCCUI - NodeGraph
---------------

'''

from PySide import QtGui, QtCore
import weakref
import json
from Dispatcher import Dispatcher
from global_defaults import *
from pprint import pprint as pp


class SwitchObj(QtCore.QObject):
    toggleSignal = QtCore.Signal(str)


class Switch(QtGui.QGraphicsItem):
    def __init__(self, parent, name):
        super(Switch, self).__init__(parent)
        self.name = name
        self.parentName = parent.name
        self.onColor = SWITCH_DEFAULT_ON_COLOR
        self.state = 0
        self.switchObj = SwitchObj()

    def toggle(self):
        self.state = not self.state
        self.switchObj.toggleSignal.emit(self.parentName)
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(0, 0, SWITCH_SIZE, SWITCH_SIZE)

    def paint(self, painter, option, widget):
        painter.setPen(SWITCH_BORDER_COLOR)
        if self.state:
            painter.setBrush(self.onColor)
        else:
            painter.setBrush(SWITCH_OFF_COLOR)
        painter.drawRect(self.boundingRect())


class Port(QtGui.QGraphicsItem):
    def __init__(self, parent, name):
        super(Port, self).__init__(parent)
        #self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)

        self.drawColor = PORT_COLOR

        self.connectedEdges = []
        self.name = name
        self.highlight = False

    # def HL(self):
    #     self.highlight = True
    #     self.drawColor = PORT_HIGHLIGHT_COLOR
    #     self.update()

    # def unHL(self):
    #     self.highlight = False
    #     self.drawColor = PORT_COLOR
    #     self.update()

    def boundingRect(self):
        return QtCore.QRectF(0, 0, PORT_SIZE, PORT_SIZE)

    def paint(self, painter, option, widget):
        if self.highlight:
            painter.setBrush(PORT_HIGHLIGHT_COLOR)
        else:
            painter.setBrush(PORT_COLOR)

        painter.drawRect(self.boundingRect())

    # def hoverEvent(self, ev):
    #     print "test"
    #     if (not ev.isExit()) and ev.acceptClicks(QtCore.Qt.LeftButton):
    #         self.hovered = True
    #     else:
    #         self.hovered = False
    #     self.update()

    def hoverEnterEvent(self, event):
        self.highlight = True
        self.update()
        #QtGui.QGraphicsItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        self.highlight = False
        self.update()
        #QtGui.QGraphicsItem.hoverLeaveEvent(self, event)

    def isConnected(self):
        if len(self.connectedEdges):
            return True
        else:
            return False

    def disconnect(self):
        '''Disconnect the port from any edges.'''
        self.connectedEdges = []

    def edgeIter(self):
        for edge in self.connectedEdges:
            yield edge

    def asDict(self):
        dictPort = {"name": self.name,
                    "type": self.__class__.__name__,
                    "connected": [edge().asDict() for edge in self.edgeIter()]}
        return dictPort



class InPort(Port):
    def __init__(self, parent, name="in"):
        super(InPort, self).__init__(parent, name)
        self.setZValue(PORT_IN_ZVAL)


class OutPort(Port):
    def __init__(self, parent, name="out"):
        super(OutPort, self).__init__(parent, name)
        self.setZValue(PORT_OUT_ZVAL)


class NodeObj(QtCore.QObject):
    '''Container object for signal emitting.'''
    paramChSignal = QtCore.Signal(str)


class Node(QtGui.QGraphicsItem):
    '''For drawing the nodes and initializing the parameter GUI.'''
    def __init__(self, parent=None, name=NODE_DEFAULT_NAME):
        super(Node, self).__init__(parent)

        self.setZValue(NODE_Z_VAL)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)

        self.setFlags(
            self.ItemIsSelectable |
            self.ItemIsFocusable
        )

        self.drawColor = NODE_DEFAULT_COLOR
        self.drawBorderColor = NODE_BORDER_COLOR
        self.size = NODE_MINIMUM_SIZE
        self.name = name
        self.label = QtGui.QGraphicsSimpleTextItem(self.name, self)

        #self.params = QtGui.QLabel(name)
        self.initParameterGui()
        self.nodeObj = NodeObj()

        self.resizeToLabel()

        self.ports = {"in": [InPort(self, "in"), InPort(self, "in2")],
            "out": [OutPort(self, "out"), OutPort(self, "out2")]}
        self.drawPorts(-PORT_SIZE, self.ports["in"])
        self.drawPorts(self.size.height(), self.ports["out"])

        self.editSwitch = Switch(self, "Edit")
        self.editSwitch.onColor = QtCore.Qt.blue
        self.viewSwitch = Switch(self, "View")
        self.viewSwitch.onColor = QtCore.Qt.red
        self.drawSwitches()

        self.ignored = False

    def initParameterGui(self):
        self.value = 0
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 10)
        slider.setValue(0)
        slider.valueChanged.connect(self.setParameters)
        self.params = slider

    def initView(self):
        print self.name

    @QtCore.Slot(int)
    def setParameters(self, val):
        self.value = val
        self.nodeObj.paramChSignal.emit(self.name)

    def getParameters(self):
        return self.value

    def boundingRect(self):
        if hasattr(self, "size"):
            return self.size
        else:
            return NODE_MINIMUM_SIZE

    def toggleIgnored(self):
        self.ignored = not self.ignored
        self.update()

    def portIter(self):
        for portType, portList in self.ports.iteritems():
            for port in portList:
                yield port

    def port(self, portName):
        for port in self.portIter():
            if portName == port.name:
                return port

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for port in self.portIter():
                    for edge in port.connectedEdges:
                        edge().adjust()
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def resizeToLabel(self):
        if hasattr(self, "label"):
            labelSizeW = self.label.boundingRect().width() + (2 * NODE_HORIZ_PAD)
            labelSizeW += (2 * SWITCH_SIZE)
            labelSizeW += (2 * NODE_LABEL_WPAD)
            labelSizeH = self.label.boundingRect().height() + (2 * NODE_VERT_PAD)
            self.size = QtCore.QRectF(0, 0, labelSizeW, labelSizeH)
            self.label.setPos(NODE_HORIZ_PAD + NODE_LABEL_WPAD + SWITCH_SIZE, NODE_VERT_PAD)

    def drawSwitches(self):
        if hasattr(self, "editSwitch"):
            self.editSwitch.setPos(NODE_HORIZ_PAD, NODE_VERT_PAD)
        if hasattr(self, "viewSwitch"):
            self.viewSwitch.setPos(NODE_HORIZ_PAD, self.size.height() - NODE_VERT_PAD - SWITCH_SIZE)

    def drawPorts(self, vertOffset, portList):
        if hasattr(self, "ports"):
            portCount = 1
            for port in portList:
                portOffset = (self.size.width() / (len(portList) + 1))
                portPos = QtCore.QPointF(portOffset * portCount - PORT_SIZE / 2,
                    vertOffset)
                port.setPos(portPos)
                portCount += 1

    def paint(self, painter, option, widget):
        '''Paint the node itself.
        '''
        #nodePen = QtGui.QPen()
        if self.isSelected():
            painter.setPen(NODE_SELECTED_BORDER_COLOR)
        else:
            painter.setPen(self.drawBorderColor)
        if self.ignored:
            painter.setBrush(NODE_IGNORED_COLOR)
        else:
            painter.setBrush(self.drawColor)
        self.drawNode(painter)

    def drawNode(self, painter):
        painter.drawRoundedRect(self.boundingRect(),
            NODE_CORNER_RADIUS[0], NODE_CORNER_RADIUS[1])

    def asDict(self):
        '''Return a dictionary to represent the node.
        '''
        dictNode = {"name": self.name,
                    "pos": (self.pos().x(),self.pos().y()),
                    "ignored": self.ignored,
                    "type": self.__class__.__name__,
                    "ports": [port.asDict() for port in self.portIter()],
                    "params": self.getParameters()
                    }
        return dictNode

    def keyPressEvent(self, ev):
        print type(ev.key())
        if ev.key() == QtCore.Qt.Key_Delete or ev.key() == QtCore.Qt.Key_Backspace:
            #if isinstance(self.target, TerminalGraphicsItem):
            self.disconnect()
            ev.accept()
        else:
            ev.ignore()

#================================================================================


class Edge(QtGui.QGraphicsItem):
    def __init__(self):
        super(Edge, self).__init__()
        self.setZValue(EDGE_Z_VAL)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

        self.setFlags(
            self.ItemIsSelectable |
            self.ItemIsFocusable
        )

        self.drawColor = EDGE_COLOR
        self.highlight = False
        self.outPort = None
        self.inPort = None
        self.sourcePoint = QtCore.QPointF(0, 0)
        self.destPoint = QtCore.QPointF(0, 0)

    def boundingRect(self):
        extra = (EDGE_LINE_WIDTH + EDGE_ARROW_SIZE) / 2.0

        return QtCore.QRectF(self.sourcePoint,
            QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
            self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def adjust(self):
        portRect = QtCore.QRectF(0, 0, PORT_SIZE, PORT_SIZE)
        outRect = self.mapRectFromItem(self.outPort(), portRect)
        inRect = self.mapRectFromItem(self.inPort(), portRect)
        outRectBottom = QtCore.QPointF(outRect.center().x(), outRect.center().y()+(outRect.height()/2))
        inRectTop = QtCore.QPointF(inRect.center().x(), inRect.center().y()-(inRect.height()/2))
        line = QtCore.QLineF(outRectBottom, inRectTop)

        self.prepareGeometryChange()
        self.sourcePoint = line.p1()
        self.destPoint = line.p2()
        self.angle = math.acos(line.dx() / line.length())

    def disconnect(self):
        if self.outPort:
            self.outPort().disconnect()
        if self.scene() is not None:
            self.scene().removeItem(self)

    def shape(self):
        '''Set the shape with pad for easy selection.'''
        path = QtGui.QPainterPath()
        path.moveTo(self.sourcePoint)
        path.lineTo(self.destPoint)
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)

    def paint(self, painter, option, widget):
        if self.isSelected() or self.highlight:
            self.drawColor = EDGE_HIGHLIGHT_COLOR
        else:
            self.drawColor = EDGE_COLOR

        line = QtCore.QLineF(self.sourcePoint, self.destPoint)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(self.drawColor, EDGE_LINE_WIDTH,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = TwoPi - angle
        destArrowP1 = self.destPoint + QtCore.QPointF(math.sin(angle - Pi / 3) * EDGE_ARROW_SIZE,
            math.cos(angle - Pi / 3) * EDGE_ARROW_SIZE)
        destArrowP2 = self.destPoint + QtCore.QPointF(math.sin(angle - Pi + Pi / 3) * EDGE_ARROW_SIZE,
                                                      math.cos(angle - Pi + Pi / 3) * EDGE_ARROW_SIZE)
        painter.setBrush(self.drawColor)
        painter.drawPolygon(QtGui.QPolygonF([line.p2(),
            destArrowP1, destArrowP2]))

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Delete or ev.key() == QtCore.Qt.Key_Backspace:
            #if isinstance(self.target, TerminalGraphicsItem):
            self.disconnect()
            ev.accept()
        else:
            ev.ignore()

    def mousePressEvent(self, ev):
        ev.ignore()

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            sel = self.isSelected()
            self.setSelected(True)
            if not sel and self.isSelected():
                self.update()

    def hoverEnterEvent(self, event):
        self.highlight = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.highlight = False
        self.update()

    def asDict(self):
        dictEdge = {"in": { "node": self.inPort().parentItem().name, "port": self.inPort().name },
                    "out": { "node": self.outPort().parentItem().name, "port": self.outPort().name}
                    }
        return dictEdge


class NodeGraphScene(QtGui.QGraphicsScene):
    '''
    '''
    def __init__(self):
        super(NodeGraphScene, self).__init__()
        #Keep a dictionary of nodes.
        self.nodeDict = {}

        #Register a dispatcher object to talk with other widgets.
        self.dispatcher = Dispatcher(self)
        self.signalMapperParam = QtCore.QSignalMapper(self)
        self.signalMapperView = QtCore.QSignalMapper(self)
        self.signalMapperView.mapped[str].connect(self.dispatcher.initViewer)
        self.signalMapperParam.mapped[str].connect(self.dispatcher.swapParams)

    def adjustSceneRect(self):
        itemsRect = self.itemsBoundingRect()
        itemsRect.adjust(20, 20, 20, 20)
        return itemsRect
        #self.setSceneRect(itemsRect)

    @QtCore.Slot(str)
    def sendUpdate(self, changedNode):
        self.dispatcher.updateQ(changedNode)

    def addNode(self, pos=(50, 50), name=NODE_DEFAULT_NAME):
        #Create node obj
        newNode = Node(name=name)
        newNode.setPos(pos[0], pos[1])
        newNode.update()
        #Add to scene
        self.addItem(newNode)
        self.nodeDict[name] = weakref.ref(newNode)
        #Reigster params with dispatcher
        self.dispatcher.registerParams(name, newNode.params)
        #Connect switches with signalmapper
        self.signalMapperParam.setMapping(newNode.editSwitch.switchObj, unicode(name))
        self.signalMapperView.setMapping(newNode.viewSwitch.switchObj, unicode(name))
        newNode.editSwitch.switchObj.toggleSignal.connect(self.signalMapperParam.map)
        newNode.viewSwitch.switchObj.toggleSignal.connect(self.signalMapperView.map)
        #Connect paramchanged with DAG update
        newNode.nodeObj.paramChSignal.connect(self.sendUpdate)
        #self.adjustSceneRect()
        return newNode

    def addEdge(self, outPort, inPort):
        '''Connect two nodes with an edge.'''
        #TODO - make this not stupid
        if outPort in self.items() \
            and inPort in self.items():
                newEdge = Edge()
                self.addItem(newEdge)
                newEdge.outPort = weakref.ref(outPort)
                newEdge.inPort = weakref.ref(inPort)
                outPort.connectedEdges.append(weakref.ref(newEdge))
                inPort.connectedEdges.append(weakref.ref(newEdge))
                newEdge.adjust()
                return newEdge
        else:
                raise ValueError("Port not found.")

    def deleteNodes(self, nodeList=[]):
        print nodeList
        self.detachNodes(nodeList)
        for node in nodeList:
            print node
            if node in self.nodeDict.keys():
                self.removeItem(self.nodeDict[node]())
                del self.nodeDict[node]

    def detachNodes(self, nodeList=[]):
        for node in nodeList:
            if node in self.nodeDict.keys():
                for port in self.nodeDict[node]().portIter():
                    if len(port.connectedEdges):
                        for edge in port.connectedEdges:
                            self.removeItem(edge())
                        port.connectedEdges = []
            else:
                raise ValueError("Node not found: " + node.name)

    def clearScene(self):
        self.deleteNodes(self.nodeDict.keys())

    def loadFromJSON(self, jsonStr):
        #pp(json.loads(jsonStr))
        loadedNodes = []
        for name, node in json.loads(jsonStr).iteritems():
            newNode = self.addNode(name=name, pos=node["pos"])
            for port in node["ports"]:
                for edge in port["connected"]:
                    try:
                        outNode = self.nodeDict[edge["out"]["node"]]
                        inNode = self.nodeDict[edge["in"]["node"]]
                        outPort = outNode().port(edge["out"]["port"])
                        inPort = inNode().port(edge["in"]["port"])
                    except KeyError:
                        print "Node not found, no edge created."
                        continue
                    self.addEdge(outPort, inPort)
            loadedNodes.append(newNode)
        return loadedNodes

    def asJSON(self, nodes=[]):
        if not nodes:
            nodes = self.nodeDict.keys()
        nodesDict = {}
        for node in nodes:
            nodesDict[node] = self.nodeDict[node]().asDict()
        return json.dumps(nodesDict, sort_keys=True, indent=4, separators=(',', ': '))

    @QtCore.Slot()
    def editSelNodes(self):
        for node in self.selectedItems():
            node.editSwitch.toggle()

    @QtCore.Slot()
    def viewSelNodes(self):
        for node in self.selectedItems():
            node.viewSwitch.toggle()

    @QtCore.Slot()
    def extractNode(self):
        self.detachNodes(self.selectedItems())

    @QtCore.Slot()
    def ignoreNode(self):
        for node in self.selectedItems():
            node.toggleIgnored()


class NodeGraphView(QtGui.QGraphicsView):
    '''
    '''
    def __init__(self, scene, parent=None):
        super(NodeGraphView, self).__init__(parent)

        self.setStyleSheet(STYLESHEET)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setViewportUpdateMode(
            QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.setScene(scene)
        self.scale(0.8, 0.8)

        self.resetDrawConnection()

    def resetDrawConnection(self):
        self.drawConnection = False
        self.drawConnectionTo = None
        self.drawConnectionFrom = None
        self.drawnConnection = Edge()
        self.drawnConnection.drawColor = EDGE_HIGHLIGHT_COLOR
        self.lastHLitem = None
        self.doConnection = False

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if type(item) == Switch:
            event.ignore()

        QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)

    def mousePressEvent(self, event):
        for item in self.items(event.pos()):
        #item = self.itemAt(event.pos())
            if type(item) == InPort:
                self.drawConnection = True
                self.drawConnectionTo = weakref.ref(item)
                break
            elif type(item) == OutPort:
                self.drawConnection = True
                self.drawConnectionFrom = weakref.ref(item)
                break
            elif type(item) == Switch:
                item.toggle()
            elif type(item) == Edge:
                #item.disconnect()
                #self.drawConnection = True
                continue
        if self.drawConnection:
            item.highlight = True
            edgePoint = self.mapToScene(event.pos())
            self.drawnConnection.sourcePoint = edgePoint
            self.drawnConnection.destPoint = edgePoint
            self.scene().addItem(self.drawnConnection)
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
        else:
            modifiers = QtGui.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.AltModifier or \
                event.button() == QtCore.Qt.MiddleButton:
                    self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.drawConnection:
            item = None
            for mmItem in self.items(event.pos()):
                #Exclude edge items
                if type(mmItem) == Edge:
                    continue
                elif type(mmItem) == InPort or type(mmItem) == OutPort:
                    print "test"
                    item = mmItem
                    break
            print item
            #item = self.itemAt(event.pos())
            self.drawnConnection.prepareGeometryChange()
            edgePoint = self.mapToScene(event.pos())
            #HIGHLIGHT VALID CONNECTIONS
            HLitem = False
            if self.drawConnectionTo:
                self.drawnConnection.sourcePoint = edgePoint
                if type(item) == OutPort:
                    print item
                    HLitem = True
            elif self.drawConnectionFrom:
                self.drawnConnection.prepareGeometryChange()
                edgePoint = self.mapToScene(event.pos())
                self.drawnConnection.destPoint = edgePoint
                if type(item) == InPort:
                    HLitem = True
            if HLitem is True:
                item.highlight = True
                self.lastHLitem = weakref.ref(item)
                self.doConnection = True
            elif self.lastHLitem:
                self.doConnection = False
                self.lastHLitem().highlight = False
            else:
                self.doConnection = False

        QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        #item = self.itemAt(event.pos())
        for mmItem in self.items(event.pos()):
            mmItem.highlight = False
        if self.drawConnection:
            if self.doConnection:
                try:
                    if self.drawConnectionTo:
                        self.scene().addEdge(self.lastHLitem(), self.drawConnectionTo())
                    elif self.drawConnectionFrom:
                        self.scene().addEdge(self.drawConnectionFrom(), self.lastHLitem())
                except:
                    self.resetDrawConnection()
            self.scene().removeItem(self.drawnConnection)
            self.resetDrawConnection()
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor,
            scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    ngScene = NodeGraphScene()
    ngView = NodeGraphView(ngScene)

    node1 = ngScene.addNode((0, 0), name="Test1")
    node2 = ngScene.addNode((-75, 75), name="Test2")
    node3 = ngScene.addNode((75, 150), name="FJEIOSFJESJFESJFEIOSJFEJFSIOSF_____FEDSJIO!@$#@!&%")
    ngScene.addEdge(node1.port("out"), node2.port("in"))

    jsonScene = ngScene.asJSON()
    ngScene.clearScene()
    ngScene.loadFromJSON(jsonScene)

    #ngScene.addEdge(node1, node2)
    #ngScene.addEdge(node2, node3)
    ngView.setGeometry(100, 100, 800, 500)

    ngView.show()
    sys.exit(app.exec_())

from PyQt5 import QtCore

def setLeftClickable(widget):
    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if event.button() == QtCore.Qt.LeftButton:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            return True
            return False
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

def setRightClickable(widget):
    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if event.button() == QtCore.Qt.RightButton:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            return True
            return False
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

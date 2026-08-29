from PySide import QtGui

class TightStackedWidget(QtGui.QStackedWidget):
    def sizeHint(self):
        widget = self.currentWidget()
        if widget:
            return widget.sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        widget = self.currentWidget()
        if widget:
            return widget.minimumSizeHint()
        return super().minimumSizeHint()
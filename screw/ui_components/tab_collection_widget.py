from typing import Callable

from PySide import QtGui, QtCore

class TabCollection(QtGui.QWidget):

    def __init__(
        self,
        add_form: Callable[[int], tuple[str | None, QtGui.QWidget]],
        preview: Callable,
        parent=None,
    ):
        super().__init__(parent)

        self._add_form = add_form
        self._preview = preview

        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QtGui.QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)

        layout.addWidget(self.tabs)

        self.add_button = QtGui.QToolButton()
        self.add_button.setText('+')
        self.tabs.setCornerWidget(
            self.add_button,
            QtCore.Qt.TopRightCorner
        )

        self.add_button.clicked.connect(self._add_via_ui)
        self.tabs.tabCloseRequested.connect(self._remove_via_ui)
        self.tabs.tabBar().tabMoved.connect(self._move_via_ui)
        # self.tabs.currentChanged.connect(self._preview)

    def _add_via_ui(self, *args):
        self.add()
        self._preview()

    def _remove_via_ui(self, *args):
        index = args[0]
        self.remove(index)
        self._preview()

    def _move_via_ui(self, *args):
        self._preview()

    def add(self):
        index = self.tabs.count()
        title, widget = self._add_form(index)
        if title is None:
            title = ''
        index = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(index)
        return widget

    def remove(self, index):
        widget = self.tabs.widget(index)
        if widget is None:
            return
        self.tabs.removeTab(index)
        widget.deleteLater()

    def count(self):
        return self.tabs.count()

    def widget(self, index):
        return self.tabs.widget(index)
    #
    # def current_widget(self):
    #     return self.tabs.currentWidget()

    def widgets(self):
        return [
            self.tabs.widget(i)
            for i in range(self.tabs.count())
        ]
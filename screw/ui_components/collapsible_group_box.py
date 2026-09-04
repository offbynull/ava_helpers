from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtWidgets import QGroupBox, QWidget


class CollapsibleGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.toggled.connect(self._sync_contents)

    def childEvent(self, event):
        super().childEvent(event)

        if event.type() in (
            QEvent.Type.ChildAdded,
            QEvent.Type.ChildRemoved,
        ):
            # Defer because ChildAdded can occur before construction/reparenting
            # has completely finished.
            QTimer.singleShot(0, self._refresh)

    def _refresh(self):
        self._sync_contents(self.isChecked())

    def _sync_contents(self, visible):
        for widget in self.findChildren(
            QWidget,
            options=Qt.FindChildOption.FindDirectChildrenOnly,
        ):
            widget.setVisible(visible)

        if self.layout():
            self.layout().invalidate()

        self.updateGeometry()
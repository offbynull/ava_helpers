import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from screw.ui_components.collapsible_group_box import CollapsibleGroupBox
from screw.ui_components.tight_stacked_widget import TightStackedWidget


_DEFAULT_THREAD_LEFT_HANDED = False
_DEFAULT_THREAD_AXIAL_OFFSET = 0 * App.Units.MilliMetre
_DEFAULT_THREAD_ROTATION_OFFSET = 90.0 * App.Units.Degree
_DEFAULT_THREAD_SINK_OFFSET = 0.2 * App.Units.MilliMetre


class ScrewForm(QtGui.QWidget):

    def __init__(
            self,
            thread_profiles,
            preview,
            parent=None
    ):
        super(ScrewForm, self).__init__(parent)

        self._thread_profiles = thread_profiles
        self._preview = preview
        layout = QtGui.QFormLayout(self)

        self._name = QtGui.QLineEdit()
        self._name.setText('Screw')
        self._name.setPlaceholderText('Enter name')
        self._name.editingFinished.connect(self._preview)
        layout.addRow('Name:', self._name)

        # Surface
        # -------
        self._surface_shape_group = QtGui.QGroupBox('Surface')
        self._surface_shape_group.toggled.connect(self._preview)
        surface_shape_layout = QtGui.QFormLayout(self._surface_shape_group)
        layout.addRow(self._surface_shape_group)

        self._cone_distance_between_radiuses = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._cone_distance_between_radiuses.setProperty('value', 50 * App.Units.MilliMetre)
        self._cone_distance_between_radiuses.editingFinished.connect(self._preview)
        surface_shape_layout.addRow('Distance:', self._cone_distance_between_radiuses)

        self._cone_top_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._cone_top_radius.setProperty('value', 50 * App.Units.MilliMetre)
        self._cone_top_radius.editingFinished.connect(self._preview)
        surface_shape_layout.addRow('Top radius:', self._cone_top_radius)

        self._cone_bottom_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._cone_bottom_radius.setProperty('value', 10 * App.Units.MilliMetre)
        self._cone_bottom_radius.editingFinished.connect(self._preview)
        surface_shape_layout.addRow('Bottom radius:', self._cone_bottom_radius)

        self._cone_helper_buttons = QtGui.QWidget()
        cone_helper_buttons_layout = QtGui.QHBoxLayout(self._cone_helper_buttons)
        surface_shape_layout.addRow(self._cone_helper_buttons)

        self._cone_radius_swap = QtGui.QToolButton()
        self._cone_radius_swap.setText('↓↑ Swap ↓↑')

        def _swap_radius():
            bottom_radius = self._cone_bottom_radius.property('value')
            top_radius = self._cone_top_radius.property('value')
            self._cone_bottom_radius.setProperty('value', top_radius)
            self._cone_top_radius.setProperty('value', bottom_radius)
            self._preview()

        self._cone_radius_swap.clicked.connect(_swap_radius)
        cone_helper_buttons_layout.addWidget(self._cone_radius_swap)

        self._cone_radius_keep_bottom = QtGui.QToolButton()
        self._cone_radius_keep_bottom.setText('↑ Keep bottom ↑')

        def _keep_bottom_radius():
            bottom_radius = self._cone_bottom_radius.property('value')
            self._cone_bottom_radius.setProperty('value', bottom_radius)
            self._cone_top_radius.setProperty('value', bottom_radius)
            self._preview()

        self._cone_radius_keep_bottom.clicked.connect(_keep_bottom_radius)
        cone_helper_buttons_layout.addWidget(self._cone_radius_keep_bottom)

        self._cone_radius_keep_top = QtGui.QToolButton()
        self._cone_radius_keep_top.setText('↓ Keep top ↓')

        def _keep_top_radius():
            top_radius = self._cone_top_radius.property('value')
            self._cone_bottom_radius.setProperty('value', top_radius)
            self._cone_top_radius.setProperty('value', top_radius)
            self._preview()

        self._cone_radius_keep_top.clicked.connect(_keep_top_radius)
        cone_helper_buttons_layout.addWidget(self._cone_radius_keep_top)

        # Thread
        # -------
        self._thread_group = CollapsibleGroupBox('Thread')
        self._thread_group.setCheckable(True)
        self._thread_group.setChecked(True)
        self._thread_group.toggled.connect(self._preview)
        thread_layout = QtGui.QFormLayout(self._thread_group)
        layout.addRow(self._thread_group)

        self._thread_profile_combo = QtGui.QComboBox()
        self.thread_profile_stack = TightStackedWidget()
        self.thread_profile_cards = []
        for thread_profile in self._thread_profiles:
            self._thread_profile_combo.addItem(thread_profile.NAME)
            card = thread_profile.Card(self._preview)
            self.thread_profile_cards.append(card)
            self.thread_profile_stack.addWidget(card.form)
        self._thread_profile_combo.currentIndexChanged.connect(self.thread_profile_stack.setCurrentIndex)
        self._thread_profile_combo.currentIndexChanged.connect(lambda _: self.thread_profile_stack.updateGeometry())
        self._thread_profile_combo.currentIndexChanged.connect(self._preview)
        thread_layout.addRow('Profile:', self._thread_profile_combo)
        thread_layout.addRow(self.thread_profile_stack)

        self._thread_starts = QtGui.QSpinBox()
        self._thread_starts.setMinimum(1)
        self._thread_starts.setValue(1)
        self._thread_starts.editingFinished.connect(self._preview)
        thread_layout.addRow('Starts:', self._thread_starts)

        self._thread_lead = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._thread_lead.setProperty('value', 5 * App.Units.MilliMetre)
        self._thread_lead.editingFinished.connect(self._preview)
        thread_layout.addRow('Lead:', self._thread_lead)

        self._thread_advanced_group = CollapsibleGroupBox('Advanced')
        self._thread_advanced_group.setCheckable(True)
        self._thread_advanced_group.setChecked(False)
        self._thread_advanced_group.toggled.connect(self._preview)
        thread_advanced_group_layout = QtGui.QFormLayout(self._thread_advanced_group)
        thread_layout.addRow(self._thread_advanced_group)

        self._thread_left_handed = Gui.UiLoader().createWidget('QCheckBox')
        self._thread_left_handed.setChecked(_DEFAULT_THREAD_LEFT_HANDED)
        self._thread_left_handed.toggled.connect(self._preview)
        thread_advanced_group_layout.addRow('Left-handed:', self._thread_left_handed)

        self._thread_axial_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._thread_axial_offset.setProperty('value', _DEFAULT_THREAD_AXIAL_OFFSET)
        self._thread_axial_offset.editingFinished.connect(self._preview)
        thread_advanced_group_layout.addRow('Axial offset:', self._thread_axial_offset)

        self._thread_rotation_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._thread_rotation_offset.setProperty('value', _DEFAULT_THREAD_ROTATION_OFFSET)
        self._thread_rotation_offset.editingFinished.connect(self._preview)
        thread_advanced_group_layout.addRow('Rotation offset:', self._thread_rotation_offset)

        self._thread_sink_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._thread_sink_offset.setProperty('value', _DEFAULT_THREAD_SINK_OFFSET)
        self._thread_sink_offset.editingFinished.connect(self._preview)
        thread_advanced_group_layout.addRow('Radius sink offset:', self._thread_sink_offset)

        # Top lead-in
        # -----------
        self._top_lead_in_group = CollapsibleGroupBox('Top lead-in')
        self._top_lead_in_group.setCheckable(True)
        self._top_lead_in_group.setChecked(False)
        self._top_lead_in_group.toggled.connect(self._preview)
        top_lead_in_layout = QtGui.QFormLayout(self._top_lead_in_group)
        layout.addRow(self._top_lead_in_group)

        self._top_lead_in_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._top_lead_in_height.setProperty('value', 3 * App.Units.MilliMetre)
        self._top_lead_in_height.editingFinished.connect(self._preview)
        top_lead_in_layout.addRow('Height:', self._top_lead_in_height)

        self._top_lead_in_radius_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._top_lead_in_radius_offset.setProperty('value', -3 * App.Units.MilliMetre)
        self._top_lead_in_radius_offset.editingFinished.connect(self._preview)
        top_lead_in_layout.addRow('Radius:', self._top_lead_in_radius_offset)

        # Bottom lead-in
        # --------------
        self._bottom_lead_in_group = CollapsibleGroupBox('Bottom lead-in')
        self._bottom_lead_in_group.setCheckable(True)
        self._bottom_lead_in_group.setChecked(False)
        self._bottom_lead_in_group.toggled.connect(self._preview)
        bottom_lead_in_layout = QtGui.QFormLayout(self._bottom_lead_in_group)
        layout.addRow(self._bottom_lead_in_group)

        self._bottom_lead_in_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._bottom_lead_in_height.setProperty('value', 3 * App.Units.MilliMetre)
        self._bottom_lead_in_height.editingFinished.connect(self._preview)
        bottom_lead_in_layout.addRow('Height:', self._bottom_lead_in_height)

        self._bottom_lead_in_radius_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self._bottom_lead_in_radius_offset.setProperty('value', -3 * App.Units.MilliMetre)
        self._bottom_lead_in_radius_offset.editingFinished.connect(self._preview)
        bottom_lead_in_layout.addRow('Radius:', self._bottom_lead_in_radius_offset)

    @property
    def name(self):
        return self._name.text()

    @property
    def surface_shape(self):
        return self._surface_shape_group.isChecked()

    @property
    def cone_distance_between_radiuses(self):
        return self._cone_distance_between_radiuses.property('value')

    @property
    def cone_top_radius(self):
        return self._cone_top_radius.property('value')

    @property
    def cone_bottom_radius(self):
        return self._cone_bottom_radius.property('value')

    @property
    def threaded(self):
        return self._thread_group.isChecked()

    @property
    def thread_profile(self):
        assert self.threaded
        return self._thread_profiles[self._thread_profile_combo.currentIndex()]

    @property
    def thread_profile_card(self):
        assert self.threaded
        return self.thread_profile_cards[self._thread_profile_combo.currentIndex()]

    @property
    def thread_starts(self):
        assert self.threaded
        return self._thread_starts.value()

    @property
    def thread_lead(self):
        assert self.threaded
        return self._thread_lead.property('value')

    @property
    def thread_axial_offset(self):
        assert self.threaded
        return self._thread_axial_offset.property('value') if self._thread_advanced_group.isChecked() else _DEFAULT_THREAD_AXIAL_OFFSET

    @property
    def thread_rotation_offset(self):
        assert self.threaded
        return self._thread_rotation_offset.property('value') if self._thread_advanced_group.isChecked() else _DEFAULT_THREAD_ROTATION_OFFSET

    @property
    def thread_sink_offset(self):
        assert self.threaded
        return self._thread_sink_offset.property('value') if self._thread_advanced_group.isChecked() else _DEFAULT_THREAD_SINK_OFFSET

    @property
    def thread_left_handed(self):
        assert self.threaded
        return self._thread_left_handed.isChecked() if self._thread_advanced_group.isChecked() else _DEFAULT_THREAD_LEFT_HANDED

    @property
    def top_led_in(self):
        return self._top_lead_in_group.isChecked()

    @property
    def top_lead_in_height(self):
        assert self.top_led_in
        return self._top_lead_in_height.property('value')

    @property
    def top_lead_in_radius_offset(self):
        assert self.top_led_in
        return self._top_lead_in_radius_offset.property('value')

    @property
    def bottom_led_in(self):
        return self._bottom_lead_in_group.isChecked()

    @property
    def bottom_lead_in_height(self):
        assert self.bottom_led_in
        return self._bottom_lead_in_height.property('value')

    @property
    def bottom_lead_in_radius_offset(self):
        assert self.bottom_led_in
        return self._bottom_lead_in_radius_offset.property('value')
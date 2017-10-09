import pprint
import logging
from Qt import QtWidgets, QtCore, QtGui

import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as import_utils

reload(import_utils)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

application = import_utils.get_application()
dockable = import_utils.get_dockable_widget(application)

if application == 'Maya':
    import mla_MayaPipe.mla_rig_utils.mla_Maya_matrix_utils as Mmu
elif application == 'Max':
    import mla_MaxPipe.mla_rig_utils.mla_Max_matrix_utils as Mmu
else:
    pass


class PosToolUI(dockable, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(PosToolUI, self).__init__(parent=parent)

        self.setWindowTitle('Position Tool')

        # UI
        self.buildUI()

        # Connexions
        self.move_pB.clicked.connect(self.move_obj)
        self.move_even_pB.clicked.connect(self.move_even_obj)
        self.constrain_pB.clicked.connect(self.constrain)
        self.constrain_even_pB.clicked.connect(self.constrain_even)

        self.translate_cB.stateChanged.connect(self.check_translate)
        self.rotate_cB.stateChanged.connect(self.check_rotate)
        self.scale_cB.stateChanged.connect(self.check_scale)

        self.point_ct_rB.toggled.connect(self.check_from_pointct)
        self.orient_ct_rB.toggled.connect(self.check_from_orientct)
        self.aim_ct_rB.toggled.connect(self.check_from_aimct)
        self.parent_ct_rB.toggled.connect(self.check_from_parentct)
        self.scale_ct_rB.toggled.connect(self.check_from_scalect)
        self.mirror_ct_rB.toggled.connect(self.check_from_mirrorct)

    def buildUI(self):
        logging.info('Building UI')

        # ========================================
        # Main layout
        layout = QtWidgets.QHBoxLayout(self)

        # Tabs
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.setObjectName("tabWidget")
        layout.addWidget(tabWidget)
        # Position tab
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        tabWidget.addTab(self.tab, 'Position')
        # Constrain tab
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        tabWidget.addTab(self.tab_2, 'Constrain')

        # ========================================
        # Channels
        channels_widget = QtWidgets.QWidget()
        channels_layout = QtWidgets.QVBoxLayout(channels_widget)
        layout.addWidget(channels_widget)
        # Checkboxes
        # Translate
        self.translate_cB = QtWidgets.QCheckBox()
        self.translate_cB.setChecked(True)
        self.translate_cB.setObjectName("translate_cB")
        self.translate_cB.setText("Translate")
        channels_layout.addWidget(self.translate_cB)
        # TX
        self.tx_cB = QtWidgets.QCheckBox()
        self.tx_cB.setChecked(True)
        self.tx_cB.setObjectName("tx_cB")
        self.tx_cB.setText("TX")
        channels_layout.addWidget(self.tx_cB)
        # TY
        self.ty_cB = QtWidgets.QCheckBox()
        self.ty_cB.setChecked(True)
        self.ty_cB.setObjectName("ty_cB")
        self.ty_cB.setText("TY")
        channels_layout.addWidget(self.ty_cB)
        # TZ
        self.tz_cB = QtWidgets.QCheckBox()
        self.tz_cB.setChecked(True)
        self.tz_cB.setObjectName("tz_cB")
        self.tz_cB.setText("TZ")
        channels_layout.addWidget(self.tz_cB)
        # Rotate
        self.rotate_cB = QtWidgets.QCheckBox()
        self.rotate_cB.setObjectName("rotate_cB")
        self.rotate_cB.setText("Rotate")
        channels_layout.addWidget(self.rotate_cB)
        # RX
        self.rx_cB = QtWidgets.QCheckBox()
        self.rx_cB.setObjectName("rx_cB")
        self.rx_cB.setText("RX")
        channels_layout.addWidget(self.rx_cB)
        # RY
        self.ry_cB = QtWidgets.QCheckBox()
        self.ry_cB.setObjectName("ry_cB")
        self.ry_cB.setText("RY")
        channels_layout.addWidget(self.ry_cB)
        # RZ
        self.rz_cB = QtWidgets.QCheckBox()
        self.rz_cB.setObjectName("rz_cB")
        self.rz_cB.setText("RZ")
        channels_layout.addWidget(self.rz_cB)
        # Scale
        self.scale_cB = QtWidgets.QCheckBox()
        self.scale_cB.setObjectName("scale_cB")
        self.scale_cB.setText("Scale")
        channels_layout.addWidget(self.scale_cB)
        # SX
        self.sx_cB = QtWidgets.QCheckBox()
        self.sx_cB.setObjectName("sx_cB")
        self.sx_cB.setText("SX")
        channels_layout.addWidget(self.sx_cB)
        # SY
        self.sy_cB = QtWidgets.QCheckBox()
        self.sy_cB.setObjectName("sy_cB")
        self.sy_cB.setText("SY")
        channels_layout.addWidget(self.sy_cB)
        # SZ
        self.sz_cB = QtWidgets.QCheckBox()
        self.sz_cB.setObjectName("sz_cB")
        self.sz_cB.setText("SZ")
        channels_layout.addWidget(self.sz_cB)

        # ========================================
        # Position tab layout
        self.position_layout = QtWidgets.QVBoxLayout(self.tab)
        self.position_layout.setObjectName("space_layout")

        # World/Object space
        self.space_groupBox = QtWidgets.QGroupBox(self.tab)
        self.space_groupBox.setTitle("")
        self.space_groupBox.setObjectName("space_groupBox")
        self.position_layout.addWidget(self.space_groupBox)
        # Buttons
        self.space_layout = QtWidgets.QVBoxLayout(self.space_groupBox)
        self.space_layout.setObjectName("space_layout")
        # World space
        self.ws_rB = QtWidgets.QRadioButton(self.space_groupBox)
        self.ws_rB.setObjectName("ws_rB")
        self.space_layout.addWidget(self.ws_rB)
        self.ws_rB.setChecked(True)
        self.ws_rB.setToolTip("Perform transformation in world space")
        self.ws_rB.setText("World space")
        # Object space
        self.os_rB = QtWidgets.QRadioButton(self.space_groupBox)
        self.os_rB.setObjectName("os_rB")
        self.space_layout.addWidget(self.os_rB)
        self.os_rB.setToolTip("Perform transformation in local space")
        self.os_rB.setText("Object space")

        # Mirroring
        self.mirroring_groupBox = QtWidgets.QGroupBox(self.tab)
        self.mirroring_groupBox.setTitle("")
        self.mirroring_groupBox.setObjectName("groupBox_4")
        self.position_layout.addWidget(self.mirroring_groupBox)
        # Buttons
        self.mirroring_layout = QtWidgets.QVBoxLayout(self.mirroring_groupBox)
        self.mirroring_layout.setObjectName("gridLayout_2")
        # Mirror
        self.mirror_cB = QtWidgets.QCheckBox(self.mirroring_groupBox)
        self.mirror_cB.setObjectName("mirror_cB")
        self.mirror_cB.setToolTip("Mirror the selected values")
        self.mirror_cB.setText("Mirror ")
        self.mirroring_layout.addWidget(self.mirror_cB)
        # Axes
        self.axis_label = QtWidgets.QLabel(self.mirroring_groupBox)
        self.axis_label.setObjectName("axis_label")
        self.axis_label.setText("Axis")
        self.mirroring_layout.addWidget(self.axis_label)
        # X
        self.mirror_x_rB = QtWidgets.QRadioButton(self.mirroring_groupBox)
        self.mirror_x_rB.setObjectName("mirror_x_rB")
        self.mirror_x_rB.setToolTip("Mirror along X axis")
        self.mirror_x_rB.setText("X")
        self.mirroring_layout.addWidget(self.mirror_x_rB)
        self.mirror_x_rB.setChecked(True)
        # Y
        self.mirror_y_rB = QtWidgets.QRadioButton(self.mirroring_groupBox)
        self.mirror_y_rB.setObjectName("mirror_y_rB")
        self.mirror_y_rB.setToolTip("Mirror along Y axis")
        self.mirror_y_rB.setText("Y")
        self.mirroring_layout.addWidget(self.mirror_y_rB)
        # Z
        self.mirror_z_rB = QtWidgets.QRadioButton(self.mirroring_groupBox)
        self.mirror_z_rB.setObjectName("mirror_z_rB")
        self.mirror_z_rB.setToolTip("Mirror along Z axis")
        self.mirror_z_rB.setText("Z")
        self.mirroring_layout.addWidget(self.mirror_z_rB)

        # Mirroring behaviour
        self.behaviour_groupBox = QtWidgets.QGroupBox(self.tab)
        self.behaviour_groupBox.setTitle("")
        self.behaviour_groupBox.setObjectName("behaviour_groupBox")
        self.position_layout.addWidget(self.behaviour_groupBox)
        # Layout
        self.behaviour_layout = QtWidgets.QVBoxLayout(self.behaviour_groupBox)
        self.behaviour_layout.setObjectName("behaviour_layout")
        # Behaviour
        self.mirror_behavior_rB = QtWidgets.QRadioButton(self.behaviour_groupBox)
        self.mirror_behavior_rB.setObjectName("mirror_behavior_rB")
        self.mirror_behavior_rB.setToolTip("Perform transformation in local space")
        self.mirror_behavior_rB.setText("Behavior")
        self.behaviour_layout.addWidget(self.mirror_behavior_rB)
        self.mirror_behavior_rB.setChecked(True)
        # Scale
        self.mirror_scale_rB = QtWidgets.QRadioButton(self.behaviour_groupBox)
        self.mirror_scale_rB.setObjectName("mirror_scale_rB")
        self.mirror_scale_rB.setToolTip("Perform transformation in world space")
        self.mirror_scale_rB.setText("Scale")
        self.behaviour_layout.addWidget(self.mirror_scale_rB)
        self.mirror_scale_rB.setChecked(False)

        # Move buttons
        # Move
        self.move_pB = QtWidgets.QPushButton(self.tab)
        self.move_pB.setMinimumSize(QtCore.QSize(0, 30))
        self.move_pB.setObjectName("move_pB")
        self.move_pB.setToolTip("select one object : move based on its own coordinates. Select 2 objects : first one : source, second one : target ; move the second one on the base of the coordinates of the first one")
        self.move_pB.setText("Move")
        self.position_layout.addWidget(self.move_pB)
        # Move even
        self.move_even_pB = QtWidgets.QPushButton(self.tab)
        self.move_even_pB.setMinimumSize(QtCore.QSize(0, 30))
        self.move_even_pB.setObjectName("move_even_pB")
        self.move_even_pB.setToolTip("multi selection : 1st object : first pair source, 2nd object : first pair target ; 3rd object : second pair source, 4th object : second pair target ; etc.")
        self.move_even_pB.setText("Move by pair")
        self.position_layout.addWidget(self.move_even_pB)

        # ========================================
        # Constrain tab layout
        self.constrain_layout = QtWidgets.QVBoxLayout(self.tab_2)
        self.constrain_layout.setObjectName("constrain_layout")

        # Maintain Offset
        self.maintain_offset_cB = QtWidgets.QCheckBox(self.tab_2)
        self.maintain_offset_cB.setObjectName("maintain_offset_cB")
        self.maintain_offset_cB.setText("Maintain offset")
        self.constrain_layout.addWidget(self.maintain_offset_cB)
        self.maintain_offset_cB.setChecked(True)

        # Aim vector
        self.aim_groupBox = QtWidgets.QGroupBox(self.tab_2)
        self.aim_groupBox.setEnabled(False)
        self.aim_groupBox.setObjectName("aim_groupBox")
        self.aim_groupBox.setTitle("Aim vector")
        self.constrain_layout.addWidget(self.aim_groupBox)
        # Aim layout
        self.aim_layout = QtWidgets.QHBoxLayout(self.aim_groupBox)
        self.aim_layout.setObjectName("aim_layout")
        # X
        self.aim_vectorX_sB = QtWidgets.QSpinBox(self.aim_groupBox)
        self.aim_vectorX_sB.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_vectorX_sB.setMaximumSize(QtCore.QSize(35, 25))
        self.aim_vectorX_sB.setMinimum(-1)
        self.aim_vectorX_sB.setMaximum(1)
        self.aim_vectorX_sB.setObjectName("aim_vectorX_sB")
        self.aim_layout.addWidget(self.aim_vectorX_sB)
        self.aim_vectorX_sB.setProperty("value", 1)
        # Y
        self.aim_vectorY_sB = QtWidgets.QSpinBox(self.aim_groupBox)
        self.aim_vectorY_sB.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_vectorY_sB.setMaximumSize(QtCore.QSize(35, 25))
        self.aim_vectorY_sB.setMinimum(-1)
        self.aim_vectorY_sB.setMaximum(1)
        self.aim_vectorY_sB.setObjectName("aim_vectorY_sB")
        self.aim_layout.addWidget(self.aim_vectorY_sB)
        # Z
        self.aim_vectorZ_sB = QtWidgets.QSpinBox(self.aim_groupBox)
        self.aim_vectorZ_sB.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.aim_vectorZ_sB.setMaximumSize(QtCore.QSize(35, 25))
        self.aim_vectorZ_sB.setMinimum(-1)
        self.aim_vectorZ_sB.setMaximum(1)
        self.aim_vectorZ_sB.setObjectName("aim_vectorZ_sB")
        self.aim_layout.addWidget(self.aim_vectorZ_sB)

        # Up vector
        self.up_groupBox = QtWidgets.QGroupBox(self.tab_2)
        self.up_groupBox.setEnabled(False)
        self.up_groupBox.setObjectName("up_groupBox")
        self.up_groupBox.setTitle("Up vector")
        self.constrain_layout.addWidget(self.up_groupBox)
        # Up layout
        self.up_Layout = QtWidgets.QHBoxLayout(self.up_groupBox)
        self.up_Layout.setObjectName("up_Layout")
        # X
        self.up_vectorX_sB = QtWidgets.QSpinBox(self.up_groupBox)
        self.up_vectorX_sB.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.up_vectorX_sB.setMaximumSize(QtCore.QSize(35, 25))
        self.up_vectorX_sB.setMinimum(-1)
        self.up_vectorX_sB.setMaximum(1)
        self.up_vectorX_sB.setObjectName("up_vectorX_sB")
        self.up_Layout.addWidget(self.up_vectorX_sB)
        # Y
        self.up_vectorY_sB = QtWidgets.QSpinBox(self.up_groupBox)
        self.up_vectorY_sB.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.up_vectorY_sB.setMaximumSize(QtCore.QSize(35, 25))
        self.up_vectorY_sB.setMinimum(-1)
        self.up_vectorY_sB.setMaximum(1)
        self.up_vectorY_sB.setObjectName("up_vectorY_sB")
        self.up_Layout.addWidget(self.up_vectorY_sB)
        self.up_vectorY_sB.setProperty("value", 1)
        # Z
        self.up_vectorZ_sB = QtWidgets.QSpinBox(self.up_groupBox)
        self.up_vectorZ_sB.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.up_vectorZ_sB.setMaximumSize(QtCore.QSize(35, 25))
        self.up_vectorZ_sB.setMinimum(-1)
        self.up_vectorZ_sB.setMaximum(1)
        self.up_vectorZ_sB.setObjectName("up_vectorZ_sB")
        self.up_Layout.addWidget(self.up_vectorZ_sB)

        # Constrain type
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.constrain_layout.addLayout(self.verticalLayout)
        # Point constrain
        self.point_ct_rB = QtWidgets.QRadioButton(self.tab_2)
        self.point_ct_rB.setChecked(True)
        self.point_ct_rB.setObjectName("point_ct_rB")
        self.point_ct_rB.setText("pointConstraint")
        self.verticalLayout.addWidget(self.point_ct_rB)
        # Orient constrain
        self.orient_ct_rB = QtWidgets.QRadioButton(self.tab_2)
        self.orient_ct_rB.setObjectName("orient_ct_rB")
        self.orient_ct_rB.setText("orientConstraint")
        self.verticalLayout.addWidget(self.orient_ct_rB)
        # Aim constrain
        self.aim_ct_rB = QtWidgets.QRadioButton(self.tab_2)
        self.aim_ct_rB.setObjectName("aim_ct_rB")
        self.aim_ct_rB.setText("aimConstraint")
        self.verticalLayout.addWidget(self.aim_ct_rB)
        # Scale constrain
        self.scale_ct_rB = QtWidgets.QRadioButton(self.tab_2)
        self.scale_ct_rB.setObjectName("scale_ct_rB")
        self.scale_ct_rB.setText("scaleConstraint")
        self.verticalLayout.addWidget(self.scale_ct_rB)
        # Parent constrain
        self.parent_ct_rB = QtWidgets.QRadioButton(self.tab_2)
        self.parent_ct_rB.setObjectName("parent_ct_rB")
        self.parent_ct_rB.setText("parentConstraint")
        self.verticalLayout.addWidget(self.parent_ct_rB)
        # Mirror constrain
        self.mirror_ct_rB = QtWidgets.QRadioButton(self.tab_2)
        self.mirror_ct_rB.setEnabled(True)
        self.mirror_ct_rB.setObjectName("mirror_ct_rB")
        self.mirror_ct_rB.setText("Mirror selected")
        self.verticalLayout.addWidget(self.mirror_ct_rB)

        # Buttons
        # Constrain
        self.constrain_pB = QtWidgets.QPushButton(self.tab_2)
        self.constrain_pB.setMinimumSize(QtCore.QSize(0, 30))
        self.constrain_pB.setObjectName("constrain_pB")
        self.constrain_pB.setText("Constrain")
        self.constrain_layout.addWidget(self.constrain_pB)
        # Constrain even
        self.constrain_even_pB = QtWidgets.QPushButton(self.tab_2)
        self.constrain_even_pB.setMinimumSize(QtCore.QSize(0, 30))
        self.constrain_even_pB.setObjectName("constrain_by_pair_pB")
        self.constrain_even_pB.setText("Constrain by pair")
        self.constrain_layout.addWidget(self.constrain_even_pB)

        # self.setTabOrder(self.tabWidget, self.ws_rB)
        # self.setTabOrder(self.ws_rB, self.os_rB)
        # self.setTabOrder(self.os_rB, self.mirror_cB)
        # self.setTabOrder(self.mirror_cB, self.mirror_x_rB)
        # self.setTabOrder(self.mirror_x_rB, self.mirror_y_rB)
        # self.setTabOrder(self.mirror_y_rB, self.mirror_z_rB)
        # self.setTabOrder(self.mirror_z_rB, self.move_pB)
        # self.setTabOrder(self.move_pB, self.move_even_pB)
        # self.setTabOrder(self.move_even_pB, self.translate_cB)
        # self.setTabOrder(self.translate_cB, self.tx_cB)
        # self.setTabOrder(self.tx_cB, self.ty_cB)
        # self.setTabOrder(self.ty_cB, self.tz_cB)
        # self.setTabOrder(self.tz_cB, self.rotate_cB)
        # self.setTabOrder(self.rotate_cB, self.rx_cB)
        # self.setTabOrder(self.rx_cB, self.ry_cB)
        # self.setTabOrder(self.ry_cB, self.rz_cB)
        # self.setTabOrder(self.rz_cB, self.scale_cB)
        # self.setTabOrder(self.scale_cB, self.sx_cB)
        # self.setTabOrder(self.sx_cB, self.sy_cB)
        # self.setTabOrder(self.sy_cB, self.sz_cB)
        # self.setTabOrder(self.sz_cB, self.maintain_offset_cB)
        # self.setTabOrder(self.maintain_offset_cB, self.aim_vectorX_sB)
        # self.setTabOrder(self.aim_vectorX_sB, self.aim_vectorY_sB)
        # self.setTabOrder(self.aim_vectorY_sB, self.aim_vectorZ_sB)
        # self.setTabOrder(self.aim_vectorZ_sB, self.up_vectorX_sB)
        # self.setTabOrder(self.up_vectorX_sB, self.up_vectorY_sB)
        # self.setTabOrder(self.up_vectorY_sB, self.up_vectorZ_sB)
        # self.setTabOrder(self.up_vectorZ_sB, self.point_ct_rB)
        # self.setTabOrder(self.point_ct_rB, self.orient_ct_rB)
        # self.setTabOrder(self.orient_ct_rB, self.aim_ct_rB)
        # self.setTabOrder(self.aim_ct_rB, self.scale_ct_rB)
        # self.setTabOrder(self.scale_ct_rB, self.parent_ct_rB)
        # self.setTabOrder(self.parent_ct_rB, self.mirror_ct_rB)
        # self.setTabOrder(self.mirror_ct_rB, self.constrain_pB)
        # self.setTabOrder(self.constrain_pB, self.constrain_even_pB)

    def check_translate(self):
        """Connect translate checking"""
        if self.translate_cB.isChecked():
            self.tx_cB.setChecked(True)
            self.ty_cB.setChecked(True)
            self.tz_cB.setChecked(True)
        else:
            self.tx_cB.setChecked(False)
            self.ty_cB.setChecked(False)
            self.tz_cB.setChecked(False)
        # QtCore.QObject.connect(self.translate_cB,
        #                        QtCore.SIGNAL("toggled(bool)"),
        #                        self.tx_cB.setChecked)
        # QtCore.QObject.connect(self.translate_cB,
        #                        QtCore.SIGNAL("toggled(bool)"),
        #                        self.ty_cB.setChecked)
        # QtCore.QObject.connect(self.translate_cB,
        #                        QtCore.SIGNAL("toggled(bool)"),
        #                        self.tz_cB.setChecked)

    def check_rotate(self):
        """Connect rotate checking"""
        if self.rotate_cB.isChecked():
            self.rx_cB.setChecked(True)
            self.ry_cB.setChecked(True)
            self.rz_cB.setChecked(True)
        else:
            self.rx_cB.setChecked(False)
            self.ry_cB.setChecked(False)
            self.rz_cB.setChecked(False)

    def check_scale(self):
        """Connect translate checking"""
        if self.rotate_cB.isChecked():
            self.rx_cB.setChecked(True)
            self.ry_cB.setChecked(True)
            self.rz_cB.setChecked(True)
        else:
            self.rx_cB.setChecked(False)
            self.ry_cB.setChecked(False)
            self.rz_cB.setChecked(False)

    def check_from_pointct(self):
        """Check translate by default when selecting point constraint"""
        if self.point_ct_rB.isChecked():
            self.translate_cB.setChecked(True)
        else:
            self.translate_cB.setChecked(False)

    def check_from_orientct(self):
        """Check rotate by default when selecting orient constraint"""
        if self.orient_ct_rB.isChecked():
            self.rotate_cB.setChecked(True)
        else:
            self.rotate_cB.setChecked(False)

    def check_from_aimct(self):
        """Enable aim and up groupBoxes when checking aimConstraint rB"""
        if self.aim_ct_rB.isChecked():
            self.aim_groupBox.setEnabled(True)
            self.up_groupBox.setEnabled(True)
            self.rotate_cB.setChecked(True)
        else:
            self.aim_groupBox.setDisabled(True)
            self.up_groupBox.setDisabled(True)
            self.rotate_cB.setChecked(False)

    def check_from_scalect(self):
        """Check scale by default when selecting scale constraint"""
        if self.scale_ct_rB.isChecked():
            self.scale_cB.setChecked(True)
        else:
            self.scale_cB.setChecked(False)

    def check_from_parentct(self):
        """Check translate/rotate by default when selecting parent constraint"""
        if self.parent_ct_rB.isChecked():
            self.translate_cB.setChecked(True)
            self.rotate_cB.setChecked(True)
        else:
            self.translate_cB.setChecked(False)
            self.rotate_cB.setChecked(False)

    def check_from_mirrorct(self):
        """Disable constrain by pair push button"""
        if self.mirror_ct_rB.isChecked():
            self.constrain_even_pB.setDisabled()
        else:
            self.constrain_even_pB.setDisabled()

    def get_data(self):
        """
        Get data from ui

        :return: dict containing all the data from the ui :
        {'attributes',
         'world_space',
         'mirror_axis',
         'mirror',
         'up_vector',
         'aim_vector',
         'maintain_offset',
         'skip_translation',
         'skip_rotation',
         'skip_scale',
         'constraint_type'}
        :rtype: dict
        """
        # Translate
        translate = list()
        if self.tx_cB.isChecked():
            translate.append('x')
        if self.ty_cB.isChecked():
            translate.append('y')
        if self.tz_cB.isChecked():
            translate.append('z')

        # Rotate
        rotate = list()
        if self.rx_cB.isChecked():
            rotate.append('x')
        if self.ry_cB.isChecked():
            rotate.append('y')
        if self.rz_cB.isChecked():
            rotate.append('z')

        # Scale
        scale = list()
        if self.sx_cB.isChecked():
            scale.append('x')
        if self.sy_cB.isChecked():
            scale.append('y')
        if self.sz_cB.isChecked():
            scale.append('z')

        # World space / object space
        world_space = self.ws_rB.isChecked()

        # Mirror
        mirror = self.mirror_cB.isChecked()

        # behavior
        behavior = self.mirror_behavior_rB.isChecked()

        # Up vector / aim vector
        up_vector = (self.up_vectorX_sB.value(),
                     self.up_vectorY_sB.value(),
                     self.up_vectorZ_sB.value())

        aim_vector = (self.aim_vectorX_sB.value(),
                      self.aim_vectorY_sB.value(),
                      self.aim_vectorZ_sB.value())

        # Mirror axis
        if self.mirror_x_rB.isChecked():
            mirror_axis = 'x'
        elif self.mirror_y_rB.isChecked():
            mirror_axis = 'y'
        else:
            mirror_axis = 'z'

        # Maintain offset
        maintain_offset = self.maintain_offset_cB.isChecked()

        # Skip axes
        skip_trans = [axis for axis in ['x', 'y', 'z'] if axis not in translate]
        skip_rot = [axis for axis in ['x', 'y', 'z'] if axis not in rotate]
        skip_scale = [axis for axis in ['x', 'y', 'z'] if axis not in scale]

        # Constraint type
        ct_rbs = [self.point_ct_rB,
                  self.orient_ct_rB,
                  self.aim_ct_rB,
                  self.scale_ct_rB,
                  self.parent_ct_rB,
                  self.mirror_ct_rB]
        constraint_type = [str(rB.text()) for rB in ct_rbs if rB.isChecked()][0]

        return {'translate': translate,
                'rotate': rotate,
                'scale': scale,
                'world_space': world_space,
                'mirror_axis': mirror_axis,
                'mirror': mirror,
                'up_vector': up_vector,
                'aim_vector': aim_vector,
                'maintain_offset': maintain_offset,
                'skip_translation': skip_trans,
                'skip_rotation': skip_rot,
                'skip_scale': skip_scale,
                'constraint_type': constraint_type,
                'behavior': behavior}

    def move_obj(self):
        data = self.get_data()
        Mmu.move_from_ui(data)

    def move_even_obj(self):
        data = self.get_data()
        Mmu.move_even_from_ui(data)

    def constrain(self):
        data = self.get_data()
        Mmu.constrain_from_ui(data)

    def constrain_even(self):
        data = self.get_data()
        Mmu.constrain_even_from_ui(data)

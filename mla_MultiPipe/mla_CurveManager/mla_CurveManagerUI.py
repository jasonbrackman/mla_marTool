import os
from pprint import pprint
import logging
from Qt import QtWidgets, QtCore, QtWidgets

import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as import_utils
import mla_GeneralPipe.mla_UI_utils.mla_UI_utils as UIu
import mla_GeneralPipe.mla_file_utils.mla_path_utils as pu
import mla_GeneralPipe.mla_file_utils.mla_file_utils as fu
import mla_GeneralPipe.mla_general_utils.mla_name_utils as nu

reload(import_utils)
reload(UIu)
reload(pu)
reload(fu)
reload(nu)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

APPLICATION = import_utils.get_application()
dockable = import_utils.get_dockable_widget(APPLICATION)

if APPLICATION == 'Maya':
    import mla_MayaPipe.mla_rig_utils.mla_Maya_matrix_utils as Mmu
    import mla_MayaPipe.mla_Maya_general_utils.mla_general_utils as Mgu
    import mla_MayaPipe.mla_Maya_general_utils.mla_Maya_curve_utils as Mcu
elif APPLICATION == 'Max':
    import mla_MaxPipe.mla_rig_utils.mla_Max_matrix_utils as Mmu
    import mla_MaxPipe.mla_Max_general_utils.mla_general_utils as Mgu
    import mla_MaxPipe.mla_Max_general_utils.mla_Max_curve_utils as Mcu
else:
    pass

reload(Mmu)
reload(Mgu)
reload(Mcu)

FOLDER_PATH = '/'.join(__file__.split('\\')[:-1])
DICTS_PATH = '%s/curve_dictionaries/%s.json' % (FOLDER_PATH, APPLICATION)


class CurveManagerUI(dockable, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(CurveManagerUI, self).__init__(parent=parent)

        self.setWindowTitle('CM')
        self.crv_data = self.get_crv_data()

        # UI
        self.buildUI()

        # Connexion
        self.save_to_dict_pB.clicked.connect(self.save_crv)
        self.delete_shape_pB.clicked.connect(self.delete_crv)
        self.creation_pB.clicked.connect(self.create_crv_from_ui)
        self.curve_edition_pB.clicked.connect(self.edit_crv_from_ui)

        if self.crv_data:
            self.crv_list = self.create_crv_list()

            # Update
            UIu.update_combobox(self.curve_cbB, self.crv_list)
            UIu.update_combobox(self.curve_to_delete_cbB, self.crv_list)

    def buildUI(self):
        logging.info('Building UI')

        # ========================================
        self.setFixedSize(QtCore.QSize(210, 270))

        # Tabs
        tabWidget = QtWidgets.QTabWidget(self)
        tabWidget.setMinimumSize(QtCore.QSize(210, 270))
        tabWidget.setStyleSheet('QTabBar::tab {height:25px; width: 105px}')
        tabWidget.setObjectName("tabWidget")
        # Curve creation/edition tab
        tab = QtWidgets.QWidget()
        tab.setObjectName("tab")
        tabWidget.addTab(tab, 'Create/Edit')
        tabWidget.setTabText(tabWidget.indexOf(tab), 'Create / Edit')
        # tabWidget.setStyleSheet(tabWidget.indexOf(tab), 105)
        # Managing tab
        tab_2 = QtWidgets.QWidget()
        tab_2.setObjectName("tab_2")
        tabWidget.addTab(tab_2, 'Managing')
        tabWidget.setTabText(tabWidget.indexOf(tab_2), "Managing")
        # tabWidget.setStyleSheet(tabWidget.indexOf(tab_2), 105)

        # ========================================
        # Creation/Edition tab layout
        creation_layout = QtWidgets.QVBoxLayout(tab)
        creation_layout.setObjectName("creation_layout")
        # creation_layout.setContentsMargins(10, 10, 10, 10)

        # Name widget
        name_widget = QtWidgets.QWidget()
        name_layout = QtWidgets.QHBoxLayout(name_widget)
        name_layout.setContentsMargins(0, 0, 0, 0)
        creation_layout.addWidget(name_widget)
        # Label
        name_label = QtWidgets.QLabel(tab)
        name_label.setFixedSize(QtCore.QSize(60, 25))
        name_label.setObjectName("label")
        name_label.setText("Name")
        name_layout.addWidget(name_label)
        # LineEdit
        self.name_lE = QtWidgets.QLineEdit(tab)
        self.name_lE.setMinimumSize(QtCore.QSize(0, 25))
        self.name_lE.setMaximumSize(QtCore.QSize(128, 25))
        self.name_lE.setObjectName("name_lE")
        name_layout.addWidget(self.name_lE)

        # Curve shape
        curve_widget = QtWidgets.QWidget()
        curve_layout = QtWidgets.QHBoxLayout(curve_widget)
        curve_layout.setContentsMargins(0, 0, 0, 0)
        creation_layout.addWidget(curve_widget)
        # Label
        label_2 = QtWidgets.QLabel(tab)
        label_2.setFixedSize(QtCore.QSize(60, 25))
        label_2.setObjectName("label_2")
        label_2.setText("Curve")
        curve_layout.addWidget(label_2)
        # ComboBox
        self.curve_cbB = QtWidgets.QComboBox(tab)
        self.curve_cbB.setMinimumSize(QtCore.QSize(0, 25))
        self.curve_cbB.setMaximumSize(QtCore.QSize(128, 25))
        self.curve_cbB.setObjectName("curve_comB")
        curve_layout.addWidget(self.curve_cbB)

        # Orientation
        orientation_widget = QtWidgets.QWidget()
        orientation_layout = QtWidgets.QHBoxLayout(orientation_widget)
        orientation_layout.setContentsMargins(0, 0, 0, 0)
        creation_layout.addWidget(orientation_widget)
        # Label
        label_3 = QtWidgets.QLabel(tab)
        label_3.setFixedSize(QtCore.QSize(60, 25))
        label_3.setObjectName("label_3")
        label_3.setText("Orientation")
        orientation_layout.addWidget(label_3)
        # RadioButtons
        self.orientation_rB_x = QtWidgets.QRadioButton(tab)
        self.orientation_rB_x.setObjectName("orientation_rB_x")
        self.orientation_rB_x.setText("X")
        self.orientation_rB_x.setChecked(True)
        orientation_layout.addWidget(self.orientation_rB_x)
        self.orientation_rB_y = QtWidgets.QRadioButton(tab)
        self.orientation_rB_y.setObjectName("orientation_rB_y")
        self.orientation_rB_y.setText("Y")
        orientation_layout.addWidget(self.orientation_rB_y)
        self.orientation_rB_z = QtWidgets.QRadioButton(tab)
        self.orientation_rB_z.setObjectName("orientation_rB_z")
        self.orientation_rB_z.setText("Z")
        orientation_layout.addWidget(self.orientation_rB_z)

        # Mirror
        mirror_widget = QtWidgets.QWidget()
        mirror_layout = QtWidgets.QHBoxLayout(mirror_widget)
        mirror_layout.setContentsMargins(0, 0, 0, 0)
        creation_layout.addWidget(mirror_widget)
        # Label
        label_4 = QtWidgets.QLabel(tab)
        label_4.setFixedSize(QtCore.QSize(60, 25))
        label_4.setObjectName("label_4")
        label_4.setText("Mirror")
        mirror_layout.addWidget(label_4)
        # CheckBoxes
        self.mirror_cB_x = QtWidgets.QCheckBox(tab)
        self.mirror_cB_x.setObjectName("mirror_cB_x")
        self.mirror_cB_x.setText("X")
        mirror_layout.addWidget(self.mirror_cB_x)
        self.mirror_cB_y = QtWidgets.QCheckBox(tab)
        self.mirror_cB_y.setObjectName("mirror_cB_y")
        self.mirror_cB_y.setText("Y")
        mirror_layout.addWidget(self.mirror_cB_y)
        self.mirror_cB_z = QtWidgets.QCheckBox(tab)
        self.mirror_cB_z.setObjectName("mirror_cB_z")
        self.mirror_cB_z.setText("Z")
        mirror_layout.addWidget(self.mirror_cB_z)

        # Creation PushButton
        self.creation_pB = QtWidgets.QPushButton(tab)
        self.creation_pB.setMinimumSize(QtCore.QSize(0, 25))
        self.creation_pB.setMaximumSize(QtCore.QSize(188, 25))
        self.creation_pB.setObjectName("creation_pB")
        self.creation_pB.setText("Creation")
        creation_layout.addWidget(self.creation_pB)

        # Remove shape CheckBox
        self.remove_shape_cB = QtWidgets.QCheckBox(tab)
        self.remove_shape_cB.setMinimumSize(QtCore.QSize(0, 25))
        self.remove_shape_cB.setObjectName("remove_shape_cB")
        self.remove_shape_cB.setText("Remove Shape")
        creation_layout.addWidget(self.remove_shape_cB)

        # Curve edition PushButton
        self.curve_edition_pB = QtWidgets.QPushButton(tab)
        self.curve_edition_pB.setMinimumSize(QtCore.QSize(0, 25))
        self.curve_edition_pB.setMaximumSize(QtCore.QSize(188, 25))
        self.curve_edition_pB.setObjectName("curve_edition_pB")
        self.curve_edition_pB.setText("Edition")
        creation_layout.addWidget(self.curve_edition_pB)

        # ========================================
        # Managing tab layout
        managing_layout = QtWidgets.QVBoxLayout(tab_2)
        managing_layout.setObjectName("managing_layout")
        # managing_layout.setContentsMargins(10, 10, 10, 10)

        # Name widget
        managing_name_widget = QtWidgets.QWidget()
        managing_name_layout = QtWidgets.QHBoxLayout(managing_name_widget)
        managing_name_layout.setContentsMargins(0, 0, 0, 0)
        managing_layout.addWidget(managing_name_widget)
        # Label
        label_5 = QtWidgets.QLabel(tab_2)
        label_5.setMinimumSize(QtCore.QSize(0, 25))
        label_5.setObjectName("label_5")
        label_5.setText("Shape name")
        managing_name_layout.addWidget(label_5)
        # LineEdit
        self.new_shape_lE = QtWidgets.QLineEdit(tab_2)
        self.new_shape_lE.setMinimumSize(QtCore.QSize(0, 25))
        self.new_shape_lE.setObjectName("new_shape_lE")
        managing_name_layout.addWidget(self.new_shape_lE)

        # Save
        self.save_to_dict_pB = QtWidgets.QPushButton(tab_2)
        self.save_to_dict_pB.setMinimumSize(QtCore.QSize(0, 25))
        self.save_to_dict_pB.setObjectName("save_to_dict_pB")
        self.save_to_dict_pB.setText("Save / Edit")
        managing_layout.addWidget(self.save_to_dict_pB)

        # Delete name widget
        delete_name_widget = QtWidgets.QWidget()
        delete_name_layout = QtWidgets.QHBoxLayout(delete_name_widget)
        delete_name_layout.setContentsMargins(0, 0, 0, 0)
        managing_layout.addWidget(delete_name_widget)
        # Label
        label_6 = QtWidgets.QLabel(tab_2)
        label_6.setMinimumSize(QtCore.QSize(0, 25))
        label_6.setMaximumSize(QtCore.QSize(59, 25))
        label_6.setObjectName("label_6")
        label_6.setText("Curve name")
        delete_name_layout.addWidget(label_6)
        # CheckBox
        self.curve_to_delete_cbB = QtWidgets.QComboBox(tab_2)
        self.curve_to_delete_cbB.setMinimumSize(QtCore.QSize(0, 25))
        self.curve_to_delete_cbB.setMaximumSize(QtCore.QSize(123, 25))
        self.curve_to_delete_cbB.setObjectName("curve_to_delete_cbB")
        delete_name_layout.addWidget(self.curve_to_delete_cbB)

        # Delete curve info pushButton
        self.delete_shape_pB = QtWidgets.QPushButton(tab_2)
        self.delete_shape_pB.setMinimumSize(QtCore.QSize(0, 25))
        self.delete_shape_pB.setObjectName("delete_shape_pB")
        self.delete_shape_pB.setText("Delete")
        managing_layout.addWidget(self.delete_shape_pB)

        tabWidget.setCurrentIndex(0)

    def get_ui_data(self):
        """
        Get data from ui
        :return:
        """
        new_shape_name = self.new_shape_lE.text()
        crv_to_delete = self.curve_to_delete_cbB.currentText()
        crv_name = self.name_lE.text()
        remove_shape = self.remove_shape_cB.isChecked()
        crv_type = self.curve_cbB.currentText()

        if self.orientation_rB_x.isChecked():
            axis = 'x'
        elif self.orientation_rB_y.isChecked():
            axis = 'y'
        else:
            axis = 'z'

        mirror = list()

        for cb in [self.mirror_cB_x, self.mirror_cB_y, self.mirror_cB_z]:
            mirror.append(cb.isChecked())

        return {'new_shape_name': new_shape_name,
                'crv_to_delete': crv_to_delete,
                'name': crv_name,
                'remove_shape': remove_shape,
                'crv_type': crv_type,
                'axis': axis,
                'mirror': mirror}

    def delete_crv(self):
        """
        Delete selected curve
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()

        crv_type = data['new_shape_name']

        fu.FileSystem.delete_if_exists('%s/%s.json'
                                       % (DICTS_PATH, crv_type))

        self.crv_dicts = self.build_files_list(DICTS_PATH)
        self.update_combobox(self.curve_comB, self.crv_dicts)
        self.update_combobox(self.curve_to_delete_cbB, self.crv_dicts)

        return

    def save_crv(self):
        """
        Save selected curve under selected name. If no name given, use crv name.
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()

        # get selection
        selection = Mgu.get_selection()
        # get the name of the curve
        crv_name = selection[0]

        if data['new_shape_name']:
            crv_type = data['new_shape_name']
        else:
            crv_type = crv_name

        crv_dict = Mcu.get_crv_info(crv_name)

        self.crv_data[crv_type] = crv_dict
        fu.FileSystem.save_to_json(self.crv_data, DICTS_PATH)

        self.crv_list = self.create_crv_list()

        UIu.update_combobox(self.curve_cbB, self.crv_list)
        UIu.update_combobox(self.curve_to_delete_cbB, self.crv_list)

        return

    def create_crv_from_ui(self):
        """
        Create curve(s) using ui data
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()
        selection = Mgu.get_selection()

        name = nu.create_name(main_name=data['name'])
        print name

        crv_dict = self.crv_data[data['crv_type']]

        Mcu.create_edit_crv(selection, crv_dict, name, create_orig=True,
                            axis=data['axis'], mirror=data['mirror'])

    def edit_crv_from_ui(self):
        """
        Edit curve(s) using ui data
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()
        selection = Mgu.get_selection()
        crv_dict = self.crv_data[data['crv_type']]
        if data['remove_shape']:
            add = False
        else:
            add = True

        Mcu.create_edit_crv(selection, crv_dict, 'ctrl', edit=True, add=add,
                            axis=data['axis'], mirror=data['mirror'])

    def get_crv_data(self):
        """
        Get data from the curve dictionary.
        :return: data of all stored curves.
        :rtype: dict
        """
        if os.path.isfile(DICTS_PATH):
            crv_data = fu.FileSystem.load_from_json(DICTS_PATH)
        else:
            crv_data = dict()

        return crv_data

    # TODO : document this functions
    def create_crv_list(self):
        """

        :return:
        """
        crv_list = list()
        for key in self.crv_data.keys():
            crv_list.append(key)

        return crv_list

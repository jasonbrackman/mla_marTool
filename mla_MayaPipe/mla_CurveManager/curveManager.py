__author__ = 'Martin'
import os

import maya.cmds as mc
from PySide.QtCore import *
from PySide.QtGui import *

import curveManager_ui
import ml_file as ml_file
import orig

reload(curveManager_ui)

folder_path = '/'.join(__file__.split('\\')[:-1])

dicts_path = folder_path + '/curve_dictionaries'


# ----------------------------------------------------------------
class CurveManager(QDialog, curveManager_ui.Ui_CMMainWindow):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.save_to_dict_pB.clicked.connect(self.save_crv)
        self.delete_shape_pB.clicked.connect(self.delete_crv)
        self.creation_pB.clicked.connect(self.create_crv_from_ui)
        self.curve_edition_pB.clicked.connect(self.edit_crv_from_ui)

        self.crv_dicts = self.build_files_list(dicts_path)

        self.update_combobox(self.curve_comB, self.crv_dicts)
        self.update_combobox(self.curve_to_delete_comB, self.crv_dicts)

    def get_ui_data(self):
        """
        Get data from ui
        :return:
        """
        new_shape_name = self.new_shape_lE.text()
        crv_to_delete = self.curve_to_delete_comB.currentText()
        crv_name = self.name_lE.text()
        remove_shape = self.remove_shape_cB.isChecked()
        crv_type = self.curve_comB.currentText()

        return {'new_shape_name': new_shape_name,
                'crv_to_delete': crv_to_delete,
                'crv_name': crv_name,
                'remove_shape': remove_shape,
                'crv_type': crv_type}

    @staticmethod
    def update_combobox(combobox, items, block='True'):
        """
        Update the given combobox
        :param combobox: combobox to update,  ie: self.bs_node_menu
        :type combobox: qt object

        :param items: list of items to add to the given combobox
        :type items: list

        :param block: Define if signal must be blocked during operation
        :type block: boolean
        """

        # --- Blocking signals from ui
        if block:
            combobox.blockSignals(True)
        else:
            pass

        # --- Init items if empty
        if items == []:
            items = ['None']

        items.sort()

        # --- Get currently selected text
        selected_text = combobox.currentText()
        # --- Clear combobox
        combobox.clear()
        # --- Add items
        combobox.addItems(items)
        # --- If current selected item in new item list, select it
        if selected_text in items:
            text_index = combobox.findText(selected_text)
            combobox.setCurrentIndex(text_index)
        else:
            combobox.setCurrentIndex(0)

        for i, item in enumerate(items):
            combobox.setItemData(i, item, Qt.ToolTipRole)

        # --- Unblocking signals from ui
        combobox.blockSignals(False)

    @staticmethod
    def build_files_list(given_path):
        """
        Create a list of all the files in the given directory
        :param given_path: path to the directory you want to list the files in
        :return: all the files in that directory (list)
        """
        file_names = list()

        # Set current directory to the given path
        os.chdir(given_path)
        # Filter files
        files = [dir_file for dir_file in os.listdir(given_path)
                 if os.path.isfile(os.path.join(given_path, dir_file))]
        # Filter maya files
        json_files = [json_file for json_file in files
                      if '.json' in json_file]
        # If no maya files
        if json_files == []:
            # list is used as verbose
            json_files = ['None']
        # If there are maya files
        else:
            # Sort them
            json_files.sort(key=lambda x: os.path.getmtime(x))
            # Get most recent in first
            json_files.reverse()

        for json_file in json_files:
            print json_file.replace('.json', '')
            file_names.append(json_file.replace('.json', ''))

        return file_names

    def delete_crv(self):
        """
        Delete selected curve
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()

        crv_type = data['new_shape_name']

        ml_file.FileSystem.delete_if_exists('%s/%s.json'
                                            % (dicts_path, crv_type))

        self.crv_dicts = self.build_files_list(dicts_path)
        self.update_combobox(self.curve_comB, self.crv_dicts)
        self.update_combobox(self.curve_to_delete_comB, self.crv_dicts)

        return

    def save_crv(self):
        """
        Save selected curve under selected name. If no name given, use crv name.
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()

        # get selection
        selection = mc.ls(sl=True)
        # get the name of the curve
        crv_name = selection[0]

        if not data['new_shape_name']:
            crv_type = crv_name
        else:
            crv_type = data['new_shape_name']

        crv_dict = self. get_crv_info(crv_name)

        ml_file.FileSystem.save_to_json(crv_dict, '%s/%s.json'
                                        % (dicts_path, crv_type))

        self.crv_dicts = self.build_files_list(dicts_path)
        self.update_combobox(self.curve_comB, self.crv_dicts)
        self.update_combobox(self.curve_to_delete_comB, self.crv_dicts)

        return

    def create_crv_from_ui(self):
        """
        Create curve(s) using ui data
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()

        crv_list = self.create_edit_crv(data['crv_type'],
                                        data['crv_name'],
                                        edit=False)

        orig.orig(crv_list)

    def edit_crv_from_ui(self):
        """
        Edit curve(s) using ui data
        :return:
        """
        # Get data from ui
        data = self.get_ui_data()

        self.create_edit_crv(data['crv_type'],
                             'ctrl',
                             edit=True,
                             add=False)

    @staticmethod
    def create_edit_crv(crv_type, name, edit=False, add=False):
        """
        Create or edit curves.

        :param crv_type: type of the curve to create
        :type crv_type: str

        :param name: name of the curve to create
        :type name: str

        :param edit: edit the selected curves instead of creating new ones
        :type edit: bool

        :param add: add to the selected shape (True) or replace it (False)
        :type add: bool

        :return:
        """
        if not name:
            name = 'ctrl'

        if not crv_type or crv_type == 'None':
            crv_type = 'circle'

        # get selection
        selection = mc.ls(sl=True)
        print 1

        crv_list = list()
        print 2

        if len(selection) > 0:
            print 3
            for obj in selection:
                print 4
                position = mc.xform(obj, q=True, matrix=True, ws=True)
                print 5
                print position

                crv_list += CurveManager.create_crv(crv_type=crv_type, name=name)
                print 6
                print crv_list

                mc.xform(name, matrix=position, ws=True)
                print 7

                if edit:
                    print 8
                    if add:
                        print 9
                        add = True
                    else:
                        print 10
                        add = False

                    print 11
                    CurveManager.modify_crv_shape(target=obj,
                                                  source=name,
                                                  delete=True,
                                                  add=add)
                    print 12
        else:
            print 13
            crv_list += CurveManager.create_crv(crv_type=crv_type, name=name)
            print 14

        return crv_list

    @staticmethod
    def get_crv_info(crv_type):
        # get the name of the shape of the curve
        crv_shape_name = mc.listRelatives(crv_type, s=True)[0]
        # get the degree, spans and calculate the numbers of CV of the curve
        crv_degree = mc.getAttr(crv_shape_name + '.degree')
        crv_span = mc.getAttr(crv_shape_name + '.spans')
        cv_number = crv_degree + crv_span

        # create a curveInfo node and connect it to the curve
        crv_info = mc.createNode('curveInfo', n=crv_type + '_curveInfo')
        mc.connectAttr(crv_type + '.worldSpace', crv_info + '.inputCurve')

        # get the knots of the curve
        knots = mc.getAttr(crv_info + '.knots')[0]

        # create an empty list for the coordinates of the points of the curve
        points = list()
        # fill the list of points coordinates
        for i in range(0, cv_number):
            point = mc.getAttr(crv_info + '.controlPoints[' + str(i) + ']')
            points.append(point[0])

        crv_dict = {'degree': crv_degree, 'points': points, 'knots': knots}

        return crv_dict

    @staticmethod
    def create_crv(crv_type='circle', name='ctrl'):
        """
        Create a curve from dict and given name

        :param crv_type: type of the curve we want to create, ie: 'Sphere',
        'Cube', etc
        :type crv_type: str

        :param name: string to name the curve after
        :type name: str

        :return: curve name
        :rtype: str
        """
        crv_dict = ml_file.FileSystem.load_from_json('%s/%s.json'
                                                     % (dicts_path, crv_type))
        degree = crv_dict['degree']
        points = crv_dict['points']
        knots = crv_dict['knots']

        mc.curve(n=name, d=degree, p=points, k=knots)

        return name

    @staticmethod
    def modify_crv_shape(target='None', source='None', delete=True, add=False):
        """
        Add a shape to a ctrl or replace the ctrl shape by the new one.

        :param source: transform of the shape you want to assign
        :type source: str

        :param target: transform of the shape you want to modify
        :type target: str

        :param delete: specify if the original source shape must be kept or not
        :type delete: bool

        :param add: specify if the source shape must replace the target shape
        or be added
        :type add: bool

        :return: transform of the modified shape
        :rtype: str
        """

        # --- Get selection
        selection = mc.ls(sl=True)

        # --- Modify target and source if none provided
        if target == 'None':
            target = selection[0]
        if target == 'None' and source == 'None':
            source = selection[1]
        elif source == 'None':
            source = selection[0]
        else:
            pass

        # --- Duplicate if you don't want to delete the original source
        if not delete:
            source = mc.duplicate(source)

        # --- Get the shapes paths
        source_shape = mc.listRelatives(source, c=True, s=True, f=True)
        target_shape = mc.listRelatives(target, c=True, s=True, f=True)
        target_shape_short = mc.listRelatives(target, c=True, s=True)

        # --- Reparent the source shape to the target transform
        new_shape_name = mc.parent(source_shape, target, s=True, add=True)
        # --- Delete the source transform
        mc.delete(source)
        # --- If not add, delete the target shape
        if not add:
            mc.delete(target_shape)

        mc.rename(new_shape_name, target_shape_short)

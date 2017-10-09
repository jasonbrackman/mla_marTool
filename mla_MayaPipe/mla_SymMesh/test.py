__author__ = 'lantonm'
from PyQt4 import uic
import sip
from PyQt4 import QtGui, QtCore
import maya.OpenMayaUI as apiUI

import maya.api.OpenMaya as om2
import maya.cmds as mc

import os
from pprint import pprint

folder_path = '/'.join(__file__.split('/')[:-1])
# ----------------------- BAKE FK CHAIN TO DYNAMIC ----------------------------
# -----------------------------------------------------------------------------
# If you put the .ui file for this example elsewhere, just change this path.
ml_sym_mesh_form, ml_sym_mesh_base = uic.loadUiType('%s/SM.ui'
                                                    % folder_path)


def get_maya_window():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    :return: QtGui.QMainWindow instance of the top level Maya windows
    :rtype: QtGui.QMainWindow
    """
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return sip.wrapinstance(long(ptr), QtCore.QObject)


def ml_sym_mesh_ui():
    """
    Main proc for interface creation.
    """
    global win_sym_mesh
    try:
        win_sym_mesh.close()
    except:
        pass
    win_sym_mesh = MLSymMesh()

    win_sym_mesh.show()


class MLSymMesh(ml_sym_mesh_form, ml_sym_mesh_base):
    def __init__(self, parent=get_maya_window()):
        """
        Initialize the class and connect all the functions to the ui.

        :param parent: object to parent the window to
        :type parent: Qt object
        """
        super(MLSymMesh, self).__init__(parent)

        self.setupUi(self)
        self.setObjectName('mlSymMesh_UI')

        # Attributes
        self.base_table = {'obj_path': om2.MDagPath(),
                           'points_pos': om2.MPointArray()}
        self.target_table = {'obj_path': om2.MDagPath(),
                             'points_pos': om2.MPointArray()}
        self.current_table = {'obj_path': om2.MDagPath(),
                              'points_pos': om2.MPointArray()}
        self.sel_vtces_idcs = {'obj_path': om2.MDagPath(),
                               'indices': om2.MIntArray()}
        self.vtcs_selection = {'obj_path': om2.MDagPath(),
                               'indices': om2.MIntArray()}
        self.revert_value = 100
        self.space = om2.MSpace.kObject
        # UNDO LIST
        self.undo = dict()

        # Connections to ui
        # Get data function
        self.get_base_pB.clicked.connect(self.get_base)
        self.get_target_pB.clicked.connect(self.get_target)
        self.get_selected_vtcs_pB.clicked.connect(self.store_vtcs_selection)
        self.reset_selected_vtcs_pB.clicked.connect(self.reset_vtcs_selection)

        self.revert_to_base_slider.valueChanged.connect(self.get_revert_value)
        self.revert_to_base_sB.valueChanged.connect(self.get_revert_value)

        # Move vertices functions
        self.bake_diff_pB.clicked.connect(self.bake_difference_on_selected)

    def store_vtcs_selection(self):
        self.vtcs_selection = self.get_sel_vtces_idcs()

        self.get_selected_vtcs_pB.setStyleSheet('background-color: red')

    def reset_vtcs_selection(self):
        self.vtcs_selection = {'obj_path': om2.MDagPath(),
                               'indices': om2.MIntArray()}

        self.get_selected_vtcs_pB.setStyleSheet('background-color: dark gray')

    def undo_last_action(self):
        """
        Undo the last move stored.

        :return:
        """
        tgt_mesh = om2.MFnMesh(self.undo['obj_path'])

        tgt_mesh.setPoints(self.undo['points_pos'], om2.MSpace.kObject)

    def revert_selected_to_base(self):
        """
        Revert selected mesh or vertices to base from the registered target
        value.

        :return:
        """
        # Get selected vertices indices
        self.sel_vtces_idcs = self.get_sel_vtces_idcs()

        # Update revert value
        self.get_revert_value()

        for dag_path in self.sel_vtces_idcs['obj_path']:
            # Update current mesh table
            self.current_table = self.get_selected_mesh_points(dag_path)

            self.undo = self.current_table

            # Check if base is registered
            if not self.base_table['points_pos']:
                print 'No base selected'
                return
            # Check if target is registered
            elif not self.target_table['points_pos']:
                print 'No target registered'
                return
            # Check if something is selected
            elif not self.sel_vtces_idcs['obj_path']:
                print 'Nothing is selected'
                return
            # Revert to base
            else:
                self.revert_to_base(self.base_table['points_pos'],
                                    self.target_table['points_pos'],
                                    self.sel_vtces_idcs['indices'],
                                    self.revert_value,
                                    dag_path,
                                    self.space)

    def revert_selected_to_base_live(self):
        """
        Revert selected mesh or vertices to base from the current value.

        :return:
        """
        # Get selected vertices indices
        self.sel_vtces_idcs = self.get_sel_vtces_idcs()

        # Update revert value
        self.get_revert_value()

        for dag_path in self.sel_vtces_idcs['obj_path']:
            # Update current mesh table
            self.current_table = self.get_selected_mesh_points(dag_path)

            self.undo = self.current_table

            # Check if base is registered
            if not self.base_table['points_pos']:
                print 'No base selected'
                return
            # Check if something is selected
            elif not self.sel_vtces_idcs['obj_path']:
                print 'Nothing is selected'
                return
            # Revert to base
            else:
                self.revert_to_base(self.base_table['points_pos'],
                                    self.current_table['points_pos'],
                                    self.sel_vtces_idcs['indices'],
                                    self.revert_value,
                                    dag_path,
                                    self.space)

    def bake_difference_on_selected(self):
        """
        Bake the difference between base and target on the selected meshes using
        vertices selection (if one has been stored or is active) or on the whole
        mesh.

        :return:
        """
        # Get selected vertices indices
        self.sel_vtces_idcs = self.get_sel_vtces_idcs()
        # If no vertices are currently selected
        if self.sel_vtces_idcs['indices'].__len__() == 0:
            # If a selection is stored
            if self.vtcs_selection['indices'].__len__() > 0:
                # Replace indices using stored selection
                self.sel_vtces_idcs['indices'] = self.vtcs_selection['indices']

        for dag_path in self.sel_vtces_idcs['obj_path']:
            # Update current mesh table
            self.current_table = self.get_selected_mesh_points(dag_path)

            self.undo = self.current_table

            # Check if base is registered
            if not self.base_table['points_pos']:
                print 'No base selected'
                return
            # Check if target is registered
            elif not self.target_table['points_pos']:
                print 'No target registered'
                return
            # Check if something is selected
            elif not self.sel_vtces_idcs['obj_path']:
                print 'Nothing is selected'
                return
            # Revert to base
            else:
                self.bake_difference(self.base_table['points_pos'],
                                     self.target_table['points_pos'],
                                     self.current_table['points_pos'],
                                     self.sel_vtces_idcs['indices'],
                                     dag_path,
                                     self.space)

    @staticmethod
    def get_selected_mesh_points(obj_dag_path=''):
        """
        Get the position of every point of the selected mesh.

        :return: dag path of the object, position of the points
        :rtype: MDagPath, MPointArray
        """
        if not obj_dag_path:
            # Get current selection
            selection_list = om2.MGlobal.getActiveSelectionList()

            # Get the dag path of the first item in the selection list
            obj_dag_path = selection_list.getDagPath(0)

        # Query vertex position
        # create a Mesh functionSet from our dag object
        mfn_object = om2.MFnMesh(obj_dag_path)

        points = mfn_object.getPoints(space=om2.MSpace.kObject)

        return {'obj_path': obj_dag_path, 'points_pos': points}

    @staticmethod
    def get_sel_vtces_idcs():
        """
        Get the indices of the selected vertices.

        :return: DagPath of the current mesh, indices of the selected vertices
        :rtype: MDagPathArray, MIntArray
        """
        # Get current selection
        selection_list = om2.MGlobal.getActiveSelectionList()

        # Get the dag path and components of the first item in the list
        obj_dag_path, components = selection_list.getComponent(0)

        # Initialize MDagPathArray
        dag_path_list = om2.MDagPathArray()

        # If no vertices selected
        if components.isNull():
            # Empty list of vertices
            selected_vertices_indices = om2.MIntArray()

            # Create iterator
            sel_iter = om2.MItSelectionList(selection_list)
            # Create list of dagPath of selected objects
            while not sel_iter.isDone():
                dag_path_list.append(sel_iter.getDagPath())
                sel_iter.next()
        # If vertices are selected
        else:
            dag_path_list.append(selection_list.getDagPath(0))
            # Query vertex indices
            fn_components = om2.MFnSingleIndexedComponent(components)
            # Create an MIntArray with the vertex indices
            selected_vertices_indices = fn_components.getElements()

        return {'obj_path': dag_path_list, 'indices': selected_vertices_indices}

    @staticmethod
    def revert_to_base(base_tbl, current_tbl, sel_vtcs_idcs, val,
                       dag_path, space):
        """
        Revert selected vertices on the target mesh to the base position.

        :param base_tbl: positions of the points of the base mesh
        :type base_tbl: MPointArray

        :param current_tbl: positions of the points of the current mesh
        :type current_tbl: MPointArray

        :param sel_vtcs_idcs: indices of the selected points on the target mesh
        :type sel_vtcs_idcs: MIntArray

        :param val: percentage used for the revert to base function
        :type val: int

        :param dag_path: MDagPathArray of targets
        :type dag_path: MDagPathArray

        :param space: space in which operate the deformation (object or world)
        :type space: constant

        :return:
        """
        # Create new table for destination position
        destination_table = om2.MPointArray()

        # Init MFnMesh
        tgt_mesh = om2.MFnMesh(dag_path)

        # Loop in MPointArray
        for i in range(base_tbl.__len__()):
            # If the current point is also in selection
            if i in sel_vtcs_idcs or sel_vtcs_idcs.__len__() == 0:
                # Modify new position
                destination_table.append(base_tbl[i]
                                         + ((current_tbl[i] - base_tbl[i])
                                            * (val / 100.00)))
            # If the current point is not selected
            else:
                # Do nothing
                destination_table.append(current_tbl[i])

        # Modify points position using the new coordinates
        tgt_mesh.setPoints(destination_table, space)

    @staticmethod
    def bake_difference(base_tbl, tgt_tbl, current_tbl, sel_vtcs_idcs,
                        dag_path, space):
        """
        Bake the difference between 2 mesh on a list of vertices on a selection
        of meshes.

        :param base_tbl: positions of the points of the base mesh
        :type base_tbl: MPointArray

        :param tgt_tbl: positions of the points of the target mesh
        :type tgt_tbl: MPointArray

        :param current_tbl: positions of the points of the current mesh
        :type current_tbl: MPointArray

        :param sel_vtcs_idcs: indices of the selected points on the target mesh
        :type sel_vtcs_idcs: MIntArray

        :param dag_path: MDagPathArray of targets
        :type dag_path: MDagPathArray

        :param space: space in which operate the deformation (object or world)
        :type space: constant

        :return:
        """
        # Create new table for destination position
        destination_table = om2.MPointArray()

        # Init MFnMesh
        tgt_mesh = om2.MFnMesh(dag_path)

        # Loop in MPointArray
        for i in range(base_tbl.__len__()):
            # If the current point is also in selection
            if i in sel_vtcs_idcs or sel_vtcs_idcs.__len__() == 0:
                # Modify new position
                destination_table.append(current_tbl[i]
                                         + (tgt_tbl[i] - base_tbl[i]))
            # If the current point is not selected
            else:
                # Do nothing
                destination_table.append(current_tbl[i])

        # Modify points position using the new coordinates
        tgt_mesh.setPoints(destination_table, space)

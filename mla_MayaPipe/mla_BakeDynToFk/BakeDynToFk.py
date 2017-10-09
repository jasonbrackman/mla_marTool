__author__ = 'lantonm'
from PyQt4 import uic
import sip
from PyQt4 import QtGui, QtCore
import maya.OpenMayaUI as apiUI

import maya.cmds as mc
import maya.mel as mm

import logging
import os
import json
from collections import OrderedDict

import mJointUtils as imp_mJointUtils

from pprint import pprint

# Instance mJointsUtils
mju = imp_mJointUtils.mJointUtils()

USER = os.getenv('USER')

folder_path = '/home/%s/.config/DynToFKChain' % USER
tool_path = '/'.join(__file__.split('/')[:-1])
# ----------------------- BAKE FK CHAIN TO DYNAMIC ----------------------------
# -----------------------------------------------------------------------------
# If you put the .ui file for this example elsewhere, just change this path.
fk_to_dyn_form, fk_to_dyn_base = uic.loadUiType('%s/dynamic_to_fk_chain.ui'
                                                % tool_path)


def get_maya_window():
    """
    Get the main Maya window as a QtGui.QMainWindow instance.

    :return: QtGui.QMainWindow instance of the top level Maya windows
    :rtype: QtGui.QMainWindow
    """
    ptr = apiUI.MQtUtil.mainWindow()
    if ptr is not None:
        return sip.wrapinstance(long(ptr), QtCore.QObject)


def bake_dyn_to_fk():
    """
    Main proc for interface creation.
    """
    global win_templates
    try:
        win_templates.close()
    except:
        pass
    win_templates = BakeDynamicToFKChain()

    win_templates.show()


class FileSystem(object):
    """
    Class to centralize file manipulation.
    """

    @staticmethod
    def create_dir(dirpath):
        """
        Create Directory Tree if it does not exist.

        :param dirpath: path where to create the directory
        :type dirpath: str
        """
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    @staticmethod
    def load_from_json(filename):
        """
        Load information from json file to a python object.

        :param filename: path and name of the file to open
        :type filename: str

        :return: data contained in the given json file
        :rtype: OrderedDict
        """
        # Parse
        filename = FileSystem.normpath(filename)
        # If Exists
        if filename:
            # Verbose
            logging.info('Load from %s' % filename)
            # Open file
            with open(filename, 'r') as file_json:
                # Load and return
                return json.load(file_json, object_pairs_hook=OrderedDict)

    @staticmethod
    def save_to_json(python_object, filename):
        """
        Save a python object to a json file.

        :param python_object: object to save
        :type python_object: dict, list or var

        :param filename: path and name of the file to save to
        :type filename: str
        """
        # Normpath
        filename = FileSystem.normpath(filename, False, True)
        # Verbose
        logging.info('Save to   %s' % filename)
        # Make Folder if doesn't exists
        FileSystem.create_dir(os.path.dirname(filename))
        # Open File
        with open(filename, 'w+') as file_json:
            # Scan
            json.dump(python_object, file_json, sort_keys=True, indent=4,
                      separators=(',', ': '))

    @staticmethod
    def normpath(filepath, must_exist=True, parse_env_vars=True):
        """
        Normalize given path.

        :param filepath: path to normalize
        :type filepath: str

        :param must_exist: defines if the path must exist or not
        :type must_exist: bool

        :param parse_env_vars: defines if we must parse env var or not
        :type parse_env_vars: bool

        :return: normalized path
        :rtype: str
        """
        # Norm
        filepath = os.path.normpath(filepath)
        # If parse_env_vars
        if parse_env_vars:
            # parse
            filepath = os.path.expandvars(filepath)
        # Make slashes for Maya compatibility
        filepath = filepath.replace('\\', '/')
        # If must_exist
        if must_exist:
            # Check if exists
            if os.path.isfile(filepath) or os.path.isdir(filepath):
                # Return
                return filepath
        else:
            return filepath


class BakeDynamicToFKChain(fk_to_dyn_form, fk_to_dyn_base):

    def __init__(self, parent=get_maya_window()):
        """
        Initialize the class and connect all the functions to the ui.

        :param parent: object to parent the window to
        :type parent: Qt object
        """
        super(BakeDynamicToFKChain, self).__init__(parent)

        self.setupUi(self)
        self.setObjectName('bake_dynamic_to_fk_chain_UI')

        self.bake_to_dyn_pushButton.clicked.connect(
            self.auto_dynamic_to_fk_chain)

        self.create_preset_file()

        self.presets = FileSystem.load_from_json('%s/presets.json'
                                                 % folder_path)

        self.update_combobox(self.preset_comboBox, self.presets.keys())
        self.update_combobox(self.delete_preset_comboBox, self.presets.keys())

        self.load_preset_pushButton.clicked.connect(self.set_values)
        self.save_preset_pushButton.clicked.connect(self.save_preset)
        self.delete_preset_pushButton.clicked.connect(self.delete_preset)

    def get_data(self):
        """
        Get data from ui.

        :return: data from ui
        :rtype: dict
        """
        # Data from UI
        # Frames
        start_frame = self.start_frame_spinBox.value()
        end_frame = self.end_frame_spinBox.value()
        offset_frame = self.offset_spinBox.value()
        # Resistance
        compression_res = self.compr_res_doubleSpinBox.value()
        stretch_res = self.stretch_res_doubleSpinBox.value()
        twist_res = self.twist_res_doubleSpinBox.value()
        bend_res = self.bend_res_doubleSpinBox.value()
        # Weight
        mass = self.mass_doubleSpinBox.value()
        drag = self.drag_doubleSpinBox.value()
        gravity = self.gravity_doubleSpinBox.value()
        # Shape
        start_curve_attract = self.start_curve_attract_doubleSpinBox.value()
        str_crv_attr_base_scale =\
            self.start_curve_attract_base_scale_doubleSpinBox.value()
        str_crv_attr_tip_scale =\
            self.start_curve_attract_tip_scale_doubleSpinBox.value()
        start_ctrl = self.start_ctrl_spinBox.value()

        return {'start_frame': start_frame,
                'end_frame': end_frame,
                'offset_frame': offset_frame,
                'compression_res': compression_res,
                'stretch_res': stretch_res,
                'twist_res': twist_res,
                'bend_res': bend_res,
                'gravity': gravity,
                'mass': mass,
                'drag': drag,
                'start_curve_attract': start_curve_attract,
                'str_crv_attr_base_scale': str_crv_attr_base_scale,
                'str_crv_attr_tip_scale': str_crv_attr_tip_scale,
                'start_ctrl': start_ctrl}

    def update_combobox(self, combobox, items, block='True'):
        """
        Update the given comboBox.

        :param combobox: combobox to update,  ie: self.muscle_comboBox
        :type combobox: Qt object

        :param items: items to add to the given comboBox
        :type items: list

        :param block: specify if we must block the signals when updating the
        comboBox.
        :type block: bool
        """

        # --- Blocking signals from ui
        if block:
            combobox.blockSignals(True)
        else:
            pass

        # --- Init items if empty
        if len(items) == 0:
            items = ['None']

        # --- Get currently selected text
        selected_text = combobox.currentText()

        # --- Clear combobox
        combobox.clear()
        # --- Add items
        combobox.addItems(items)

        # --- If current selected item in new item list, select it
        if selected_text in items:
            self.select_combobox_index_from_text(combobox, selected_text)
        else:
            combobox.setCurrentIndex(0)

        for i, item in enumerate(items):
            combobox.setToolTip(item)

        # --- Unblocking signals from ui
        combobox.blockSignals(False)

    @staticmethod
    def select_combobox_index_from_text(combobox, text):
        """
        Select given text in the given comboBox.

        :param combobox: the comboBox you want to set selection
        :type combobox: Qt object

        :param text: The text you want to select
        :type text: str
        """
        # Get index from the text
        text_index = combobox.findText(text)
        # Select text from index
        combobox.setCurrentIndex(text_index)

    def create_preset_file(self):
        """
        Create a default preset file in user area when none exists.
        """
        # Define where is the default preset file
        preset_file = '%s/presets.json' % folder_path

        if not os.path.exists(preset_file):
            # Read original preset file
            self.presets = FileSystem.load_from_json('%s/presets.json'
                                                     % tool_path)

            self.save_preset()

    def save_preset(self):
        """
        Save the current ui values as a preset under the given name.
        """
        # Get preset name
        preset_name = str(self.preset_name_lineEdit.text())

        # Prevent from overriding default preset
        if preset_name == 'default':
            mc.confirmDialog(title='Warning : overwrite preset',
                             message='You cannot overwrite the default preset',
                             button=['Cancel'],
                             defaultButton='Cancel',
                             dismissString='Cancel')
            print 'Operation cancelled'
            return
        # Warn when overriding existing preset
        elif preset_name in self.presets.keys():
            overwrite = mc.confirmDialog(title='Warning : overwrite preset',
                                         message='You are about to overwrite '
                                                 'the preset named : %s'
                                                 % preset_name,
                                         button=['Continue', 'Cancel'],
                                         defaultButton='Cancel',
                                         dismissString='Cancel')

            if overwrite != 'Continue':
                print 'Operation cancelled'
                return
            else:
                pass
        # Continue in case of new preset
        else:
            pass

        if preset_name != '':
            # Get ui data
            data = self.get_data()

            # Add new preset to preset dict
            preset = {'start_frame': data['start_frame'],
                      'end_frame': data['end_frame'],
                      'offset_frame': data['offset_frame'],
                      'comp_res': data['compression_res'],
                      'stretch_res': data['stretch_res'],
                      'twist_res': data['twist_res'],
                      'bend_res': data['bend_res'],
                      'gravity': data['gravity'],
                      'mass': data['mass'],
                      'drag': data['drag'],
                      'curve_attract': data['start_curve_attract'],
                      'curve_attract_base_scale': data['str_crv_attr_base_scale'],
                      'curve_attract_tip_scale': data['str_crv_attr_tip_scale'],
                      'start_ctrl': data['start_ctrl']}

            self.presets[preset_name] = preset

        # Save preset dict
        FileSystem.save_to_json(self.presets, '%s/presets.json' % folder_path)

        # Update ui comboBoxes with the new preset
        self.update_combobox(self.preset_comboBox, self.presets.keys())
        self.update_combobox(self.delete_preset_comboBox, self.presets.keys())

    def delete_preset(self):
        """
        Delete the selected preset.
        """
        # Get the preset name
        preset_name = str(self.delete_preset_comboBox.currentText())

        # Prevent from deleting default preset
        if preset_name == 'default':
            mc.confirmDialog(title='Warning : delete preset',
                             message='You cannot delete the default preset',
                             button=['Cancel'],
                             defaultButton='Cancel',
                             dismissString='Cancel')
            print 'Operation cancelled'
            return
        # Warn before deleting preset
        elif preset_name in self.presets.keys():
            delete = mc.confirmDialog(title='Warning : delete preset',
                                      message='You are about to delete the '
                                              'preset named : %s'
                                              % preset_name,
                                      button=['Continue', 'Cancel'],
                                      defaultButton='Cancel',
                                      dismissString='Cancel')

            if delete != 'Continue':
                print 'Operation cancelled'
                return
            else:
                pass
        # If preset do not exists, verbose
        else:
            print 'The selected preset no longer exists'
            return

        # Remove selected preset from preset dict
        self.presets.pop(preset_name)

        # Save preset dict
        FileSystem.save_to_json(self.presets, '%s/presets.json' % folder_path)

        # Update ui comboBoxes with the new preset dict
        self.update_combobox(self.preset_comboBox, self.presets.keys())
        self.update_combobox(self.delete_preset_comboBox, self.presets.keys())

    def set_values(self):
        """
        Set the ui values with the selected preset values.
        """
        # Get preset name
        preset = str(self.preset_comboBox.currentText())

        # Set values
        # Frames
        self.start_frame_spinBox.setValue(
            self.presets[preset]['start_frame'])
        self.end_frame_spinBox.setValue(
            self.presets[preset]['end_frame'])
        self.offset_spinBox.setValue(
            self.presets[preset]['offset_frame'])
        # Resistance
        self.compr_res_doubleSpinBox.setValue(
            self.presets[preset]['comp_res'])
        self.stretch_res_doubleSpinBox.setValue(
            self.presets[preset]['stretch_res'])
        self.twist_res_doubleSpinBox.setValue(
            self.presets[preset]['twist_res'])
        self.bend_res_doubleSpinBox.setValue(
            self.presets[preset]['bend_res'])
        # Weight
        self.gravity_doubleSpinBox.setValue(
            self.presets[preset]['gravity'])
        self.mass_doubleSpinBox.setValue(
            self.presets[preset]['mass'])
        self.drag_doubleSpinBox.setValue(
            self.presets[preset]['drag'])
        # Shape
        self.start_curve_attract_doubleSpinBox.setValue(
            self.presets[preset]['curve_attract'])
        self.start_curve_attract_base_scale_doubleSpinBox.setValue(
            self.presets[preset]['curve_attract_base_scale'])
        self.start_curve_attract_tip_scale_doubleSpinBox.setValue(
            self.presets[preset]['curve_attract_tip_scale'])
        # Start ctrl
        self.start_ctrl_spinBox.setValue(
            self.presets[preset]['start_ctrl'])

    def auto_dynamic_to_fk_chain(self):
        """
        Call the bake_dynamic_to_fk_chain from the ui
        """
        # Get ui data
        data = self.get_data()

        # Get chains from current selection
        fk_chains = self.get_fk_chains(data['start_ctrl'])

        # Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            # Call generic function with UI data
            self.bake_dynamic_to_fk_chain(fk_chains,
                                          data['start_frame'],
                                          data['end_frame'],
                                          data['offset_frame'],
                                          data['compression_res'],
                                          data['stretch_res'],
                                          data['twist_res'],
                                          data['bend_res'],
                                          data['gravity'],
                                          data['mass'],
                                          data['drag'],
                                          data['start_curve_attract'],
                                          data['str_crv_attr_base_scale'],
                                          data['str_crv_attr_tip_scale'])
        finally:
            mc.undoInfo(closeChunk=True)

    @staticmethod
    def bake_dynamic_to_fk_chain(fk_chains, start_frame, end_frame,
                                 frame_offset,
                                 compression_res=10.0, stretch_res=10.0,
                                 twist_res=1.0, bend_res=10.0,
                                 gravity=9.8, mass=10.0, drag=0.05,
                                 start_curve_attract=0.0,
                                 str_crv_attr_base_scale=1.0,
                                 str_crv_attr_tip_scale=0.2):
        """
        Initialize and launch the creation and bake of the animation on the
        selected fk chains.

        :param fk_chains: {'fk_chain_1': ['ctrl', 'ctrl', ...],
                           'fk_chain_2': ['ctrl', 'ctrl', ...],
                           ...}
        :type fk_chains: dict

        :param start_frame: start frame
        :type start_frame: int

        :param end_frame: end frame
        :type end_frame: int

        :param frame_offset: number of frame to offset
        :type frame_offset: int

        :param compression_res: compression resistance
        :type compression_res: float

        :param stretch_res: stretch resistance
        :type stretch_res: float

        :param twist_res: twist resistance
        :type twist_res: float

        :param bend_res: bend resistance
        :type bend_res: float

        :param mass: mass
        :type mass: float

        :param drag: drag
        :type drag: float

        :param gravity: gravity
        :type gravity: float

        :param start_curve_attract: start curve attract
        :type start_curve_attract: float

        :param str_crv_attr_base_scale: value of the first point on the
        attraction scale curve(.attractionScale[0].attractionScale_FloatValue)
        :type str_crv_attr_base_scale: float

        :param str_crv_attr_tip_scale: value of the last point on the
        attraction scale curve(.attractionScale[1].attractionScale_FloatValue)
        :type str_crv_attr_tip_scale: float
        """
        crv_setup_d = dict()

        # Create curve setup
        for chain in fk_chains:
            crv_setup_d[chain] = BakeDynamicToFKChain.create_dynamic_setup(
                start_frame, chain, fk_chains[chain], compression_res,
                stretch_res, twist_res, bend_res, gravity, mass, drag,
                start_curve_attract, str_crv_attr_base_scale,
                str_crv_attr_tip_scale)

        BakeDynamicToFKChain.bake_to_ctrls(start_frame, end_frame,
                                           frame_offset, crv_setup_d,
                                           fk_chains)

        BakeDynamicToFKChain.clean_scene(crv_setup_d)

    @staticmethod
    def bake_to_ctrls(start_frame, end_frame, frame_offset,
                      crv_setup_d, fk_chains):
        """
        Bake simulation movement to ctrls.

        :param start_frame: start frame
        :type start_frame: int

        :param end_frame: end frame
        :type end_frame: int

        :param crv_setup_d: hair related nodes by fk chain
        :type crv_setup_d: dict

        :param fk_chains: ctrls list by fk chain
        :type fk_chains: dict

        :param frame_offset: number of frame to offset
        :type frame_offset: int
        """
        # Loop in frames
        for frame in range(start_frame, end_frame + 1):
            mc.currentTime(frame)
            # Loop in fk chains : determine cv number
            for chain in crv_setup_d:
                out_crv_name = crv_setup_d[chain][3]
                out_crv_shape = mc.listRelatives(out_crv_name,
                                                 c=True, s=True)[0]
                out_crv_degree = mc.getAttr('%s.degree' % out_crv_shape)
                out_crv_span = mc.getAttr('%s.spans' % out_crv_shape)
                out_cv_number = out_crv_degree + out_crv_span
                # Loop in cvs : query world position, paste it on ctrl, query
                # local position of ctrl, key it on the corresponding frame
                for cv in range(1, out_cv_number):
                    cv_pos = mc.xform('%s.cv[%s]' % (out_crv_shape, cv),
                                      q=True, t=True, ws=True)

                    # ROTATE CALCULATION AND KEYING
                    # Create tmp transform and aim to it
                    tmp_cv = mc.createNode('transform', n='tmp_frame_%s_cv_%s'
                                                          % (frame, cv))
                    mc.xform(tmp_cv, t=cv_pos, ws=True)
                    if ':r_' in chain or chain.startswith('r_'):
                        tmp_ct = mc.aimConstraint(tmp_cv,
                                                  fk_chains[chain][cv - 1],
                                                  aim=[0.0, -1.0, 0.0],
                                                  mo=False)
                    else:
                        tmp_ct = mc.aimConstraint(tmp_cv,
                                                  fk_chains[chain][cv - 1],
                                                  aim=[0.0, 1.0, 0.0], mo=False)
                    # Get rotate values and clean nodes
                    rotate = mc.xform(fk_chains[chain][cv - 1], q=True,
                                      ro=True, os=True)

                    # Add keyframes
                    if mc.getAttr('%s.rx' % fk_chains[chain][cv - 1], k=True):
                        mc.setKeyframe(fk_chains[chain][cv - 1],
                                       at='rx',
                                       t=frame + frame_offset,
                                       v=rotate[0])
                    if mc.getAttr('%s.ry' % fk_chains[chain][cv - 1], k=True):
                        mc.setKeyframe(fk_chains[chain][cv - 1],
                                       at='ry',
                                       t=frame + frame_offset,
                                       v=rotate[1])
                    if mc.getAttr('%s.rz' % fk_chains[chain][cv - 1], k=True):
                        mc.setKeyframe(fk_chains[chain][cv - 1],
                                       at='rz',
                                       t=frame + frame_offset,
                                       v=rotate[2])

                    mc.delete(tmp_ct, tmp_cv)

    @staticmethod
    def clean_scene(crv_setup_d):
        """
        Delete all hair related nodes.

        :param crv_setup_d: hair related nodes
        :type crv_setup_d: dict
        """
        for chain in crv_setup_d:
            mc.delete(crv_setup_d[chain])

        mc.delete('nucleus1')

    @staticmethod
    def create_dynamic_setup(start_frame, fk_chain, ctrls,
                             compression_res=10.0, stretch_res=10.0,
                             twist_res=1.0, bend_res=10.0,
                             gravity=9.8, mass=10.0, drag=0.05,
                             start_curve_attract=0.0,
                             str_crv_attr_base_scale=1.0,
                             str_crv_attr_tip_scale=0.2):
        """
        Create the curve for the given fk chain, make it dynamic and set the
        attributes.

        :param start_frame: start frame (nucleus)
        :type start_frame: int

        :param fk_chain: name of the fk chain to bake
        :type fk_chain: str

        :param ctrls: list of the ctrls to bake (from the given fk chain)
        :type ctrls: list

        :param compression_res: compression resistance (hair system)
        :type compression_res: float

        :param stretch_res: stretch resistance (hair system)
        :type stretch_res: float


2016-11-15 10:49 GMT-08:00 Martin L'ANTON <lantonmartin@gmail.com>:
https://docs.google.com/spreadsheets/d/1eR2oAXOuflr8CZeGoz3JTrsgNj3KuefbdXJOmNtjEVM/edit#gid=0
        :param twist_res: twist resistance (hair system)
        :type twist_res: float

        :param bend_res: bend resistance (hair system)
        :type bend_res: float

        :param mass: mass (hair system)
        :type mass: float

        :param drag: drag (hair system)
        :type drag: float

        :param gravity: gravity (nucleus)
        :type gravity: float

        :param start_curve_attract: start curve attract (hair system)
        :type start_curve_attract: float

        :param str_crv_attr_base_scale: value of the first point on the
        attraction scale curve(.attractionScale[0].attractionScale_FloatValue)
        (hair system)
        :type str_crv_attr_base_scale: float

        :param str_crv_attr_tip_scale: value of the last point on the
        attraction scale curve(.attractionScale[1].attractionScale_FloatValue)
        (hair system)
        :type str_crv_attr_tip_scale: float

        :return: [follicle, follicle_grp, hair_system, output_crv,
        output_crv_grp, curve]
        :rtype: list
        """
        # Set current frame
        mc.currentTime(start_frame)
        # Create curve
        mc.select(ctrls)
        curve = mju.mCurveOnTranform()
        curve = mc.rename(str(curve), '%s_crv' % fk_chain)
        # Making curve dynamic
        mc.select(curve)
        mm.eval('makeCurvesDynamic 2 {"0", "0", "0", "1", "0"}')
        # Attach curve to setup
        curve_setup = BakeDynamicToFKChain.attach_curve_to_setup(
            fk_chain, curve)

        # Set follicle
        follicle_shape = mc.listRelatives(curve_setup[0], c=True, s=True)[0]
        mc.setAttr('%s.pointLock' % follicle_shape, 1)

        # Set hair system
        mc.setAttr('%s.compressionResistance' % curve_setup[2], compression_res)
        mc.setAttr('%s.stretchResistance' % curve_setup[2], stretch_res)
        mc.setAttr('%s.twistResistance' % curve_setup[2], twist_res)
        mc.setAttr('%s.bendResistance' % curve_setup[2], bend_res)
        mc.setAttr('%s.mass' % curve_setup[2], mass)
        mc.setAttr('%s.drag' % curve_setup[2], drag)
        mc.setAttr('%s.startCurveAttract' % curve_setup[2], start_curve_attract)
        mc.setAttr('%s.attractionScale[0].attractionScale_FloatValue'
                   % curve_setup[2],
                   str_crv_attr_base_scale)
        mc.setAttr('%s.attractionScale[1].attractionScale_FloatValue'
                   % curve_setup[2],
                   str_crv_attr_tip_scale)

        # Set nucleus
        mc.setAttr('nucleus1.startFrame', start_frame)
        mc.setAttr('nucleus1.gravity', gravity)

        curve_setup.append(curve)

        return curve_setup

    @staticmethod
    def attach_curve_to_setup(fk_chain, curve):
        """
        Rename the hair nodes and parent them to the setup corresponding to the
        given fk_chain.

        :param fk_chain: name of the fk chain to attach the curve to
        :type fk_chain: str

        :param curve: name of the curve
        :type curve: str

        :return: [follicle, follicle_grp, hair_system, output_crv,
        output_crv_grp]
        :rtype: list
        """
        output_crv = mc.listRelatives('hairSystem1OutputCurves',
                                      c=True, s=False)
        # Rename
        follicle = mc.rename('follicle1', '%s_follicle' % fk_chain)
        hair_system = mc.rename('hairSystem1', '%s_hairSystem' % fk_chain)
        follicle_grp = mc.rename('hairSystem1Follicles', '%s_grp' % follicle)
        output_crv = mc.rename(output_crv, curve.replace('crv', 'output_crv'))
        output_crv_grp = mc.rename('hairSystem1OutputCurves', '%s_grp'
                                   % output_crv)

        # Hierarchy
        mc.parent(follicle_grp, '%s_seg_01_zero' % fk_chain)
        hair_grp = mc.group([hair_system, output_crv_grp],
                            n='%s_hair' % fk_chain)

        if len(fk_chain.split(':')) > 1:
            mc.parent(hair_grp, '%s:noTransform' % fk_chain.split(':')[0])
        else:
            mc.parent(hair_grp, 'noTransform')

        return [follicle,
                follicle_grp,
                hair_system,
                output_crv,
                output_crv_grp,
                hair_grp]

    @staticmethod
    def get_fk_chains(start_ctrl):
        """
        Get the selected fk_chains and remove double if needed.
        :return: {'fk_chain_1': ['ctrl', 'ctrl', ...],
                  'fk_chain_2': ['ctrl', 'ctrl', ...],
                  ...}
        """
        selection = mc.ls(sl=True)
        fk_chain_dict = dict()

        for obj in selection:
            fk_chain = '_'.join(obj.split('_')[:-3])
            fk_chain_dict[fk_chain] = BakeDynamicToFKChain.get_fk_chain_ctrls(
                fk_chain, start_ctrl)

        return fk_chain_dict

    @staticmethod
    def get_fk_chain_ctrls(fk_chain, start_ctrl):
        """
        Get the controllers of the given fk_chain
        :param fk_chain: '%s_%s' % (side, name) : fk_chain to query ctrls
        :type fk_chain: str

        :param start_ctrl: number of the ctrl to use as start point for the crv
        :type start_ctrl: int

        :return: list of the ctrls below (and including) start_ctrl on the given
        fk chain
        :rtype: list
        """
        fk_ctrls = list()
        i = start_ctrl

        while mc.objExists('%s_seg_%s_ctrl' % (fk_chain, '{0:02d}'.format(i))):
            fk_ctrls.append('%s_seg_%s_ctrl' % (fk_chain, '{0:02d}'.format(i)))
            i += 1

        return fk_ctrls
__author__ = 'm.lanton'
"""Copyright (c) 2015 Martin L'Anton

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, sublicense, and/or distribute copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------DOCUMENTATION---------------------------------------------------------
The following script (BlendShape Manager) is mainly composed of a 5 parts GUI and the related functions.
The 3 center column lists : blendshape nodes of the scene, targets of the selected (in first column) blendshape node,
controllers of the scene (every curve containing the letters 'ctrl' without matching Case)

Buttons :
----------------------------
Refresh : Update the UI

Create blendshape node : Create a new maya blendshape node; select all the targets you need, then select the base.

Add blendshape target : Add a new target to the selected blendshape node; select the blendshape node in the UI and the
targets is your current scene selection

Extract blendshape targets : Create a new version of the targets which are selected in the UI; if targets already exist,
then create duplicates named as 'extract', if not it recreates the targets and reconnects them to the blendshape node
(edit them will edit the actual blendshape).

Delete blendshape node : delete the blendshape node which is selected in the UI.

Remove blendshape target : remove the target which is selected in the UI from the blendshape node.

Create in-between : Create a new in-between shape; select the target you want to add an in-between to in the UI, select
the in-between in the scene, specify a value for the in-between in the corresponding field in the UI.
----------------------------
Connect : Create a setRange and set it to connect the selected attribute to the selected target weight; min and max
values are used to define the range the controller will proceed. If you want the min value of the controller to activate
the max value of the target, use the 'negative' checkbox.

Break connection : Delete all setRanges whom name contains blendshapeNodeName_targetName
then disconnect every attribute connected to the target weight.

Create attr : Create a new float attribute from the name in the corresponding field on the selected, and then connect it
the same way than the Connect button.

Delete attr : will delete the selected (in UI) attribute in addition to the 'Break connection' function.
----------------------------

Unconnected functions :
write_setup_to_dict : write the setup of the selected blendshape node to a dictionary.
ie : BSM = BlendShapeManager()
     setup = BSM.write_setup_to_dict()

create_setup_from_dict : create setup on the specified blendshape node from the specified dictionary.
ie : BSM = BlendShapeManager()
     setup = BSM.write_setup_to_dict()
     BSM.create_setup_from_dict(newBlendshapeNode, setup)
"""

from pprint import pprint

import maya.cmds as mc
import maya.mel as mel
from PySide.QtCore import *
from PySide.QtGui import *

import BSM_ui as BSM_ui

reload(BSM_ui)

class Proc (QDialog, BSM_ui.Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.testList = ['None']
        # ------------------ DATAS ------------------ #
        self.bcs_loaded = self.is_bcs_loaded(verbose=True)  # bcs plugin load state
        self.scene_nomenclature = self.check_scene_nomenclature()
        self.blendshapes_datas = self.list_blend_shape_datas()  # Dictionary storing the current scene blendShape datas
        self.controllers_datas = self.list_controllers_datas()
        self.connections = dict()
        # ------------------ MENUS ------------------ #
        # ------------------------------------------- #
        bs_nodes_list = [node for node in self.blendshapes_datas]
        self.update_combobox(self.bs_node_menu, bs_nodes_list)
        # --- Connect
        self.bs_node_menu.currentIndexChanged.connect(self.update_bs_targets_qlistwidget)
        # ------------------------------------------- #
        self.update_bs_targets_qlistwidget([])
        # ------------------------------------------- #
        controllers_list = [controller for controller in self.controllers_datas]
        controllers_list.sort()
        self.controllers_menu.addItems(controllers_list)
        # --- Connect
        self.controllers_menu.currentIndexChanged.connect(self.update_attributes_menu)
        # ------------------------------------------- #
        self.update_attributes_menu()

        # ----------------- BUTTONS ----------------- #
        self.refresh_button.clicked.connect(self.refresh_ui)
        self.create_bs_button.clicked.connect(self.create_blendshape_node)
        self.add_targets_button.clicked.connect(self.add_blendshape_target)
        self.extract_targets_button.clicked.connect(self.extract_multi_blendshape_target)
        self.delete_bs_button.clicked.connect(self.delete_blendshape_node)
        self.remove_targets_button.clicked.connect(self.remove_blendshape_target)
        self.add_inbetween_button.clicked.connect(self.create_in_between)

        self.connect_button.clicked.connect(self.connect_button_func)
        self.disconnect_button.clicked.connect(self.disconnect_button_func)
        self.create_attr_button.clicked.connect(self.connect_new_attr_button_func)
        self.delete_attr_button.clicked.connect(self.delete_attr_button_func)
        self.export_connections_button.clicked.connect(self.write_setup_to_dict)
        self.import_connections_button.clicked.connect(self.create_setup_from_dict)
        self.reset_all_ctrl.clicked.connect(self.reset_ctrl)

    # -------------------------------------------------DATAS FOR UI-----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # --- Define what to do when print button is hit
    def print_list(self, given_list):
        def callable_print_list():
            pprint(given_list)
        return callable_print_list

    # ------------------------------------------------------------------------------------------------------------------
    def check_scene_nomenclature(self):
        """
        Check if the scene nomenclature is right
        :return: nomenclature state (boolean)
        """
        # --- List all dag objects in the scene with their short name
        scene_obj = mc.ls(dag=True)
        # --- Scene nomenclature error is by default False
        scene_nomenclature_error = False
        # --- Create an empty list for the errors
        errors_list = list()

        # --- For all dag objects in the scene
        for obj in scene_obj:
            # --- If there is more than one object than match this name, it contains a '|', therefore :
            if '|' in obj:
                # --- We get the last part of that object, which is the actual short name
                wrong_name = obj.split('|')[-1]
                # --- For all object in the scene, if it matches the current short name, put it in a list
                wrong_names = [obj for obj in scene_obj if obj.split('|')[-1] == wrong_name]
                # --- Append the error_list with the sentence containing the result
                errors_list.append(' - More than one object match name : %s : \n %s' % (wrong_name, wrong_names))
                # --- Remove all occurrence from the scene_obj list to avoid showing the result more than once
                for occurrence in wrong_names:
                    scene_obj.remove(occurrence)

        # --- If the error_list is not empty, then, create a window showing all the results
        if len(errors_list) > 0:
            # --- scene_nomenclature_error set to True
            scene_nomenclature_error = True
            # --- Delete window if it already exists
            if mc.window('Nomenclature_error', exists=True):
                    mc.deleteUI('Nomenclature_error', window=True)
            # --- Create the window
            mc.window('Nomenclature_error', title='Nomenclature error', sizeable=True)
            # --- Create the layout
            mc.rowColumnLayout('nomenclature_error_layout')
            mc.text(label='Some errors were found in scene nomenclature.'
                          '\n The script may not work perfectly. \n Errors are :', height=25, align='center')
            mc.separator(height=25, visible=False)
            # --- For every error in errors_list, show it
            for obj in errors_list:
                mc.text(label=obj, height=50, align='left')
                # --- Print button
            mc.button('print', label='Print in script editor', height=50, command=self.print_list(errors_list))
            mc.showWindow()
        # --- If there is no error
        else:
            # --- Delete window if it already exists
            if mc.window('Nomenclature_error', exists=True):
                    mc.deleteUI('Nomenclature_error', window=True)

        # --- Return scene_nomenclature state
        return scene_nomenclature_error

    # ------------------------------------------------------------------------------------------------------------------
    def is_bcs_loaded(self, verbose=False):
        """
        Detect if bcs plug-in is loaded
        :param verbose: boolean which indicates if we must print verbose or not.
        :return: bcs plugin state (boolean)
        """
        is_loaded = mc.pluginInfo(['DPK_bcs'], q=True, loaded=True)

        if verbose:
            if is_loaded:
                print 'DPK_bcs is loaded.'
            else:
                print 'DPK_bcs is not loaded.'
        else:
            pass

        return is_loaded

    # ------------------------------------------------------------------------------------------------------------------
    def list_blend_shape_nodes(self):
        """
        List the different blendShape nodes in the scene, whether they are DPK_bcs or usual blendShape nodes.
        :rtype : list
        :return: [list, list]
        """

        blend_shape_nodes_list = mc.ls(et='blendShape')

        if self.bcs_loaded:
            dpk_bcs_nodes_list = mc.ls(et='DPK_bcs')
        else:
            dpk_bcs_nodes_list = list()

        return [blend_shape_nodes_list, dpk_bcs_nodes_list]

    # ------------------------------------------------------------------------------------------------------------------
    def list_blend_shape_datas(self):
        """
        Create a dictionary containing all blendShape nodes and their inputs.
        :return: dict of which each entry contains a dict, itself containing the type (DPK or standard) and the targets
        of the corresponding blendShape node
        """

        # --- List the blendShape nodes
        bs_nodes_list = self.list_blend_shape_nodes()

        # --- Create a dict for the blendShape nodes and their targets
        blendshape_dict = dict()

        # --- Classic blendShape nodes
        for blendShapeNode in bs_nodes_list[0]:
            # --- Create a dict of the targets of the given blendShapeNode
            blendshape_node_dict = dict()
            blendshape_node_dict['type'] = mc.nodeType(blendShapeNode)  # type of the blendShape node (DPK or standard)
            # --- Create a list of the targets
            blendshape_targets_dict = dict()
            # --- List standard blendShape weights
            weights = mc.listAttr(blendShapeNode+'.w', multi=True)  # targets of the node
            # --- For every target, return bilateral False
            for target in weights:
                # --- Create an empty dict for every target
                target_dict = dict()
                # --- If not, just write the weight
                target_dict['bilateral'] = False
                target_dict['weights'] = [target]
                # --- for every target, add its dictionary to the blendshape_targets_list
                blendshape_targets_dict[target] = target_dict

            # --- Write the blendshape_targets_list to the corresponding entry of blendshape_node_dict
            blendshape_node_dict['targets'] = blendshape_targets_dict
            # --- Write every blendshape_node_dict to the corresponding entry of blendshape_dict
            blendshape_dict[blendShapeNode] = blendshape_node_dict

        # --- DPK_bcs nodes
        for blendShapeNode in bs_nodes_list[1]:
            # --- Create a dict of the targets of the given blendShapeNode
            blendshape_node_dict = dict()
            blendshape_node_dict['type'] = mc.nodeType(blendShapeNode)
            # --- Create a list of the targets
            blendshape_targets_dict = dict()
            # --- List DPK_bcs blendShape weights
            weights = mel.eval('DPK_bcs -query -getWeight -name "%s"' % blendShapeNode)
            # --- For every target, check if it is bilateral or not
            for target in weights:
                # --- Create an empty dict for every target
                target_dict = dict()
                # --- Get the weight index of every target
                get_weight_index = mel.eval('DPK_bcs -query -gw -called "%s" "%s" ' % (target, blendShapeNode))
                # --- Check if bilateral
                if mel.eval('DPK_bcs -query -weight %s -getBilateral "%s"' % (get_weight_index, blendShapeNode)):
                    # --- If bilateral, write the bilateral state and bilateral weights
                    target_dict['bilateral'] = True
                    target_dict['weights'] = [target+'R', target+'L']
                else:
                    # --- If not, just write the weight
                    target_dict['bilateral'] = False
                    target_dict['weights'] = [target]
                # --- for every target, add its dictionary to the blendshape_targets_list
                blendshape_targets_dict[target] = target_dict

            # --- Write the blendshape_targets_list to the corresponding entry of blendshape_node_dict
            blendshape_node_dict['targets'] = blendshape_targets_dict
            # --- Write every blendshape_node_dict to the corresponding entry of blendshape_dict
            blendshape_dict[blendShapeNode] = blendshape_node_dict

        return blendshape_dict

    # ------------------------------------------------------------------------------------------------------------------
    def list_controllers(self):
        """
        List all the controllers in the scene.
        :return: list of the controllers in the scene
        """

        transform_list = [transform for transform in mc.ls(et='transform')
                          if mc.listRelatives(transform, c=True, s=True) is not None]

        nurbs_list = [transform for transform in transform_list
                      if mc.nodeType(mc.listRelatives(transform, c=True, s=True)[0]) == 'nurbsCurve'
                      or mc.nodeType(mc.listRelatives(transform, c=True, s=True)[0]) == 'nurbsSurface']

        controllers_list = [transform for transform in nurbs_list
                            if 'ctrl' in transform.lower()
                            and mc.getAttr('%s.visibility' % transform) is True]

        # --- Fill the controller list with 'None' if there is no controller in the scene
        if len(controllers_list) == 0:
            controllers_list = ['None']

        controllers_list.sort()

        return controllers_list

    # ------------------------------------------------------------------------------------------------------------------
    def list_controllers_datas(self):
        """
        List all the extra attributes of the given controller.
        :return: dict of the extra attributes per controller
        """

        controllers = self.list_controllers()

        controllers_dict = dict()

        for controller in controllers:
            if controller != 'None':
                controllers_dict[controller] = mc.listAttr(controller, s=True, k=True, u=True)
            else:
                controllers_dict[controller] = ['None']

        return controllers_dict

    # ------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------UPDATE UI FUNCTIONS--------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def reorder_weights(self):
        """
        Reorder the weights to get no empty slot
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        # --- List the weights
        weights = mel.eval('DPK_bcs -query -getWeight "%s"' % datas[0])
        weights_name = mel.eval('DPK_bcs -query -getWeight -name "%s"' % datas[0])
        for i, name in enumerate(weights_name):
            if name == '':
                weights.pop(i)

        weights_string = str(weights)
        weights_string = weights_string.replace('[', '{')
        weights_string = weights_string.replace(']', '}')

        # --- Reorder the weights using the new list of indices
        mel.eval('DPK_bcs -edit -reorderWeights %s "%s"' % (weights_string, datas[0]))

    # ------------------------------------------------------------------------------------------------------------------
    def create_weights_list(self):
        """
        Create targets list from
        :return: weights (list)
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()

        # --- Create the list of target
        if datas[0] == 'None':
            blend_shape_targets_list = ['None']
        elif datas[0] == '':
            blend_shape_targets_list = ['None']
        else:
            blend_shape_targets_list = list()
            # --- For every target in the blendshapes_datas of the selected blendShape node
            for target in self.blendshapes_datas[datas[0]]['targets']:
                # --- Add the weight_list of the target
                blend_shape_targets_list += self.blendshapes_datas[datas[0]]['targets'][target]['weights']

        return blend_shape_targets_list

    # ------------------------------------------------------------------------------------------------------------------
    def get_target_from_weight(self, weight):
        """
        Get the target from a given weight
        :param: weight: the given weight (string)
        :return: target (string)
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()

        returned_target = 'None'

        for target in self.blendshapes_datas[datas[0]]['targets']:
            if weight in self.blendshapes_datas[datas[0]]['targets'][target]['weights']:
                returned_target = target

        return returned_target

# ------------------------------------------------------------------------------------------------------------------
    def update_combobox(self, combobox, items):
        """
        Update the given combobox
        :param combobox: combobox to update,  ie: self.bs_node_menu
        :param items: list of items to add to the given combobox
        """

        # --- Blocking signals from ui
        combobox.blockSignals(True)

        # --- Init items if empty
        if items == []:
            items = ['None']

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

        # --- Unblocking signals from ui
        combobox.blockSignals(False)
        
    # ------------------------------------------------------------------------------------------------------------------
    def update_attributes_menu(self):
        """
        Update the attributes menu
        """
        # --- Get the controller which is selected in the UI
        controller = self.get_ui_datas()[2]

        if controller == '':
            controller = "None"

        self.update_combobox(self.attributes_menu, self.controllers_datas[controller])

    # ------------------------------------------------------------------------------------------------------------------
    def get_selected_targets(self):
        """
        Get currently selected bs_targets
        :return:
        """
        selected_bs_targets_items = self.bs_targets_list.selectedItems()
        selected_bs_targets = list()
        for item in selected_bs_targets_items:
            selected_bs_targets.append(item.text())

        return selected_bs_targets
    
    # ------------------------------------------------------------------------------------------------------------------
    def update_bs_targets_qlistwidget(self, selected_bs_targets):
        """
        Update the targets qlistwidget
        """
        # --- If called by bs_node_menu combobox, type is int, then create selection list
        if type(selected_bs_targets) is not list:
            selected_bs_targets = self.get_selected_targets()

        # --- Create the list of target
        bs_targets = self.create_weights_list()

        self.bs_targets_list.clear()
        self.bs_targets_list.addItems(bs_targets)
        # --- If currently selected text in new item list, select it
        for text in selected_bs_targets:
            if text in bs_targets:
                items = self.bs_targets_list.findItems(text, Qt.MatchExactly)
                for item in items:
                    idx = self.bs_targets_list.indexFromItem(item)
                    #index = self.bs_targets_list.row(item)
                    self.bs_targets_list.item(idx.row()).setSelected(True)
    
    # ------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------GET DATAS FOR FUNCTIONS-----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def get_ui_datas(self):
        """
        Gets all the datas from the ui.
        :return: list [string, string, string, string, float, float, string]
        """

        blendshape_node = self.bs_node_menu.currentText()
        blendshape_target = self.get_selected_targets()
        controller = self.controllers_menu.currentText()
        attribute = self.attributes_menu.currentText()
        attribute_min = self.min_value.value()
        attribute_max = self.max_value.value()
        new_attribute = self.new_attr_name.text()


        return [blendshape_node, blendshape_target, controller, attribute, attribute_min, attribute_max, new_attribute]

    # ------------------------------------------------------------------------------------------------------------------
    def get_target_index(self, target):
        """
        Get the index of given blendShape target
        :param target: the target which we want the index
        :return: int(index)
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        # --- Determine index
        target_weight_index = [i+1 for i, obj in enumerate(mc.aliasAttr(datas[0], query=True)) if obj == target][0]
        index = int(mc.aliasAttr(datas[0], query=True)[target_weight_index].split('[')[1].split(']')[0])

        return index

    # ------------------------------------------------------------------------------------------------------------------
    def get_blendshape_base(self):
        """
        Get blendShape base
        :rtype : string
        :return: str(base)
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        # --- Get base
        history = mc.listHistory(datas[0], future=True, leaf=True)
        shape = mc.ls(history, type=('mesh', 'nurbsSurface', 'nurbsCurve'))
        base = mc.listRelatives(shape, fullPath=True, parent=True, type='transform')[0]

        return base
    
    # ------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------BUTTONS FUNCTIONS----------------------------------------------------
    # -------------------------------------------BLENDSHAPES BUTTONS FUNCTIONS------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def refresh_ui(self):
        """
        Update the UI
        """
        # --- Is BCS loaded, in order to update scene datas
        self.bcs_loaded = self.is_bcs_loaded()

        # --- Update dictionaries storing the current scene blendShape datas
        self.blendshapes_datas = self.list_blend_shape_datas()
        self.controllers_datas = self.list_controllers_datas()

        # --- Get currently selected targets
        selected_bs_targets = self.get_selected_targets()

        # --- Refresh BlendShape nodes comboBox
        bs_nodes_list = [node for node in self.blendshapes_datas]
        self.update_combobox(self.bs_node_menu, bs_nodes_list)

        # --- Refresh blendShape targets qlistwidget
        self.update_bs_targets_qlistwidget(selected_bs_targets)

        # --- Refresh controllers comboBox
        controllers_list = [controller for controller in self.controllers_datas]
        controllers_list.sort()
        self.update_combobox(self.controllers_menu, controllers_list)

        # --- Refresh attribute optionMenu
        self.update_attributes_menu()

    # ------------------------------------------------------------------------------------------------------------------
    def create_blendshape_node(self):
        """
        Creates a new blendShape node, last selected geometry is the base, the other ones are the targets.
        """

        # --- Get the selection
        selection = mc.ls(sl=True, transforms=True)
        # --- Get the base from selection
        base = selection[-1]

        # --- Define an increment number
        i = 0
        # --- Increment it if a blendshape_node already exists with that name
        while mc.objExists(base+'_blendShape_node_'+str(i)):
            i += 1

        # --- Define the name in function of the increment
        blendshape_node_name = base+'_blendShape_node_'+str(i)

        # --- Create the new blendshape node
        mc.blendShape(selection, frontOfChain=True, name=blendshape_node_name)

        # --- Refresh the ui to get the node in the list
        self.refresh_ui()

    # ------------------------------------------------------------------------------------------------------------------
    def add_blendshape_target(self):
        """
        Add blendShape target(s) to the specified blendShape node (see ui).
        """

        # --- Get datas and selection
        datas = self.get_ui_datas()
        selection = mc.ls(sl=True, transforms=True)
        # --- Get base
        base = self.get_blendshape_base()

        # --- Define what to do if this a DPK_bcs node or a simple blendshape node
        if self.blendshapes_datas[datas[0]]['type'] == 'DPK_bcs':
            for target in selection:
                weight_index = mel.eval('DPK_bcs -e -createWeight -name "%s" "%s"' % (target, datas[0]))
                index = mel.eval('DPK_bcs -e -createWPos -weight %s "%s"' % (weight_index, datas[0]))
                mel.eval('DPK_bcs -e -createDataPoint -name "%s" -dataPointPosition %s -go "%s" "%s"'
                         % (target, index, target, datas[0]))
        else:
            # --- Define new index ------------------------------
            # --- Get the weight and their indices
            target_per_index = mc.aliasAttr(datas[0], query=True)
            # --- Create empty weight list
            weight_list = list()
            # --- Create empty indices list
            indices_list = list()
            # --- List the weights
            for i in range(0, len(target_per_index)):
                if i % 2 != 0:
                    weight_list.append(target_per_index[i])
            # --- split all the weights to get the index
            for index in weight_list:
                index = int(index.split('[')[1].split(']')[0])
                indices_list.append(index)
            # --- Sort the indices by numerical order, so the last one of the list is actually the higher index
            indices_list.sort()
            # --- Increment 1 to create the new index
            last_index = indices_list[-1]
            new_index = last_index+1

            # --- Add all the targets to the blendShape node. Increment index by 1 for every target it adds
            for target in selection:
                mc.blendShape(datas[0], e=True, target=(base, new_index, target, 1.0))
                new_index += 1

        # --- refresh ui
        self.refresh_ui()

    # ------------------------------------------------------------------------------------------------------------------
    def extract_blendshape_target(self, given_weight, delete=False):
        """
        Recreate the specified target and reconnect it to the blendShape node, delete it, and then reconnect it properly
        if delete flag is True
        :param given_weight : string (the target to extract or delete)
        :param delete : boolean (whether target must be extracted (False) or deleted (True)
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        # --- Get base
        base = self.get_blendshape_base()
        # --- Get the weights
        weights = self.create_weights_list()
        # --- Define what is my target
        target = self.get_target_from_weight(given_weight)

        # --- Create an empty dict for the connections
        connection_dict = dict()

        # --- Check that selection is not empty, if it is, print and pass
        if given_weight is 'None':
            print 'Nothing is selected'
            extract = 'None'
        else:
            # --- List the connections, add it to the dictionary, disconnect it, set all the weights to O
            for weight in weights:
                # --- If it is a DPK_bcs node, define the weight attribute name
                if self.blendshapes_datas[datas[0]]['type'] == 'DPK_bcs':
                    weight = "weight[%s]" % self.get_target_index(weight)
                # --- Then, list the connections and store them to a dict
                if mc.listConnections('%s.%s' % (datas[0], weight), plugs=True) is not None:
                    connection = mc.listConnections('%s.%s' % (datas[0], weight), plugs=True)[0]
                    connection_dict[weight] = connection
                    mc.disconnectAttr(connection, '%s.%s' % (datas[0], weight))
                mc.setAttr('%s.%s' % (datas[0], weight), 0)

            # --- Define what to do if it is a classic blendShape node
            if self.blendshapes_datas[datas[0]]['type'] != 'DPK_bcs':
                # --- Set the target weight to 1
                mc.setAttr('%s.%s' % (datas[0], target), 1)
                # --- Extract the target by duplicating the base
                extract = mc.duplicate(base, name=target+'_extract')[0]
                self.unlock_attributes(extract)

                # --- Reconnect target if it doesn't exist
                if mc.objExists(target) is False:
                    # --- Determine index
                    index = self.get_target_index(target)
                    # --- Rename extract as target
                    extract = mc.rename(extract, target)
                    # --- Reconnect it at the same index
                    mc.blendShape(datas[0], edit=True, target=(base, index, extract, 1.0))
                    # --- Delete the target index (since I can't find a way to rename it)
                    mc.blendShape(datas[0], edit=True, remove=True, target=(base, index, extract, 1.0))
                    # --- Delete it or reconnect it at the same index (to get the right name this time)
                    if delete:
                        mc.delete(extract)
                    else:
                        mc.blendShape(datas[0], edit=True, target=(base, index, extract, 1.0))
                # --- Reconnect all the connections
                self.create_setup_from_dict(datas[0], connection_dict)

            # --- Define what to do if it is a DPK_bcs node
            else:
                if mc.objExists(target):
                    # --- If target is bilateral, set both weights to 1
                    if self.blendshapes_datas[datas[0]]['targets'][target]['bilateral']:
                        mc.setAttr('%s.%s'
                                   % (datas[0], self.blendshapes_datas[datas[0]]['targets'][target]['weights'][0]), 1)
                        mc.setAttr('%s.%s'
                                   % (datas[0], self.blendshapes_datas[datas[0]]['targets'][target]['weights'][1]), 1)
                    # --- If not, set only the target to 1 (since there is only target weight)
                    else:
                        mc.setAttr('%s.%s' % (datas[0], target), 1)
                    # --- Extract the target by duplicating the base
                    extract = mc.duplicate(base, name=target+'_extract')[0]
                    self.unlock_attributes(extract)
                else:
                    # --- Get the index of the dataPoint
                    get_datapoint_index = mel.eval('DPK_bcs -query -getDataPoint -called "%s" "%s"'
                                                   % (target, datas[0]))
                    # --- Extract the dataPoint
                    extract = mel.eval('DPK_bcs -edit -dataPoint %s -geometryType "edit" -geometryMode true "%s"'
                                       % (get_datapoint_index, datas[0]))
                # --- Reconnect all the connections
                    self.create_setup_from_dict(datas[0], connection_dict)
                # --- If delete flag is True
                if delete:
                    # --- Reconnect all the connections
                    self.create_setup_from_dict(datas[0], connection_dict)
                    # --- Get the index of the given weight
                    get_weight_index = mel.eval('DPK_bcs -query -gw -called "%s" "%s" ' % (target, datas[0]))
                    # --- Remove the weight from the DPK_bcs node
                    mel.eval('DPK_bcs -edit -delete -weight %s -f "%s"' % (get_weight_index, datas[0]))
                    # --- Delete the extract
                    mc.delete(extract)

            # --- Reorder the dpk_bcs weights
            if self.blendshapes_datas[datas[0]]['type'] == 'DPK_bcs':
                self.reorder_weights()

            # --- set the attribute back to 0
            try:
                mc.setAttr('%s.%s' % (datas[0], target), 0)
            except:
                pass

        return extract

    # ------------------------------------------------------------------------------------------------------------------
    def extract_multi_blendshape_target(self):
        """
        Recreate the specified target(s), reconnect them to the blendShape node, and move them
        """

        # --- Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            # --- Get the datas from the ui
            datas = self.get_ui_datas()
            base = self.get_blendshape_base()

            # --- List existing extracts
            extracts = [mesh for mesh in mc.ls(transforms=True) if '_extract' in mesh]

            # --- Get the bounding box
            bbox = mc.exactWorldBoundingBox(base, ignoreInvisible=True)
            # --- Calculate extract move
            bbox_size = [0, 0]
            bbox_size[0] = bbox[3] - bbox[0]
            bbox_size[1] = bbox[5] - bbox[2]
            # --- Calculate height
            bbox_height = bbox[4] - bbox[1]
            # --- Sort the length and height to get the higher one at index [1]
            bbox_size.sort()

            # --- Increment x for every existing extract
            x = bbox_size[1]*1.5

            for existing_extract in extracts:
                x += (bbox_size[1]*1.5)

            # --- Extract target for every selected target
            for target in datas[1]:
                extract = self.extract_blendshape_target(target, delete=False)
                # --- Set the translateY value
                if 'None' in extract:
                    pass
                elif not 'extract' in extract:
                    y = 0
                    # --- Move the extracted geometry
                    mc.xform(extract, translation=[x, y, 0])
                else:
                    y = bbox_height*1.2
                    # --- Move the extracted geometry
                    mc.xform(extract, translation=[x, y, 0])

                # --- Increment i
                x += bbox_size[1]*1.5
        finally:
            mc.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------------------------------------------------------
    def delete_blendshape_node(self):
        """
        Delete specified blendShape node.
        """

        datas = self.get_ui_datas()

        mc.delete(datas[0])

        self.refresh_ui()

    # ------------------------------------------------------------------------------------------------------------------
    def remove_blendshape_target(self):
        """
        Add blendShape target(s) to the specified blendShape node (see ui).
        """

        # --- Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            # --- Get datas from ui
            datas = self.get_ui_datas()

            for target in datas[1]:
                if mc.objExists(target) is False or self.blendshapes_datas[datas[0]]['type'] == 'DPK_bcs':
                    self.extract_blendshape_target(target, delete=True)
                else:
                    # --- Get index
                    index = self.get_target_index(target)
                    # --- Get base
                    base = self.get_blendshape_base()
                    # --- Remove it
                    mc.blendShape(datas[0], edit=True, remove=True, target=(base, index, target, 1.0))

                self.refresh_ui()
        finally:
            mc.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------------------------------------------------------
    def create_in_between(self):
        """
        Create a new in between
        """

        # --- Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            # --- Get datas from ui
            datas = self.get_ui_datas()
            # --- Get in between value, base, index, and new_target
            in_between_value = self.inbetween_value.value()
            base = self.get_blendshape_base()
            index = self.get_target_index(datas[1][0])
            new_target = mc.ls(sl=True, transforms=True)[0]
            weight = self.get_target_from_weight(datas[1][0])

            # --- Create the new in between
            if self.blendshapes_datas[datas[0]]['type'] == 'DPK_bcs':
                # --- Get the index of the selected weight
                get_weight_index = mel.eval('DPK_bcs -query -gw -called "%s" "%s" ' % (weight, datas[0]))
                # --- Get the index of the weight pos
                get_wp_index = mel.eval('DPK_bcs -query -gwp -w %s "%s" ' % (get_weight_index, datas[0]))
                # --- Create the new weightPos
                index = mel.eval('DPK_bcs -e -wPosGrp %s -createWPos -wPosPosition %s "%s"'
                                 % (get_wp_index[0], in_between_value, datas[0]))
                # --- Create a new dataPoint at the created weight using new_target
                mel.eval('DPK_bcs -e -createDataPoint -name "%s" -dataPointPosition %s -go "%s" "%s"'
                         % (new_target, index, new_target, datas[0]))
            else:
                mc.blendShape(datas[0], e=True, inBetween=True, target=(base, index, new_target, in_between_value))
        finally:
            mc.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------CONTROLLERS BUTTONS FUNCTIONS------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def connect_button_func(self):
        """
        Connect selected attribute to selected blendShape target
        """
        self.connect_func(False)

    # ------------------------------------------------------------------------------------------------------------------
    def connect_new_attr_button_func(self):
        """
        Create the attribute before connecting it.
        """
        self.connect_func(True)

    # ------------------------------------------------------------------------------------------------------------------
    def connect_func(self, new_attr=False):
        """
        Connect selected attribute to selected blendShape target. If new_attr is true, then create the attribute before
        connecting it.
        :param new_attr: boolean
        """

        # --- Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            # --- Get datas from ui
            datas = self.get_ui_datas()
            check = 'continue'

            # --- Get checkbox state
            negative = self.negative.isChecked()
            # --- Define what to do if negative
            if negative:
                extrem_x = 'minX'
            else:
                extrem_x = 'maxX'

            # --- Create new attribute if needed
            if new_attr:
                # --- Check if an attribute with the same name already exists on the controller
                if mc.objExists('%s.%s' % (datas[2], datas[6])):
                    check = 'stop'
                    print ('An attribute with the same name already exists on that controller. Operation interrupted')
                # --- If not, create a new attribute
                else:
                    if negative:
                        mc.addAttr(datas[2], longName=datas[6], attributeType='float',
                                   hidden=False, keyable=True, minValue=datas[5], maxValue=datas[4])
                    else:
                        mc.addAttr(datas[2], longName=datas[6], attributeType='float',
                                   hidden=False, keyable=True, minValue=datas[4], maxValue=datas[5])
                    # --- Changing attribute with new attribute
                    datas[3] = datas[6]
                    self.refresh_ui()
                    check = 'continue'
                    print 'ok'

            # --- If the attribute fills the requirements
            if check == 'continue':
                # --- Then connect all the selected targets to the attribute
                for target in datas[1]:
                    s_range = mc.createNode('setRange', n='SR_%s_%s_to_%s_%s' % (datas[2], datas[3], datas[0], target))
                    mc.connectAttr('%s.%s' % (datas[2], datas[3]), '%s.%s' % (s_range, 'valueX'), force=True)
                    mc.setAttr('%s.%s' % (s_range, 'oldMinX'), datas[4])
                    mc.setAttr('%s.%s' % (s_range, 'oldMaxX'), datas[5])
                    mc.setAttr('%s.%s' % (s_range, extrem_x), 1)
                    mc.connectAttr('%s.%s' % (s_range, 'outValueX'), '%s.%s' % (datas[0], target), force=True)
        finally:
            mc.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect_button_func(self):
        """
        Disconnect everything from selected blendShape target and delete the setRange if it exists.
        """

        self.disconnect_func()

    # ------------------------------------------------------------------------------------------------------------------
    def delete_attr_button_func(self):
        """
        Disconnect everything from selected blendShape target and delete the setRange if it exists.
        """

        # --- Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            # --- Get datas from ui
            datas = self.get_ui_datas()
            self.disconnect_func()
            mc.deleteAttr('%s.%s' % (datas[2], datas[3]))
        finally:
            mc.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect_func(self):
        """
        Disconnect everything from selected blendShape target, delete the setRange if it exists, and if delete_attr is
        True, then delete the named attribute.
        """

        # --- Open history chunk
        mc.undoInfo(openChunk=True)
        try:
            datas = self.get_ui_datas()
            # --- List all setRange in the scene
            all_set_range_nodes = mc.ls(exactType='setRange')

            for target in datas[1]:
                # --- Get defined set range if it exists, and delete it
                set_range = [node for node in all_set_range_nodes
                             if node.split('_to_')[-1] == '%s_%s' % (datas[0], target)]
                for obj in set_range:
                    mc.delete(obj)

                # --- List the connections
                connections = mc.listConnections('%s.%s' % (datas[0], target), plugs=True)

                # --- Try to disconnect them
                try:
                    if len(connections) > 0:
                        for connection in connections:
                            mc.disconnectAttr(connection, '%s.%s' % (datas[0], target))
                except:
                    pass

                mc.setAttr('%s.%s' % (datas[0], target), 0)

            self.refresh_ui()
        finally:
            mc.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------------------------------------------------------
    def write_setup_to_dict(self):
        """
        Save the current blendShape node setup to dict. TO CORRECT !!!
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        # --- Get the weights
        weights = self.create_weights_list()

        # --- Create an empty dict for the connections
        connection_dict = dict()

        for weight in weights:
            # --- If it is a DPK_bcs node, define the weight attribute name
            if self.blendshapes_datas[datas[0]]['type'] == 'DPK_bcs':
                weight = "weight[%s]" % self.get_target_index(weight)
            # --- Then, list the connections and store them to a dict
            if mc.listConnections('%s.%s' % (datas[0], weight), plugs=True) is not None:
                connection = mc.listConnections('%s.%s' % (datas[0], weight), plugs=True)[0]
                connection_dict[weight] = connection

        self.connections = connection_dict

    # ------------------------------------------------------------------------------------------------------------------
    def create_setup_from_dict(self, blendshape_node, connection_dict):
        """
        Create a setup from connections stored into the given dictionary. TO CORRECT !!!
        :param connection_dict: dictionary of all connections to do to the given blendshape node
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        if type(blendshape_node) is not str:
            blendshape_node = datas[0]
            connection_dict = self.connections

        # --- Reconnect all the connections
        for weight in connection_dict:
            mc.connectAttr(connection_dict[weight], '%s.%s' % (blendshape_node, weight))

    # ------------------------------------------------------------------------------------------------------------------
    def reset_ctrl(self):
        """
        Reset all ctrl attributes to 0, scale to 1.
        """

        for controller in self.controllers_datas:
            for attribute in self.controllers_datas[controller]:
                try :
                    if 'scale' in attribute or 'visibility' in attribute:
                        mc.setAttr('%s.%s' % (controller, attribute), 1)
                    else:
                        mc.setAttr('%s.%s' % (controller, attribute), 0)
                except:
                    pass

    # ------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------OTHER FUNCTIONS-------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def unlock_attributes(self, object):
        mc.setAttr(object + ".tx", lock = False)
        mc.setAttr(object + ".ty", lock = False)
        mc.setAttr(object + ".tz", lock = False)
        mc.setAttr(object + ".rx", lock = False)
        mc.setAttr(object + ".ry", lock = False)
        mc.setAttr(object + ".rz", lock = False)
        mc.setAttr(object + ".sx", lock = False)
        mc.setAttr(object + ".sy", lock = False)
        mc.setAttr(object + ".sz", lock = False)
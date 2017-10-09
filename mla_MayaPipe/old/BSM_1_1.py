__author__ = 'Martin L\'Anton'
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

import maya.cmds as mc
import maya.mel as mel
from pprint import pprint


class BlendShapeManager():
    def __init__(self):
        """
        init class
        """

        self.widgets = {}  # Dictionary which stores the tool's UI
        self.bcs_loaded = self.is_bcs_loaded(verbose=True)  # bcs plugin load state
        self.scene_nomenclature = self.check_scene_nomenclature()
        self.blendshapes_datas = self.list_blend_shape_datas()  # Dictionary storing the current scene blendShape datas
        self.controllers_datas = self.list_controllers_datas()

    # -------------------------------------------------DATAS FOR UI-----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # --- Define what to do when print button is hit
    def print_list(self, given_list):
        def callable_print_list(*args):
            pprint(given_list)
        return callable_print_list
    # ------------------------------------------------------------------------------------------------------------------
    def check_scene_nomenclature(self, *args):
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
            if '|' in obj :
                # --- We get the last part of that object, which is the actual short name
                wrong_name = obj.split('|')[-1]
                # --- For all object in the scene, if it matches the current short name, put it in a list
                wrong_names = [obj for obj in scene_obj if obj.split('|')[-1] == wrong_name]
                # --- Append the error_list with the sentence containing the result
                errors_list.append(' - More than one object match name : %s : \n %s' % (wrong_name, wrong_names))
                # --- Remove all occurence from the scene_obj list to avoid showing the result more than once
                for occurence in wrong_names :
                    scene_obj.remove(occurence)

        # --- If the error_list is not empty, then, create a window showing all the results
        if len(errors_list) > 0:
            # --- scene_nomenclature_error set to True
            scene_nomenclature_error = True
            # --- Delete window if it already exists
            if mc.window('Nomenclature_error', exists=True):
                    mc.deleteUI('Nomenclature_error', window=True)
            #--- Create the window
            mc.window('Nomenclature_error', title='Nomenclature error', sizeable=True)
            # --- Create the layout
            mc.rowColumnLayout('nomenclature_error_layout')
            mc.text(label='Some errors were found in scene nomenclature. \n The script may not work perfectly. \n Errors are :', height=25, align='center')
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
    def is_bcs_loaded(self, verbose=False, *args):
        """
        Detect if bcs plug-in is loaded
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
    def list_blend_shape_nodes(self, *args):
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
    def list_blend_shape_datas(self, *args):
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
    def list_controllers(self, *args):
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
    def list_controllers_datas(self,  *args):
        """
        List all the extra attributes of the given controller.
        :return: dict of the extra attributes per controller
        """

        controllers = self.list_controllers()

        controllers_dict = dict()

        for controller in controllers:
            if controller != 'None':
                controllers_dict[controller] = mc.listAttr(controller, s=True, k=True)
            else:
                controllers_dict[controller] = ['None']

        return controllers_dict
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------MANAGER------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def ui(self):
        """
        Create the UI
        """

        if mc.window('BlendShapeManager_Window', exists=True):
            mc.deleteUI('BlendShapeManager_Window', window=True)

        # --- Create window
        self.widgets['window'] = mc.window('BlendShapeManager_Window', title='BlendShape Manager 2014 1.1', sizeable=False)
        # --- Create main layout
        self.widgets['main_column_layout'] = mc.rowLayout('main_column_layout',
                                                          numberOfColumns=5,
                                                          parent=self.widgets['window'])

        # --------------------------------------------------------------------------------------------------------------
        # --- Create the left button panel (blendshapes utilities) = column 1
        self.widgets['left_buttons_column_label'] = mc.frameLayout('left_buttons_column_label',
                                                                   label='Blendshapes utilities',
                                                                   width=200,
                                                                   height=342,
                                                                   borderStyle='etchedIn',
                                                                   parent=self.widgets['main_column_layout'])
        self.widgets['left_buttons_column'] = mc.columnLayout('left_buttons_column',
                                                              parent=self.widgets['left_buttons_column_label'])
        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        #  --- Attributes optionMenu
        self.widgets['bs_nodes_part'] = mc.columnLayout('bs_nodes_part',
                                                        width=200,
                                                        height=36,
                                                        parent=self.widgets['left_buttons_column'])
        self.widgets['bs_nodes_optionmenu'] = mc.optionMenu('bs_nodes_optionmenu',
                                                            label='Blendshape nodes',
                                                            width=194,
                                                            height=35,
                                                            parent=self.widgets['bs_nodes_part'])
        # --- Create a 'None' entry in the attribute optionMenu
        mc.menuItem(label='None', parent=self.widgets['bs_nodes_optionmenu'])
        # --------------------------------------------------------------------------------------------------------------
        # --- Create the buttons
        self.widgets['refresh_button'] = mc.button('refresh_button',
                                                   label='Refresh',
                                                   width=195,
                                                   height=35,
                                                   recomputeSize=False,
                                                   parent=self.widgets['left_buttons_column'],
                                                   command=self.refresh_ui)
        self.widgets['create_blendshape'] = mc.button('create_blendshape',
                                                      label='Create blendshape',
                                                      width=195,
                                                      height=35, recomputeSize=False,
                                                      parent=self.widgets['left_buttons_column'],
                                                      command=self.create_blendshape_node)
        self.widgets['add_target'] = mc.button('add_target',
                                               label='Add target(s)',
                                               width=195,
                                               height=35,
                                               recomputeSize=False,
                                               parent=self.widgets['left_buttons_column'],
                                               command=self.add_blendshape_target)
        self.widgets['extract_targets'] = mc.button('extract_targets',
                                                    label='Extract targets',
                                                    width=195,
                                                    height=35,
                                                    recomputeSize=False,
                                                    parent=self.widgets['left_buttons_column'],
                                                    command=self.extract_multi_blendshape_target)
        self.widgets['delete_blendshape_node'] = mc.button('delete_blendshape_node',
                                                           label='Delete blendshape node(s)',
                                                           width=195,
                                                           height=35,
                                                           recomputeSize=False,
                                                           parent=self.widgets['left_buttons_column'],
                                                           command=self.delete_blendshape_node)
        self.widgets['remove_target'] = mc.button('remove_target',
                                                  label='Remove target',
                                                  width=195,
                                                  height=35,
                                                  recomputeSize=False,
                                                  parent=self.widgets['left_buttons_column'],
                                                  command=self.remove_blendshape_target)
        # --------------------------------------------------------------------------------------------------------------
        # --- In between floatField and button
        self.widgets['in_between_option'] = mc.rowColumnLayout('in_between_option',
                                                               numberOfColumns=2,
                                                               parent=self.widgets['left_buttons_column'])
        self.widgets['in_between_label'] = mc.text('in_between_label',
                                                   label='In-between value',
                                                   width=95,
                                                   height=35,
                                                   parent=self.widgets['in_between_option'])
        self.widgets['in_between_floatfield'] = mc.floatField('in_between_floatfield',
                                                              width=100,
                                                              height=35,
                                                              parent=self.widgets['in_between_option'],
                                                              value=0.5)
        self.widgets['in_between'] = mc.button('in_between',
                                               label='In-between',
                                               width=195,
                                               height=35,
                                               recomputeSize=False,
                                               parent=self.widgets['left_buttons_column'],
                                               command=self.create_in_between)

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --- Create the blendshape nodes scrollList = column 2
        self.widgets['bs_nodes_scrollList_label'] = mc.frameLayout('bs_nodes_scrollList_label',
                                                                   label='Blendshape nodes',
                                                                   width=200,
                                                                   borderStyle='etchedIn',
                                                                   parent=self.widgets['main_column_layout'])
        self.widgets['bs_nodes_scrollList'] = mc.textScrollList('bs_nodes_scrollList',
                                                                allowMultiSelection=False,
                                                                height=320,
                                                                parent=self.widgets['bs_nodes_scrollList_label'])

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --- Create the blendshape targets scrollList = column 3
        self.widgets['bs_targets_scrollList_label'] = mc.frameLayout('bs_targets_scrollList_label',
                                                                     label='Blendshape targets',
                                                                     width=200,
                                                                     borderStyle='etchedIn',
                                                                     parent=self.widgets['main_column_layout'])
        self.widgets['bs_targets_scrollList'] = mc.textScrollList('bs_targets_scrollList',
                                                                  allowMultiSelection=True,
                                                                  height=320,
                                                                  parent=self.widgets['bs_targets_scrollList_label'])

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --- Create the controllers scrollList = column 4
        self.widgets['controllers_scrollList_label'] = mc.frameLayout('controllers_scrollList_label',
                                                                      label='Controllers',
                                                                      width=200,
                                                                      borderStyle='etchedIn',
                                                                      parent=self.widgets['main_column_layout'])
        self.widgets['controllers_scrollList'] = mc.textScrollList('controllers_scrollList',
                                                                   allowMultiSelection=False,
                                                                   height=320,
                                                                   parent=self.widgets['controllers_scrollList_label'],
                                                                   selectCommand=self.update_attributes_menu)

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # --- Create the left button panel (connexion utilities) = column 5
        self.widgets['right_buttons_column_label'] = mc.frameLayout('right_buttons_column_label',
                                                                    label='Controllers utilities',
                                                                    width=200,
                                                                    borderStyle='etchedIn',
                                                                    parent=self.widgets['main_column_layout'])
        self.widgets['right_buttons_column'] = mc.columnLayout('right_buttons_column',
                                                               height=320,
                                                               parent=self.widgets['right_buttons_column_label'])
        # --------------------------------------------------------------------------------------------------------------
        # --- Attributes optionMenu
        self.widgets['attributes_part'] = mc.columnLayout('right_buttons_column',
                                                          width=194,
                                                          height=35,
                                                          parent=self.widgets['right_buttons_column'])
        self.widgets['attribute'] = mc.optionMenu('attribute',
                                                  label='Attribute',
                                                  width=194,
                                                  height=35,
                                                  parent=self.widgets['attributes_part'])
        # --- Create a 'None' entry in the attribute optionMenu
        mc.menuItem(label='None', parent=self.widgets['attribute'])

        # --------------------------------------------------------------------------------------------------------------
        # --- RowColumnLayout
        self.widgets['connect_options'] = mc.rowColumnLayout('connect_options',
                                                             numberOfColumns=2,
                                                             width=194,
                                                             parent=self.widgets['right_buttons_column'])
        # --------------------------------------------------------------------------------------------------------------
        # --- Min and Max label
        self.widgets['min_label'] = mc.text('min_label',
                                            label='Min',
                                            width=97,
                                            height=35,
                                            parent=self.widgets['connect_options'])
        self.widgets['max_label'] = mc.text('max_label',
                                            label='Max',
                                            width=97,
                                            height=35,
                                            parent=self.widgets['connect_options'])
        # --------------------------------------------------------------------------------------------------------------
        # --- Min and Max floatField
        self.widgets['min_field'] = mc.floatField('min_field',
                                                  width=97,
                                                  height=35,
                                                  parent=self.widgets['connect_options'])
        self.widgets['max_field'] = mc.floatField('max_field',
                                                  width=97,
                                                  height=35,
                                                  parent=self.widgets['connect_options'],
                                                  value=1.0)
        # --------------------------------------------------------------------------------------------------------------
        # --- Negative value connect option
        self.widgets['negative_checkBox'] = mc.checkBox('negative_checkBox',
                                                        label='Negative',
                                                        width=194,
                                                        height=35,
                                                        parent=self.widgets['right_buttons_column'])
        # --------------------------------------------------------------------------------------------------------------
        # --- Connect and break connection buttons
        self.widgets['connect_buttons'] = mc.rowColumnLayout('connect_buttons',
                                                             numberOfColumns=2,
                                                             width=194,
                                                             parent=self.widgets['right_buttons_column'])
        self.widgets['connect_button'] = mc.button('connect_button',
                                                   label='Connect',
                                                   width=97,
                                                   height=35,
                                                   recomputeSize=False,
                                                   parent=self.widgets['connect_buttons'],
                                                   command=self.connect_button(False))
        self.widgets['break_button'] = mc.button('break_button',
                                                 label='Break Connection',
                                                 width=97,
                                                 height=35,
                                                 recomputeSize=False,
                                                 parent=self.widgets['connect_buttons'],
                                                 command=self.disconnect_button(False))

        # --------------------------------------------------------------------------------------------------------------
        # --- RowColumnLayout
        self.widgets['new_attr_options'] = mc.rowColumnLayout('new_attr_options',
                                                              numberOfColumns=2,
                                                              parent=self.widgets['right_buttons_column'])
        # --------------------------------------------------------------------------------------------------------------
        # --- New attribute textField
        self.widgets['new_attr_label'] = mc.text('new_attr_label',
                                                 label='New attribute',
                                                 height=35,
                                                 parent=self.widgets['new_attr_options'])
        self.widgets['new_attr_textField'] = mc.textField('new_attr_textField',
                                                          height=35,
                                                          width=97,
                                                          parent=self.widgets['new_attr_options'])
        # --------------------------------------------------------------------------------------------------------------
        # --- Connect and break connection buttons
        self.widgets['new_attr_button'] = mc.button('new_attr_button',
                                                    label='Create attr',
                                                    width=97,
                                                    height=35,
                                                    recomputeSize=False,
                                                    parent=self.widgets['new_attr_options'],
                                                    command=self.connect_button(True))
        self.widgets['delete_attr_button'] = mc.button('delete_attr_button',
                                                       label='Delete attr',
                                                       width=97,
                                                       height=35,
                                                       recomputeSize=False,
                                                       parent=self.widgets['new_attr_options'],
                                                       command=self.disconnect_button(True))

        self.refresh_ui()
        mc.showWindow(self.widgets['window'])

    # ------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------GET DATAS FOR FUNCTIONS-----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def get_selected_textscrolllist_item(self, text_scroll_list, *args):
        """
        get the selected item in the given textScrollList.
        :param text_scroll_list:
        :return: string
        """

        selected_item = mc.textScrollList(self.widgets[text_scroll_list], q=True, selectItem=True)
        if selected_item is None:
            selected_item = ['None']
        return selected_item

    # ------------------------------------------------------------------------------------------------------------------
    def get_ui_datas(self, *args):
        """
        Gets all the datas from the ui.
        :return: list [string, string, string, string, float, float, string]
        """

        blendshape_node = mc.optionMenu(self.widgets['bs_nodes_optionmenu'], q=True, value=True)
        blendshape_target = self.get_selected_textscrolllist_item('bs_targets_scrollList')
        controller = self.get_selected_textscrolllist_item('controllers_scrollList')[0]
        attribute = mc.optionMenu(self.widgets['attribute'], q=True, value=True)
        attribute_min = mc.floatField(self.widgets['min_field'], q=True, value=True)
        attribute_max = mc.floatField(self.widgets['max_field'], q=True, value=True)
        new_attribute = mc.textField(self.widgets['new_attr_textField'], q=True, text=True)

        return [blendshape_node, blendshape_target, controller, attribute, attribute_min, attribute_max, new_attribute]

    # ------------------------------------------------------------------------------------------------------------------
    def get_target_index(self, target, *args):
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
    def get_blendshape_base(self, *args):
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

    # ---------------------------------------------UPDATE UI FUNCTIONS--------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def reorder_weights(self, *args):
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
    def create_weights_list(self, *args):
        """
        Create targets list from
        :return: weights (list)
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()

        # --- Create the list of target
        if datas[0] == "None":
            blend_shape_targets_list = ['None']
        else:
            blend_shape_targets_list = list()
            # --- For every target in the blendshapes_datas of the selected blendShape node
            for target in self.blendshapes_datas[datas[0]]['targets']:
                # --- Add the weight_list of the target
                blend_shape_targets_list += self.blendshapes_datas[datas[0]]['targets'][target]['weights']

        return blend_shape_targets_list

    # ------------------------------------------------------------------------------------------------------------------
    def get_target_from_weight(self, weight, *args):
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
    def update_bs_targets_textscrolllist(self, *args):
        """
        Update the targets textScrollList
        """

        print "update_bs_targets_textscrolllist is being called"
        # --- Create the list of target
        blend_shape_targets_list = self.create_weights_list()

        self.update_textscrolllist_items('bs_targets_scrollList', blend_shape_targets_list)

    # ------------------------------------------------------------------------------------------------------------------
    def update_textscrolllist_items(self, text_scroll_list, items_list, *args):
        """
        Update the given textScrollList with the given item list
        :param text_scroll_list:
        :param items_list:
        """

        # --- Get the already selected item
        selected_item = mc.textScrollList(self.widgets[text_scroll_list], q=True, selectItem=True)

        # --- Remove all entries of the given textScrollList
        mc.textScrollList(self.widgets[text_scroll_list], edit=True, removeAll=True)
        # --- If the list is empty, fill it with 'None' string value at index 1
        if items_list is None:
            items_list = ['None']

        # --- For every item in items_list, add it to the textscrolllist
        for item in items_list:
            mc.textScrollList(self.widgets[text_scroll_list], edit=True, append=item)

        # --- Select the last selected item if something was selected
        try:
            mc.textScrollList(self.widgets[text_scroll_list], edit=True, selectItem=selected_item)
        except:
            mc.textScrollList(self.widgets[text_scroll_list], edit=True, selectIndexedItem=1)

    # ------------------------------------------------------------------------------------------------------------------
    def update_optionmenu_items(self, optionmenu, item_list, *args):
        """
        Update the given optionmenu with given item list.
        """
        # --- Get info from ui before deleting
        label = mc.optionMenu(self.widgets[optionmenu], q=True, label=True)
        width = mc.optionMenu(self.widgets[optionmenu], q=True, width=True)
        height = mc.optionMenu(self.widgets[optionmenu], q=True, height=True)
        parent = mc.optionMenu(self.widgets[optionmenu], q=True, parent=True)
        value = mc.optionMenu(self.widgets[optionmenu], q=True, value=True)

        # --- Delete the attribute optionMenu
        mc.deleteUI(self.widgets[optionmenu])
        # --- Re Create the attribute optionMenu
        self.widgets[optionmenu] = mc.optionMenu(label=label,
                                                 width=width,
                                                 height=height,
                                                 parent=parent)
        # --- For every attribute contained in the dict of the given controller
        for item in item_list:
            mc.menuItem(label=item, parent=self.widgets[optionmenu])
        if value in item_list:
            mc.optionMenu(self.widgets[optionmenu], e=True, value=value)

    # ------------------------------------------------------------------------------------------------------------------
    def update_attributes_menu(self, *args):
        """
        Update the attributes menu
        """

        # --- Get the controller which is selected in the UI
        controller = self.get_selected_textscrolllist_item('controllers_scrollList')[0]

        if controller is None:
            controller = "None"

        self.update_optionmenu_items('attribute', self.controllers_datas[controller])

    # ---------------------------------------------BUTTONS FUNCTIONS----------------------------------------------------
    # -------------------------------------------RIGHT BUTTONS FUNCTIONS------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def refresh_ui(self, *args):
        """
        Update the UI
        """

        self.bcs_loaded = self.is_bcs_loaded()

        # Dictionary storing the current scene blendShape datas
        self.blendshapes_datas = self.list_blend_shape_datas()
        self.controllers_datas = self.list_controllers_datas()

        # --- Refresh BlendShape nodes textscrolllist
        blend_shape_nodes_list = [node for node in self.blendshapes_datas]
        if len(blend_shape_nodes_list) == 0:
            blend_shape_nodes_list = ['None']
        self.update_optionmenu_items('bs_nodes_optionmenu', blend_shape_nodes_list)
        self.update_textscrolllist_items('bs_nodes_scrollList', blend_shape_nodes_list)

        # --- Refresh blendShape targets textscrolllist
        self.update_bs_targets_textscrolllist()

        # --- Refresh controllers textscrolllist
        controllers_list = [controller for controller in self.controllers_datas]
        controllers_list.sort()
        self.update_textscrolllist_items('controllers_scrollList', controllers_list)

        # --- Refresh attribute optionMenu
        self.update_attributes_menu()

    # ------------------------------------------------------------------------------------------------------------------
    def create_blendshape_node(self, *args):
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
    def add_blendshape_target(self, *args):
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
                mel.eval('DPK_bcs -e -createDataPoint -name "%s" -dataPointPosition %s -go "%s" "%s"' % (target, index, target, datas[0]))
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
    def extract_blendshape_target(self, given_weight, delete=False, *args):
        """
        Recreate the specified target and reconnect it to the blendShape node, delete it, and then reconnect it properly
        if delete flag is True
        :param target : string (the target to extract or delete)
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
                        mc.setAttr('%s.%s' % (datas[0], self.blendshapes_datas[datas[0]]['targets'][target]['weights'][0]), 1)
                        mc.setAttr('%s.%s' % (datas[0], self.blendshapes_datas[datas[0]]['targets'][target]['weights'][1]), 1)
                    # --- If not, set only the target to 1 (since there is only target weight)
                    else:
                        mc.setAttr('%s.%s' % (datas[0], target), 1)
                    # --- Extract the target by duplicating the base
                    extract = mc.duplicate(base, name=target+'_extract')[0]
                else:
                    # --- Get the index of the dataPoint
                    get_datapoint_index = mel.eval('DPK_bcs -query -getDataPoint -called "%s" "%s"' % (target, datas[0]))
                    # --- Extract the dataPoint
                    extract = mel.eval('DPK_bcs -edit -dataPoint %s -geometryType "edit" -geometryMode true "%s"' % (get_datapoint_index, datas[0]))
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
    def extract_multi_blendshape_target(self, *args):
        """
        Recreate the specified target(s), reconnect them to the blendShape node, and move them
        """

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

        # --- Increment i for every existing extract
        x = bbox_size[1]*2
        for existing_extract in extracts:
            x += (bbox_size[1]*2)

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
                y = bbox_height
                # --- Move the extracted geometry
                mc.xform(extract, translation=[x, y, 0])

            # --- Increment i
            x += bbox_size[1]*2

    # ------------------------------------------------------------------------------------------------------------------
    def delete_blendshape_node(self, *args):
        """
        Delete specified blendShape node.
        """

        datas = self.get_ui_datas()

        mc.delete(datas[0])

        self.refresh_ui()

    # ------------------------------------------------------------------------------------------------------------------
    def remove_blendshape_target(self, *args):
        """
        Add blendShape target(s) to the specified blendShape node (see ui).
        """
        
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

    # ------------------------------------------------------------------------------------------------------------------
    def create_in_between(self, *args):
        """
        Create a new in between
        """

        # --- Get datas from ui
        datas = self.get_ui_datas()
        # --- Get in between value, base, index, and new_target
        in_between_value = mc.floatField(self.widgets['in_between_floatfield'], q=True, value=True)
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
            index = mel.eval('DPK_bcs -e -wPosGrp %s -createWPos -wPosPosition %s "%s"' % (get_wp_index[0], in_between_value, datas[0]))
            # --- Create a new dataPoint at the created weight using new_target
            mel.eval('DPK_bcs -e -createDataPoint -name "%s" -dataPointPosition %s -go "%s" "%s"' % (new_target, index, new_target, datas[0]))
        else:
            mc.blendShape(datas[0], e=True, inBetween=True, target=(base, index, new_target, in_between_value))

    # --------------------------------------------LEFT BUTTONS FUNCTIONS------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def connect_button(self, new_attr=False, *args):
        """
        Connect selected attribute to selected blendShape target. If new_attr is true   , then create the attribute before
        connecting it.
        :param new_attr: boolean
        :return: connect_attribute() function
        """

        def connect_attribute(*args):  # Creates a callable object
            # --- Get datas from ui
            datas = self.get_ui_datas()
            check = 'continue'

            # --- Get checkbox state
            negative = mc.checkBox(self.widgets['negative_checkBox'], query=True, value=True)
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
                    mc.addAttr(datas[2], longName=datas[6], attributeType='float',
                               hidden=False, keyable=True, maxValue=datas[5])
                    # --- Changing attribute with new attribute
                    datas[3] = datas[6]
                    self.refresh_ui()
                    check = 'continue'

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

        return connect_attribute

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect_button(self, delete_attr=False, *args):
        """
        Disconnect everything from selected blendShape target, delete the setRange if it exists, and if delete_attr is
        True, then delete the named attribute.
        :param delete_attr: boolean
        :return: disconnect() function
        """

        def disconnect(*args):  # Creates a callable object
            datas = self.get_ui_datas()
            # --- List all setRange in the scene
            all_set_range_nodes = mc.ls(exactType='setRange')

            # --- Define what to do if delete_attr is True
            if delete_attr:
                    mc.deleteAttr('%s.%s' % (datas[2], datas[3]))
            # --- Define what to do if delete_attr is False
            else:
                for target in datas[1]:
                    # --- Get defined set range if it exists, and delete it
                    set_range = [node for node in all_set_range_nodes if node.split('_to_')[-1] == '%s_%s' % (datas[0], target)]
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

            self.refresh_ui()

        return disconnect

    # ------------------------------------------------------------------------------------------------------------------
    def write_setup_to_dict(self, *args):
        """
        Save the current blendShape node setup to dict. TO CORRECT !!!
        :return: setup_dict (dict)
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

        return connection_dict

    # ------------------------------------------------------------------------------------------------------------------
    def create_setup_from_dict(self, blendshape_node, connection_dict, *args):
        """
        Create a setup from connections stored into the given dictionary. TO CORRECT !!!
        :param connection_dict: dictionary of all connections to do to the given blendshape node
        """
        # --- Reconnect all the connections
        for weight in connection_dict:
            mc.connectAttr(connection_dict[weight], '%s.%s' % (blendshape_node, weight))

    # ------------------------------------------------------------------------------------------------------------------
    def reset_ctrl(self, *args):
        """
        Reset all ctrl attributes to 0, scale to 1.
        """

        for controller in self.controllers_datas:
            print controller
            for attribute in self.controllers_datas[controller]:
                print attribute
                if 'scale' in attribute or 'visibility' in attribute:
                    mc.setAttr('%s.%s' % (controller, attribute), 1)
                else:
                    mc.setAttr('%s.%s' % (controller, attribute), 0)
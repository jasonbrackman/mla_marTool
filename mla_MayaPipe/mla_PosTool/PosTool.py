__author__ = 'lantonm'
import maya.cmds as mc
from PySide.QtCore import *
from PySide.QtGui import *

import PosTool_ui

reload(PosTool_ui)


folder_path = '/'.join(__file__.split('/')[:-1])

# -------------------------------------- EXPORT TEMPLATES ----------------------
# ------------------------------------------------------------------------------
class MLAPosTool(QDialog, PosTool_ui.Ui_MPosToolMainWindow):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setObjectName('m_pos_tool_ui')

        self.move_pB.clicked.connect(self.move_from_ui)
        self.move_even_pB.clicked.connect(self.move_even_from_ui)

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
        behavior = self.behavior_cB.isChecked()

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
                'behavior': behavior
                }

    def move_from_ui(self):
        """
        Use move function using ui's data
        :return:
        """
        self.data = self.get_data()

        selection = mc.ls(sl=True)

        self.move(selection, self.data['translate'],
                  self.data['rotate'], self.data['scale'],
                  self.data['world_space'], self.data['mirror'],
                  self.data['mirror_axis'], self.data['behavior'])

    def move_even_from_ui(self):
        """
        Use move_transform function using ui's data
        :return:
        """
        self.data = self.get_data()

        selection = mc.ls(sl=True)

        self.move_even(selection, self.data['translate'], self.data['rotate'],
                       self.data['scale'], self.data['world_space'],
                       self.data['mirror'], self.data['mirror_axis'],
                       self.data['behavior'])

    @staticmethod
    def move_even(obj_list=(), translate=('x', 'y', 'z'),
                  rotate=('x', 'y', 'z'), scale=(),
                  world_space=True, mirror=False, mirror_axis='x',
                  behavior=False):
        """
        Call the move function by even
        :param obj_list: list of objects to move by pair
        :type obj_list: list

        :param translate: tuple of translate channel to move
        :type translate: tuple

        :param rotate: tuple of rotate channel to move
        :type rotate: tuple

        :param scale: tuple of scale channel to move
        :type scale: tuple

        :param world_space: world space by default, object space if False
        :type world_space: boolean

        :param mirror: mirror state
        :type mirror: boolean

        :param mirror_axis: mirror axis
        :type mirror_axis: str

        :param behavior: mirroring behavior/orientation
        :type behavior: boolean

        :return:
        """
        # UNDO : Open history chunk
        mc.undoInfo(openChunk=True)

        try:
            if len(obj_list) == 0:
                obj_list = mc.ls(sl=True, et='transform')

            for i, obj in enumerate(obj_list):
                if i % 2 == 0:
                    source = obj
                    target = obj_list[i + 1]

                    MLAPosTool.move(source_target=[source, target],
                                    translate=translate,
                                    rotate=rotate,
                                    scale=scale,
                                    world_space=world_space,
                                    mirror=mirror,
                                    mirror_axis=mirror_axis,
                                    behavior=behavior)
        # UNDO : Close history chunk
        finally:
            mc.undoInfo(closeChunk=True)

    @staticmethod
    def move(source_target=(), translate=('x', 'y', 'z'),
             rotate=('x', 'y', 'z'), scale=(),
             world_space=True, mirror=False, mirror_axis='x',
             behavior=False):
        """
        Move an object according to another object's coordinates, to snap or
        mirror position, in world or object space, using a specified mirror
        axis.

        :param source_target: couple source/target
        :type source_target: list

        :param translate: tuple of translate channel to move
        :type translate: tuple

        :param rotate: tuple of rotate channel to move
        :type rotate: tuple

        :param scale: tuple of scale channel to move
        :type scale: tuple

        :param world_space: world space by default, object space if False
        :type world_space: boolean

        :param mirror: mirror state
        :type mirror: boolean

        :param mirror_axis: mirror axis
        :type mirror_axis: str

        :param behavior: mirroring behavior/orientation
        :type behavior: boolean

        :return:
        """
        # UNDO : Open history chunk
        mc.undoInfo(openChunk=True)

        try:
            # Define couple source/target if not already defined
            if len(source_target) == 0:
                if len(mc.ls(sl=True)) > 1:
                    source_target = mc.ls(sl=True)[:2]
                else:
                    source_target = mc.ls(sl=True)

            # If no source and target given, or to get from selection : return
            if len(source_target) == 0:
                print "No source and no target, skipped."
                return
            # If only one object selected : mirror from its own coordinates
            elif len(source_target) == 1:
                source_target.append(source_target[0])
            else:
                source_target = source_target[:2]

            source = source_target[0]
            target = source_target[1]

            # Get initial transforms from source and target
            if world_space:
                source_translate = mc.xform(source, q=True, t=True, ws=True)
                source_rotate = mc.xform(source, q=True, ro=True, ws=True)
                source_scale = mc.xform(source, q=True, s=True, ws=True)

                target_translate = mc.xform(target, q=True, t=True, ws=True)
                target_rotate = mc.xform(target, q=True, ro=True, ws=True)
                target_scale = mc.xform(target, q=True, s=True, ws=True)
            else:
                source_translate = mc.xform(source, q=True, t=True, os=True)
                source_rotate = mc.xform(source, q=True, ro=True, os=True)
                source_scale = mc.xform(source, q=True, s=True, os=True)

                target_translate = mc.xform(target, q=True, t=True, os=True)
                target_rotate = mc.xform(target, q=True, ro=True, os=True)
                target_scale = mc.xform(target, q=True, s=True, os=True)

            # Defining mirror multiplier
            if mirror and mirror_axis == 'x':
                mir_val = [-1, 1, 1]
            elif mirror and mirror_axis == 'y':
                mir_val = [1, -1, 1]
            elif mirror and mirror_axis == 'z':
                mir_val = [1, 1, -1]
            else:
                mir_val = [1, 1, 1]

            translate_value = [0, 0, 0]
            rotate_value = [0, 0, 0]
            scale_value = [1, 1, 1]

            # Defining transforms
            # ------------------------------------------------------------------
            # TRANSLATE
            if 'x' in translate:
                translate_value[0] = source_translate[0] * mir_val[0]
            else:
                translate_value[0] = target_translate[0]

            if 'y' in translate:
                translate_value[1] = source_translate[1] * mir_val[1]
            else:
                translate_value[1] = target_translate[1]

            if 'z' in translate:
                translate_value[2] = source_translate[2] * mir_val[2]
            else:
                translate_value[2] = target_translate[2]
            # ------------------------------------------------------------------
            # ROTATE
            # X axis
            if 'x' in rotate:
                # If mirror
                if mirror:
                    # If behavior
                    if behavior:
                        # If mirror X or Y
                        if mirror_axis == 'x' or mirror_axis == 'y':
                            rotate_value[0] = source_rotate[0] + 180
                            # If mirror Z
                        else:
                            rotate_value[0] = source_rotate[0]
                    # If orientation
                    else:
                        # If mirror X or Y
                        if mirror_axis == 'x' or mirror_axis == 'y':
                            rotate_value[0] = 180 - source_rotate[0]
                        # If mirror Z
                        else:
                            rotate_value[0] = -source_rotate[0]
                # If rotate X in attribute BUT NOT mirror
                else:
                    rotate_value[0] = source_rotate[0]
            # If NOT rotate X in attributes
            else:
                rotate_value[0] = target_rotate[0]
            # --------------------
            # Y axis
            if 'y' in rotate:
                # If mirror
                if mirror:
                    # If behavior
                    if behavior:
                        # If mirror X or Y
                        if mirror_axis == 'x' or mirror_axis == 'y':
                            rotate_value[1] = - source_rotate[1]
                        # If mirror Z
                        else:
                            rotate_value[1] = source_rotate[1]
                    # If orientation
                    else:
                        # If mirror X or Y
                        if mirror_axis == 'x' or mirror_axis == 'y':
                            rotate_value[1] = source_rotate[1]
                        # If mirror Z
                        else:
                            rotate_value[1] = -source_rotate[1]
                # If rotate Y in attribute BUT NOT mirror
                else:
                    rotate_value[1] = source_rotate[1]
            # If NOT rotate Y attributes
            else:
                rotate_value[1] = target_rotate[1]
            # --------------------
            # Z axis
            if 'z' in rotate:
                # If mirror
                if mirror:
                    # If behavior
                    if behavior:
                        # If mirror X
                        if mirror_axis == 'x':
                            rotate_value[2] = -source_rotate[2]
                        # If mirror Y
                        elif mirror_axis == 'y':
                            # If rotate z is negative
                            if source_rotate[2] < 0:
                                rotate_value[2] = -180 - source_rotate[2]
                            # If rotate z is positive
                            else:
                                rotate_value[2] = 180 - source_rotate[2]
                        # If mirror Z
                        else:
                            # If rotate z is negative
                            if source_rotate[2] < 0:
                                rotate_value[2] = source_rotate[2] + 180
                            # If rotate z is positive
                            else:
                                rotate_value[2] = source_rotate[2] - 180
                    # If orientation
                    else:
                        # If mirror X
                        if mirror_axis == 'x':
                            rotate_value[2] = 180 - source_rotate[2]
                        # If mirror Y
                        elif mirror_axis == 'y':
                            rotate_value[2] = -source_rotate[2]
                        # If mirror Z
                        else:
                            rotate_value[2] = source_rotate[2]
                # If rotate Z in attribute BUT NOT mirror
                else:
                    rotate_value[2] = source_rotate[2]
            # If NOT rotate Z in attributes
            else:
                rotate_value[2] = target_rotate[2]
            # ------------------------------------------------------------------
            # SCALE
            if 'x' in scale:
                scale_value[0] = source_scale[0] * mir_val[0]
            else:
                scale_value[0] = target_scale[0]

            if 'y' in scale:
                scale_value[1] = source_scale[1] * mir_val[1]
            else:
                scale_value[1] = target_scale[1]

            if 'z' in scale:
                scale_value[2] = source_scale[2] * mir_val[2]
            else:
                scale_value[2] = target_scale[2]

            # Normalize rotate values
            for i, value in enumerate(rotate):
                if value > 180:
                    rotate_value[i] -= 360
                elif value < -180:
                    rotate_value[i] += 360
                else:
                    rotate_value[i] = value

            # Move the target according to the new coordinates
            if world_space:
                print(source_translate, source_rotate, source_scale,
                      target_translate, target_rotate, target_scale,)
                mc.xform(target, t=translate_value, ws=True)
                mc.xform(target, ro=rotate_value, ws=True)
                mc.xform(target, s=scale_value, ws=True)
            else:
                print(source_translate, source_rotate, source_scale,
                      target_translate, target_rotate, target_scale,)
                mc.xform(target, t=translate_value, os=True)
                mc.xform(target, ro=rotate_value, os=True)
                mc.xform(target, s=scale_value, os=True)
                # UNDO : Close history chunk
        finally:
            mc.undoInfo(closeChunk=True)

    def constrain_from_ui(self):
        """
        Create a constraint using ui's data
        :return:
        """
        data = self.get_data()

        selection = mc.ls(sl=True)

        if data['constraint_type'] == 'Mirror selected':
            targets = selection
            source = ''
        elif len(selection) > 1:
            targets = selection[:-1]
            source = selection[-1]
        else:
            print 'You need to select at least 2 objects to constrain',
            return

        self.constrain(constraint_type=data['constraint_type'],
                       targets=targets,
                       source=source,
                       aim_vector=data['aim_vector'],
                       up_vector=data['up_vector'],
                       maintain_offset=data['maintain_offset'],
                       skip=(data['skip_translation'],
                             data['skip_rotation'],
                             data['skip_scale']))

    def constrain_even_from_ui(self):
        """
        Call constrain function by even using ui's data
        :return:
        """
        data = self.get_data()

        selection = mc.ls(sl=True)

        for i, obj in enumerate(selection):
            if i % 2 == 0:
                self.constrain(constraint_type=data['constraint_type'],
                               targets=[selection[i]],
                               source=selection[i + 1],
                               aim_vector=data['aim_vector'],
                               up_vector=data['up_vector'],
                               maintain_offset=data['maintain_offset'],
                               skip=(data['skip_translation'],
                                     data['skip_rotation'],
                                     data['skip_scale']))

    @staticmethod
    def constrain(constraint_type='Parent constraint', targets='', source='',
                  aim_vector=(1, 0, 0), up_vector=(0, 1, 0),
                  maintain_offset=True, skip=((), (), ()), ct_name=''):
        """
        Create a constraint of the specified type on specified objects. If
        either sources or target are missing, it uses the current selection.

        :param constraint_type: type of the constraint you want to create.
        :type constraint_type: str

        :param targets: objects constraining
        :type targets: list

        :param source: object constrained
        :type source: str

        :param aim_vector: vector used to aim
        :type aim_vector: tuple

        :param up_vector: vector used as up
        :type up_vector: tuple

        :param maintain_offset: specify if current offset must be maintained
        :type maintain_offset: bool

        :param skip: axes to skip when constraining ((trans), (rot), (scale))
        :type skip: tuple

        :param ct_name: name of the newly created constraint
        :type ct_name: str

        :return:
        """
        # Get selection if necessary
        if constraint_type != 'Mirror selected':
            if not targets or not source:
                selection = mc.ls(sl=True)
                targets = selection[:-1]
                source = selection[-1]

        # Create name if not provided
        if len(ct_name) == 0:
            ct_from = targets[0]
            for i, obj in enumerate(targets):
                if i != 0:
                    ct_from += '_AND_%s' % obj
            ct_name = '%s_TO_%s' % (ct_from, source)

        if constraint_type == 'pointConstraint':
            mc.pointConstraint(targets, source, mo=maintain_offset, sk=skip[0],
                               n=ct_name)
        elif constraint_type == 'orientConstraint':
            mc.orientConstraint(targets, source, mo=maintain_offset, sk=skip[1],
                                n=ct_name)
        elif constraint_type == 'aimConstraint':
            mc.aimConstraint(targets, source, aim=aim_vector, u=up_vector,
                             mo=maintain_offset, sk=skip[1], n=ct_name)
        elif constraint_type == 'scaleConstraint':
            mc.scaleConstraint(targets, source, mo=maintain_offset, sk=skip[2],
                               n=ct_name)
        elif constraint_type == 'parentConstraint':
            mc.parentConstraint(targets, source, mo=maintain_offset, st=skip[0],
                                sr=skip[1], n=ct_name)
        else:
            MLAPosTool.mirror_constraint(targets)

    @staticmethod
    def mirror_constraint(constraints=()):
        """
        Mirror the given constraints

        :param constraints: names of the constraints to duplicate
        :type constraints: list

        :return: names of the newly created constraints
        :rtype: list
        """
        new_constraints = list()

        # Define constraint types
        ct_types = ['pointConstraint',
                    'orientConstraint',
                    'aimConstraint',
                    'scaleConstraint',
                    'parentConstraint']
        # Define attributes to look at
        out_connections = ['constraintRotateX',
                           'constraintRotateY',
                           'constraintRotateZ',
                           'constraintTranslateX',
                           'constraintTranslateY',
                           'constraintTranslateZ',
                           'constraintScaleX',
                           'constraintScaleY',
                           'constraintScaleZ']
        in_connections = ['RotateX',
                          'RotateY',
                          'RotateZ',
                          'TranslateX',
                          'TranslateY',
                          'TranslateZ',
                          'ScaleX',
                          'ScaleY',
                          'ScaleZ']
        offset = ['targetOffsetTranslateX',
                  'targetOffsetTranslateY',
                  'targetOffsetTranslateZ',
                  'targetOffsetRotateX',
                  'targetOffsetRotateY',
                  'targetOffsetRotateZ',
                  'targetOffsetScaleX',
                  'targetOffsetScaleY',
                  'targetOffsetScaleZ']

        # Define default values
        aim = [1, 0, 0]
        up = [0, 1, 0]
        maintain_offset = False
        skip_trans = list()
        skip_rot = list()
        skip_scale = list()

        # Loop in constraints
        for ct in constraints:
            ct_type = mc.nodeType(ct)
            # If not a constraint : pass
            if ct_type not in ct_types:
                pass
            # If constraint : get required data
            else:
                # Get targets (and aim, and up in case of aimConstraint)
                if ct_type == ct_types[0]:
                    targets = mc.pointConstraint(ct, q=True, targetList=True)
                elif ct_type == ct_types[1]:
                    targets = mc.orientConstraint(ct, q=True, targetList=True)
                elif ct_type == ct_types[2]:
                    targets = mc.aimConstraint(ct, q=True, targetList=True)
                    aim = mc.aimConstraint(ct, q=True, aim=True)
                    up = mc.aimConstraint(ct, q=True, u=True)
                elif ct_type == ct_types[3]:
                    targets = mc.scaleConstraint(ct, q=True, targetList=True)
                elif ct_type == ct_types[4]:
                    targets = mc.parentConstraint(ct, q=True, targetList=True)
                else:
                    targets = list()

                # Get constrained object
                cnted = ''

                for attr in out_connections:
                    if mc.objExists('%s.%s' % (ct, attr)):
                        if mc.listConnections('%s.%s' % (ct, attr),
                                              d=True, s=False):
                            cnted = mc.listConnections('%s.%s' % (ct, attr),
                                                       d=True, s=False)[0]
                            new_cnted = MLAPosTool.get_opposite_name(cnted)
                            break
                        else:
                            pass

                # Get new targets
                new_targets = list()

                for target in targets:
                    new_targets.append(MLAPosTool.get_opposite_name(target))

                # Get maintain_offset
                for i in range(len(targets)):
                    for attr in offset:
                        if mc.objExists('%s.target[%s].%s' % (ct, i, attr)):
                            if mc.getAttr('%s.target[%s].%s' % (ct, i, attr)) \
                                    != 0:
                                maintain_offset = True
                                break

                # Get skip translate, rotate, scale
                for duo in [[0, skip_trans], [3, skip_rot], [6, skip_scale]]:
                    for i, attr in enumerate(['x', 'y', 'z']):
                        idx = i + duo[0]
                        out_attr = '%s.%s' % (ct, out_connections[idx])
                        in_attr = '%s.%s' % (cnted, in_connections[idx])
                        if mc.objExists(out_attr):
                            if mc.objExists(in_attr):
                                if mc.isConnected(in_attr, out_attr):
                                    duo[1].append(attr)

                # Create new name in case the constrained object is a center
                # object (and therefore gets only new targets on the existing
                # constraint)
                if new_cnted.lower().startswith('c_'):
                    ct_from = new_targets[0]
                    for i, obj in enumerate(targets):
                        if i != 0:
                            ct_from += '_AND_%s' % obj
                    ct_name = '%s_AND_%s' % (ct_from, ct)
                else:
                    ct_name = ''

                print ct_name

                # Create constraint
                MLAPosTool.constrain(constraint_type=ct_type,
                                     targets=new_targets,
                                     source=new_cnted,
                                     aim_vector=aim,
                                     up_vector=up,
                                     maintain_offset=maintain_offset,
                                     skip=(skip_trans, skip_rot, skip_scale),
                                     ct_name=ct_name)

    @staticmethod
    def get_opposite_name(obj):
        """
        Get the name of the opposite object (same name, on the other side).

        :param obj: Name of the object which you want to find the opposite
        :type obj: str

        :return: name of the opposite object
        :rtype: str
        """

        if obj.startswith('l_'):
            opposite_name = obj.replace('l_', 'r_')
        elif obj.startswith('r_'):
            opposite_name = obj.replace('r_', 'l_')
        elif obj.startswith('L_'):
            opposite_name = obj.replace('L_', 'R_')
        elif obj.startswith('R_'):
            opposite_name = obj.replace('R_', 'L_')
        elif obj.startswith('left_'):
            opposite_name = obj.replace('left_', 'right_')
        elif obj.startswith('right_'):
            opposite_name = obj.replace('right_', 'left_')
        elif obj.startswith('LEFT_'):
            opposite_name = obj.replace('LEFT_', 'RIGHT_')
        elif obj.startswith('RIGHT_'):
            opposite_name = obj.replace('RIGHT_', 'LEFT_')
        else:
            opposite_name = obj

        return opposite_name
import maya.cmds as mc
import mla_GeneralPipe.mla_general_utils.mla_name_utils as nu
import orig as orig

reload(nu)
reload(orig)


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

                move(source_target=[source, target], translate=translate,
                     rotate=rotate, scale=scale, world_space=world_space,
                     mirror=mirror, mirror_axis=mirror_axis, behavior=behavior)
    # UNDO : Close history chunk
    finally:
        mc.undoInfo(closeChunk=True)


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
        mirror_constraint(targets)


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
                        new_cnted = nu.get_opposite_name(cnted)
                        break
                    else:
                        pass

            # Get new targets
            new_targets = list()

            for target in targets:
                new_targets.append(nu.get_opposite_name(target))

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
            constrain(constraint_type=ct_type,
                      targets=new_targets,
                      source=new_cnted,
                      aim_vector=aim,
                      up_vector=up,
                      maintain_offset=maintain_offset,
                      skip=(skip_trans, skip_rot, skip_scale),
                      ct_name=ct_name)


def orient_mirror_shape(shape, axis='x', mirror=(False, False, False)):
    """
    Rotate and orient a mesh, curve, nurbs, etc.
    :param shape: Name of the shape to rotate and mirror (mesh, curve, etc)
    :type shape: str

    :param axis: Axis to orient the shape to. Default x (no rotation)
    :type axis: str

    :param mirror: Axis to mirror the shape along. Default (0, 0, 0) (no mirror)
    :type mirror: tuple / list

    :return:
    """
    parent = mc.listRelatives(shape, p=True)

    # Transform shape
    shape_orig = orig.orig([shape])
    if axis == 'x':
        pass
    elif axis == 'y':
        mc.setAttr('%s.rz' % shape, 90)
    else:
        mc.setAttr('%s.ry' % shape, 90)
    mc.makeIdentity(shape, r=True, a=True)

    mirr_value = list()
    for each_axis in mirror:
        if not each_axis:
            mirr_value.append(1)
        else:
            mirr_value.append(-1)

    mc.setAttr('%s.scale' % shape, mirr_value[0], mirr_value[1], mirr_value[2],
               type="double3")
    mc.makeIdentity(shape, s=True, a=True)

    # Clean hierarchy
    if parent:
        mc.parent(shape, parent)
    else:
        mc.parent(shape, w=True)
    mc.delete(shape_orig)

    return shape
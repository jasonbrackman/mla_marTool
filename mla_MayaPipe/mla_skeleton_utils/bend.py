__author__ = 'm.lanton'
from math import fabs

import maya.cmds as mc

import Python.mla_general_utils.ml_utilities as mlutilities
from Python.mla_rig_utils import orig as orig


# ----------------------------------------------------------------
def count_non_linear(deform_type):
    """that function counts the nonLinear nodes of the specified type

    :param deform_type: type of the deformer to count
    :type deform_type: string"""

    # lists the nonlinear nodes
    i = 0
    non_linears = mc.ls(et='nonLinear')
    # increment i depending of the asked type of node
    for node in non_linears:
        if deform_type == 'bend':
            if mc.objExists(node + '.curvature'):
                i += 1
        elif deform_type == 'flare':
            if mc.objExists(node + '.curve'):
                i += 1
        elif deform_type == 'sine':
            if mc.objExists(node + '.highBound') and mc.objExists(node + '.wavelength'):
                i += 1
        elif deform_type == 'squash':
            if mc.objExists(node + '.factor'):
                i += 1
        elif deform_type == 'twist':
            if mc.objExists(node + '.startAngle'):
                i += 1
        elif deform_type == 'wave':
            if mc.objExists(node + '.minRadius') and mc.objExists(node + '.wavelength'):
                i += 1
        else:
            pass
    #return the number of nonLinear nodes of the specified type
    return i


#----------------------------------------------------------------
def create_deform(deform_type, axis, node):
    """that function creates a nonLinear deformer of the specified type and rename it and its Handle according to the
    specified type and axis

    :param deform_type: type of the deformer to create
    :type deform_type: string

    :param axis: axis of influence of the deformer
    :type axis: string

    :param node: node to deform
    :type node: string

    :return: name of the new deformer and name of its handle
    :rtype: list"""

    # counts the nonLinear of the specified type and defines the name of the new node to create
    count = count_non_linear(deform_type) + 1
    deform = deform_type + str(count)
    # select the geometry to deform and create the deformer
    mc.select(node)
    mc.nonLinear(typ=deform_type)
    # rename the deformer
    deform_name = mc.rename(deform, node + '_' + deform_type + '_' + axis)
    deform_handle = mc.rename(deform + 'Handle', node + '_' + deform_type + 'Handle_' + axis)
    # return both the name of the newly created nonLinear and his handle
    return [deform_name, deform_handle]


#----------------------------------------------------------------
def create_bend_squash(bounds=False, center='low'):
    """that function creates a system composed of 2 bend (X and Z) and a squash"""

    # lists the current selected nodes
    selection = mc.ls(sl=True)
    i = 0

    # creates the system for every node in the current selection
    for node in selection:

        low_bound_ctrl = node+'_lowBound_ctrl'
        high_bound_ctrl = node+'_highBound_ctrl'

        # positions according to the bbox of the current node
        x1, y1, z1, x2, y2, z2 = mc.exactWorldBoundingBox(selection[i], calculateExactly=True,
                                                          ignoreInvisible=True)
        bbox_size = [0, 0]
        bbox_size[0] = x2 - x1
        bbox_size[1] = y2 - y1
        bbox_size.sort()
        ctrl_size = bbox_size[1] * 0.5
        pointer_size = [ctrl_size/4, ctrl_size/4, ctrl_size/4]

        low_pos = ((x2 + x1) / 2, y1, (z2 + z1) / 2)
        high_pos = ((x2 + x1) / 2, y2, (z2 + z1) / 2)
        mid_pos = ((x2 + x1) / 2, (y2 + y1) / 2, (z2 + z1) / 2)

        # defines bounds according to the specified parameter
        bound = [-2, 2]
        if center == 'mid':
            center_position = mid_pos
            bound = [-1, 1]
            low_bound_pos = low_pos
            high_bound_pos = high_pos
        elif center == 'high':
            center_position = high_pos
            low_bound_pos = low_pos
            high_bound_pos = [high_pos[0], high_pos[1]*3, high_pos[2]]
        else:
            center_position = low_pos
            low_bound_pos = [low_pos[0], low_pos[1]*3, low_pos[2]]
            high_bound_pos = high_pos

        # creates the first bend
        bend_x = create_deform('bend', 'X', node)
        mc.xform(bend_x[1], t=center_position, ro=[0, 0, 0])
        orig_bend_x = orig.orig([bend_x[1]])
        mc.setAttr(bend_x[0] + '.lowBound', bound[0])
        mc.setAttr(bend_x[0] + '.highBound', bound[1])

        # creates the second bend
        bend_z = create_deform('bend', 'Z', node)
        mc.xform(bend_z[1], t=center_position, ro=[0, 90, 0])
        orig_bend_z = orig.orig([bend_z[1]])
        mc.setAttr(bend_z[0] + '.lowBound', bound[0])
        mc.setAttr(bend_z[0] + '.highBound', bound[1])

        # creates the squash
        squash = create_deform('squash', 'Y', node)
        mc.xform(squash[1], t=center_position)
        orig_squash = orig.orig([squash[1]])
        mc.setAttr(squash[0] + '.lowBound', bound[0])
        mc.setAttr(squash[0] + '.highBound', bound[1])

        # creates the controller for the system
            # defines the ctrl name
        ctrl_name = node+'_ctrl'
        bendsquash_ctrl_name = node+'_bendSquash_ctrl'
        bendsquash_SR_name = node + '_bendSquash_SR'
        bendSquash_bounds_SR_name = node+'_bendSquash_bounds_SR'
        
            # creation and zeroOut
        orig_ctrl = mlutilities.create_ctrl(ctrl_type='quad_arrow', name=bendsquash_ctrl_name, sca=[ctrl_size, ctrl_size*0.5, ctrl_size])[1]
            # place the zeroOut
        mc.xform(orig_ctrl, t=[high_pos[0], high_pos[1]/10*12, high_pos[2]])

            # creates and set setRange node
        mc.createNode('setRange', n=bendsquash_SR_name)
        mc.setAttr(bendsquash_SR_name+'.min', -180, -10, 180, type="double3")
        mc.setAttr(bendsquash_SR_name+'.max', 180, 10, -180, type="double3")
        mc.setAttr(bendsquash_SR_name+'.oldMin', -10, -bbox_size[1]*4, -10, type="double3")
        mc.setAttr(bendsquash_SR_name+'.oldMax', 10, bbox_size[1]*4, 10, type="double3")
            # connects ctrl to SR and SR to nonLinears
        mc.connectAttr(bendsquash_ctrl_name+'.translateX', bendsquash_SR_name+'.valueX')
        mc.connectAttr(bendsquash_SR_name+'.outValueX', bend_x[0]+'.curvature')
        mc.connectAttr(bendsquash_ctrl_name+'.translateY', bendsquash_SR_name+'.valueY')
        mc.connectAttr(bendsquash_SR_name+'.outValueY', squash[0]+'.factor')
        mc.connectAttr(bendsquash_ctrl_name+'.translateZ', bendsquash_SR_name+'.valueZ')
        mc.connectAttr(bendsquash_SR_name+'.outValueZ', bend_z[0]+'.curvature')

        mc.hide(orig_bend_x, orig_bend_z, orig_squash)

        # parent to existing hierarchy
        if mc.objExists(ctrl_name):
            mc.parent(orig_bend_x, orig_bend_z, orig_squash, orig_ctrl, ctrl_name)
        elif mc.objExists('helper_ctrl'):
            mc.parent(orig_bend_x, orig_bend_z, orig_squash, orig_ctrl, 'helper_ctrl')
        else:
            mc.parent(orig_bend_x, orig_bend_z, orig_squash, orig_ctrl, 'walk_ctrl')

        if bounds:
            hb_limit_up = float(mid_pos[1]+9*fabs(high_bound_pos[1]))
            hb_limit_down = float(mid_pos[1]-11*fabs(high_bound_pos[1]))
            lb_limit_up = float(mid_pos[1]+9*fabs(low_bound_pos[1]))
            lb_limit_down = float(mid_pos[1]-11*fabs(low_bound_pos[1]))
            # creates bounds pointers
            mlutilities.create_ctrl(ctrl_type='pointer', size=pointer_size, name=high_bound_ctrl, rotation=[180, 0, 0])
            mc.xform(high_bound_ctrl, t=high_bound_pos)
            orig_highbound = orig.orig([high_bound_ctrl])
            mlutilities.create_ctrl(ctrl_type='pointer', size=pointer_size, name=low_bound_ctrl)
            mc.xform(low_bound_ctrl, t=low_bound_pos)
            orig_lowbound = orig.orig([low_bound_ctrl])

            # creates bounds SR and set it
            mc.createNode('setRange', n='bendSquash_bounds_SR')
            mc.setAttr(bendSquash_bounds_SR_name+'.min', -10, -10, 0, type="double3")
            mc.setAttr(bendSquash_bounds_SR_name+'.max', 10, 10, 0, type="double3")
            mc.setAttr(bendSquash_bounds_SR_name+'.oldMin', hb_limit_down, lb_limit_down, 0.0, type="double3")
            mc.setAttr(bendSquash_bounds_SR_name+'.oldMax', hb_limit_up, lb_limit_up, 0.0, type="double3")
            # connects controllers to SR and SR to nonLinears
            mc.connectAttr(node+'_highBound_ctrl.translateY', bendSquash_bounds_SR_name+'.valueX')
            mc.connectAttr(bendSquash_bounds_SR_name+'.outValueX', bend_x[0]+'.highBound')
            mc.connectAttr(bendSquash_bounds_SR_name+'.outValueX', bend_z[0]+'.highBound')
            mc.connectAttr(node+'_lowBound_ctrl.translateY', bendSquash_bounds_SR_name+'.valueY')
            mc.connectAttr(bendSquash_bounds_SR_name+'.outValueY', bend_x[0]+'.lowBound')
            mc.connectAttr(bendSquash_bounds_SR_name+'.outValueY', bend_z[0]+'.lowBound')

                # parent to existing hierarchy
            if mc.objExists(bendsquash_ctrl_name):
                mc.parent(orig_highbound, orig_lowbound, ctrl_name)
            elif mc.objExists('helper_ctrl'):
                mc.parent(orig_highbound, orig_lowbound, 'helper_ctrl')
            else:
                mc.parent(orig_highbound, orig_lowbound, 'walk_ctrl')

        i += 1
    mlutilities.rigset()


def create_simple_bend(bounds=False, center='low', direction='Z'):
    """that function creates a bend system"""

    # lists the current selected nodes
    selection = mc.ls(sl=True)
    i = 0

    # creates the system for every node in the current selection
    for node in selection:


        low_bound_ctrl = node+'_lowBound_ctrl'
        high_bound_ctrl = node+'_highBound_ctrl'
        # positions according to the bbox of the current node
        x1, y1, z1, x2, y2, z2 = mc.exactWorldBoundingBox(selection[i], calculateExactly=True,
                                                          ignoreInvisible=True)

        bbox_size = [0, 0]
        bbox_size[0] = x2 - x1
        bbox_size[1] = y2 - y1
        bbox_size.sort()
        ctrl_size = bbox_size[1] * 0.5
        pointer_size = [ctrl_size/4, ctrl_size/4, ctrl_size/4]

        low_pos = ((x2 + x1) / 2, y1, (z2 + z1) / 2)
        high_pos = ((x2 + x1) / 2, y2, (z2 + z1) / 2)
        mid_pos = ((x2 + x1) / 2, (y2 + y1) / 2, (z2 + z1) / 2)

        # defines bounds according to the specified parameter
        bound = [-2, 2]
        if center == 'mid':
            center_position = mid_pos
            bound = [-1, 1]
            low_bound_pos = low_pos
            high_bound_pos = high_pos
        elif center == 'high':
            center_position = high_pos
            low_bound_pos = low_pos
            high_bound_pos = [high_pos[0], high_pos[1]*3, high_pos[2]]
        else:
            center_position = low_pos
            low_bound_pos = [low_pos[0], low_pos[1]*3, low_pos[2]]
            high_bound_pos = high_pos

        # creates the first bend
        bend = create_deform('bend', direction, node)
        mc.xform(bend[1], t=center_position)
        if direction.lower() == 'z':
            mc.xform(bend[1], ro=[0, -90, 0])
        orig_bend = orig.orig([bend[1]])
        mc.setAttr(bend[0]+'.lowBound', bound[0])
        mc.setAttr(bend[0]+'.highBound', bound[1])
        mc.setAttr(bend[1]+'.visibility', 0)


        # creates the controller for the system
            # defines the ctrl name
        ctrl_name = node+'_ctrl'
        bend_ctrl_name = node+'_bend_ctrl'
        bend_sr = node+'_bend_SR'
        bend_bounds_sr=node+'_bend_bounds_SR'
            # creation and zeroOut
        mc.circle(nr=[0, 1, 0], r=0.1, ch=False, n=bend_ctrl_name)
        mlutilities.color([bend_ctrl_name], 'yellow')
        orig_ctrl = orig.orig([bend_ctrl_name])
            # place the zeroOut
        mc.xform(orig_ctrl, t=[high_pos[0], high_pos[1]/10*12, high_pos[2]])
            # creates and set setRange node
        mc.createNode('setRange', n=bend_sr)
        mc.setAttr(bend_sr+'.min', -180, -10, 180, type="double3")
        mc.setAttr(bend_sr+'.max', 180, 10, -180, type="double3")
        mc.setAttr(bend_sr+'.oldMin', -10, -bbox_size[1]*4, -10, type="double3")
        mc.setAttr(bend_sr+'.oldMax', 10, bbox_size[1]*4, 10, type="double3")
            # connects ctrl to SR and SR to nonLinears
        translate_attribute = '.translate'+direction
        mc.connectAttr(bend_ctrl_name+translate_attribute, bend_sr+'.valueX')
        mc.connectAttr(bend_sr+'.outValueX', bend[0]+'.curvature')
        mc.hide(orig_bend)


        # parent to existing hierarchy
        if mc.objExists(ctrl_name):
            mc.parent(orig_bend, orig_ctrl, ctrl_name)
        elif mc.objExists('helper_ctrl'):
            mc.parent(orig_bend, orig_ctrl, 'helper_ctrl')
        else:
            mc.parent(orig_bend, orig_ctrl, 'walk_ctrl')

        if bounds:
            hb_limit_up = float(mid_pos[1]+9*fabs(high_bound_pos[1]))
            hb_limit_down = float(mid_pos[1]-11*fabs(high_bound_pos[1]))
            lb_limit_up = float(mid_pos[1]+9*fabs(low_bound_pos[1]))
            lb_limit_down = float(mid_pos[1]-11*fabs(low_bound_pos[1]))
            # creates bounds pointers
            mlutilities.create_ctrl(ctrl_type='pointer', size=pointer_size, name=high_bound_ctrl, rotation=[180, 0, 0])
            mc.xform(high_bound_ctrl, t=high_bound_pos)
            orig_highbound = orig.orig([high_bound_ctrl])
            mlutilities.create_ctrl(ctrl_type='pointer', size=pointer_size, name=low_bound_ctrl)
            mc.xform(low_bound_ctrl, t=low_bound_pos)
            orig_lowbound = orig.orig([low_bound_ctrl])
            # creates bounds SR and set it
            mc.createNode('setRange', n='bend_bounds_SR')
            mc.setAttr(bend_bounds_sr+'.min', -10, -10, 0, type="double3")
            mc.setAttr(bend_bounds_sr+'.max', 10, 10, 0, type="double3")
            mc.setAttr(bend_bounds_sr+'.oldMin', hb_limit_down, lb_limit_down, 0.0, type="double3")
            mc.setAttr(bend_bounds_sr+'.oldMax', hb_limit_up, lb_limit_up, 0.0, type="double3")
            # connects controllers to SR and SR to nonLinears
            mc.connectAttr(node+'_highBound_ctrl.translateY', bend_bounds_sr+'.valueX')
            mc.connectAttr(bend_bounds_sr+'.outValueX', bend[0]+'.highBound')
            mc.connectAttr(node+'_lowBound_ctrl.translateY', bend_bounds_sr+'.valueY')
            mc.connectAttr(bend_bounds_sr+'.outValueY', bend[0]+'.lowBound')

                # parent to existing hierarchy
            if mc.objExists(bend_ctrl_name):
                mc.parent(orig_highbound, orig_lowbound, ctrl_name)
            elif mc.objExists('helper_ctrl'):
                mc.parent(orig_highbound, orig_lowbound, 'helper_ctrl')
            else:
                mc.parent(orig_highbound, orig_lowbound, 'walk_ctrl')

        i += 1
    mlutilities.rigset()
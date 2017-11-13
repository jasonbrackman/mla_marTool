import maya.cmds as mc

import mla_GeneralPipe.mla_general_utils.mla_name_utils as nu
import mla_MayaPipe.mla_rig_utils.orig as orig
import mla_MayaPipe.mla_rig_utils.mla_Maya_matrix_utils as Mmu

reload(nu)
reload(orig)
reload(Mmu)


def create_edit_crv(selection, crv_dict, name, edit=False, add=False,
                    create_orig=False, axis='x', mirror=(False, False, False)):
    """
    Create or edit curves.

    :param selection: active selection
    :type selection: list

    :param crv_dict: data to create chosen curve
    :type crv_dict: dict

    :param name: name of the curve to create
    :type name: str

    :param edit: edit the selected curves instead of creating new ones
    :type edit: bool

    :param add: add to the selected shape (True) or replace it (False)
    :type add: bool

    :param create_orig:
    :type create_orig:

    :param axis: axis to orient the shape to. Default X.
    :type axis: str

    :param mirror: axis to mirror the shape along. Default none.
    :type mirror: tuple / list

    :return:
    """
    if not name:
        name = 'ctrl'

    crv_list = list()

    # If we are operating on a list of object
    if len(selection) > 0:
        for obj in selection:
            position = mc.xform(obj, q=True, matrix=True, ws=True)

            crv_name = create_crv(crv_dict=crv_dict, name=name)
            Mmu.orient_mirror_shape(crv_name, axis, mirror)

            mc.xform(name, matrix=position, ws=True)

            # If editing the curves
            if edit:
                if add:
                    add = True
                else:
                    add = False

                modify_crv_shape(target=obj, source=name, delete=True, add=add)
            # If creating the curves, create the orig node
            else:
                if create_orig:
                    if 'ctrl' in name:
                        orig_name = orig.orig(nodes=[crv_name])
                    else:
                        orig_name = orig.orig(nodes=[crv_name], replace='')
                    crv_list += (crv_name, orig_name)
                else:
                    crv_list += crv_name
    # If we are just creating a single curve
    else:
        crv_name = create_crv(crv_dict=crv_dict, name=name)
        Mmu.orient_mirror_shape(crv_name, axis, mirror)

        if create_orig:
            if 'ctrl' in name:
                orig_name = orig.orig(nodes=[crv_name])
            else:
                orig_name = orig.orig(nodes=[crv_name], replace='')
            crv_list += (crv_name, orig_name)
        else:
            crv_list += crv_name

    return crv_list


def create_crv(crv_dict, name='ctrl'):
    """
    Create a curve from dict and given name.

    :param crv_dict: data to create chosen curve
    :type crv_dict: dict

    :param name: string to name the curve after
    :type name: str

    :return: curve name
    :rtype: str
    """
    degree = crv_dict['degree']
    points = crv_dict['points']
    knots = crv_dict['knots']

    name = nu.create_name(main_name=name)

    mc.curve(n=name, d=degree, p=points, k=knots)

    return name


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
    # Modify target and source if none provided
    if target == 'None':
        target = mc.ls(sl=True)[0]
    if target == 'None' and source == 'None':
        source = mc.ls(sl=True)[1]
    elif source == 'None':
        source = mc.ls(sl=True)[0]
    else:
        pass

    # Duplicate if you don't want to delete the original source
    if not delete:
        source = mc.duplicate(source)

    # Get the shapes paths
    source_shape = mc.listRelatives(source, c=True, s=True, f=True)
    target_shape = mc.listRelatives(target, c=True, s=True, f=True)

    # Parent the source shape to the target transform
    new_shape_name = mc.parent(source_shape, target, s=True, add=True)
    # Delete the source transform
    mc.delete(source)
    # If not add, delete the target shape
    if not add:
        mc.delete(target_shape)

    mc.rename(new_shape_name, '%sShape1' % target)


def get_crv_info(crv_name):
    """
    Get the degree, points position and knots of a curve.
    :param crv_name: curve to get the information from.
    :type crv_name: str

    :return: degree, points and knots of the curve
    :rtype: dict
    """
    # get the name of the shape of the curve
    crv_shape_name = mc.listRelatives(crv_name, s=True)[0]
    # get the degree, spans and calculate the numbers of CV of the curve
    crv_degree = mc.getAttr(crv_shape_name + '.degree')
    crv_span = mc.getAttr(crv_shape_name + '.spans')
    cv_number = crv_degree + crv_span

    # create a curveInfo node and connect it to the curve
    crv_info = mc.createNode('curveInfo', n=crv_name + '_curveInfo')
    mc.connectAttr(crv_name + '.worldSpace', crv_info + '.inputCurve')

    # get the knots of the curve
    knots = mc.getAttr(crv_info + '.knots')[0]

    # create an empty list for the coordinates of the points of the curve
    points = list()
    # fill the list of points coordinates
    for i in range(0, cv_number):
        point = mc.getAttr(crv_info + '.controlPoints[' + str(i) + ']')
        points.append(point[0])

    mc.delete(crv_info)

    crv_dict = {'degree': crv_degree, 'points': points, 'knots': knots}

    return crv_dict
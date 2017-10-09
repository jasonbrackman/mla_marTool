import maya.cmds as mc
from Python.mla_general_utils.ml_utilities import create_condition


def rivet_to_edge(edges=[], aim=True):
    """
    Create a rivet on one or two edge(s).

    :param edges: flattened list of one or 2 edge(s)
    :type edges: list

    :param aim: specify if the rivet must aim on the edge or not
    :type aim: bool

    :return : name of the new rivet created
    :rtype: str
    """

    rivet_number = 0
    while mc.objExists('rivet%s' % '{0:02d}'.format(rivet_number)):
        rivet_number += 1

    rivet_number = '{0:02d}'.format(rivet_number)

    if len(edges) == 1:

        edge = edges[0]
        obj = edge.split('.')[0]
        edge_idx = edge.split('[')[1].split(']')[0]

        # Create curve
        cfme = mc.createNode('curveFromMeshEdge',
                             n='cfme_rivet%s' % rivet_number)
        mc.connectAttr('%s.worldMesh[0]' % obj, '%s.inputMesh' % cfme)
        mc.setAttr('%s.edgeIndex[0]' % cfme, int(edge_idx))

        # Create point
        poci = mc.createNode('pointOnCurveInfo',
                             n='poci_rivet%s' % rivet_number)
        mc.connectAttr('%s.outputCurve' % cfme, '%s.inputCurve' % poci)

        # Create rivet and attach it
        rivet = mc.createNode('transform', n='rivet%s' % rivet_number)
        mc.addAttr(rivet, ln='parameter', at='double', dv=1.5)
        mc.connectAttr('%s.parameter' % rivet, '%s.parameter' % poci)
        mc.connectAttr('%s.position' % poci, '%s.translate' % rivet)

        # If aim, create aim ct
        if aim:
            aim = mc.createNode('aimConstraint', n='rivet%s_aim' % rivet_number,
                                p=rivet)
            mc.connectAttr('%s.normal' % poci,
                           '%s.target[0].targetTranslate' % aim)
            mc.connectAttr('%s.tangent' % poci, '%s.worldUpVector' % aim)

            mc.connectAttr('%s.constraintRotateX' % aim, '%s.rotateX' % rivet)
            mc.connectAttr('%s.constraintRotateY' % aim, '%s.rotateY' % rivet)
            mc.connectAttr('%s.constraintRotateZ' % aim, '%s.rotateZ' % rivet)
        return rivet

    elif len(edges) == 2:
        cfme = list()
        i = 0

        # Create curves
        for edge in edges:
            obj = edge.split('.')[0]
            edge_idx = edge.split('[')[1].split(']')[0]

            cfme.append(mc.createNode('curveFromMeshEdge',
                                      n='cfme%s_rivet%s' % (i+1, rivet_number)))
            mc.connectAttr('%s.worldMesh[0]' % obj, '%s.inputMesh' % cfme[i])
            mc.setAttr('%s.edgeIndex[0]' % cfme[i], int(edge_idx))
            i += 1

        # Create surface and get info
        loft = mc.createNode('loft', n='loft_rivet%s' % rivet_number)
        mc.connectAttr('%s.outputCurve' % cfme[0], '%s.inputCurve[0]' % loft)
        mc.connectAttr('%s.outputCurve' % cfme[1], '%s.inputCurve[1]' % loft)

        posi = mc.createNode('pointOnSurfaceInfo', 'pointOnSurfaceInfo_rivet%s'
                             % rivet_number)
        mc.connectAttr('%s.outputSurface' % loft, '%s.inputSurface' % posi)

        # Create rivet and attach it
        rivet = mc.createNode('transform', n='rivet%s' % rivet_number)
        mc.addAttr(rivet, ln='parameterU', at='double', dv=0.5)
        mc.addAttr(rivet, ln='parameterV', at='double', dv=0.5)
        mc.connectAttr('%s.parameterU' % rivet, '%s.parameterU' % posi)
        mc.connectAttr('%s.parameterV' % rivet, '%s.parameterV' % posi)
        mc.connectAttr('%s.position' % posi, '%s.translate' % rivet)

        # If aim, create aim ct
        if aim:
            mc.addAttr(rivet, ln='tangent', at='enum', en='U:V', dv=0)
            aim = mc.createNode('aimConstraint', n='rivet%s_aim' % rivet_number,
                                p=rivet)
            mc.connectAttr('%s.normal' % posi,
                           '%s.target[0].targetTranslate' % aim)

            mc.connectAttr('%s.constraintRotateX' % aim, '%s.rotateX' % rivet)
            mc.connectAttr('%s.constraintRotateY' % aim, '%s.rotateY' % rivet)
            mc.connectAttr('%s.constraintRotateZ' % aim, '%s.rotateZ' % rivet)

            # Condition
            create_condition('cond_rivet%s' % rivet_number,
                             first_term='%s.tangent' % rivet,
                             second_term=1.0,
                             cit_r='%s.tangentUx' % posi,
                             cit_g='%s.tangentUy' % posi,
                             cit_b='%s.tangentUz' % posi,
                             cif_r='%s.tangentVx' % posi,
                             cif_g='%s.tangentVy' % posi,
                             cif_b='%s.tangentVz' % posi,
                             out_color_r='%s.worldUpVectorX' % aim,
                             out_color_g='%s.worldUpVectorY' % aim,
                             out_color_b='%s.worldUpVectorZ' % aim,)

        return rivet

    else:
        print 'Invalid parameter : must provide one or two edge(s)'
        return


def rivet_to_curve(curve_point='', aim=True):
    """
    Create a rivet on a curve point.

    :param curve_point: curve point name
    :type curve_point: string

    :param aim: specify if the rivet must aim on the edge or not
    :type aim: bool

    :return : name of the new rivet created
    :rtype: str
    """

    rivet_number = 0
    while mc.objExists('rivet%s' % '{0:02d}'.format(rivet_number)):
        rivet_number += 1

    rivet_number = '{0:02d}'.format(rivet_number)

    cp = curve_point
    obj = cp.split('.')[0]
    cp_val = float(cp.split('[')[1].split(']')[0])

    # Create sub curve
    sub_curve = mc.createNode('subCurve', n='subCurve_rivet%s' % rivet_number)
    mc.connectAttr('%s.worldSpace[0]' % obj, '%s.inputCurve' % sub_curve)

    # Create point
    poci = mc.createNode('pointOnCurveInfo',
                         n='poci_rivet%s' % rivet_number)
    mc.connectAttr('%s.outputCurve' % sub_curve, '%s.inputCurve' % poci)

    # Create rivet and attach it
    rivet = mc.createNode('transform', n='rivet%s' % rivet_number)
    mc.addAttr(rivet, ln='parameter', at='double', dv=cp_val)
    mc.connectAttr('%s.parameter' % rivet, '%s.parameter' % poci)
    mc.connectAttr('%s.position' % poci, '%s.translate' % rivet)

    # If aim, create aim ct
    if aim:
        aim = mc.createNode('aimConstraint', n='rivet%s_aim' % rivet_number,
                            p=rivet)
        mc.connectAttr('%s.normal' % poci,
                       '%s.target[0].targetTranslate' % aim)
        mc.connectAttr('%s.tangent' % poci, '%s.worldUpVector' % aim)

        mc.connectAttr('%s.constraintRotateX' % aim, '%s.rotateX' % rivet)
        mc.connectAttr('%s.constraintRotateY' % aim, '%s.rotateY' % rivet)
        mc.connectAttr('%s.constraintRotateZ' % aim, '%s.rotateZ' % rivet)
    return rivet

def rivet_to_surface(surface_point='', aim=True):
    """
    Create a rivet on a curve point.

    :param surface_point: surface point name
    :type surface_point: string

    :param aim: specify if the rivet must aim on the edge or not
    :type aim: bool

    :return : name of the new rivet created
    :rtype: str
    """
    cfme = list()
    i = 0

    rivet_number = 0
    while mc.objExists('rivet%s' % '{0:02d}'.format(rivet_number)):
        rivet_number += 1

    rivet_number = '{0:02d}'.format(rivet_number)

    sp = surface_point
    obj = sp.split('.')[0]
    sp_u_val = float(sp.split('[')[1].split(']')[0])
    sp_v_val = float(sp.split('[')[2].split(']')[0])

    # Create and connect pointOnSurfaceInfo

    posi = mc.createNode('pointOnSurfaceInfo', 'pointOnSurfaceInfo_rivet%s'
                         % rivet_number)
    mc.connectAttr('%s.worldSpace[0]' % obj, '%s.inputSurface' % posi)

    # Create rivet and attach it
    rivet = mc.createNode('transform', n='rivet%s' % rivet_number)
    mc.addAttr(rivet, ln='parameterU', at='double', dv=sp_u_val)
    mc.addAttr(rivet, ln='parameterV', at='double', dv=sp_v_val)
    mc.connectAttr('%s.parameterU' % rivet, '%s.parameterU' % posi)
    mc.connectAttr('%s.parameterV' % rivet, '%s.parameterV' % posi)
    mc.connectAttr('%s.position' % posi, '%s.translate' % rivet)

    # If aim, create aim ct
    if aim:
        mc.addAttr(rivet, ln='tangent', at='enum', en='U:V', dv=0)
        aim = mc.createNode('aimConstraint', n='rivet%s_aim' % rivet_number,
                            p=rivet)
        mc.connectAttr('%s.normal' % posi,
                       '%s.target[0].targetTranslate' % aim)

        mc.connectAttr('%s.constraintRotateX' % aim, '%s.rotateX' % rivet)
        mc.connectAttr('%s.constraintRotateY' % aim, '%s.rotateY' % rivet)
        mc.connectAttr('%s.constraintRotateZ' % aim, '%s.rotateZ' % rivet)

        # Condition
        create_condition('cond_rivet%s' % rivet_number,
                         first_term='%s.tangent' % rivet,
                         second_term=1.0,
                         cit_r='%s.tangentUx' % posi,
                         cit_g='%s.tangentUy' % posi,
                         cit_b='%s.tangentUz' % posi,
                         cif_r='%s.tangentVx' % posi,
                         cif_g='%s.tangentVy' % posi,
                         cif_b='%s.tangentVz' % posi,
                         out_color_r='%s.worldUpVectorX' % aim,
                         out_color_g='%s.worldUpVectorY' % aim,
                         out_color_b='%s.worldUpVectorZ' % aim,)

    return rivet

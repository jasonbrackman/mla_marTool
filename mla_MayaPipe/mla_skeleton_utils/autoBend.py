# --------------By MARTIN L'ANTON--------------
# ---------------------------------------------
# -----------------------------------
# --HOW TO USE IT--------------------
# -----------------------------------
# Select all the curves you need to be dynamic, then the curve you want to use
# as controller for your clusters, and run the scripts, then you just have to
# specify the number of bones you want.
# -----------------------------------
import maya.cmds as mc

from Python.mla_rig_utils import orig as orig


def manual_bend_chain(controller, curves):
    """Create a stretchable and bendable chain of bones on a curve"""

    if not controller or not curves:
        selection = mc.ls(sl=True, fl=True)
        controller = selection[-1]
        curves = selection[:-1]

    # dialog box
    result = mc.promptDialog(title='Number of bones',
                             message='Type the number of bones that you want on'
                                     ' your curve(s)',
                             button=['OK', 'Cancel'],
                             defaultButton='OK',
                             cancelButton='Cancel',
                             dismissString='Cancel')
    
    if result == 'OK':
        bones_nbr = mc.promptDialog(query=True, text=True)
        
    else:
        mc.confirmDialog(title='Confirm',
                         message='You have to type a number of bone(s)',
                         button=['Yes'],
                         defaultButton='Yes')
        return
    
    bones_nbr = int(bones_nbr)
    
    for crv in curves:
        bend_chain(crv, controller, bones_nbr)


def bend_chain(crv, controller, bones_nbr):
    jnt_nbr = bones_nbr + 1
    # get shape
    crv_shape = mc.listRelatives(crv, c=True, s=True)[0]

    # calculation of the number of cv
    crv_degree = mc.getAttr(crv_shape + '.degree')
    crv_span = mc.getAttr(crv_shape + '.spans')

    cv_nbr = crv_degree + crv_span

    # place curve pivot on first cv
    crv_info = mc.createNode('curveInfo', n=crv + '_curveInfo')
    mc.connectAttr(crv_shape + '.worldSpace', crv_info + '.inputCurve')

    cv_tx = mc.getAttr(crv_info + '.controlPoints[0].xValue')
    cv_ty = mc.getAttr(crv_info + '.controlPoints[0].yValue')
    cv_tz = mc.getAttr(crv_info + '.controlPoints[0].zValue')
    mc.xform(crv, piv=(cv_tx, cv_ty, cv_tz), ws=True)

    # Stretch creation
    mult = mc.shadingNode('multiplyDivide', asUtility=True,
                          name='multiplyDivide_STRETCH_' + crv)
    mc.connectAttr('%s.arcLength' % crv_info, '%s.input1X' % mult)
    crv_length = mc.getAttr(crv_info + '.arcLength')
    mc.setAttr(mult + '.input2X', crv_length)
    mc.setAttr(mult + '.operation', 2)

    # Joint chain creation
    jnt_length = crv_length / bones_nbr
    first_jnt = mc.joint(p=(cv_tx, cv_ty, cv_tz), name='SK_' + crv + '_0')

    for i in range(1, jnt_nbr):
        i = str(i)
        current_jnt = mc.joint(p=(jnt_length, 0, 0), r=True,
                               name='SK_' + crv + '_' + i)
        mc.connectAttr(mult + '.outputX',
                       current_jnt + '.scaleX')

    # ikSpline creation
    ik = 'IKSPLINE_' + crv
    mc.ikHandle(curve=crv, ee='SK_' + crv + '_' + str(bones_nbr),
                sol='ikSplineSolver', sj=first_jnt,
                name=ik, ccv=0)
    jnt_rotation = mc.xform(first_jnt, q=True, ro=True)

    # Orig joint
    orig.orig([first_jnt], 'orig')

    # offset de l'ik
    orig.orig([ik], 'orig')

    for j in range(0, cv_nbr):
        # Creation des clusters :)

        cls_nbr = str(j)
        cv = (crv + '.cv[' + cls_nbr + ']')

        mc.select(cv)
        cluster = mc.cluster()
        mc.select(deselect=True)

        # Recuperation de la position des clusters
        cls_pos_x = mc.getAttr('%s.controlPoints[%s].xValue'
                               % (crv_info, cls_nbr))
        cls_pos_y = mc.getAttr('%s.controlPoints[%s].yValue'
                               % (crv_info, cls_nbr))
        cls_pos_z = mc.getAttr('%s.controlPoints[%s].zValue'
                               % (crv_info, cls_nbr))

        # Controllers creation
        ctrl = mc.duplicate(controller, name='%s_%s_ctrl' % (crv, cls_nbr))
        ctrl = mc.rename(ctrl, '%s_%s_ctrl' % (crv, cls_nbr))
        mc.xform(ctrl, t=(cls_pos_x, cls_pos_y, cls_pos_z), ws=True)
        mc.xform(ctrl, ro=jnt_rotation)

        # Controllers orig
        orig.orig([ctrl], 'orig')

        # Cluster hierarchy

        mc.parent(cluster, ctrl)

    mc.select('%s_*_ctrl_orig' % crv)
    mc.group(name='%s_ctrl_grp' % crv)
    mc.select(deselect=True)

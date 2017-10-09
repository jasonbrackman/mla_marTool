import maya.cmds as mc

def orig(nodes=list(), suffix='orig'):
    """create a zero group.
    :param nodes: names of the node to offset (list)
    :type nodes: list

    :return: name of the orig
    :rtype: str
    """
    orig_grp = ''
    for obj in nodes:
        node_parent = mc.listRelatives(obj, p=True)
        orig_grp = mc.group(em=True, name='%s_%s' % (obj, suffix))
        constraint = mc.parentConstraint(obj, orig_grp, mo=False)
        mc.delete(constraint)
        if node_parent:
            mc.parent(orig_grp, node_parent)
        mc.parent(obj, orig_grp)

    return orig_grp

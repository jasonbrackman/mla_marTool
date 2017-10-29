import maya.cmds as mc


def orig(nodes=list(), suffix='orig', replace='ctrl'):
    """create a zero group.
    :param nodes: names of the node to offset (list)
    :type nodes: list

    :param suffix: string to add at the end of the group name
    :type suffix: str

    :param replace: if specified, replace the given string from the node with
    the suffix
    :type replace: str

    :return: name of the orig
    :rtype: str
    """
    if not nodes:
        nodes = mc.ls(sl=True)

    orig_grp = ''
    for obj in nodes:
        node_parent = mc.listRelatives(obj, p=True)
        if replace != '':
            orig_name = obj.replace(replace, suffix)
        else:
            orig_name = '%s_%s' % (obj, suffix)
        orig_grp = mc.group(em=True, name=orig_name)
        constraint = mc.parentConstraint(obj, orig_grp, mo=False)
        mc.delete(constraint)
        if node_parent:
            mc.parent(orig_grp, node_parent)
        mc.parent(obj, orig_grp)

    return orig_grp

import maya.cmds as mc


def add_blendshape_target(targets, blendshape_node):
    """
    Add blendShape target(s) to the specified blendShape node (see ui).
    :param targets: target(s) to add to the given blendShape node
    :type targets: list

    :param blendshape_node: blendShape node to add the target(s) to
    :type blendshape_node: str
    """
    # --- Get base
    base = get_blendshape_base(blendshape_node)

    # --- Define new index ------------------------------
    # --- Get the weight and their indices
    target_per_index = mc.aliasAttr(blendshape_node, query=True)
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

    # --- Sort the indices by numerical order,
    # so the last one of the list is actually the higher index
    indices_list.sort()
    # --- Increment 1 to create the new index
    last_index = indices_list[-1]
    new_index = last_index + 1
    # --- Add all the targets to the blendShape node.
    # Increment index by 1 for every target it adds
    for target in targets:
        mc.blendShape(blendshape_node, e=True,
                      target=(base, new_index, target, 1.0))
        new_index += 1


def get_blendshape_base(blendshape_node):
    """
    Get blendShape base
    :rtype : string
    :return: str(base)
    """
    # --- Get base
    history = mc.listHistory(blendshape_node, future=True, leaf=True)
    shape = mc.ls(history, type=('mesh', 'nurbsSurface', 'nurbsCurve'))
    base = mc.listRelatives(shape,
                            fullPath=True,
                            parent=True,
                            type='transform')[0]
    return base
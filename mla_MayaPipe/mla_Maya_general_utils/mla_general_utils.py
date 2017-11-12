import maya.cmds as mc


def check_obj_exists(obj_name):
    """
    Check if an object exists

    :param obj_name: name of the object to check
    :type obj_name: str

    :return: whether the object exists or not
    :rtype: bool
    """
    if mc.objExists(obj_name):
        return True
    else:
        return False


def rename(obj, name):
    """
    Rename the given object with the given name.

    :param obj: object to rename
    :type obj: str

    :param name: name to give to the object
    :type name: str

    :return: new name of the object
    :rtype: str
    """
    name = mc.rename(obj, name)
    return name


def get_selection():
    """
    Get active selection and return it.

    :return: active selection
    :rtype : list
    """
    selection = mc.ls(sl=True, fl=True)
    return selection


def open_undo_chunk():
    mc.undoInfo(openChunk=True)


def close_undo_chunk():
    mc.undoInfo(closeChunk=True)

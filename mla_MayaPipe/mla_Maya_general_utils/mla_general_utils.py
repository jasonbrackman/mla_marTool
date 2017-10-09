import maya.cmds as mc


def check_obj_exists(objname):
    """
    Check if an object exists

    :param objname: name of the object to check
    :type objname: str

    :return: whether the object exists or not
    :rtype: bool
    """
    if mc.objExists(objname):
        return True
    else:
        return False
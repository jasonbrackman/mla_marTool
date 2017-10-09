import maya.cmds as mc
import mla_GeneralPipe.mla_general_utils.mla_name_utils as nu

reload(nu)


def rename(obj_list=[], side='', main_name='', digits='##', suffix=''):
    """
    
    :param obj_list:
    :type obj_list: list
    
    :param side:
    :type side: str
    
    :param main_name:
    :type main_name: str
    
    :param digits:
    :type digits: str
    
    :param suffix:
    :type suffix: str
    
    :return: 
    """
    inc_nbr = 0

    for obj in obj_list:
        inc_nbr += 1
        increm = nu.create_increment(inc_nbr, len(digits))

        name = '%s_%s_%s_%s' % (side, main_name, increm, suffix)
        while mc.objExists(name):
            inc_nbr += 1
            increm = nu.create_increment(inc_nbr, len(digits))
            name = '%s_%s_%s_%s' % (side, main_name, increm, suffix)

        mc.rename(obj, name)

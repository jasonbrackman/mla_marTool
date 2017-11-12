import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as Miu
import re

reload(Miu)

application = Miu.get_application()

if application == 'Maya':
    import mla_MayaPipe.mla_Maya_general_utils.mla_general_utils as gu
elif application == 'Max':
    # TODO : create this one!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    import mla_MaxPipe.mla_Max_general_utils.mla_general_utils as gu


def rename(obj_list=[], prefix=None, main_name=None, suffix=None, search=None,
           replace=None):
    """

    :param obj_list: Objects to rename
    :type obj_list: list

    :param prefix: prefix of the name
    :type prefix: str

    :param main_name: main part of the name
    :type main_name: str

    :param suffix: suffix of the name
    :type suffix: str

    :param search: string to look for and replace
    :type search: str

    :param replace: str to replace the searched part with
    :type replace: str

    :return:
    """
    gu.open_undo_chunk()

    inc_nbr = 1

    obj_new_names = list()

    for obj in obj_list:
        if not main_name:
            main_part = obj
        else:
            main_part = main_name

        new_name = create_name(prefix, main_part, suffix, search, replace)

        obj_new_names.append(new_name)

        gu.rename(obj, new_name)

    gu.close_undo_chunk()

    return obj_new_names


def get_opposite_name(obj):
    """
    Get the name of the opposite object (same name, on the other side).

    :param obj: Name of the object which you want to find the opposite
    :type obj: str

    :return: name of the opposite object
    :rtype: str
    """

    if obj.startswith('l_'):
        opposite_name = obj.replace('l_', 'r_')
    elif obj.startswith('r_'):
        opposite_name = obj.replace('r_', 'l_')
    elif obj.startswith('L_'):
        opposite_name = obj.replace('L_', 'R_')
    elif obj.startswith('R_'):
        opposite_name = obj.replace('R_', 'L_')
    elif obj.startswith('left_'):
        opposite_name = obj.replace('left_', 'right_')
    elif obj.startswith('right_'):
        opposite_name = obj.replace('right_', 'left_')
    elif obj.startswith('LEFT_'):
        opposite_name = obj.replace('LEFT_', 'RIGHT_')
    elif obj.startswith('RIGHT_'):
        opposite_name = obj.replace('RIGHT_', 'LEFT_')
    elif '_l_' in obj:
        opposite_name = obj.replace('_l_', '_r_')
    elif '_r_' in obj:
        opposite_name = obj.replace('_r_', '_l_')
    elif '_L_' in obj:
        opposite_name = obj.replace('_L_', '_R_')
    elif '_R_' in obj:
        opposite_name = obj.replace('_R_', '_L_')
    elif '_left_' in obj:
        opposite_name = obj.replace('_left_', '_right_')
    elif '_right_' in obj:
        opposite_name = obj.replace('_right_', '_left_')
    elif '_LEFT_' in obj:
        opposite_name = obj.replace('_LEFT_', '_RIGHT_')
    elif '_RIGHT_' in obj:
        opposite_name = obj.replace('_RIGHT_', '_LEFT_')
    else:
        opposite_name = obj

    return opposite_name


def create_increment(number=0, digits=2):
    """
    Convert hash characters (##) into a number of digits :
    ex: create_increment(number=24, digits=4) = '0024'
        create_increment(number=753, digits=4) = '0753'
        create_increment(number=2, digits=2) = '02'
    
    :param number: number to convert into digits
    :type number: int, str
    
    :param digits: str too convert to digits
    :type digits: int

    :return: incremented number
    :rtype: str
    """
    if type(number) == str:
        number = int(number)

    return format(number, '0%sd' % digits)


def create_name(prefix=None, main_name=None, suffix=None, search=None,
                replace=None):
    """
    Create a name with prefix, main part, suffix, search and replace.

    :param prefix: prefix of the name
    :type prefix: str

    :param main_name: main part of the name
    :type main_name: str

    :param suffix: suffix of the name
    :type suffix: str

    :param search: string to search for
    :type search: str

    :param replace: string to replace the searched part with
    :type replace: str

    :return:
    """
    full_name = main_name
    if prefix and type(prefix) == str:
        full_name = prefix + full_name
    if suffix and type(suffix) == str:
        full_name = full_name + suffix

    digit_pattern = re.findall('(#+)', full_name)
    if digit_pattern:
        inc_nbr = 0
        digit_pattern = digit_pattern[0]
        digit_number = len(digit_pattern)

        while gu.check_obj_exists(full_name.replace(digit_pattern, create_increment(inc_nbr, digit_number))):
            inc_nbr += 1

        new_name = full_name.replace(digit_pattern, create_increment(inc_nbr, digit_number))
    else:
        new_name = full_name

    if search:
        if not replace:
            replace = ''
        new_name = new_name.replace(search, replace)

    return new_name

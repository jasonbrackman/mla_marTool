import pymxs as mxs
import mla_GeneralPipe.mla_general_utils.mla_name_utils as nu

reload(nu)


def move_from_ui(data):
    """
    Use move function using ui's data
    :return:
    """
    pass


def move_even_from_ui(data):
    """
    Use move_transform function using ui's data
    :return:
    """
    pass


def move_even(obj_list=(), translate=('x', 'y', 'z'),
              rotate=('x', 'y', 'z'), scale=(),
              world_space=True, mirror=False, mirror_axis='x',
              behavior=False):
    """
    Call the move function by even
    :param obj_list: list of objects to move by pair
    :type obj_list: list

    :param translate: tuple of translate channel to move
    :type translate: tuple

    :param rotate: tuple of rotate channel to move
    :type rotate: tuple

    :param scale: tuple of scale channel to move
    :type scale: tuple

    :param world_space: world space by default, object space if False
    :type world_space: boolean

    :param mirror: mirror state
    :type mirror: boolean

    :param mirror_axis: mirror axis
    :type mirror_axis: str

    :param behavior: mirroring behavior/orientation
    :type behavior: boolean

    :return:
    """
    pass

def move(source_target=(), translate=('x', 'y', 'z'),
         rotate=('x', 'y', 'z'), scale=(),
         world_space=True, mirror=False, mirror_axis='x',
         behavior=False):
    """
    Move an object according to another object's coordinates, to snap or
    mirror position, in world or object space, using a specified mirror
    axis.

    :param source_target: couple source/target
    :type source_target: list

    :param translate: tuple of translate channel to move
    :type translate: tuple

    :param rotate: tuple of rotate channel to move
    :type rotate: tuple

    :param scale: tuple of scale channel to move
    :type scale: tuple

    :param world_space: world space by default, object space if False
    :type world_space: boolean

    :param mirror: mirror state
    :type mirror: boolean

    :param mirror_axis: mirror axis
    :type mirror_axis: str

    :param behavior: mirroring behavior/orientation
    :type behavior: boolean

    :return:
    """
    pass


def constrain_from_ui(data):
    """
    Create a constraint using ui's data
    :return:
    """
    pass


def constrain_even_from_ui(data):
    """
    Call constrain function by even using ui's data
    :return:
    """
    pass


def constrain(constraint_type='Parent constraint', targets='', source='',
              aim_vector=(1, 0, 0), up_vector=(0, 1, 0),
              maintain_offset=True, skip=((), (), ()), ct_name=''):
    """
    Create a constraint of the specified type on specified objects. If
    either sources or target are missing, it uses the current selection.

    :param constraint_type: type of the constraint you want to create.
    :type constraint_type: str

    :param targets: objects constraining
    :type targets: list

    :param source: object constrained
    :type source: str

    :param aim_vector: vector used to aim
    :type aim_vector: tuple

    :param up_vector: vector used as up
    :type up_vector: tuple

    :param maintain_offset: specify if current offset must be maintained
    :type maintain_offset: bool

    :param skip: axes to skip when constraining ((trans), (rot), (scale))
    :type skip: tuple

    :param ct_name: name of the newly created constraint
    :type ct_name: str

    :return:
    """
    pass


def mirror_constraint(constraints=()):
    """
    Mirror the given constraints

    :param constraints: names of the constraints to duplicate
    :type constraints: list

    :return: names of the newly created constraints
    :rtype: list
    """

import mla_Multi_import_utils as Multi_import_utils
reload(Multi_import_utils)

application, mc, api = Multi_import_utils.import_from_application()


def get_current_scene_path(extended=True):
    """
    Get the path of currently opened scene
    :param extended: defines if we want the file extension included in the path.
    :type extended: bool

    :return: path to the currently opened scene
    :rtype: str
    """
    if application == 'Maya':
        path = '%s' % mc.file(q=True, exn=extended)
    elif application == 'Max':
        path = None
    else:
        path = None

    return path
import os
import maya.cmds as mc
import mla_file_library as fl
import mla_path_utils as path_utils
reload(fl)
DEFAULT_PROJECT_PATH = 'D:/BOULOT/TRAVAUX_PERSO/MAYA PROJECTS'


# TODO
def set_current_project_directory(project):
    """
    Set maya project in the current selected project.

    :param project: project to set maya to
    :type project: str
    """
    # Build path
    proj_path = path_utils.build_path(project=project, return_type='project')
    # Set current directory
    mc.workspace(dir=proj_path)

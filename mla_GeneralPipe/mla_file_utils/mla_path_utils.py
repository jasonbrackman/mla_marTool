import logging
import os

MAYA_PROJECT_PATH = 'D:/BOULOT/TRAVAUX_PERSO/MAYA PROJECTS'
MAX_PROJECT_PATH = 'D:/BOULOT/TRAVAUX_PERSO/3DSMAX PROJECTS'


def build_path(project, scenes_sound='', asset_anim='', asset_type='', asset='',
               task='', filename='', return_type='project'):
    """
    Build path from given data.
    
    :param project: project to create path with
    :type project: str

    :param scenes_sound: type of scene or file to look for
    :type scenes_sound: str

    :param asset_anim: type of asset or animation to look for
    :type asset_anim: str
    
    :param asset_type: type to look for
    :type asset_type: str
    
    :param asset: asset to look for
    :type asset: str
    
    :param task: task to look for
    :type task: str
    
    :param filename: file to look for
    :type filename: str
    
    :param return_type: defines what type of path we want to output
    :type return_type: str
    
    :return: path to selected task/file
    :rtype: str
    """

    logging.info(filename)
    # Build project path
    if return_type == 'project':
        return_path = '%s/%s' % (MAYA_PROJECT_PATH, project)

    elif return_type == 'directory':
        return_path = '%s/%s/%s/%s/%s/%s/%s' % (MAYA_PROJECT_PATH,
                                                project, scenes_sound,
                                                asset_anim, asset_type, asset,
                                                task)

    # Build file path
    elif return_type == 'file':
        return_path = '%s/%s/%s/%s/%s/%s/%s/%s' % (MAYA_PROJECT_PATH,
                                                   project, scenes_sound,
                                                   asset_anim, asset_type,
                                                   asset, task, filename)

    # Build wip path
    elif return_type == 'wip':
        if filename == 'No file in this directory' \
                or filename == '' \
                or len(filename.split('_')) != 4 \
                or build_increment(filename.split('_')[3]):
            wip_file = '%s_%s_%s_00.ma' % (asset_type, asset, task)
        else:
            # Split file name
            wip_file = filename.split('.')[0]
            logging.debug(wip_file)
            wip_file = wip_file.split('_')
            logging.debug(wip_file)
            # Increment version number
            wip_file[3] = build_increment(wip_file[3])
            logging.debug(wip_file[3])
            # Join publish file name
            wip_file = '_'.join(wip_file)
            logging.debug(wip_file)
        # Build path
        return_path = '%s/%s/%s/%s/%s/%s/%s/%s' % (MAYA_PROJECT_PATH,
                                                   project, scenes_sound,
                                                   asset_anim, asset_type,
                                                   asset, task, wip_file)

    # Build publish path
    else:
        # Split file name
        publish_file = filename.split('_')
        # Remove increment and extension
        publish_file = publish_file[:3]
        logging.debug(publish_file)
        # Append PUBLISH plus extension
        publish_file.append('PUBLISH.ma')
        logging.debug(publish_file)
        # Join publish file name
        publish_file = '_'.join(publish_file)
        logging.debug(publish_file)
        # Build path
        return_path = '%s/%s/%s/%s/%s/%s/%s' % (MAYA_PROJECT_PATH,
                                                project, scenes_sound,
                                                asset_anim, asset_type, asset,
                                                publish_file)

    # print return_path
    return return_path


# TODO : remove this
def build_increment(number, digits=3):
    """
    Increment the given number and return it as a 2 decimal string (ie : 01, 02, etc.)
    :param number: number you want to increment
    :type number: str

    :param digits: number of digits the string should contain in total
    :type digits: int

    :return: incremented number
    :rtype: str
    """
    try:
        # Set it as an integer
        increment = int(number)
        # Increment
        increment += 1
        # List it
        increment = str(increment).zfill(digits)

    except ValueError:
        increment = None
        logging.error('"%s" is not a number' % number)

    return increment


def create_subdir_list(given_path):
    """
    create list of the subdirectories in the given directory
    
    :param given_path: directory to list subdirectories in
    :type given_path: str
    
    :return: list of the subdirectories
    :rtype: list
    """
    # print 'Listing sub directories in %s' % given_path
    # List all the directories at the given path
    subdir_list = [sub_path for sub_path in os.listdir(given_path)
                   if os.path.isdir(given_path+'/'+sub_path)]

    # Removing mayaSwatches, keyboard and edits
    subdir_list = [directory for directory in subdir_list
                   if directory != '.mayaSwatches'
                   and directory != 'Keyboard'
                   and directory != 'edits']

    # Returning list
    return subdir_list


def build_files_list(given_path):
    """
    Create a list of all the files in the given directory
    
    :param given_path: path to the directory you want to list the files in
    :type given_path: str
    
    :return: all the files in that directory
    :rtype: list
    """
    # Set current directory to the given path
    os.chdir(given_path)
    # Filter files
    files = [dir_file for dir_file in os.listdir(given_path)
             if os.path.isfile(os.path.join(given_path, dir_file))]
    # Filter maya files
    maya_files = [maya_file for maya_file in files
                  if '.ma' in maya_file
                  or '.mb' in maya_file
                  or '.fbx' in maya_file]
    # If no maya files
    if not maya_files:
        # list is used as verbose
        maya_files = ['No file in this directory']
    # If there are maya files
    else:
        # Sort them
        maya_files.sort(key=lambda x: os.path.getmtime(x))
        # Get most recent in first
        maya_files.reverse()

    return maya_files


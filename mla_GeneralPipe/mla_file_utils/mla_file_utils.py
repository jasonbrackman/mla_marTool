import glob
import json
import logging
import os
import shutil
import stat
from collections import OrderedDict

import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as import_utils

application, mc, api = import_utils.import_from_application()


class FileSystem(object):
    """
    Class to centralize files manipulation.
    """

    @staticmethod
    def find_in_upper_folders(search_root, filename):
        # Conform Path
        search_root = os.path.realpath(search_root)
        # Search for
        found_file_path = glob.glob(os.path.join(search_root, filename))
        # If found
        if found_file_path:
            # Return
            return found_file_path[0]
        # Not found, go up, recurse
        return FileSystem.find_in_upper_folders(os.path.dirname(search_root),
                                                filename)

    @staticmethod
    def mkdir(dirpath):
        """Create Directory Tree if it does not exist"""
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    @staticmethod
    def load_from_json(filename):
        """
        Load content of given json file into python object.
        :param filename: path/name of the file to load
        :type filename: str

        :return: content of the file
        :rtype: OrderedDict
        """
        # Parse
        filename = FileSystem.normpath(filename)
        # If Exists
        if filename:
            # Verbose
            logging.info('Load from %s' % filename)
            # Open file
            with open(filename, 'r') as file_json:
                # Load and return
                return json.load(file_json, object_pairs_hook=OrderedDict)

    @staticmethod
    def save_to_json(python_object, filename):
        """
        Dump python object into json file
        :param python_object: object to dump
        :type python_object: object

        :param filename: path of the file to save
        :type filename: str
        """
        # Normpath
        filename = FileSystem.normpath(filename, False, True)
        # Verbose
        logging.info('Save to   %s' % filename)
        # Make Folder if doesn't exists
        FileSystem.mkdir(os.path.dirname(filename))
        # Open File
        with open(filename, 'w+') as file_json:
            # Scan
            json.dump(python_object, file_json, sort_keys=True, indent=4,
                      separators=(',', ': '))

    @staticmethod
    def copy_file(path_source, path_destination):
        """
        Copy a file and create and create tree and/or file if necessary.
        :param path_source: path of the file to copy
        :type path_source: str

        :param path_destination: path where to copy the file
        :type path_destination: str

        :return:-1 if an empty file is created
        """
        # If source is different from destination
        if path_source is not path_destination:
            # If source exists
            if os.path.isfile(path_source):
                # If path does not exists
                if not os.path.exists(os.path.dirname(path_destination)):
                    # Create
                    os.makedirs(os.path.dirname(path_destination))
                # Verbose
                logging.info('Copying %s' % os.path.normpath(path_source))
                logging.info('     -> %s' % os.path.normpath(path_destination))
                # Try
                try:
                    # Delete if destination exists
                    FileSystem.delete_if_exists(path_destination)
                    # Copy
                    shutil.copy(path_source, path_destination)
                    # Set Readonly
                    os.chmod(path_destination, stat.S_IREAD)
                    # Success
                    return True
                # Error
                except:
                    # Verbose
                    logging.warn('Error Copying file !')
                    # Failure
                    return False
            # Si la source n'exsite pas
            else:
                # Verbose
                logging.info('Source File doesnt exists %s' % path_source)
                logging.info('Creating Empty File       %s' % path_destination)
                # Try
                try:
                    # Create an empty file
                    with open(path_destination, 'w+'):
                        pass
                    # Return
                    return True
                # Error
                except:
                    # Verbose
                    logging.warn('Error Creating file !')
                    # Failure
                    return False
        # Failure
        return False

    @staticmethod
    def delete_if_exists(filepath):
        """
        :param filepath: path of the file to delete
        :type filepath: str
        :return:
        """
        # If file exists
        if os.path.isfile(filepath):
            # Remove Attributes
            os.chmod(filepath, stat.S_IWRITE)
            # Remove File
            os.remove(filepath)
            # Verbose
            logging.info('Removed %s' % filepath)
            # Return
            return True
        # Return
        return False

    @staticmethod
    def normpath(filepath, must_exist=True, parse_env_vars=True):
        """
        Normalize a path
        :param filepath: path to normalize
        :type filepath: str

        :param must_exist: specify if the path must exist or not
        :type must_exist: bool

        :param parse_env_vars: specify if we must parse env var
        :type parse_env_vars: bool

        :return:
        """
        # Norm
        filepath = os.path.normpath(filepath)
        # If parse env vars
        if parse_env_vars:
            # Parse
            filepath = os.path.expandvars(filepath)
        # Make Slashes for Maya Compatibility
        filepath = filepath.replace('\\', '/')
        # If Must Exist
        if must_exist:
            # Check Exist
            if os.path.isfile(filepath) or os.path.isdir(filepath):
                # Return
                return filepath
        # If not Must Exist
        else:
            # Return
            return filepath

    @staticmethod
    def compress_env_vars(filepath, var_names=[]):
        """

        :param filepath:
        :param var_names:
        :return:
        """
        # Normpath
        filepath = FileSystem.normpath(filepath, must_exist=False,
                                       parse_env_vars=False)
        # Each Env var
        for env_var_name, env_var_values in os.environ.items():
            # If Name given or no name given
            if env_var_name in var_names or var_names == []:
                # Split and normalize
                splitted_values = [
                    FileSystem.normpath(env_path, must_exist=False,
                                        parse_env_vars=False) for env_path in
                    env_var_values.split(";")]
                # Only one value possible
                if len(splitted_values) == 1:
                    # Replace in filepath
                    filepath = filepath.replace(splitted_values[0],
                                                '$' + env_var_name)
        # Return
        return filepath

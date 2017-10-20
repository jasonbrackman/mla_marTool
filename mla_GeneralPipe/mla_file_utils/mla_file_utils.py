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
        search_root = os.path.realpath(search_root)
        found_file_path = glob.glob(os.path.join(search_root, filename))
        if found_file_path:
            return found_file_path[0]
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
        filename = FileSystem.normpath(filename)
        if filename:
            logging.info('Load from %s' % filename)
            with open(filename, 'r') as file_json:
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
        filename = FileSystem.normpath(filename, False, True)
        logging.info('Save to   %s' % filename)
        FileSystem.mkdir(os.path.dirname(filename))
        with open(filename, 'w+') as file_json:
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
        if path_source is path_destination:
            return False
        if os.path.isfile(path_source):
            if not os.path.exists(os.path.dirname(path_destination)):
                os.makedirs(os.path.dirname(path_destination))
            logging.info('Copying %s' % os.path.normpath(path_source))
            logging.info('     -> %s' % os.path.normpath(path_destination))
            try:
                FileSystem.delete_if_exists(path_destination)
                shutil.copy(path_source, path_destination)
                os.chmod(path_destination, stat.S_IREAD)
                return True
            except:
                logging.warn('Error Copying file !')
                return False
        else:
            logging.info('Source File doesnt exists %s' % path_source)
            logging.info('Creating Empty File       %s' % path_destination)
            try:
                with open(path_destination, 'w+'):
                    pass
                return True
            except:
                logging.warn('Error Creating file !')
                return False

    @staticmethod
    def delete_if_exists(filepath):
        """
        :param filepath: path of the file to delete
        :type filepath: str
        :return:
        """
        if not os.path.isfile(filepath):
            return False
        os.chmod(filepath, stat.S_IWRITE)
        os.remove(filepath)
        logging.info('Removed %s' % filepath)
        return True

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
        filepath = os.path.normpath(filepath)
        if parse_env_vars:
            filepath = os.path.expandvars(filepath)
        filepath = filepath.replace('\\', '/')
        if must_exist:
            if os.path.isfile(filepath) or os.path.isdir(filepath):
                return filepath
        else:
            return filepath

    @staticmethod
    def compress_env_vars(filepath, var_names=[]):
        """

        :param filepath:
        :param var_names:
        :return:
        """
        filepath = FileSystem.normpath(filepath, must_exist=False,
                                       parse_env_vars=False)
        for env_var_name, env_var_values in os.environ.items():
            if env_var_name not in var_names and var_names != []:
                continue
            splitted_values = [
                FileSystem.normpath(env_path, must_exist=False,
                                    parse_env_vars=False) for env_path in
                env_var_values.split(";")]
            # Only one value possible
            if len(splitted_values) == 1:
                # Replace in filepath
                filepath = filepath.replace(splitted_values[0],
                                            '$' + env_var_name)
        return filepath

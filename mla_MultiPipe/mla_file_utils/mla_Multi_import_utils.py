import os
import logging
import importlib
from Qt import QtWidgets, QtCore, QtGui


def import_if_available(package, module_name=None):
    """
    Import the module if it is available.

    :param package: name of the package to import.
    :type package: str

    :param module_name: name of the module to import from package (optional)
    :type module_name: str

    :return: module
    :rtype: python module
    """

    my_module = None

    if package:
        try:
            my_module = __import__(package, globals(), locals(), [module_name], 0)
        except ImportError:
            my_module = None
        finally:
            return my_module
    else:
        return None


def get_application():
    """
    Get name of the current application.

    :return: name of the application
    :rtype: str
    """
    mc = import_if_available(package='maya.cmds', module_name='cmds')
    mxs = import_if_available(package='pymxs')

    if mc:
        return 'Maya'
    elif mxs:
        return 'Max'
    else:
        return None


def import_from_application():
    """
    Import python modules depending on current application.

    :return: name of the current application, python modules
    :rtype: str, module, module
    """
    application = get_application()

    if application == 'Maya':
        import maya.cmds as mc
        import maya.api.OpenMaya as om2
        return application, mc, om2
    elif application == 'Max':
        import pymxs as mxs
        import MaxPlus
        return application, mxs, MaxPlus
    else:
        return None, None, None


def get_dockable_widget(application):
    """
    Get the proper widget to inherit to make windows dockable.
    :param application: name of the current application.
    :type application: str

    :return: MayaQWidgetDockableMixin or QtWidgets.QGroupBox
    :rtype: class
    """
    if application == 'Maya':
        from maya.app.general.mayaMixin import MayaQWidgetDockableMixin as dockable
    elif application == 'Max':
        dockable = QtWidgets.QGroupBox
    else:
        print 'No dockable found'
        dockable = QtWidgets.QGroupBox

    return dockable


def get_rig_modules(application):
    """
    Get modules for rig builder.

    :param application: name of the current application.
    :type application: str

    :return: rig modules
    :rtype: dict : {'module': module, ...}
    """
    modules = dict()

    if application == 'Maya':
        absolute_path = 'E:\development\Python\mla_MayaPipe\mla_rig_modules'
        relative_path = 'mla_MayaPipe.mla_rig_modules'
    elif application == 'Max':
        absolute_path = 'E:\development\Python\mla_MaxPipe\mla_rig_modules'
        relative_path = 'mla_MaxPipe.mla_rig_modules'
    else:
        print 'No rig modules for this software'
        absolute_path = None
        relative_path = None

    if absolute_path:
        # Set current directory to the given path
        os.chdir(absolute_path)
        # Filter files
        files = [dir_file for dir_file in os.listdir(absolute_path)
                 if os.path.isfile(os.path.join(absolute_path, dir_file))]
        logging.debug('Files are %s' % files)

        # Filter python files
        python_files = [python_file for python_file in files
                        if '.py' in python_file and not '.pyc' in python_file]
        logging.debug('Python files are %s' % python_files)

        module_files = python_files
        module_files.remove('__init__.py')
        logging.debug('Module files are %s' % module_files)

        # Get module and store it into the dict
        for module_file in module_files:
            logging.debug(module_file)
            print module_file

            module_name = module_file.split('.')[0]
            logging.debug(module_name)
            print module_name

            module_path = '%s.%s' % (relative_path, module_name)
            logging.debug(module_path)
            print module_path

            module_obj = importlib.import_module(module_path)
            modules[module_name] = module_obj

    return modules

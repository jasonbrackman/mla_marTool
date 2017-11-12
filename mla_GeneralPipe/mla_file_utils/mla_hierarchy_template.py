from collections import OrderedDict
import logging
import time
import re
import os

import mla_GeneralPipe.mla_file_utils.mla_file_utils as fu
import mla_GeneralPipe.mla_file_utils.mla_path_utils as pu
import mla_GeneralPipe.mla_file_utils.mla_format_utils as format_utils
import mla_GeneralPipe.mla_file_utils.mla_file_library as fl
import mla_GeneralPipe.mla_general_utils.mla_name_utils as nu
import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as Miu
import mla_MultiPipe.mla_file_utils.mla_Multi_file_utils as Mfu
import mla_MultiPipe.mla_file_utils.mla_Multi_path_utils as Mpu

reload(fu)
reload(pu)
reload(format_utils)
reload(fl)
reload(nu)
reload(Miu)
reload(Mfu)
reload(Mpu)

application = Miu.get_application()

# Set project path and file types depending on application
if application == 'Maya':
    types = ['.ma', '.mb', '.fbx', '.obj']
elif application == 'Max':
    types = ['.max', '.fbx', '.obj']
else:
    types = []

# Define the path of the hierarchy_template file
location = '\\'.join(__file__.split('\\')[0:-1])
hierarchy_template_path = os.path.join(location, 'hierarchy_templates.json')


class HierarchyTemplate(dict):

    def __init__(self):
        super(HierarchyTemplate, self).__init__()

        # Get template hierarchies if the file already exists
        if os.path.isfile(hierarchy_template_path):
            logging.info('template hierarchy file exists')
            self.hierarchy_templates = fu.FileSystem.load_from_json(
                hierarchy_template_path)
        # Create an empty OrderedDict if the file doesn't exist
        else:
            logging.info('template hierarchy file does not exist')
            self.hierarchy_templates = OrderedDict()

    def set_hierarchy_template(self,
                               hierarchy_template_name='',
                               hierarchy_path='',
                               depth=6,
                               increment_depth_save=6,
                               increment_digits=3,
                               increment_template_file_name=
                               '{depth4}_{depth5}_{depth6}_v{increment}.ext',
                               publish_depth_save=6,
                               publish_template_file_name=
                               '{depth4}_{depth5}_{depth6}_PUBLISH.ext',
                               edit=False):
        """
        Create hierarchy template and store it into json file.

        :param hierarchy_template_name: name to give to the current hierarchy
        template
        :type hierarchy_template_name: str

        :param hierarchy_path: path to the top folder of the hierarchy
        :type hierarchy_path: str

        :param depth: number of levels in the hierarchy
        :type depth: int

        :param increment_depth_save: depth level to which save the incremented files
        :type increment_depth_save: int

        :param increment_digits: number of digits in the increment number
        :type increment_digits: int

        :param increment_template_file_name: define template name for incremented
        files. Accepted string parts are {*depth_level*}, {increment} and words.
        Each part must be separated by an underscore. You can specify a range of
        character inside of a depth level.
        Example :'{depth4}_{depth5}_{depth6}_{increment}.ext',
        '{depth4[0:2]}_{depth5}_{depth6}_PUBLISH.ext'
        :type increment_template_file_name: str

        :param publish_depth_save: depth level to which save the published files
        :type publish_depth_save: int

        :param publish_template_file_name: define template name for published files
        :type publish_template_file_name: str

        :param edit: define if the file must be edited (True) or created (False)
        :type edit: bool
        """
        # Check if a hierarchy template name is specified, if not, return
        if not hierarchy_template_name:
            logging.error('No hierarchy template name specified')
            return

        # Get specified hierarchy template if in edit mode and if it exists
        if edit:
            if self.hierarchy_templates[hierarchy_template_name]:
                hierarchy = self.hierarchy_templates[hierarchy_template_name]
            else:
                logging.warning(
                    'Specified hierarchy template does not exist and'
                    'therefore cannot be edited. It will be created'
                    'instead')
                hierarchy = dict()
        else:
            # Creating template hierarchy dict
            hierarchy = dict()

        # Set or modify hierarchy information (depending on the mode)
        if hierarchy_template_name:
            hierarchy['hierarchy_template_name'] = hierarchy_template_name
        if hierarchy_path:
            hierarchy['hierarchy_path'] = hierarchy_path
        if depth:
            hierarchy['depth'] = depth
        if increment_depth_save:
            hierarchy['increment_depth_save'] = increment_depth_save
        if increment_digits:
            hierarchy['increment_digits'] = increment_digits
        if increment_template_file_name:
            inc_grp = [grp for grp
                       in re.findall('(\{increment\})',
                                     increment_template_file_name) if grp != '']
            if len(inc_grp) > 1:
                raise ValueError('You cannot specify two increments.')
            else:
                hierarchy[
                    'increment_template_file_name'] = increment_template_file_name
        if publish_depth_save:
            hierarchy['publish_depth_save'] = publish_depth_save
        if publish_template_file_name:
            inc_grp = [grp for grp
                       in re.findall('(\{increment\})',
                                     publish_template_file_name) if grp != '']
            if len(inc_grp) > 0:
                raise ValueError(
                    'You cannot specify increments for publish files.')
            hierarchy['publish_template_file_name'] = publish_template_file_name

        if depth or not edit:
            for i in range(depth + 1):
                hierarchy['depth%s' % i] = list()
        if not edit:
            hierarchy['hierarchy_file_types'] = list()

        # Add template hierarchy to template hierarchy file
        self.hierarchy_templates[hierarchy_template_name] = hierarchy
        logging.debug(self.hierarchy_templates)

        # Save
        fu.FileSystem.save_to_json(self.hierarchy_templates, hierarchy_template_path)

    def customize_hierarchy_template(self, depth=None, template_type=None,
                                     folder_name=None, master_folder=None,
                                     hierarchy_template=None, file_type=None):
        """
        Customize hierarchy template to add folders

        :param depth: depth level to add the
        :type depth: int

        :param template_type: type to give to the depth level, accepted types
        are : fixed, dynamic, fixed by folder, dynamic by folder
        :type template_type: str

        :param folder_name: name to give to the folder if 'fixed'
        or 'fixed by folder'
        :type folder_name: str

        :param master_folder: folder from which the new level set up will be
        dependent (must be one level higher in hierarchy)
        :type master_folder: str

        :param hierarchy_template: hierarchy template to edit
        :type hierarchy_template: str

        :param file_type: file extension to add to the 'hierarchy_file_types' entry,
        used to look for specific file extensions when listing hierarchy
        through FileLibrary
        :type file_type: str
        """
        # Get specified hierarchy template to update from hierarchy dict
        current_template = self.hierarchy_templates[hierarchy_template]

        if not file_type:
            # Set up current hierarchy depth level depending on specified depth type
            # If type is fixed, add the folder name
            if template_type == 'fixed':
                current_template['depth%s' % depth].append(folder_name)

            # If type is dynamic, set the depth as list of one str
            elif template_type == 'dynamic':
                current_template['depth%s' % depth] = ['**dynamic']

            # If type is fixed by folder
            elif template_type == 'fixed by folder':
                # If there is already a dict stored for this depth level, add the
                # folder name to the list
                if type(current_template['depth%s' % depth]) == dict:
                    depth_template = current_template['depth%s' % depth]
                    if len(depth_template[master_folder]) > 0:
                        depth_template[master_folder].append(folder_name)
                # If there is no dict stored for this depth level, create a dict
                # with a list containing the folder name at the right index
                else:
                    depth_template = dict()
                    depth_template[master_folder] = [folder_name]
                # Replace old level value by the newly edited dict
                current_template['depth%s' % depth] = depth_template

            # If the type is dynamic by folder, set the depth for the master folder
            # as a list of one str
            elif template_type == 'dynamic by folder':
                if type(current_template['depth%s' % depth]) == dict:
                    depth_template = current_template['depth%s' % depth]
                    depth_template[master_folder] = ['**dynamic']
                else:
                    depth_template = dict()
                    depth_template[master_folder] = ['**dynamic']
                # Replace old level value by the newly edited dict
                current_template['depth%s' % depth] = depth_template

            # Else, pass
            else:
                pass
        else:
            # Set up current hierarchy file types depending on specified file types
            # If type is fixed, add the folder name
            if template_type == 'fixed':
                current_template['hierarchy_file_types'].append(folder_name)

            # If type is dynamic, set the depth as list of one str
            elif template_type == 'dynamic':
                logging.warning('hierarchy_file_types cannot be dynamic')

            # If type is fixed by folder
            elif template_type == 'fixed by folder':
                # If there is already a dict stored for this depth level, add the
                # file type to the list
                if type(current_template['hierarchy_file_types']) == dict:
                    types_template = current_template['hierarchy_file_types']
                    if len(types_template[master_folder]) > 0:
                        types_template[master_folder].append(file_type)
                # If there is no dict stored for this depth level, create a dict
                # with a list containing the folder name at the right index
                else:
                    types_template = dict()
                    types_template[master_folder] = [folder_name]
                # Replace old level value by the newly edited dict
                current_template['hierarchy_file_types'] = types_template

            # If the type is dynamic by folder, set the depth for the master folder
            # as a list of one str
            elif template_type == 'dynamic by folder':
                logging.warning('hierarchy_file_types cannot be dynamic')

            # Else, pass
            else:
                pass

        # Save
        fu.FileSystem.save_to_json(self.hierarchy_templates, hierarchy_template_path)

    def build_hierarchy_path(self, hierarchy_template_name='', folder_list=[],
                             add_filename=False):
        """
        Build a path from given hierarchy and folder list.

        :param hierarchy_template_name: name of the hierarchy template to browse in
        :type hierarchy_template_name: str

        :param folder_list: list of folders to build the current path
        :type folder_list: list

        :param add_filename: name of the file to add at the end of the path
        :type add_filename: str

        :return:
        """
        hierarchy_template = self.hierarchy_templates[hierarchy_template_name]
        hierarchy_path = hierarchy_template['hierarchy_path']

        # Build path from root path and specified folders
        return_path = hierarchy_path
        for folder in folder_list:
            return_path = os.path.join(return_path, folder)
        if add_filename:
            return_path = self.build_file_name(hierarchy_template_name=
                                               hierarchy_template_name,
                                               folder_path=return_path,
                                               return_path=True)

        return return_path

    def list_hierarchy_from_template(self, hierarchy_template_name=''):
        """
        List all the content of the selected hierarchy.

        :param hierarchy_template_name: name of the hierarchy template to browse in
        :type hierarchy_template_name: str

        :return: folders and files contained in the selected hierarchy
        :rtype: dict
        """
        hierarchy_template = self.hierarchy_templates[hierarchy_template_name]
        folder_path = hierarchy_template['hierarchy_path']
        depth = 1

        hierarchy_content = self.list_hierarchy_content(folder_path,
                                                        hierarchy_template,
                                                        depth)

        return hierarchy_content

    def list_hierarchy_content(self, folder_path='', hierarchy_template=dict,
                               current_depth=int):
        """
        Recursively list the content of a folder.

        :param folder_path: path to the folder whom you want to list the content
        :type folder_path: str

        :param hierarchy_template: hierarchy template of the hierarchy to explore
        :type hierarchy_template: dict

        :param current_depth: depth level to list
        :type current_depth: int

        :return: content of the folder
        :rtype: dict
        """

        file_types = hierarchy_template['file_types']

        if current_depth == hierarchy_template['depth']:
            if type(file_types) == list:
                hierarchy_content = fl.FileLibrary(folder_path,
                                                   file_types=file_types)
            elif type(file_types) == dict:
                hierarchy_content = None
                for folder in file_types.keys():
                    if folder in folder_path:
                        hierarchy_content = fl.FileLibrary(folder_path,
                                                           file_types=
                                                           file_types[folder])
            else:
                hierarchy_content = None
        else:
            hierarchy_content = dict()
            depth_content = pu.create_subdir_list(folder_path)
            for folder in depth_content:
                current_depth += 1
                next_path = os.path.join(folder_path, folder)
                folder_content = self.list_hierarchy_content(next_path,
                                                             hierarchy_template,
                                                             current_depth)
                hierarchy_content[folder] = folder_content

        return hierarchy_content

    def build_file_name(self, hierarchy_template_name='', folder_path='',
                        filetype='', selected_file_name='', return_path=False,
                        return_current_increment=False):
        """
        Build file name from specified hierarchy template and folder path.
        Can also be used to query the increment of the current or selected file.

        :param hierarchy_template_name: name of the hierarchy template to browse in
        :type hierarchy_template_name: str

        :param folder_path: path to the folder where the file is going to be saved
        :type folder_path: str

        :param filetype: type of the file whom you want to create the name.
        type accepted are: increment, publish, image_increment, image_publish
        :type filetype: str

        :param selected_file_name: name of the file we want to increment, in
        increment mode
        :type selected_file_name: str

        :param return_path: specify if we want to include the path in the return
        value
        :type return_path: bool

        :param return_current_increment: specifies if the function must return only
        the increment of the current file
        :type return_current_increment: bool

        :return: name of the new file (incremented or published), or increment of
        the current file
        :rtype : str
        """
        hierarchy_template = self.hierarchy_templates[hierarchy_template_name]

        # Define file_template_name and file extension
        if filetype == 'increment':
            grab_file_template_name = 'increment_template_file_name'
        elif filetype == 'publish':
            grab_file_template_name = 'publish_template_file_name'
        elif filetype == 'image_increment':
            grab_file_template_name = 'increment_template_file_name'
        elif filetype == 'image_publish':
            grab_file_template_name = 'publish_template_file_name'
        else:
            raise ValueError(
                'Invalid file type. Valid file types are : increment, '
                'publish, image_increment, image_publish')

        file_template_name = hierarchy_template[grab_file_template_name]
        hierarchy_path = hierarchy_template['hierarchy_path']

        file_extension = file_template_name.split('.')[-1]

        # Define filename before replace its group parts
        filename = file_template_name.split('.')[0]

        # Get depth levels
        depth_levels = list()
        splitted_path = [folder_path, '']
        while splitted_path[0] != hierarchy_path:
            splitted_path = os.path.split(splitted_path[0])
            depth_levels.insert(0, splitted_path[1])

        # Get the different parts of the name
        str_grps = re.findall('(\{[a-zA-Z0-9\[\]]*\})+', file_template_name)

        if str_grps:
            for str_grp in str_grps:
                str_grp = str_grp[1:-1]

                # Take care of the depth groups
                if 'depth' in str_grp:
                    # Check if there is a range factor
                    depth_str_range = [grp for grp
                                       in re.findall('(\[.*\])', str_grp)
                                       if grp != '']
                    # Remove range factor and get range values
                    if depth_str_range:
                        str_grp = str_grp.replace(depth_str_range[0], '')
                        range_val = depth_str_range[0].split(':')
                    else:
                        range_val = None

                    # Get depth number
                    if str_grp in hierarchy_template.keys():
                        depth_number = int(str_grp.replace('depth', ''))
                    else:
                        raise ValueError('One or more of the depth(s) level(s)'
                                         ' specified in %s are invalid.'
                                         % grab_file_template_name)

                    # Replace group in filename
                    if range_val:
                        if len(range_val) == 1:
                            filename.replace(str_grp, depth_levels[depth_number]
                            [int(range_val[0])])
                        else:
                            filename.replace(str_grp, depth_levels[depth_number]
                            [int(range_val[0]):int(range_val[1])])
                    else:
                        filename.replace(str_grp, depth_levels[depth_number])

                # Take care of the increment group (for incremented files only)
                elif 'increment' in str_grp:
                    # When wwe want the actual filename
                    if not return_current_increment:
                        inc = self.build_file_name(hierarchy_template_name,
                                                   folder_path,
                                                   filetype, return_path=False,
                                                   return_current_increment=True)
                        inc = nu.create_increment(inc,
                                                  hierarchy_template[
                                                      'increment_digits'])

                        filename.replace(str_grp, inc)
                    # When we want the increment number
                    else:
                        # Get proper file name
                        if selected_file_name == '':
                            current_file_name = \
                            os.path.split(Mpu.get_current_scene_path(False))[1]
                        else:
                            current_file_name = selected_file_name

                        # Create increment and return it
                        if not current_file_name or current_file_name == 'untitled':
                            increment = nu.create_increment(str(-1),
                                                            hierarchy_template[
                                                                'increment_digits'])
                        else:
                            increment = current_file_name. \
                                replace(filename.split('{')[0], ''). \
                                replace(filename.split('}')[1], '')
                        return increment

                # Raise error in case of invalid group part(s)
                else:
                    raise ValueError('Invalid group parts in %s'
                                     % grab_file_template_name)

        filename = '.'.join([filename, file_extension])

        if return_path:
            filename = os.path.join(folder_path, filename)

        return filename

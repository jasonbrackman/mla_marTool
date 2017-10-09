import os
import time
import logging

import mla_GeneralPipe.mla_file_utils.mla_file_utils as file_ut
import mla_GeneralPipe.mla_file_utils.mla_format_utils as format_utils
import mla_path_utils as pu
import mla_MultiPipe.mla_file_utils.mla_Multi_file_utils as Multi_file_ut
import mla_MultiPipe.mla_file_utils.mla_Multi_path_utils as Multi_path_ut
import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as Multi_import_ut

reload(file_ut)
reload(format_utils)
reload(pu)
reload(Multi_file_ut)
reload(Multi_path_ut)
reload(Multi_import_ut)

application = Multi_import_ut.get_application()


class FileLibrary(dict):

    def __init__(self, project='', scenes_sound='', asset_anim='',
                 asset_type='', asset='', task='', file_types=['.ma', '.mb']):
        """

        :param project: project to look in
        :type project: str

        :param scenes_sound: scenes_sound to look in
        e.g. scenes, sound, sourceimages
        :type scenes_sound: str

        :param asset_anim: asset_anim to look in, e.g. ASSETS, ANIMATION
        :type asset_anim: str

        :param asset_type: asset_type to look in, e.g. PR, CHR, VEH, EPISODE
        :type asset_type: str

        :param asset: asset to look in, e.g. ZIGGS, SHOT001
        :type asset: str

        :param task: task to look in, e.g. SHADING, MODELLING, ANIMATION, LAYOUT
        :type task: str

        :param file_types: file extensions to look for
        e.g. .jpg, .png, .ma, .mp4
        :type file_types: list

        """
        super(FileLibrary, self).__init__()

        self.project = project
        self.scenes_sound = scenes_sound
        self.asset_anim = asset_anim
        self.asset_type = asset_type
        self.asset = asset
        self.task = task
        self.file_types = file_types

        self.directory = pu.build_path(self.project, self.scenes_sound,
                                       self.asset_anim, self.asset_type,
                                       self.asset, self.task,
                                       return_type='directory')

        self.find()

    def find(self):
        """
        List all the files in the given directory
        :return:
        """
        # logging.debug(self.file_types)

        # If the path does not exists
        if not os.path.exists(self.directory):
            logging.warning('Directory does not exist')
            return

        files = os.listdir(self.directory)
        print files

        specific_files = list()

        for f_type in self.file_types:
            specific_files += [f for f in files if f.endswith(f_type)]

        for f in specific_files:
            name, ext = os.path.splitext(f)
            path = os.path.join(self.directory, f)

            # Get information if exists
            info_file = '%s.json' % name
            if info_file in files:
                info_file = os.path.join(self.directory, info_file)
                info = file_ut.FileSystem.load_from_json(info_file)
            # Else, create it
            else:
                info = dict()

                screenshot = '%s_screenshot.jpg' % name
                if screenshot in files:
                    info['screenshot'] = os.path.join(self.directory,
                                                      '%s_screenshot.jpg'
                                                      % name)

                # Date and formatting
                creation_date = time.localtime(os.path.getctime(path))
                creation_date = format_utils.convert_to_readable_date(creation_date)

                modification_date = time.localtime(os.path.getmtime(path))
                modification_date = format_utils.convert_to_readable_date(modification_date)

                # Create info dict
                info['name'] = name
                info['path'] = path
                info['file type'] = '.%s' % path.split('.')[-1]
                info['creation'] = creation_date
                info['modification'] = modification_date
                info['size'] = os.path.getsize(path)

            self[name] = info

    def save_file(self, wip=False, publish=False, screenshot=True, **info):
        """

        :param wip: specify if the file must be saved as a wip
        :type wip: bool

        :param publish: specify if the file must be saved as a publish
        :type publish: bool

        :param screenshot: specify if a screenshot must be done during saving
        :type screenshot: bool

        :return:
        """

        path = Multi_path_ut.get_current_scene_path()
        logging.info('path of open file is : %s' % path)
        name = path.split('/')[-1].split('.')[0]
        ext = path.split('.')[-1]

        # Create path
        if wip:
            path = pu.build_path(self.project, self.scenes_sound,
                                 self.asset_anim, self.asset_type, self.asset,
                                 self.task, '%s.%s' % (name, ext), 'wip')
            name = path.split('/')[-1].split('.')[0]
            Multi_file_ut.save_file(path)

        if publish:
            path = pu.build_path(self.project, self.scenes_sound,
                                 self.asset_anim, self.asset_type, self.asset,
                                 self.task, '%s.%s' % (name, ext), 'publish')
            name = path.split('/')[-1].split('.')[0]
            Multi_file_ut.save_file(path)

        if not wip and not publish:
            Multi_file_ut.save_file(path)

        print path
        # logging.info('path is : ', path)

        # Create screenshot
        if screenshot:
            screenshot_path = self.save_screenshot(name)

        path_extended = Multi_path_ut.get_current_scene_path()

        # Date and formatting
        creation_date = time.localtime(os.path.getctime(path_extended))
        creation_date = format_utils.convert_to_readable_date(creation_date)

        modification_date = time.localtime(os.path.getmtime(path_extended))
        modification_date = format_utils.convert_to_readable_date(modification_date)

        # Create info dict
        info['name'] = name
        info['path'] = path_extended
        info['file type'] = '.%s' % path_extended.split('.')[-1]
        info['creation'] = creation_date
        info['modification'] = modification_date
        info['size'] = os.path.getsize(path_extended)

        if screenshot:
            info['screenshot'] = screenshot_path

        # Save info dict
        info_path = path_extended.replace(info['file type'], '.json')

        logging.debug(info_path)

        file_ut.FileSystem.save_to_json(info, info_path)

        # Update class to add current item
        self[name] = info

    def open_file(self, name):
        """

        :param name:
        :return:
        """
        path = self[name]['path']

        if application == 'Maya':
            openable = ['.ma', '.mb', '.fbx', '.obj']
        elif application == 'Max':
            openable = ['.max', '.fbx', '.obj']
        else:
            openable = []

        extension = '.%s' % path.split('.')[-1]

        if extension in openable:
            Multi_file_ut.open_file(path)
        else:
            logging.warning('%s is not openable' % path)
            return

    def import_file(self, name):
        path = self[name]['path']

        if application == 'Maya':
            importable = ['.ma', '.mb', '.fbx', '.obj']
        elif application == 'Max':
            importable = ['.max', '.fbx', '.obj']
        else:
            importable = []

        texture_types = ['.jpg', '.jpeg', '.jpe', '.psd', '.psb', '.tif',
                         '.tiff', '.png', '.pns', '.bmp', '.rle', '.dib',
                         '.raw', '.pxr', '.pbm', '.pgm', '.ppm', '.pnm', '.pfm',
                         '.pam', '.tga', '.vda', '.icb', '.vst']
        sound_types = ['.mpeg', '.mp4', '.mp3', '.wma']

        extension = '.%s' % path.split('.')[-1]

        if extension in importable:
            Multi_file_ut.import_scene_file(path)
            return
        elif extension in texture_types:
            file_node = Multi_file_ut.import_image_file(path)
            return file_node
        elif extension in sound_types:
            Multi_file_ut.import_sound_file(path, name)
        else:
            logging.warning('%s is not importable' % path)
            return

    def reference_file(self, name):
        path = self[name]['path']

        if application == 'Maya':
            referenceable = ['.ma', '.mb']
        elif application == 'Max':
            referenceable = ['.max']
        else:
            referenceable = []

        extension = '.%s' % path.split('.')[-1]

        if extension in referenceable:
            Multi_file_ut.reference_file(path)
        else:
            logging.warning('%s is not referenceable' % path)
            return

    def save_screenshot(self, name):
        """

        :param name:
        :return:
        """
        path = os.path.join(self.directory, '%s_screenshot.jpg' % name)

        Multi_file_ut.save_screenshot(path)

        return path

import mla_MultiPipe.mla_file_utils.mla_Multi_path_utils as Multi_path_utils
import mla_path_utils as path_utils
import mla_hierarchy_utils as hierarchy_utils
from mla_GeneralPipe.mla_UI_utils import mla_UI_utils
from Qt import QtWidgets, QtCore, QtGui
import logging

reload(Multi_path_utils)
reload(path_utils)
reload(hierarchy_utils)
reload(mla_UI_utils)


class PathConstructorUI(QtWidgets.QGroupBox):

    def __init__(self):
        super(PathConstructorUI, self).__init__()

        # Get current open file
        self.path = Multi_path_utils.get_current_scene_path()

        self.setWindowTitle('Path Constructor UI')
        self.setMinimumSize(800, 165)
        self.buildUI()

        self.data = dict()

        self.hierarchy = hierarchy_utils.list_hierarchy()

        # Populating menus
        self.project_list = [project for project in self.hierarchy.keys()]
        self.project_list.sort()

        mla_UI_utils.update_combobox(self.project, self.project_list)

        self.update_scenes_sound_combobox()

        # Connecting ui selections
        self.project.currentIndexChanged.connect(
            self.update_asset_anim_combobox)

        self.scenes_sound.currentIndexChanged.connect(
            self.update_scenes_sound_combobox)

        self.asset_anim.currentIndexChanged.connect(
            self.update_asset_type_combobox)

        self.asset_type.currentIndexChanged.connect(
            self.update_asset_shot_combobox)

        self.asset.currentIndexChanged.connect(
            self.update_task_combobox)

        self.set_path_field.pressed.connect(self.update_path)
        self.set_path_field.released.connect(self.select_from_path)

        # Select currently open scene if possible
        # self.select_from_path()

        logging.debug('===== END OF INIT =====')

    def buildUI(self):
        # print 'Building UI'
        layout = QtWidgets.QVBoxLayout(self)

        # Path constructor main widget
        path_constructor_widget = QtWidgets.QWidget()
        path_constructor_layout = QtWidgets.QHBoxLayout(path_constructor_widget)
        layout.addWidget(path_constructor_widget)

        #     Project
        project_widget = QtWidgets.QWidget()
        project_layout = QtWidgets.QVBoxLayout(project_widget)
        path_constructor_layout.addWidget(project_widget)
        project_widget.setFixedWidth(120)

        project_label = QtWidgets.QLabel('Project')
        project_layout.addWidget(project_label)

        self.project = QtWidgets.QComboBox()
        project_layout.addWidget(self.project)

        #     Scene / sound / sourceimages
        scenes_sound_widget = QtWidgets.QWidget()
        scenes_sound_layout = QtWidgets.QVBoxLayout(scenes_sound_widget)
        path_constructor_layout.addWidget(scenes_sound_widget)
        scenes_sound_widget .setFixedWidth(120)

        scenes_sound_label = QtWidgets.QLabel('File type')
        scenes_sound_layout.addWidget(scenes_sound_label)

        self.scenes_sound = QtWidgets.QComboBox()
        scenes_sound_layout.addWidget(self.scenes_sound)

        #     Asset / anim
        asset_anim_widget = QtWidgets.QWidget()
        asset_anim_layout = QtWidgets.QVBoxLayout(asset_anim_widget)
        path_constructor_layout.addWidget(asset_anim_widget)
        asset_anim_widget.setFixedWidth(120)

        asset_anim_label = QtWidgets.QLabel('Asset / anim')
        asset_anim_layout.addWidget(asset_anim_label)

        self.asset_anim = QtWidgets.QComboBox()
        asset_anim_layout.addWidget(self.asset_anim)

        #     Type
        asset_type_widget = QtWidgets.QWidget()
        asset_type_layout = QtWidgets.QVBoxLayout(asset_type_widget)
        path_constructor_layout.addWidget(asset_type_widget)
        asset_type_widget.setFixedWidth(120)

        self.asset_type_label = QtWidgets.QLabel('Type')
        asset_type_layout.addWidget(self.asset_type_label)

        self.asset_type = QtWidgets.QComboBox()
        asset_type_layout.addWidget(self.asset_type)

        #     Asset
        asset_widget = QtWidgets.QWidget()
        asset_layout = QtWidgets.QVBoxLayout(asset_widget)
        path_constructor_layout.addWidget(asset_widget)
        asset_widget.setFixedWidth(120)

        self.asset_label = QtWidgets.QLabel('Asset')
        asset_layout.addWidget(self.asset_label)

        self.asset = QtWidgets.QComboBox()
        asset_layout.addWidget(self.asset)

        #     Task
        task_widget = QtWidgets.QWidget()
        task_layout = QtWidgets.QVBoxLayout(task_widget)
        path_constructor_layout.addWidget(task_widget)
        task_widget.setFixedWidth(120)

        task_label = QtWidgets.QLabel('Task')
        task_layout.addWidget(task_label)

        self.task = QtWidgets.QComboBox()
        task_layout.addWidget(self.task)

        # Path search field
        path_field_main_widget = QtWidgets.QWidget()
        path_field_main_layout = QtWidgets.QHBoxLayout(path_field_main_widget)
        layout.addWidget(path_field_main_widget)

        path_field_widget = QtWidgets.QWidget()
        path_field_layout = QtWidgets.QHBoxLayout(path_field_widget)
        path_field_main_layout.addWidget(path_field_widget)

        path_field_label = QtWidgets.QLabel('Path')
        path_field_layout.addWidget(path_field_label)
        self.path_field = QtWidgets.QLineEdit()
        path_field_layout.addWidget(self.path_field)

        path_button_widget = QtWidgets.QWidget()
        path_button_layout = QtWidgets.QHBoxLayout(path_button_widget)
        path_field_main_layout.addWidget(path_button_widget)
        path_button_widget.setFixedWidth(115)

        self.set_path_field = QtWidgets.QPushButton('Set')
        path_button_layout.addWidget(self.set_path_field)
        logging.debug('===== END OF BUILD UI =====')

    def get_pc_ui_datas(self):
        """
        Get datas from UI
        :return: list of all the UI datas
        :rtype: dict
        """
        # Project
        project = self.project.currentText()
        # Scene / sound
        scenes_sound = self.scenes_sound.currentText()

        # Asset/Anim
        asset_anim = self.asset_anim.currentText()
        # Asset type
        asset_type_episode = self.asset_type.currentText()
        # Asset
        asset_shot = self.asset.currentText()
        # Task
        task = self.task.currentText()

        logging.debug('===== END OF GET DATA =====')

        return {'project': project,
                'scenes_sound': scenes_sound,
                'asset_anim': asset_anim,
                'asset_type_episode': asset_type_episode,
                'asset_shot': asset_shot,
                'task': task}

    def update_scenes_sound_combobox(self):
        """
        Update asset_type/episode comboBox according to the project, asset/anim
        """
        # Get datas from ui
        self.data = self.get_pc_ui_datas()
        # Build list
        scenes_sound_list = [asset_type for asset_type
                             in self.hierarchy[self.data['project']]]

        # Update comboBox
        mla_UI_utils.update_combobox(self.scenes_sound, scenes_sound_list)

        # Init update asset/shot combobox
        self.update_asset_anim_combobox()
        logging.debug('===== END OF scenes_sound comboBox UPDATE =====')

    def update_asset_anim_combobox(self):
        """
        Update asset/anim comboBox according to the project
        """
        # Get datas from ui
        self.data = self.get_pc_ui_datas()
        # Set project directory
        # path_utils.set_current_project_directory(self.data['project'])

        # Build list
        asset_anim_list = [directory for directory
                           in self.hierarchy[self.data['project']]
                           [self.data['scenes_sound']]]

        # Update comboBox
        mla_UI_utils.update_combobox(self.asset_anim, asset_anim_list)

        # Init update type/episode combobox
        self.update_asset_type_combobox()
        logging.debug('===== END OF asset_anim comboBox UPDATE =====')

    def update_asset_type_combobox(self):
        """
        Update asset_type/episode comboBox according to the project, asset/anim
        """
        # Get datas from ui
        self.data = self.get_pc_ui_datas()
        # Build list
        types_list = [asset_type for asset_type
                      in self.hierarchy[self.data['project']]
                      [self.data['scenes_sound']]
                      [self.data['asset_anim']]]

        # Change labels according to selection
        if self.data['asset_anim'] == 'ANIMATION':
            self.asset_type_label.setText('Episode')
            self.asset_label.setText('Shot')
        else:
            self.asset_type_label.setText('Type')
            self.asset_label.setText('Asset')

        # Update comboBox
        mla_UI_utils.update_combobox(self.asset_type, types_list)

        # Init update asset/shot combobox
        self.update_asset_shot_combobox()
        # print '===== END OF asset_type comboBox UPDATE ====='

    def update_asset_shot_combobox(self):
        """
        Update asset/shot comboBox according to the project, asset/anim, 
        asset_type/episode
        """
        # Get datas from ui
        self.data = self.get_pc_ui_datas()
        # Build list
        assets_list = [asset for asset
                       in self.hierarchy[self.data['project']]
                       [self.data['scenes_sound']]
                       [self.data['asset_anim']]
                       [self.data['asset_type_episode']]]

        # Update comboBox
        mla_UI_utils.update_combobox(self.asset, assets_list)

        # Init update task combobox
        self.update_task_combobox()

    def update_task_combobox(self):
        """
        Update task comboBox according to the project, asset/anim, asset_type/episode, asset/shot
        """
        # Get datas from ui
        self.data = self.get_pc_ui_datas()
        # Build list
        task_list = [asset for asset in
                     self.hierarchy[self.data['project']]
                     [self.data['scenes_sound']]
                     [self.data['asset_anim']]
                     [self.data['asset_type_episode']]
                     [self.data['asset_shot']]]

        # Update comboBox
        mla_UI_utils.update_combobox(self.task, task_list, block=False)

    def select_from_path(self):
        """
        Set the different comboBox according to the open file 
        """
        default_project_path = '%s/' % path_utils.MAYA_PROJECT_PATH

        if self.path.startswith(default_project_path):
            self.path = self.path.split(default_project_path)[1]

            self.select_from_path()
        else:
            # If yes, split it and defines the different part
            path_split = self.path.split('/')
            if len(path_split) >= 1:
                project = path_split[0]
            else:
                project = ''

            if len(path_split) >= 2:
                scenes_sound = path_split[1]
            else:
                scenes_sound = ''

            if len(path_split) >= 3:
                asset_anim = path_split[2]
            else:
                asset_anim = ''

            if len(path_split) >= 4:
                asset_type_episode = path_split[3]
            else:
                asset_type_episode = ''

            if len(path_split) >= 5:
                asset_shot = path_split[4]
            else:
                asset_shot = ''

            if len(path_split) >= 6:
                task = path_split[5]
            else:
                task = ''

            # Try to select project, asset/anim, and so on
            if project in self.hierarchy:
                mla_UI_utils.select_combobox_index_from_text(
                    self.project, project)
                if scenes_sound in self.hierarchy[project]:
                    mla_UI_utils.select_combobox_index_from_text(self.scenes_sound, scenes_sound)

                    if asset_anim in self.hierarchy[project][scenes_sound]:
                        mla_UI_utils.select_combobox_index_from_text(self.asset_anim, asset_anim)

                        if asset_type_episode in self.hierarchy[project][scenes_sound][asset_anim]:
                            mla_UI_utils.select_combobox_index_from_text(self.asset_type, asset_type_episode)

                            if asset_shot in self.hierarchy[project][scenes_sound][asset_anim][asset_type_episode]:
                                mla_UI_utils.select_combobox_index_from_text(self.asset, asset_shot)

                                if task in self.hierarchy[project][scenes_sound][asset_anim][asset_type_episode][asset_shot]:
                                    mla_UI_utils.select_combobox_index_from_text(self.task, task)

                                else:
                                    logging.warning('%s not found' % task)
                            else:
                                logging.warning('%s not found' % asset_shot)
                        else:
                            logging.warning('%s not found' % asset_type_episode)
                    else:
                        logging.warning('%s not found' % asset_anim)
                else:
                    logging.warning('%s not found' % scenes_sound)
            else:
                logging.warning('%s not found' % project)

    def update_path(self):
        self.path = self.path_field.text().replace('\\', '/')

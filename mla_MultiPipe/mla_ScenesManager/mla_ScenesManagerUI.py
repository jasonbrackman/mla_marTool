import pprint
import logging

from Qt import QtWidgets, QtCore, QtGui

import mla_GeneralPipe.mla_file_utils.mla_file_utils as file_utils
import mla_GeneralPipe.mla_file_utils.mla_format_utils as format_utils
import mla_GeneralPipe.mla_file_utils.mla_path_utils as path_utils
import mla_GeneralPipe.mla_file_utils.mla_path_constructor_ui as pcui
import mla_GeneralPipe.mla_UI_utils.mla_UI_utils as mla_UI_utils
import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as import_utils

reload(file_utils)
reload(format_utils)
reload(path_utils)
reload(pcui)
reload(mla_UI_utils)
reload(import_utils)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

application = import_utils.get_application()
dockable = import_utils.get_dockable_widget(application)


class AssetManagerUI(dockable, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(AssetManagerUI, self).__init__(parent=parent)

        self.setWindowTitle('Asset Manager UI')
        self.setMinimumSize(825, 550)
        # Path constructor
        self.path_constructor = pcui.PathConstructorUI()
        # UI
        self.buildUI()

        # Connexions
        self.path_constructor.task.currentIndexChanged.connect(
            self.update_files_list)

        self.files_list_widget.currentItemChanged.connect(self.update_file_info)

        self.open_button.clicked.connect(self.open_file)
        self.import_button.clicked.connect(self.import_file)
        self.reference_button.clicked.connect(self.reference_file)

        self.small.clicked.connect(self.set_small_icons)
        self.medium.clicked.connect(self.set_medium_icons)
        self.large.clicked.connect(self.set_large_icons)

        self.save_button.clicked.connect(self.save_file)
        self.save_wip_button.clicked.connect(self.save_wip_file)
        self.save_publish_button.clicked.connect(self.save_publish_file)

        # Initialize UI
        self.hierarchy = self.path_constructor.hierarchy

        self.path_constructor.select_from_path()

        self.data = dict()
        self.data = self.path_constructor.get_pc_ui_datas()

    def buildUI(self):
        logging.info('Building UI')
        layout = QtWidgets.QVBoxLayout(self)

        # Path constructor main widget
        layout.addWidget(self.path_constructor)

        # Display info widget
        self.display_info = QtWidgets.QListWidget()
        self.display_info.setFixedSize(807, 107)
        self.display_info.setStyleSheet('background-color: #202020; color: white; border-bottom: 1px white;')
        layout.addWidget(self.display_info)

        # Open button widgets
        open_button_widget = QtWidgets.QWidget()
        open_button_layout = QtWidgets.QHBoxLayout(open_button_widget)
        layout.addWidget(open_button_widget)

        self.open_button = QtWidgets.QPushButton('Open')
        open_button_layout.addWidget(self.open_button)

        self.import_button = QtWidgets.QPushButton('Import')
        open_button_layout.addWidget(self.import_button)

        self.reference_button = QtWidgets.QPushButton('Reference')
        open_button_layout.addWidget(self.reference_button)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        open_button_layout.addWidget(sep)

        self.small = QtWidgets.QPushButton('Small')
        self.small.setFixedWidth(50)
        open_button_layout.addWidget(self.small)

        self.medium = QtWidgets.QPushButton('Medium')
        self.medium.setFixedWidth(50)
        open_button_layout.addWidget(self.medium)

        self.large = QtWidgets.QPushButton('Large')
        self.large.setFixedWidth(50)
        open_button_layout.addWidget(self.large)

        # Files list widget
        self.files_list_widget = QtWidgets.QListWidget()
        self.files_list_widget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.files_list_widget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.set_small_icons()
        layout.addWidget(self.files_list_widget)

        # Comment widget
        comment_widget = QtWidgets.QWidget()
        comment_layout = QtWidgets.QHBoxLayout(comment_widget)
        layout.addWidget(comment_widget)

        comment_label = QtWidgets.QLabel('Comment')
        comment_layout.addWidget(comment_label)
        self.comment = QtWidgets.QLineEdit()
        comment_layout.addWidget(self.comment)

        # Button widget
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_widget)
        layout.addWidget(button_widget)

        self.save_button = QtWidgets.QPushButton('Save')
        button_layout.addWidget(self.save_button)

        self.save_wip_button = QtWidgets.QPushButton('Save wip')
        button_layout.addWidget(self.save_wip_button)

        self.save_publish_button = QtWidgets.QPushButton('Save publish')
        button_layout.addWidget(self.save_publish_button)

        logging.info('===== END OF BUILD UI =====')

    def update_files_list(self):
        logging.info('Updating list')

        if self.files_list_widget.currentItem():
            current_file = self.files_list_widget.currentItem().text()
        else:
            current_file = None

        self.files_list_widget.clear()

        # Get path constructor data
        pcui_data = self.path_constructor.get_pc_ui_datas()

        project = pcui_data['project']
        scenes_sound = pcui_data['scenes_sound']
        asset_anim = pcui_data['asset_anim']
        asset_type_episode = pcui_data['asset_type_episode']
        asset_shot = pcui_data['asset_shot']
        task = pcui_data['task']

        if project and scenes_sound and asset_anim and asset_type_episode \
                and asset_shot and task:
            current_library = self.hierarchy[project][scenes_sound][asset_anim][
                asset_type_episode][asset_shot][task]

            files_list = list()
            for name, info in current_library.items():
                files_list.append(name)

            files_list.sort()
            files_list.reverse()

            for name in files_list:
                info = current_library[name]
                item = QtWidgets.QListWidgetItem(name)
                self.files_list_widget.addItem(item)

                screenshot = info.get('screenshot')
                logging.info('screenshot is : %s' % screenshot)
                if screenshot:
                    icon = QtGui.QIcon(screenshot)
                    item.setIcon(icon)

                item.setToolTip(pprint.pformat(info))
                print pprint.pformat(info)
        else:
            files_list = None

        if current_file:
            if files_list:
                if current_file in files_list:
                    item = self.files_list_widget.findItems(current_file,
                                                            QtCore.Qt.MatchExactly)[0]
                    self.files_list_widget.setCurrentItem(item)

    def update_file_info(self):
        self.display_info.clear()

        current_file = self.files_list_widget.currentItem().text()

        current_library = self.get_current_library()

        # name
        if 'name' in current_library[current_file]:
            self.display_info.addItem('Name : %s'
                                      % current_library[current_file]['name'])
        else:
            self.display_info.addItem('Name : ')

        # extension
        if 'file type' in current_library[current_file]:
            self.display_info.addItem('File extension : %s'
                                      % current_library[current_file][
                                          'file type'])
        else:
            self.display_info.addItem('File extension : ')

        # name
        if 'size' in current_library[current_file]:
            size = format_utils.convert_to_readable_size(current_library[current_file][
                                          'size'])
            self.display_info.addItem('Size : %s'
                                      % size)
        else:
            self.display_info.addItem('Size : ')

        # creation date
        if 'creation' in current_library[current_file]:
            self.display_info.addItem('Creation date : %s'
                                      % current_library[current_file][
                                          'creation'])
        else:
            self.display_info.addItem('Creation date : ')

        # creation date
        if 'modification' in current_library[current_file]:
            self.display_info.addItem('Modification date : %s'
                                      % current_library[current_file][
                                          'modification'])
        else:
            self.display_info.addItem('Modification date : ')

        # path
        if 'path' in current_library[current_file]:
            self.display_info.addItem('Path : %s'
                                      % current_library[current_file]['path'])
        else:
            self.display_info.addItem('Path : ')

        # comment
        if 'comment' in current_library[current_file]:
            self.display_info.addItem('Comment : %s'
                                      % current_library[current_file][
                                          'comment'])
        elif 'Comment' in current_library[current_file]:
            self.display_info.addItem('Comment : %s'
                                      % current_library[current_file][
                                          'Comment'])
        elif 'COMMENT' in current_library[current_file]:
            self.display_info.addItem('Comment : %s'
                                      % current_library[current_file][
                                          'COMMENT'])
        else:
            self.display_info.addItem('Comment : ')

    def set_small_icons(self):
        size = 64
        buff = 12

        self.files_list_widget.setIconSize(QtCore.QSize(size, size))
        self.files_list_widget.setGridSize(QtCore.QSize(size+buff, size+buff))
        self.small.setStyleSheet('background-color: #05B8CC; color: black')
        self.medium.setStyleSheet('background-color: dark gray; color: white')
        self.large.setStyleSheet('background-color: dark gray; color: white')

    def set_medium_icons(self):
        size = 128
        buff = 24

        self.files_list_widget.setIconSize(QtCore.QSize(size, size))
        self.files_list_widget.setGridSize(QtCore.QSize(size+buff, size+buff))
        self.small.setStyleSheet('background-color: dark gray; color: white')
        self.medium.setStyleSheet('background-color: #05B8CC; color: black')
        self.large.setStyleSheet('background-color: dark gray; color: white')

    def set_large_icons(self):
        size = 256
        buff = 24

        self.files_list_widget.setIconSize(QtCore.QSize(size, size))
        self.files_list_widget.setGridSize(QtCore.QSize(size+buff, size+buff))
        self.small.setStyleSheet('background-color: dark gray; color: white')
        self.medium.setStyleSheet('background-color: dark gray; color: white')
        self.large.setStyleSheet('background-color: #05B8CC; color: black')

    def get_current_library(self):
        pcui_data = self.path_constructor.get_pc_ui_datas()

        project = pcui_data['project']
        scenes_sound = pcui_data['scenes_sound']
        asset_anim = pcui_data['asset_anim']
        asset_type_episode = pcui_data['asset_type_episode']
        asset_shot = pcui_data['asset_shot']
        task = pcui_data['task']

        current_library = self.hierarchy[project][scenes_sound][asset_anim][
            asset_type_episode][asset_shot][task]

        return current_library

    def open_file(self):
        current_file = self.files_list_widget.currentItem().text()

        current_library = self.get_current_library()

        current_library.open_file(current_file)

    def import_file(self):
        current_file = self.files_list_widget.currentItem().text()

        current_library = self.get_current_library()

        current_library.import_file(current_file)

    def reference_file(self):
        current_file = self.files_list_widget.currentItem().text()

        current_library = self.get_current_library()

        current_library.reference_file(current_file)

    def save_file(self):
        comment = self.comment.text()

        current_library = self.get_current_library()

        current_library.save_file(comment=comment)

        self.update_files_list()

    def save_wip_file(self):
        comment = self.comment.text()

        current_library = self.get_current_library()

        current_library.save_file(wip=True, comment=comment)

        self.update_files_list()

    def save_publish_file(self):
        comment = self.comment.text()

        current_library = self.get_current_library()

        current_library.save_file(wip=True, publish=True, comment=comment)

        self.update_files_list()


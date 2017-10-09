import mla_MultiPipe.mla_file_utils.mla_Multi_file_utils as file_utils
import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as import_utils
# import mla_file_utils.mla_path_utils as path_utils
import mla_GeneralPipe.mla_file_utils.mla_path_constructor_ui as pcui
from Qt import QtWidgets, QtCore, QtGui
import logging

reload(pcui)
reload(file_utils)
reload(import_utils)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

application = import_utils.get_application()
dockable = import_utils.get_dockable_widget(application)


class RigBuilderUI(dockable, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(RigBuilderUI, self).__init__(parent=parent)

        self.setWindowTitle('Rig Builder UI')
        # Path constructor
        self.path_constructor = pcui.PathConstructorUI()
        # UI
        self.buildUI()

        self.modules = import_utils.get_rig_modules(application)

        self.populate_modules()

    def buildUI(self):
        logging.info('Building UI')
        layout = QtWidgets.QVBoxLayout(self)

        # Path constructor main widget
        layout.addWidget(self.path_constructor)

        # Main part
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main_widget)
        layout.addWidget(main_widget)

        # Stack
        stack_main_widget = QtWidgets.QWidget()
        stack_main_layout = QtWidgets.QVBoxLayout(stack_main_widget)
        main_layout.addWidget(stack_main_widget)

        # Stack buttons
        stack_button_widget = QtWidgets.QWidget()
        stack_button_layout = QtWidgets.QHBoxLayout(stack_button_widget)
        stack_main_layout.addWidget(stack_button_widget)

        self.stack_up_button = QtWidgets.QPushButton('Move Up')
        stack_button_layout.addWidget(self.stack_up_button)

        self.stack_down_button = QtWidgets.QPushButton('Move Down')
        stack_button_layout.addWidget(self.stack_down_button)

        # Stack ListWidget
        self.stack_list_widget = QtWidgets.QListWidget()
        stack_main_layout.addWidget(self.stack_list_widget)

        # Modules main layout
        modules_main_widget = QtWidgets.QWidget()
        modules_main_layout = QtWidgets.QVBoxLayout(modules_main_widget)
        main_layout.addWidget(modules_main_widget)

        # Modules list main layout
        modules_list_main_widget = QtWidgets.QWidget()
        modules_list_main_layout = QtWidgets.QHBoxLayout(modules_list_main_widget)
        modules_main_layout.addWidget(modules_list_main_widget)

        # Modules list buttons
        modules_list_button_widget = QtWidgets.QWidget()
        modules_list_button_layout = QtWidgets.QVBoxLayout(modules_list_button_widget)
        modules_list_main_layout.addWidget(modules_list_button_widget)

        self.stack_add_button = QtWidgets.QPushButton('<')
        self.stack_add_button.setFixedWidth(25)
        self.stack_add_button.setFixedHeight(100)
        modules_list_button_layout.addWidget(self.stack_add_button)

        self.stack_remove_button = QtWidgets.QPushButton('>')
        self.stack_remove_button.setFixedWidth(25)
        self.stack_remove_button.setFixedHeight(100)
        modules_list_button_layout.addWidget(self.stack_remove_button)

        # Modules ListWidget
        self.modules_list_widget = QtWidgets.QListWidget()
        self.modules_list_widget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.modules_list_widget.setResizeMode(QtWidgets.QListWidget.Adjust)
        modules_list_main_layout.addWidget(self.modules_list_widget)

        # Modules options groupBox
        self.modules_options_group_box = QtWidgets.QGroupBox()
        self.modules_options_group_box.setMinimumHeight(200)
        modules_main_layout.addWidget(self.modules_options_group_box)

        # Open / Save buttons main widget
        open_save_buttons_widget = QtWidgets.QWidget()
        open_save_buttons_layout = QtWidgets.QHBoxLayout(open_save_buttons_widget)
        layout.addWidget(open_save_buttons_widget)

        # Buttons
        self.open_button = QtWidgets.QPushButton('Open rig template')
        open_save_buttons_layout.addWidget(self.open_button)

        self.save_button = QtWidgets.QPushButton('Save rig template')
        open_save_buttons_layout.addWidget(self.save_button)

        self.save_wip_button = QtWidgets.QPushButton('Save WIP rig template')
        open_save_buttons_layout.addWidget(self.save_wip_button)

        self.import_button = QtWidgets.QPushButton('Import rig template')
        open_save_buttons_layout.addWidget(self.import_button)

        # Build buttons
        build_buttons_widget = QtWidgets.QWidget()
        build_buttons_layout = QtWidgets.QHBoxLayout(build_buttons_widget)
        layout.addWidget(build_buttons_widget)

        self.create_button = QtWidgets.QPushButton('Create guides')
        build_buttons_layout.addWidget(self.create_button)

        self.build_button = QtWidgets.QPushButton('Build rig')
        build_buttons_layout.addWidget(self.build_button)

        self.publish_button = QtWidgets.QPushButton('Publish rig template')
        build_buttons_layout.addWidget(self.publish_button)

    def populate_modules(self):
        """
        Populate list of modules depending on the current application.
        """
        self.modules_list_widget.clear()

        for module in self.modules:
            item = QtWidgets.QListWidgetItem()
            widget = QtWidgets.QGroupBox()
            layout = QtWidgets.QHBoxLayout(widget)

            label = QtWidgets.QLabel(module)
            layout.addWidget(label)

            item.setSizeHint(widget.sizeHint())

            self.modules_list_widget.addItem(item)
            self.modules_list_widget.setItemWidget(item, widget)

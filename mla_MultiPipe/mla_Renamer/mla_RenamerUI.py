import mla_MultiPipe.mla_file_utils.mla_Multi_file_utils as file_utils
import mla_MultiPipe.mla_file_utils.mla_Multi_import_utils as import_utils
import mla_GeneralPipe.mla_general_utils.mla_name_utils as name_utils
from Qt import QtWidgets, QtCore, QtGui
import logging

reload(file_utils)
reload(import_utils)
reload(name_utils)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

application = import_utils.get_application()
dockable = import_utils.get_dockable_widget(application)

if application == 'Maya':
    import mla_MayaPipe.mla_Maya_general_utils.mla_general_utils as gu
elif application == 'Max':
    # TODO : create this one!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    import mla_MaxPipe.mla_Max_general_utils.mla_general_utils as gu

reload(gu)

class RenamerUI(dockable, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(RenamerUI, self).__init__(parent=parent)

        self.setWindowTitle('Renamer UI')

        # UI
        self.buildUI()

        self.rename_button.clicked.connect(self.rename)

    def buildUI(self):
        logging.info('Building UI')
        layout = QtWidgets.QVBoxLayout(self)

        # Main part
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        layout.addWidget(main_widget)

        # Search/Replace
        search_replace_widget = QtWidgets.QWidget()
        search_replace_layout = QtWidgets.QHBoxLayout(search_replace_widget)
        main_layout.addWidget(search_replace_widget)

        search_label = QtWidgets.QLabel('Search')
        search_label.setFixedWidth(62)
        search_replace_layout.addWidget(search_label)
        self.search = QtWidgets.QLineEdit()
        search_replace_layout.addWidget(self.search)

        replace_label = QtWidgets.QLabel('Replace')
        # replace_label.setFixedWidth(62)
        search_replace_layout.addWidget(replace_label)
        self.replace = QtWidgets.QLineEdit()
        search_replace_layout.addWidget(self.replace)
        
        # Prefix
        prefix_widget = QtWidgets.QWidget()
        prefix_layout = QtWidgets.QHBoxLayout(prefix_widget)
        main_layout.addWidget(prefix_widget)
        
        prefix_label = QtWidgets.QLabel('Prefix')
        prefix_label.setFixedWidth(62)
        prefix_layout.addWidget(prefix_label)
        self.prefix = QtWidgets.QLineEdit()
        prefix_layout.addWidget(self.prefix)

        # Main_name
        main_name_widget = QtWidgets.QWidget()
        main_name_layout = QtWidgets.QHBoxLayout(main_name_widget)
        main_layout.addWidget(main_name_widget)

        main_name_label = QtWidgets.QLabel('Main Name')
        main_name_label.setFixedWidth(62)
        main_name_layout.addWidget(main_name_label)
        self.main_name = QtWidgets.QLineEdit()
        main_name_layout.addWidget(self.main_name)

        # suffix
        suffix_widget = QtWidgets.QWidget()
        suffix_layout = QtWidgets.QHBoxLayout(suffix_widget)
        main_layout.addWidget(suffix_widget)

        suffix_label = QtWidgets.QLabel('Suffix')
        suffix_label.setFixedWidth(62)
        suffix_layout.addWidget(suffix_label)
        self.suffix = QtWidgets.QLineEdit()
        suffix_layout.addWidget(self.suffix)

        self.rename_button = QtWidgets.QPushButton('Rename')
        main_layout.addWidget(self.rename_button)

    def rename(self):
        search = self.search.text()
        replace = self.replace.text()
        prefix = self.prefix.text()
        main_name = self.main_name.text()
        suffix = self.suffix.text()

        selection = gu.get_selection()

        name_utils.rename(selection, prefix, main_name, suffix, search, replace)

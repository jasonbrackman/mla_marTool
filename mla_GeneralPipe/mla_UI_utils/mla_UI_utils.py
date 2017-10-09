from Qt import QtWidgets, QtCore, QtGui
from Qt import __binding__
import logging

# try:
#     import pyside2uic as pysideuic
#     from shiboken2 import wrapInstance
#
# except ImportError:
#     import pysideuic as pysideuic
#     from shiboken import wrapInstance
#
#
# def get_maya_window():
#     """
#     Get the main Maya window as a QtGui.QMainWindow instance
#
#     :return: QtWidgets.QMainWindow instance of the top level Maya windows
#     """
#     ptr = OMui.MQtUtil.mainWindow()
#     if ptr is not None:
#         return wrapInstance(long(ptr), QtWidgets.QWidget)


def update_combobox(combobox, items, block='True'):
    """
    Update the given comboBox
    :param combobox: combobox to update,  ie: self.task_combobox
    :type combobox: QWidget
    
    :param items: list of items to add to the given comboBox
    :type items: list
    
    :param block: specify if blockSignals method should be set as True for the given comboBox
    :type block: bool    
    """

    # --- Blocking signals from ui
    if block:
        combobox.blockSignals(True)
    else:
        pass

    # --- Init items if empty
    if not items:
        items = ['None']

    # --- Get currently selected text
    selected_text = combobox.currentText()

    # --- Clear combobox
    combobox.clear()
    # --- Add items
    combobox.addItems(items)

    # combobox.setCurrentIndex(-1)

    # --- If current selected item in new item list, select it
    if selected_text in items:
        select_combobox_index_from_text(combobox, selected_text)
    else:
        combobox.setCurrentIndex(0)

    for i, item in enumerate(items):
        combobox.setItemData(i, item, QtCore.Qt.ToolTipRole)

    # --- Unblocking signals from ui
    combobox.blockSignals(False)


def select_combobox_index_from_text(combobox, text):
    """
    Select given text in the given comboBox
    :param combobox: the comboBox you want to set selection
    :param text: The text you want to select
    """
    # Get index from the text
    text_index = combobox.findText(text)
    # Select text from index
    combobox.setCurrentIndex(text_index)

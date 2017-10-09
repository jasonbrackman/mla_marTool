__author__ = 'm.lanton'
from PySide.QtGui import *
from maya import OpenMayaUI
from shiboken import wrapInstance

import BSM_1_3.BSM as bsm

reload(bsm)


def main():
    # Close all windows
    global WIDGET_HOLDER

    try:
        WIDGET_HOLDER.close()
    except (AttributeError, NameError):
        pass
    # Get Pyside instance of Maya MainWindow
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    main_window = wrapInstance(long(ptr), QWidget)
    # New Window
    WIDGET_HOLDER = bsm.Proc(parent=main_window)
    # Store to prevent garbage collection
    # Show
    WIDGET_HOLDER.show()
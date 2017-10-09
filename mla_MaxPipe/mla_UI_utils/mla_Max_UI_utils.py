from Qt import QtWidgets, QtCore, QtGui
# import MaxPlus


class MaxDockableWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(MaxDockableWidget, self).__init__(parent=parent)

        # MaxPlus.MakeQWidgetDockable(self, 14)

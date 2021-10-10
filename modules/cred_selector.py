from qtpy import QtGui, QtWidgets, uic
import os


class ItemSelector(QtWidgets.QWidget):

    def __init__(self, mainwindow, side, credstore):
        super().__init__()
        self.side = side
        self.mainwindow = mainwindow
        self.credstore = credstore
        item_selector_ui = os.path.join(self.mainwindow.basedir, 'data/cred_selector.ui')
        uic.loadUi(item_selector_ui, self)

    def load_presets(self):
        if self.credstore:
            pass

    def clear_creds(self):
        self.userIDLineEdit.clear()
        self.passwordKeyTokenLineEdit.clear()
        self.serviceURLLineEdit.clear()

    def reset_creds(self):
        self.userIDLineEdit.clear()
        self.passwordKeyTokenLineEdit.clear()
        self.serviceURLLineEdit.clear()
        self.presetComboBox.clear()




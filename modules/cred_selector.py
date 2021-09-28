from qtpy import QtGui, QtWidgets, uic
import os

class ItemSelector(QtWidgets.QWidget):

    def __init__(self, mainwindow, side, ):
        super().__init__()
        self.side = side
        self.mainwindow = mainwindow
        self.credential_database = None
        item_selector_ui = os.path.join(self.mainwindow.basedir, 'data/cred_selector.ui')
        uic.loadUi(item_selector_ui, self)

    def register_credential_database(self, cred_database):
        self.credential_database = cred_database

    def load_presets(self):
        if self.credential_database:
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




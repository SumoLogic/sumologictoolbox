
from qtpy import QtWidgets, QtGui, QtCore
import pathlib

class ShowTextDialog(QtWidgets.QDialog):

    def __init__(self, title, text, base_dir):
        super(ShowTextDialog, self).__init__()
        self.title = title
        self.text = text
        self.last_search = "Up"
        self.icons = {}
        iconpath = str(pathlib.Path(base_dir + '/data/arrow-up.svg'))
        self.icons['ArrowUp'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(base_dir + '/data/arrow-down.svg'))
        self.icons['ArrowDown'] = QtGui.QIcon(iconpath)
        self.setupUi(self)
        self.searchbox.textChanged.connect(lambda: self.search(
            self.searchbox.text()
        ))
        self.searchup.clicked.connect(lambda: self.search_up(
            self.searchbox.text()
        ))
        self.searchdown.clicked.connect(lambda: self.search_down(
            self.searchbox.text()
        ))



    def setupUi(self, Dialog):
        Dialog.setObjectName("JSONDisplay")
        self.setWindowTitle(self.title)

        self.searchlayout = QtWidgets.QHBoxLayout()
        self.searchbox = QtWidgets.QLineEdit()
        self.searchbox.setPlaceholderText('Search')
        self.searchlayout.addWidget(self.searchbox)
        self.searchup = QtWidgets.QPushButton()
        self.searchup.setIcon(self.icons['ArrowUp'])
        self.searchlayout.addWidget(self.searchup)
        self.searchdown = QtWidgets.QPushButton()
        self.searchdown.setIcon(self.icons['ArrowDown'])
        self.searchlayout.addWidget(self.searchdown)
        self.textedit = QtWidgets.QTextEdit()
        self.textedit.setText(self.text)
        # self.textedit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.textedit.setReadOnly(True)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.searchlayout)
        self.layout.addWidget(self.textedit)
        self.setLayout(self.layout)


    def search(self, search_text):
        self.textedit.textCursor().clearSelection()
        if self.last_search == 'Up':
            search_result = self.textedit.find(search_text)
            if search_result:
                self.last_search = 'Down'
            else:
                search_result = self.textedit.find(search_text, QtGui.QTextDocument.FindBackward)
                self.last_search = 'Up'




    def search_down(self, search_text):
        search_result = self.textedit.find(search_text)

    def search_up(self, search_text):
        search_result = self.textedit.find(search_text, QtGui.QTextDocument.FindBackward)


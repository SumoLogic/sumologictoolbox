__author__ = 'Tim MacDonald'
# Copyright 2019 Timothy MacDonald
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from PyQt5 import QtCore, QtGui, QtWidgets

class findReplaceCopyDialog(QtWidgets.QDialog):

    def __init__(self, fromcategories, tocategories, parent=None):
        super(findReplaceCopyDialog, self).__init__(parent)
        self.objectlist = []
        self.setupUi(self, fromcategories, tocategories)

    def setupUi(self, frcd, fromcategories, tocategories):

        # setup static elements
        frcd.setObjectName("FindReplaceCopy")
        frcd.resize(1150, 640)
        self.buttonBox = QtWidgets.QDialogButtonBox(frcd)
        self.buttonBox.setGeometry(QtCore.QRect(10, 600, 1130, 35))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBoxOkCancel")
        self.label = QtWidgets.QLabel(frcd)
        self.label.setGeometry(QtCore.QRect(20, 10, 1120, 140))
        self.label.setWordWrap(True)
        self.label.setObjectName("labelInstructions")
        self.scrollArea = QtWidgets.QScrollArea(frcd)
        self.scrollArea.setGeometry(QtCore.QRect(10, 150, 1130, 440))
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidget = QtWidgets.QWidget()
        self.scrollAreaWidgetContents = QtWidgets.QFormLayout()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # set up the list of destination categories to populate into the comboboxes
        itemmodel = QtGui.QStandardItemModel()
        for tocategory in tocategories:
            text_item = QtGui.QStandardItem(str(tocategory))
            itemmodel.appendRow(text_item)
        itemmodel.sort(0)

        # Create 1 set of (checkbox, label, combobox per fromcategory


        for index, fromcategory in enumerate(fromcategories):

            objectdict = {'checkbox': None, 'label': None, 'combobox': None}
            layout = QtWidgets.QHBoxLayout()
            objectdict['checkbox'] = QtWidgets.QCheckBox()
            objectdict['checkbox'].setGeometry(QtCore.QRect(0, 0, 20, 20))
            objectdict['checkbox'].setText("")
            objectdict['checkbox'].setObjectName("checkBox" + str(index))
            layout.addWidget(objectdict['checkbox'])
            objectdict['label']= QtWidgets.QLabel()
            objectdict['label'].setGeometry(QtCore.QRect(0, 0, 480, 25))
            objectdict['label'].setObjectName("comboBox" + str(index))
            objectdict['label'].setText(fromcategory)
            layout.addWidget(objectdict['label'])
            objectdict['combobox'] = QtWidgets.QComboBox()
            objectdict['combobox'].setGeometry(QtCore.QRect(550, 0, 485, 25))
            objectdict['combobox'].setObjectName("comboBox" + str(index))
            objectdict['combobox'].setModel(itemmodel)
            objectdict['combobox'].setEditable(True)
            layout.addWidget(objectdict['combobox'])
            self.objectlist.append(objectdict)
            self.scrollAreaWidgetContents.addRow(layout)

        self.scrollAreaWidget.setLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollArea.show()


        self.retranslateUi(frcd)
        self.buttonBox.accepted.connect(frcd.accept)
        self.buttonBox.rejected.connect(frcd.reject)
        QtCore.QMetaObject.connectSlotsByName(frcd)

    def retranslateUi(self, FindReplaceCopy):
        _translate = QtCore.QCoreApplication.translate
        FindReplaceCopy.setWindowTitle(_translate("FindReplaceCopy", "Dialog"))
        self.label.setText(_translate("FindReplaceCopy",
                                      "<html><head/><body><p>Each entry on the left is one of the source categories present in your content. </p><p>From the drop downs on the right select the source categories you want to replace them with or type your own. These have been populated from your destination org/tenant. </p><p>Checked items will be replaced, unchecked items will not be modified. </p><p>Note: The query that populates the destination dropdowns only searches for source categories that have ingested something in the last hour. If you are sporadically ingesting data then some source categories may not show up. You can type those in manually.</p></body></html>"))

    def getresults(self):
        results = []
        for object in self.objectlist:
            if str(object['checkbox'].checkState()) == '2':
                objectdata = { 'from': str(object['label'].text()), 'to': str(object['combobox'].currentText())}
                results.append(objectdata)
        return results


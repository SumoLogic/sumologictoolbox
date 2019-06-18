__author__ = 'Tim MacDonald'

import sys
import json
import re
import csv
import pytz
import os.path
from datetime import datetime
from tzlocal import get_localzone
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from sumologic import SumoLogic
import pathlib
import os
import traceback
import logzero
from logzero import logger



# detect if in Pyinstaller package and build appropriate base directory path
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

# Setup logging
logzero.logfile("sumotoolbox.log")
logzero.loglevel(level=10) #  Info Logging
# Log messages
logger.info("SumoLogicToolBox started.")

# This script uses Qt Designer files to define the UI elements which must be loaded
qtMainWindowUI = os.path.join(basedir, 'data/sumotoolbox.ui')

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindowUI)


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
        self.label.setGeometry(QtCore.QRect(20, 10, 1120, 100))
        self.label.setWordWrap(True)
        self.label.setObjectName("labelInstructions")
        self.scrollArea = QtWidgets.QScrollArea(frcd)
        self.scrollArea.setGeometry(QtCore.QRect(10, 110, 1130, 460))
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1130, 460))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # set up the list of destination categories to populate into the comboboxes
        itemmodel = QtGui.QStandardItemModel()
        for tocategory in tocategories:
            text_item = QtGui.QStandardItem(str(tocategory))
            itemmodel.appendRow(text_item)

        # Create 1 set of (checkbox, label, combobox per fromcategory

        x = 10
        y = 0
        width = 1040
        height = 40

        for index, fromcategory in enumerate(fromcategories):

            objectdict = {'groupbox': None, 'checkbox': None, 'label': None, 'combobox': None}

            #objectdict['groupbox'] = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
            #objectdict['groupbox'].setGeometry(QtCore.QRect(x, y, width, height))
            #objectdict['groupbox'].setTitle("")
            #objectdict['groupbox'].setObjectName("groupBox" + str(index))
            objectdict['checkbox'] = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            objectdict['checkbox'].setGeometry(QtCore.QRect(x + 10, y + 14, 20, 20))
            objectdict['checkbox'].setText("")
            objectdict['checkbox'].setObjectName("checkBox" + str(index))
            objectdict['label']= QtWidgets.QLabel(self.scrollAreaWidgetContents)
            objectdict['label'].setGeometry(QtCore.QRect(x + 40, y + 10, 480, 25))
            objectdict['label'].setObjectName("comboBox")
            objectdict['label'].setText(fromcategory)
            objectdict['combobox'] = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
            objectdict['combobox'].setGeometry(QtCore.QRect( x + 550, y + 10, 485, 25))
            objectdict['combobox'].setObjectName("comboBox" + str(index))
            objectdict['combobox'].setModel(itemmodel)
            objectdict['combobox'].setEditable(True)
            self.objectlist.append(objectdict)
            y = y + 35

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.retranslateUi(frcd)
        self.buttonBox.accepted.connect(frcd.accept)
        self.buttonBox.rejected.connect(frcd.reject)
        QtCore.QMetaObject.connectSlotsByName(frcd)

    def retranslateUi(self, FindReplaceCopy):
        _translate = QtCore.QCoreApplication.translate
        FindReplaceCopy.setWindowTitle(_translate("FindReplaceCopy", "Dialog"))
        self.label.setText(_translate("FindReplaceCopy",
                                      "<html><head/><body><p>Each entry on the left is one of the source categories present in your content. </p><p>From the drop downs on the right select the source categories you want to replace them with or type your own. These have been populated from your destination org/tenant. </p><p>Checked items will be replaced, unchecked items will be ignored. </p></body></html>"))


class sumotoolbox(QtWidgets.QMainWindow, Ui_MainWindow):



    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        # detect if we are running in a pyinstaller bundle and set the base directory for file loads"
        if getattr(sys, 'frozen', False):
            self.basedir = sys._MEIPASS
        else:
            self.basedir = os.path.dirname(__file__)

        self.setupUi(self)





        # set up some variables we'll need later to do stuff. These are attached to the pyqt5 objects so they
        # persist through method calls (you can't return values from methods called with signals)
        self.contentListWidgetLeft.currentContent = {}
        self.contentListWidgetRight.currentContent = {}
        self.contentListWidgetLeft.currentdirlist = []
        self.contentListWidgetRight.currentdirlist = []

        self.initModels()  # load all the comboboxes and such with values
        self.loadcredentials()  # if a credential file exists populate the creds with values
        # connect all of the UI button elements to their respective methods

        #Set up a signal if the tabs are clicked
        self.tabWidget.currentChanged.connect(self.tabchange)

        # UI Buttons for Collection API tab
        self.pushButtonUpdateListLeft.clicked.connect(lambda: self.updatecollectorlist(
            self.listWidgetLeftCollectors,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())))

        self.pushButtonUpdateListRight.clicked.connect(lambda: self.updatecollectorlist(
            self.listWidgetRightCollectors,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text())))

        self.pushButtonCopySourcesLeftToRight.clicked.connect(lambda: self.copysources(
            self.listWidgetLeftCollectors,
            self.listWidgetRightCollectors,
            self.listWidgetLeftSources,
            self.listWidgetRightSources,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()) ))

        self.pushButtonCopySourcesRightToLeft.clicked.connect(lambda: self.copysources(
            self.listWidgetRightCollectors,
            self.listWidgetLeftCollectors,
            self.listWidgetRightSources,
            self.listWidgetLeftSources,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()) ))

        self.pushButtonBackupCollectorLeft.clicked.connect(lambda: self.backupcollector(
            self.listWidgetLeftCollectors,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())))

        self.pushButtonBackupCollectorRight.clicked.connect(lambda: self.backupcollector(
            self.listWidgetRightCollectors,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text())))

        self.pushButtonDeleteCollectorLeft.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetLeftCollectors,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())
        ))

        self.pushButtonDeleteCollectorRight.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetRightCollectors,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text())
        ))

        self.pushButtonDeleteSourcesLeft.clicked.connect(lambda: self.deletesources(
            self.listWidgetLeftCollectors,
            self.listWidgetLeftSources,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())
        ))

        self.pushButtonDeleteSourcesRight.clicked.connect(lambda: self.deletesources(
            self.listWidgetRightCollectors,
            self.listWidgetRightSources,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text())
        ))

        # self.pushButtonRestoreSources.clicked.connect(self.restoresources)

        # set up a signal to update the source list if a new collector is set
        self.listWidgetLeftCollectors.itemSelectionChanged.connect(lambda: self.updatesourcelist(
            self.listWidgetLeftCollectors,
            self.listWidgetLeftSources,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())
        ))

        self.listWidgetRightCollectors.itemSelectionChanged.connect(lambda: self.updatesourcelist(
            self.listWidgetRightCollectors,
            self.listWidgetRightSources,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text())
        ))

        # UI Buttons for Search API Tab
        self.pushButtonStartSearch.clicked.connect(lambda: self.runsearch(
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())
        ))

        # Content Pane Signals
        # Left Side
        self.pushButtonUpdateContentLeft.clicked.connect(lambda: self.updatecontentlist(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.contentListWidgetLeft.itemDoubleClicked.connect(lambda item: self.doubleclickedcontentlist(
            item,
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonParentDirContentLeft.clicked.connect(lambda: self.parentdircontentlist(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.buttonGroupContentLeft.buttonClicked.connect(lambda: self.contentradiobuttonchanged(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft,
            self.pushButtonContentDeleteLeft
        ))

        self.pushButtonContentNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentDeleteLeft.clicked.connect(lambda: self.delete_content(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentCopyLeftToRight.clicked.connect(lambda: self.copycontent(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentFindReplaceCopyLeftToRight.clicked.connect(lambda: self.findreplacecopycontent(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        # Right Side
        self.pushButtonUpdateContentRight.clicked.connect(lambda: self.updatecontentlist(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.contentListWidgetRight.itemDoubleClicked.connect(lambda item: self.doubleclickedcontentlist(
            item,
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonParentDirContentRight.clicked.connect(lambda: self.parentdircontentlist(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.buttonGroupContentRight.buttonClicked.connect(lambda: self.contentradiobuttonchanged(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight,
            self.pushButtonContentDeleteRight
        ))

        self.pushButtonContentNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentDeleteRight.clicked.connect(lambda: self.delete_content(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentCopyRightToLeft.clicked.connect(lambda: self.copycontent(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text()),
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text()),
            self.buttonGroupContentRight.checkedId(),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

    # Start methods for Content Tab

    def findreplacecopycontent(self, ContentListWidgetFrom, ContentListWidgetTo, fromurl, fromid, fromkey, tourl, toid, tokey,
                    fromradioselected, toradioselected, todirectorylabel):

        logger.info("Copying Content")

        selecteditems = ContentListWidgetFrom.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                exportsuccessful = False
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                if (toradioselected == -2):  # Personal Folder Selected
                    contents = []
                    for selecteditem in selecteditems:
                        for child in ContentListWidgetFrom.currentContent['children']:
                            if child['name'] == str(selecteditem.text()):
                                item_id = child['id']
                                contents.append(fromsumo.export_content_job_sync(item_id))
                                exportsuccessful = True
                elif toradioselected == -4:  # Admin Recommended Folders Selected
                    currentdir = ContentListWidgetTo.currentdirlist[-1]
                    if currentdir['id'] != 'TOP':
                        contents = []
                        for selecteditem in selecteditems:
                            for child in ContentListWidgetFrom.currentContent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']
                                    contents.append(fromsumo.export_content_job_sync(item_id))
                                    exportsuccessful = True
            except Exception as e:
                logger.exception(e)
                self.errorbox('Source:Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
            if exportsuccessful:
                categories=[]
                for content in contents:
                    contentstring = json.dumps(content)
                    categories = categories + re.findall(r'\"_sourceCategory\s*=\s*([^\s\\|]*)', contentstring)
                uniquecategories = list(set(categories))  # dedup the list
                print(len(uniquecategories))
                list2 = ['test','test2']
                dialog = findReplaceCopyDialog(uniquecategories, list2)
                dialog.exec()
                dialog.show()

        else:
            self.errorbox('You have not made any selections.')
            return


    def copycontent(self, ContentListWidgetFrom, ContentListWidgetTo, fromurl, fromid, fromkey, tourl, toid, tokey, fromradioselected, toradioselected, todirectorylabel):
        logger.info("Copying Content")
        try:
            selecteditems = ContentListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                if (toradioselected == -2):  # Personal Folder Selected
                    for selecteditem in selecteditems:
                        for child in ContentListWidgetFrom.currentContent['children']:
                            if child['name'] == str(selecteditem.text()):
                                item_id = child['id']
                                content = fromsumo.export_content_job_sync(item_id)
                                tofolderid = ContentListWidgetTo.currentContent['id']
                                status = tosumo.import_content_job_sync(tofolderid, content)
                                self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected, todirectorylabel)
                    return
                elif toradioselected == -4:  # Admin Recommended Folders Selected
                    currentdir = ContentListWidgetTo.currentdirlist[-1]
                    if currentdir['id'] != 'TOP':
                        for selecteditem in selecteditems:
                            for child in ContentListWidgetFrom.currentContent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']
                                    content = fromsumo.export_content_job_sync(item_id)
                                    tofolderid = ContentListWidgetTo.currentContent['id']
                                    status = tosumo.import_content_job_sync(tofolderid, content, adminmode=True)
                                    self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected, todirectorylabel)
                        return
                    else:
                        self.errorbox(
                            'Sorry, this tool in not currently capable of copying to the top-level directory in the Admin Recommended folder due to API limitations. Suggested workaround is to make the top level folder in the SumoLogic UI and then copy content into it. This should be fixed soon!')

            else:
                self.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')

    def create_folder(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        message = '''
    Please enter the name of the folder you wish to create:
        
                    '''
        text, result = QtWidgets.QInputDialog.getText(self, 'Create Folder...', message)
        for item in ContentListWidget.currentContent['children']:
            if item['name'] == str(text):
                self.errorbox('That Directory Name Already Exists!')
                return
        try:
            if radioselected == -2:  # if "Personal Folder" radio button is selected
                logger.info("Creating New Folder in Personal Folder Tree")
                sumo = SumoLogic(id, key, endpoint=url)
                error = sumo.create_folder(str(text), str(ContentListWidget.currentContent['id']))

                self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                return
            elif radioselected == -4:  # "Admin Folders" is selected
                logger.info("Creating New Folder in Admin Recommended Folder Tree")
                currentdir = ContentListWidget.currentdirlist[-1]
                if currentdir['id'] != 'TOP':
                    sumo = SumoLogic(id, key, endpoint=url)
                    error = sumo.create_folder(str(text), str(ContentListWidget.currentContent['id']), adminmode=True)

                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                    return
                else:
                    self.errorbox('Sorry, this tool in not currently capable of creating a top-level directory in the Admin Recommended folder due to API limitations. Creating sub-folders works fine. Suggested workaround is to make the top level folder in the SumoLogic UI and then use this tool to copy content into it. This should be fixed soon!')
                    return
        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')

    def delete_content(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("Deleting Content")
        selecteditems = ContentListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            message = "You are about to delete the following item(s):\n\n"
            for selecteditem in selecteditems:
                message = message + str(selecteditem.text()) + "\n"
            message = message + '''
This is exceedingly DANGEROUS!!!! 
Please be VERY, VERY, VERY sure you want to do this!
You could lose quite a bit of work if you delete the wrong thing(s).

If you are absolutely sure, type "DELETE" in the box below.

                    '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text) == 'DELETE')):
                try:
                    if radioselected == -2:  # if "Personal Folder" radio button is selected
                        sumo = SumoLogic(id, key, endpoint=url)
                        for selecteditem in selecteditems:

                            for child in ContentListWidget.currentContent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']

                            result = sumo.delete_content_job_sync(item_id)

                        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    elif radioselected == -4:  # "Admin Folders" is selected
                        sumo = SumoLogic(id, key, endpoint=url)
                        for selecteditem in selecteditems:

                            for child in ContentListWidget.currentContent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']

                            result = sumo.delete_content_job_sync(item_id)

                        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('This tool is not currently capableYou Cannot Delete The Shared Content of other Users.')
                        return

                except Exception as e:
                    logger.exception(e)
                    self.errorbox('Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')

    def contentradiobuttonchanged(self, ContentListWidget,url, id, key, radioselected, directorylabel, pushButtonContentDelete):
        ContentListWidget.currentdirlist = []
        if radioselected == -2:
            pushButtonContentDelete.setEnabled(True)
        elif radioselected == -3:
            pushButtonContentDelete.setEnabled(False)
        else:
            pushButtonContentDelete.setEnabled(True)
        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)

    def updatecontentlist(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        sumo = SumoLogic(id, key, endpoint=url)
        if ContentListWidget.currentdirlist:
            currentdir = ContentListWidget.currentdirlist[-1]
        else:
            currentdir = {'name': None, 'id': 'TOP'}
        try:
            if (not ContentListWidget.currentContent) or (currentdir['id'] == 'TOP'):
                if radioselected == -2:  # if "Personal Folder" radio button is selected
                    logger.info("Updating Personal Folder List")
                    ContentListWidget.currentContent = sumo.get_personal_folder()

                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Personal Folder', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentContent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Incorrect Credentials or Wrong Endpoint.')
                        return
                elif radioselected == -3:  # if "Global Folders" radio button is selected
                    logger.info("Updating Global Folder List")
                    ContentListWidget.currentContent = sumo.get_global_folder_sync()

                    # Rename dict key from "data" to "children" for consistency
                    ContentListWidget.currentContent['children'] = ContentListWidget.currentContent.pop('data')
                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Global Folders', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentContent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Incorrect Credentials or Wrong Endpoint.')
                        return
                else:  # "Admin Folders" must be selected
                    logger.info("Updating Admin Folder List")
                    ContentListWidget.currentContent = sumo.get_admin_folder_sync()

                    # Rename dict key from "data" to "children" for consistency
                    ContentListWidget.currentContent['children'] = ContentListWidget.currentContent.pop('data')
                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Admin Recommended', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentContent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Incorrect Credentials or Wrong Endpoint.')
                        return

            else:
                ContentListWidget.currentContent = sumo.get_folder(currentdir['id'])
                self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                return

        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials or Wrong Endpoint.')
            return


    def doubleclickedcontentlist(self, item, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("Going Down One Content Folder")
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            for child in ContentListWidget.currentContent['children']:
                if (child['name'] == item.text()) and (child['itemType'] == 'Folder'):
                    ContentListWidget.currentContent = sumo.get_folder(child['id'])

                    dir = {'name': item.text(), 'id': child['id']}
                    ContentListWidget.currentdirlist.append(dir)

        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials or Wrong Endpoint.')
        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)

    def parentdircontentlist(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("Going Up One Content Folder")
        sumo = SumoLogic(id, key, endpoint=url)
        currentdir = ContentListWidget.currentdirlist[-1]
        if currentdir['id'] != 'TOP':
            parentdir = ContentListWidget.currentdirlist[-2]
        else:
            return
        try:

            if parentdir['id'] == 'TOP':
                ContentListWidget.currentdirlist = []
                self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                return

            else:
                ContentListWidget.currentdirlist.pop()
                ContentListWidget.currentContent = sumo.get_folder(parentdir['id'])

                self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                return
        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials or Wrong Endpoint.')


    def updatecontentlistwidget(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        try:
            ContentListWidget.clear()
            sumo = SumoLogic(id, key, endpoint=url)
            for object in ContentListWidget.currentContent['children']:
                item_name = ''
                if radioselected == -3:
                    logger.info("Getting User info for Global Folder")
                    user_info = sumo.get_user(object['id'])
                    item_name = '[' + user_info['firstName'] + ' ' + user_info['lastName'] + ']'
                item_name = item_name + object['name']
                item = ContentListWidget.addItem(item_name)  # populate the list widget in the GUI
                items = ContentListWidget.findItems(item_name, QtCore.Qt.MatchExactly)
                if object['itemType'] != 'Folder':
                    items[0].setForeground(QtGui.QBrush(QtCore.Qt.blue))

            dirname = ''
            for dir in ContentListWidget.currentdirlist:
                dirname = dirname + '/' + dir['name']
            directorylabel.setText(dirname)

        except Exception as e:
            logger.exception(e)


    # End Methods for Content Tab



    # Start Methods for Collector Tab
    def getcollectorid(self, collectorname, url, id, key):
        logger.info("Getting Collector IDs")
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            sumocollectors = sumo.collectors()

            for sumocollector in sumocollectors:
                if sumocollector['name'] == collectorname:
                    return sumocollector['id']
        except Exception as e:
            logger.exception(e)

            
    def getsourceid(self, collectorid, sourcename, url, id, key):
        logger.info("Getting Source IDs")
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            sumosources = sumo.sources(collectorid)

            for sumosource in sumosources:
                if sumosource['name'] == sourcename:
                    return sumosource['id']
            return False
        except Exception as e:
            logger.exception(e)


    def updatecollectorlist(self, CollectorListWidget, url, id, key):
        logger.info("Updating Collector List")
        CollectorListWidget.clear()  # clear the list first since it might already be populated
        regexprog = re.compile(r'\S+')  # make sure username and password have something in them
        if (re.match(regexprog, id) != None) and (re.match(regexprog, key) != None):
            # access the API with provided credentials
            sumo = SumoLogic(id, key, endpoint=url)
            try:
                collectors = sumo.collectors()  # get list of collectors


                for collector in collectors:
                    item = CollectorListWidget.addItem(collector['name'])  # populate the list widget in the GUI
                    items = CollectorListWidget.findItems(collector['name'], QtCore.Qt.MatchExactly)
                    if collector['collectorType'] == 'Installable':
                        print(len(items))
                        items[0].setForeground(QtGui.QBrush(QtCore.Qt.blue))
                    if collector['alive'] == False:
                        items[0].setData(6, QtGui.QFont("Arial",pointSize=10,italic=True))

            except Exception as e:
                logger.exception(e)
                self.errorbox('Incorrect Credentials or Wrong Endpoint.')

        else:
            self.errorbox('No user and/or password.')

    def updatesourcelist(self, CollectorListWidget, SourceListWidget, url, id, key):
        logger.info("Updating Source List")
        SourceListWidget.clear()  # clear the list first since it might already be populated
        collectors = CollectorListWidget.selectedItems()
        if (len(collectors) > 1) or (len(collectors) < 1):
            return
        else:
            collector = self.getcollectorid(collectors[0].text(), url, id, key)
            sumo = SumoLogic(id, key, endpoint=url)
            # populate the list of sources
            sources = sumo.sources(collector)
            for source in sources:
                SourceListWidget.addItem(source['name'])  # populate the display with sources

    def copysources(self, CollectorListWidgetFrom, CollectorListWidgetTo, SourceListWidgetFrom, SourceListWidgetTo,
                    fromurl, fromid, fromkey, tourl, toid, tokey):
        logger.info("Copying Sources")
        try:
            fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
            sourcecollectorlist = CollectorListWidgetFrom.selectedItems()  # get the selected source collector
            if len(sourcecollectorlist) == 1:  # make sure there is a collector selected, otherwise bail
                sourcecollector = sourcecollectorlist[0].text()  # qstring to string conversion
                sourcecollectorid = self.getcollectorid(sourcecollector, fromurl, fromid, fromkey)
                destinationcollectorlist = CollectorListWidgetTo.selectedItems()  # get the selected dest collector
                if len(destinationcollectorlist) == 1:  # make sure there is a collector selected, otherwise bail
                    destinationcollectorname = destinationcollectorlist[0].text()
                    destinationcollectorid = self.getcollectorid(destinationcollectorname, tourl, toid,
                                                                 tokey)  # qstring to string conversion
                    tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                    fromsources = SourceListWidgetFrom.selectedItems()  # get the selected sources
                    if len(fromsources) > 0:  # make sure at least one source is selected
                        fromsourcelist = []
                        for fromsource in fromsources:  # iterate through source names to build a warning message
                            fromsourcelist.append(fromsource.text())
                        message = "You are about to copy the following sources from collector \"" + sourcecollector + "\" to \"" + destinationcollectorname + "\". Is this correct? \n\n"
                        for source in fromsourcelist:
                            message = message + source + "\n"
                        result = QtWidgets.QMessageBox.question(self, 'Really Copy?', message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)# bring up the copy dialog
                        if result:  # If they clicked "OK" rather than cancel
                            sumosources = fromsumo.sources(sourcecollectorid)
                            for source in fromsourcelist:  # iterate through the selected sources and copy them
                                for sumosource in sumosources:
                                    if sumosource['name'] == source:
                                        if 'id' in sumosource:  # the API creates an ID so this must be deleted before sending
                                            del sumosource['id']
                                        if 'alive' in sumosource:
                                            del sumosource[
                                                'alive']  # the API sets this itself so this must be deleted before sending
                                        template = {}
                                        template[
                                            'source'] = sumosource  # the API expects a dict with a key called 'source'
                                        notduplicate = True
                                        sumotosourcelist = tosumo.sources(destinationcollectorid)
                                        for sumotosource in sumotosourcelist:
                                            if sumotosource[
                                                'name'] == source:  # make sure the source doesn't already exist in the destination
                                                notduplicate = False
                                        if notduplicate:  # finally lets copy this thing
                                            tosumo.create_source(destinationcollectorid, template)
                                        else:
                                            self.errorbox(source + ' already exists, skipping.')
                            # call the update method for the dest sources since they have changed after the copy
                            self.updatesourcelist(CollectorListWidgetTo, SourceListWidgetTo, tourl, toid, tokey)

                    else:
                        self.errorbox('No Sources Selected.')
                else:
                    self.errorbox('You Must Select Exactly 1 Destination Collector.')
            else:
                self.errorbox('No Source Collector Selected.')
        except Exception as e:
            self.errorbox('Encountered a bug. Check the console output.')
            logger.exception(e)
            traceback.print_exc()

    def backupcollector(self, CollectorListWidget, url, id, key):
        logger.info("Backing Up Collector")
        collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
        if len(collectornamesqstring) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url)
                for collectornameqstring in collectornamesqstring:
                    collectorid = self.getcollectorid(str(collectornameqstring.text()), url, id, key)
                    savefilepath = pathlib.Path(savepath + r'/' + str(collectornameqstring.text()) + r'.json')
                    savefilesourcespath = pathlib.Path(savepath + r'/' + str(collectornameqstring.text()) + r'_sources' + r'.json')

                    if savefilepath:
                        with savefilepath.open(mode='w') as filepointer:
                            json.dump(sumo.collector(collectorid), filepointer)
                    if savefilesourcespath:
                        with savefilesourcespath.open(mode='w') as filepointer:
                            json.dump(sumo.sources(collectorid), filepointer)
                    message = message + str(collectornameqstring.text()) + ' '
                self.infobox('Wrote files ' + message)
            else:
                self.errorbox("You don't have permissions to write to that directory")

        else:
            self.errorbox('No Source Collector Selected.')

    def deletecollectors(self, CollectorListWidget, url, id, key):
        logger.info("Deleting Collectors")
        collectornamesqstring = CollectorListWidget.selectedItems()
        if len(collectornamesqstring) > 0:  # make sure something was selected
            message = "You are about to delete the following collector(s):\n\n"
            for collectornameqstring in collectornamesqstring:
                message = message + str(collectornameqstring.text()) + "\n"
            message = message + '''
This is exceedingly DANGEROUS!!!! 
Please be VERY, VERY, VERY sure you want to do this!
Even if you have backed up your collectors to file you CANNOT
restore installed collectors using this tool or the Sumo Logic API.
    
If you are absolutely sure, type "DELETE" in the box below.
              
            '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text)=='DELETE')):
                sumo = SumoLogic(id, key, endpoint=url)
                for collectornameqstring in collectornamesqstring:
                    try:
                        collectorid = self.getcollectorid(str(collectornameqstring.text()), url, id, key)
                        sumo.delete_collector(collectorid)
                    except Exception as e:
                        self.errorbox('Failed to delete collector: ' + str(collectornamesqstring.text()))
                        logger.exception(e)
                        traceback.print_exc()
                self.updatecollectorlist(CollectorListWidget, url, id, key)

        else:
            self.errorbox('No Collector Selected')

    # This is broken and not connected to any button currently
    def restoresources(self):
        destinationcollector = self.ListWidgetRightCollectors.selectedItems()
        if len(destinationcollector) == 1:
            destinationcollectorqstring = destinationcollector[0]
            destinationcollector = str(destinationcollector[0].text())
            restorefile = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Open Backup..', selectedFilter='*.json'))
            sources = None
            try:
                with open(restorefile) as data_file:
                    sources = json.load(data_file)
            except Exception as e:
                self.errorbox('Failed to load JSON file.')
                logger.exception(e)
                traceback.print_exc()

            if sources:
                self.restoresourcesUI.dateTimeEdit.setMaximumDate(QtCore.QDate.currentDate())
                self.restoresourcesUI.dateTimeEdit.setDate(QtCore.QDate.currentDate())
                self.restoresourcesUI.listWidgetRestoreSources.clear()
                sourcedict = {}
                for source in sources:
                    sourcedict[source['name']] = ''
                for source in sourcedict:
                    self.restoresourcesUI.listWidgetRestoreSources.addItem(source)
                result = self.restoresourcesUI.exec_()
                overridecollectiondate = self.restoresourcesUI.checkBoxOverrideCollectionStartTime.isChecked()
                overridedate = self.restoresourcesUI.dateTimeEdit.dateTime()
                overridedatemillis = long(overridedate.currentMSecsSinceEpoch())
                if result:
                    selectedsources = self.restoresourcesUI.listWidgetRestoreSources.selectedItems()
                    if len(selectedsources) > 0:
                        for selectedsource in selectedsources:
                            for sumosource in sources:
                                if sumosource['name'] == str(selectedsource.text()):
                                    if 'id' in sumosource:
                                        del sumosource['id']
                                    if 'alive' in sumosource:
                                        del sumosource['alive']
                                    if overridecollectiondate:
                                        sumosource['cutoffTimestamp'] = overridedatemillis
                                    template = {}
                                    template['source'] = sumosource
                                    notduplicate = True
                                    for sumodest in self.destinationsources:
                                        if sumodest['name'] == source:
                                            notduplicate = False
                                    if notduplicate:
                                        self.sumodestination.create_source(
                                            self.destinationcollectordict[destinationcollector], template)
                                    else:
                                        self.errorbox(source + ' already exists, skipping.')
                            self.updatedestinationlistsource(destinationcollectorqstring, destinationcollectorqstring)
                    else:
                        self.errorbox('No sources selected for import.')





        else:
            self.errorbox('No Destination Collector Selected.')

    def deletesources(self, CollectorListWidget, SourceListWidget, url, id, key):
        logger.info("Deleting Sources")
        collectornamesqstring = CollectorListWidget.selectedItems()
        if  len(collectornamesqstring) == 1:  # make sure something was selected
            collectorid = self.getcollectorid(str(collectornamesqstring[0].text()), url, id, key)
            sourcenamesqstring = SourceListWidget.selectedItems()
            if len(sourcenamesqstring) > 0:  # make sure something was selected
                message = "You are about to delete the following source(s):\n\n"
                for sourcenameqstring in sourcenamesqstring:
                    message = message + str(sourcenameqstring.text()) + "\n"
                message = message + '''
This could be exceedingly DANGEROUS!!!! 
Please be VERY, VERY, VERY sure you want to do this!
                
If you are absolutely sure, type "DELETE" in the box below.
    
                        '''
                text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
                if (result and (str(text) == 'DELETE')):
                    sumo = SumoLogic(id, key, endpoint=url)
                    for sourcenameqstring in sourcenamesqstring:
                        try:
                            sourceid = self.getsourceid(collectorid, str(sourcenameqstring.text()), url, id, key)
                            sumo.delete_source(collectorid, sourceid)
                        except Exception as e:
                            self.errorbox('Failed to delete source: ' + str(sourcenameqstring.text()))
                            logger.exception(e)
                            traceback.print_exc()
                    self.updatesourcelist(CollectorListWidget, SourceListWidget, url, id, key)

            else:
                self.errorbox('No Source(s) Selected')
        else:
            self.errorbox('You must select 1 and only 1 collector.')
    # End Methods for Collector Tab

    # Start Methods for Search Tab
    def runsearch(self, url, id, key):
        logger.info("Running a Search")
        self.tableWidgetSearchResults.clear()
        selectedtimezone = str(self.comboBoxTimeZone.currentText())
        starttime = str(self.dateTimeEditSearchStartTime.dateTime().toString(QtCore.Qt.ISODate))
        endtime = str(self.dateTimeEditSearchEndTime.dateTime().toString(QtCore.Qt.ISODate))
        searchstring = str(self.plainTextEditSearch.toPlainText())
        regexprog = re.compile(r'\S+')
        jobsubmitted = False
        savetofile = self.checkBoxSaveSearch.isChecked()
        converttimefromepoch = self.checkBoxConvertTimeFromEpoch.isChecked()
        self.jobmessages = []
        self.jobrecords = []

        if (re.match(regexprog, id) != None) and (re.match(regexprog, key) != None):
            sumo = SumoLogic(id, key, endpoint=url)

            if (re.match(regexprog, searchstring)) != None:
                try:
                    searchjob = sumo.search_job(searchstring, starttime, endtime, selectedtimezone)
                    jobsubmitted = True
                except:
                    self.errorbox('Incorrect Credentials.')
                if jobsubmitted:
                    self.labelSearchResultCount.setText('0')
                    jobstatus = sumo.search_job_status(searchjob)
                    nummessages = jobstatus['messageCount']
                    numrecords = jobstatus['recordCount']
                    self.labelSearchResultCount.setText(str(nummessages))
                    while jobstatus['state'] == 'GATHERING RESULTS':
                        jobstatus = sumo.search_job_status(searchjob)
                        numrecords = jobstatus['recordCount']
                        nummessages = jobstatus['messageCount']
                        self.labelSearchResultCount.setText(str(nummessages))
                    if nummessages is not 0:

                        # return messages
                        if self.buttonGroupOutputType.checkedId() == -2:
                            iterations = nummessages // 10000 + 1
                            for iteration in range(1, iterations + 1):
                                messages = sumo.search_job_messages(searchjob, limit=10000,
                                                                               offset=((iteration - 1) * 10000))
                                for message in messages['messages']:
                                    self.jobmessages.append(message)
                            self.tableWidgetSearchResults.setRowCount(len(self.jobmessages))
                            self.tableWidgetSearchResults.setColumnCount(2)
                            self.tableWidgetSearchResults.setHorizontalHeaderLabels(['time', '_raw'])
                            index = 0
                            for message in self.jobmessages:
                                if converttimefromepoch:
                                    timezone = pytz.timezone(selectedtimezone)
                                    converteddatetime = datetime.fromtimestamp(
                                        float(message['map']['_messagetime']) / 1000, timezone)
                                    timestring = str(converteddatetime.strftime('%Y-%m-%d %H:%M:%S'))
                                    message['map']['_messagetime'] = timestring
                                self.tableWidgetSearchResults.setItem(index, 0, QtWidgets.QTableWidgetItem(
                                    message['map']['_messagetime']))
                                self.tableWidgetSearchResults.setItem(index, 1,
                                                                      QtWidgets.QTableWidgetItem(message['map']['_raw']))
                                index += 1
                            self.tableWidgetSearchResults.resizeRowsToContents()
                            self.tableWidgetSearchResults.resizeColumnsToContents()
                            if savetofile:
                                filenameqstring, filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save CSV', 'logexport.csv', filter='*.csv')
                                filename = str(filenameqstring)
                                savefilepath = pathlib.Path(filename)
                                if savefilepath:
                                    try:
                                        with savefilepath.open(mode='w') as csvfile:
                                            messagecsv = csv.DictWriter(csvfile, self.jobmessages[0]['map'].keys())
                                            messagecsv.writeheader()
                                            for entry in self.jobmessages:
                                                messagecsv.writerow(entry['map'])
                                    except Exception as e:
                                        self.errorbox("Failed writing. Check destination permissions.")
                                        logger.exception(e)
                                        traceback.print_exc()
                        # return records
                        if self.buttonGroupOutputType.checkedId() == -3:
                            iterations = numrecords // 10000 + 1
                            for iteration in range(1, iterations + 1):
                                records = sumo.search_job_records(searchjob, limit=10000,
                                                                             offset=((iteration - 1) * 10000))
                                for record in records['records']:
                                    self.jobrecords.append(record)
                            self.tableWidgetSearchResults.setRowCount(len(self.jobrecords))
                            numfields = len(records['fields'])
                            self.tableWidgetSearchResults.setColumnCount(numfields)
                            fieldnames = []
                            for field in records['fields']:
                                fieldnames.append(field['name'])
                            self.tableWidgetSearchResults.setHorizontalHeaderLabels(fieldnames)
                            index = 0
                            if len(self.jobrecords) > 0:
                                for record in self.jobrecords:
                                    columnnum = 0
                                    for fieldname in fieldnames:
                                        if converttimefromepoch and (fieldname == '_timeslice'):
                                            timezone = pytz.timezone(selectedtimezone)
                                            converteddatetime = datetime.fromtimestamp(
                                                float(record['map'][fieldname]) / 1000, timezone)
                                            timestring = str(converteddatetime.strftime('%Y-%m-%d %H:%M:%S'))
                                            record['map']['_timeslice'] = timestring
                                        self.tableWidgetSearchResults.setItem(index, columnnum, QtWidgets.QTableWidgetItem(
                                            record['map'][fieldname]))
                                        columnnum += 1
                                    index += 1
                                self.tableWidgetSearchResults.resizeRowsToContents()
                                self.tableWidgetSearchResults.resizeColumnsToContents()
                                if savetofile:
                                    filenameqstring, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save CSV', '', filter='*.csv')
                                    filename = str(filenameqstring)
                                    savefilepath = pathlib.Path(filename)
                                    if savefilepath:
                                        try:
                                            with savefilepath.open(mode='w') as csvfile:
                                                recordcsv = csv.DictWriter(csvfile, self.jobrecords[0]['map'].keys())
                                                recordcsv.writeheader()
                                                for entry in self.jobrecords:
                                                    recordcsv.writerow(entry['map'])
                                        except Exception as e:
                                            self.errorbox("Failed writing. Check destination permissions.")
                                            logger.exception(e)
                                            traceback.print_exc()
                            else:
                                self.errorbox('Search did not return any records.')
                    else:
                        self.errorbox('Search did not return any messages.')
            else:
                self.errorbox('Please enter a search.')
        else:
            self.errorbox('No user and/or password.')
    # End Methods for Search Tab

    # Start Misc/Utility Methods
    def tabchange(self, index):
        if index == 0:
            self.ComboBoxRightRegion.setEnabled(True)
            self.LineEditRightUserName.setEnabled(True)
            self.LineEditRightPassword.setEnabled(True)
        if index == 1:
            self.ComboBoxRightRegion.setEnabled(True)
            self.LineEditRightUserName.setEnabled(True)
            self.LineEditRightPassword.setEnabled(True)
        if index == 2:
            self.ComboBoxRightRegion.setEnabled(False)
            self.LineEditRightUserName.setEnabled(False)
            self.LineEditRightPassword.setEnabled(False)

    def loadcredentials(self):
        logger.info("Looking for Credential File")
        # look to see if the credential file exists and load credentials if it does
        # fail if anything at all goes wrong
        if os.path.isfile(os.path.join(self.basedir, 'data/credentials.json')):
            try:
                with open(os.path.join(self.basedir, 'data/credentials.json'), 'r') as filepointer:
                    credentials = json.load(filepointer)
                self.LineEditLeftUserName.setText(credentials['source']['user'])
                self.LineEditLeftPassword.setText(credentials['source']['password'])
                self.LineEditRightUserName.setText(credentials['destination']['user'])
                self.LineEditRightPassword.setText(credentials['destination']['password'])
                logger.info("Found it! Creds will be populated.")
            except Exception as e:
                print("failed to load creds")
                logger.exception(e)
        else:
            logger.info("Didn't find it. :(  Creds will be blank.")


    def errorbox(self, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText(message)
        msgBox.addButton(QtWidgets.QPushButton('OK'), QtWidgets.QMessageBox.RejectRole)
        ret = msgBox.exec_()

    def infobox(self, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Info')
        msgBox.setText(message)
        msgBox.addButton(QtWidgets.QPushButton('OK'), QtWidgets.QMessageBox.RejectRole)
        ret = msgBox.exec_()

    def initModels(self):
        # Load API Endpoint List from file and create model for the comboboxes
        with open(os.path.join(self.basedir, 'data/apiurls.json'), 'r') as infile:
            self.loadedapiurls = json.load(infile)

        self.apiurlsmodel = QtGui.QStandardItemModel()
        for key in self.loadedapiurls:
            text_item = QtGui.QStandardItem(key)
            self.apiurlsmodel.appendRow(text_item)

        self.ComboBoxLeftRegion.setModel(self.apiurlsmodel)
        self.ComboBoxRightRegion.setModel(self.apiurlsmodel)

        # Load Timezones and create model for timezone combobox

        self.timezonemodel = QtGui.QStandardItemModel()
        for zone in pytz.common_timezones:
            text_item = QtGui.QStandardItem(zone)
            self.timezonemodel.appendRow(text_item)

        self.comboBoxTimeZone.setModel(self.timezonemodel)

        # set search start and endtimes to now-ish
        self.dateTimeEditSearchStartTime.setDateTime(QtCore.QDateTime.currentDateTime().addSecs(-900))
        self.dateTimeEditSearchEndTime.setDateTime(QtCore.QDateTime.currentDateTime())

        # set timezone combobox to local timezone
        localtimezone = str(get_localzone())
        index = self.comboBoxTimeZone.findText(localtimezone, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.comboBoxTimeZone.setCurrentIndex(index)
    # End Misc/Utility Methods

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = sumotoolbox()
    window.show()
    sys.exit(app.exec_())
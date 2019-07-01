__author__ = 'Tim MacDonald'
# Copyright 2015 Timothy MacDonald
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import sys
import json
import re
import csv
import pytz
import os.path
from datetime import datetime
from tzlocal import get_localzone
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pathlib
import os
import logzero
from logzero import logger
import configparser
import shutil

#local imports
from sumologic import SumoLogic
from credentials import CredentialsDB
from dialogs import *

# detect if in Pyinstaller package and build appropriate base directory path
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

# Setup logging
logzero.logfile("sumotoolbox.log")
logzero.loglevel(level=20)  #  Info Logging
# Log messages
logger.info("SumoLogicToolBox started.")

# This script uses Qt Designer files to define the UI elements which must be loaded
qtMainWindowUI = os.path.join(basedir, 'data/sumotoolbox.ui')

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindowUI)



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

        # variable to hold whether we've authenticated the cred database
        self.cred_db_authenticated = False
        # set up some variables we'll need later to do stuff. These are attached to the pyqt5 objects so they
        # persist through method calls (you can't return values from methods called with signals)
        self.reset_stateful_objects()

        self.initModels()  # load all the comboboxes and such with values

        # load the config file and if it doesn't exist copy it from the template
        self.init_and_load_config_file()

        # Configure the creddb buttons according to the config file settings
        self.initial_config_cred_db_buttons()


        # connect all of the UI button elements to their respective methods

        #Set up a signal if the tabs are clicked
        self.tabWidget.currentChanged.connect(self.tabchange)

        #UI Buttons for Credential Store

        self.pushButtonCreateCredentialDatabase.clicked.connect(self.createcredb)
        self.pushButtonLoadCredentialDatabase.clicked.connect(self.loadcreddb)
        self.pushButtonDeleteCredentialDatabase.clicked.connect(self.deletecreddb)

        # Left Preset Buttons

        self.pushButtonCreatePresetLeft.clicked.connect(lambda: self.create_preset(
            self.comboBoxRegionLeft,
            self.lineEditUserNameLeft,
            self.lineEditPasswordLeft,
            self.comboBoxPresetLeft,
            'left'
        ))

        self.comboBoxPresetLeft.currentIndexChanged.connect(lambda: self.load_preset(
            str(self.comboBoxPresetLeft.currentText()),
            self.comboBoxRegionLeft,
            self.lineEditUserNameLeft,
            self.lineEditPasswordLeft,
            self.comboBoxPresetLeft,
            'left'
        ))

        self.pushButtonDeletePresetLeft.clicked.connect(lambda: self.delete_preset(
            str(self.comboBoxPresetLeft.currentText()),
            self.comboBoxRegionLeft,
            self.lineEditUserNameLeft,
            self.lineEditPasswordLeft,
            self.comboBoxPresetLeft,
            'left'
        ))

        self.pushButtonUpdatePresetLeft.clicked.connect(lambda: self.update_preset(
            str(self.comboBoxPresetLeft.currentText()),
            str(self.comboBoxRegionLeft.currentText()),
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        # Right Preset Buttons

        self.pushButtonCreatePresetRight.clicked.connect(lambda: self.create_preset(
            self.comboBoxRegionRight,
            self.lineEditUserNameRight,
            self.lineEditPasswordRight,
            self.comboBoxPresetRight,
            'right'
        ))

        self.comboBoxPresetRight.currentIndexChanged.connect(lambda: self.load_preset(
            str(self.comboBoxPresetRight.currentText()),
            self.comboBoxRegionRight,
            self.lineEditUserNameRight,
            self.lineEditPasswordRight,
            self.comboBoxPresetRight,
            'right'
        ))

        self.pushButtonDeletePresetRight.clicked.connect(lambda: self.delete_preset(
            str(self.comboBoxPresetRight.currentText()),
            self.comboBoxRegionRight,
            self.lineEditUserNameRight,
            self.lineEditPasswordRight,
            self.comboBoxPresetRight,
            'right'
        ))

        self.pushButtonUpdatePresetRight.clicked.connect(lambda: self.update_preset(
            str(self.comboBoxPresetRight.currentText()),
            str(self.comboBoxRegionRight.currentText()),
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        # UI Buttons for Collection API tab
        self.pushButtonUpdateListLeft.clicked.connect(lambda: self.updatecollectorlist(
            self.listWidgetCollectorsLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateListRight.clicked.connect(lambda: self.updatecollectorlist(
            self.listWidgetCollectorsRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        self.pushButtonCopySourcesLeftToRight.clicked.connect(lambda: self.copysources(
            self.listWidgetCollectorsLeft,
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesLeft,
            self.listWidgetSourcesRight,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        self.pushButtonCopySourcesRightToLeft.clicked.connect(lambda: self.copysources(
            self.listWidgetCollectorsRight,
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesRight,
            self.listWidgetSourcesLeft,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupCollectorLeft.clicked.connect(lambda: self.backupcollector(
            self.listWidgetCollectorsLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupCollectorRight.clicked.connect(lambda: self.backupcollector(
            self.listWidgetCollectorsRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteCollectorLeft.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetCollectorsLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteCollectorRight.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetCollectorsRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteSourcesLeft.clicked.connect(lambda: self.deletesources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteSourcesRight.clicked.connect(lambda: self.deletesources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        # set up a signal to update the source list if a new collector is set
        self.listWidgetCollectorsLeft.itemSelectionChanged.connect(lambda: self.updatesourcelist(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.listWidgetCollectorsRight.itemSelectionChanged.connect(lambda: self.updatesourcelist(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        # UI Buttons for Search API Tab
        self.pushButtonStartSearch.clicked.connect(lambda: self.runsearch(
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        # Content Pane Signals
        # Left Side
        self.pushButtonUpdateContentLeft.clicked.connect(lambda: self.updatecontentlist(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.contentListWidgetLeft.itemDoubleClicked.connect(lambda item: self.doubleclickedcontentlist(
            item,
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonParentDirContentLeft.clicked.connect(lambda: self.parentdircontentlist(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.buttonGroupContentLeft.buttonClicked.connect(lambda: self.contentradiobuttonchanged(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft,
            self.pushButtonContentDeleteLeft
        ))

        self.pushButtonContentNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentDeleteLeft.clicked.connect(lambda: self.delete_content(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentCopyLeftToRight.clicked.connect(lambda: self.copycontent(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentFindReplaceCopyLeftToRight.clicked.connect(lambda: self.findreplacecopycontent(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        # Right Side
        self.pushButtonUpdateContentRight.clicked.connect(lambda: self.updatecontentlist(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.contentListWidgetRight.itemDoubleClicked.connect(lambda item: self.doubleclickedcontentlist(
            item,
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonParentDirContentRight.clicked.connect(lambda: self.parentdircontentlist(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.buttonGroupContentRight.buttonClicked.connect(lambda: self.contentradiobuttonchanged(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight,
            self.pushButtonContentDeleteRight
        ))

        self.pushButtonContentNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentDeleteRight.clicked.connect(lambda: self.delete_content(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentCopyRightToLeft.clicked.connect(lambda: self.copycontent(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentRight.checkedId(),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentFindReplaceCopyRightToLeft.clicked.connect(lambda: self.findreplacecopycontent(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentRight.checkedId(),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentBackupLeft.clicked.connect(lambda: self.backupcontent(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text())
        ))

        self.pushButtonContentBackupRight.clicked.connect(lambda: self.backupcontent(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text())
        ))

        self.pushButtonContentRestoreLeft.clicked.connect(lambda: self.restorecontent(
            self.contentListWidgetLeft,
            self.loadedapiurls[str(self.comboBoxRegionLeft.currentText())],
            str(self.lineEditUserNameLeft.text()),
            str(self.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentRestoreRight.clicked.connect(lambda: self.restorecontent(
            self.contentListWidgetRight,
            self.loadedapiurls[str(self.comboBoxRegionRight.currentText())],
            str(self.lineEditUserNameRight.text()),
            str(self.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))


    # method to reset all objects that are dependent on creds (such as collectors and content lists)
    def reset_stateful_objects(self, side='both'):

        if side == 'both':
            left = True
            right = True
        if side == 'left':
            left = True
            right = False
        if side == 'right':
            left = False
            right = True

        if left:
            self.listWidgetCollectorsLeft.clear()
            self.listWidgetSourcesLeft.clear()
            self.contentListWidgetLeft.clear()
            self.contentListWidgetLeft.currentcontent = {}
            self.contentListWidgetLeft.currentdirlist = []
            self.contentListWidgetLeft.updated = False

        if right:
            self.listWidgetCollectorsRight.clear()
            self.listWidgetSourcesRight.clear()
            self.contentListWidgetRight.clear()
            self.contentListWidgetRight.currentcontent = {}
            self.contentListWidgetRight.currentdirlist = []
            self.contentListWidgetRight.updated = False

        return

    # Start methods for Credential Database

    def createcredb(self):
        logger.info('Creating credential store')
        #check to see if there is already a dbfile and ask if it should be removed to create a new one
        db_file = pathlib.Path('credentials.db')
        if db_file.is_file():
            message = "It looks like you already have a credential database. Do you want to delete it (and it's passwords) and create a new one? If so type 'DELETE' in the box below:"
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text) == 'DELETE')):
                os.remove('credentials.db')
            else:
                return
        # get the password that will be used for the new database
        dialog = NewPasswordDialog()
        dialog.exec()
        dialog.show()
        if str(dialog.result()) == '1':
            password = dialog.getresults()
            if password:
                try:
                    # We pass a username here (from the config file) just in case someone has written their own
                    # version of the CredentialDB class that requires both a username/id AND password
                    # however the version distributed with sumologictoolbox ignores the username.
                    self.credentialstore = CredentialsDB(password, username=self.config['Credential Store']['username'], create_new=True)
                    # restrict permissions on the db file to just the user. May not be effective on Windows
                    os.chmod(str(db_file), 0o600)
                    self.cred_db_authenticated = True
                except Exception as e:
                    logger.exception(e)
                    self.errorbox("Something went wrong\n\n" + str(e))
                self.set_creddbbuttons()
                return
            else:
                return
        return

    def loadcreddb(self):
        logger.info('Loading credential store')
        db_file = pathlib.Path('credentials.db')
        if db_file.is_file():
            message = "Please enter your credentials database password."
            password, result = QtWidgets.QInputDialog.getText(self, 'Enter password', message, QtWidgets.QLineEdit.Password)
            if result:
                try:
                    # create the cred store instance
                    self.credentialstore = CredentialsDB(password)
                    self.cred_db_authenticated = True
                    # turn on the UI buttons
                    self.set_creddbbuttons()
                    # populate the preset dropdowns
                    self.populate_presets()
                    preset = self.comboBoxPresetLeft.currentText()
                    # load the first preset in the list (if it's there)
                    if preset:
                        self.load_preset(
                            preset,
                            self.comboBoxRegionLeft,
                            self.lineEditUserNameLeft,
                            self.lineEditPasswordLeft,
                            self.comboBoxPresetLeft,
                            'left'
                        )
                        self.load_preset(
                            preset,
                            self.comboBoxRegionRight,
                            self.lineEditUserNameRight,
                            self.lineEditPasswordRight,
                            self.comboBoxPresetLeft,
                            'right'
                        )

                        
                except Exception as e:
                    logger.exception(e)
                    self.errorbox(str(e))
                    self.cred_db_authenticated = False
                    self.set_creddbbuttons()
                return
            else:
                return
        else:
            self.errorbox("You don't appear to have a credentials database. You must create one first.")
            return
        return

    def deletecreddb(self):
        db_file = pathlib.Path('credentials.db')
        if db_file.is_file():
            message = '''
Do you really want to delete your credential database? 
If so type 'DELETE' in the box below:"

'''
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text) == 'DELETE')):
                os.remove(str(db_file))
                self.cred_db_authenticated = False
                self.set_creddbbuttons()

    def populate_presets(self):
        logger.info('Populating presets')
        self.comboBoxPresetLeft.clear()
        self.comboBoxPresetRight.clear()
        try:
            names = self.credentialstore.list_names()
            names = sorted(names,  key=str.lower)
            for name in names:
                self.comboBoxPresetLeft.addItem(name)
                self.comboBoxPresetRight.addItem(name)
        except Exception as e:
            logger.exception(e)
            self.errorbox('Something went wrong\n\n' + str(e))
        return

    def add_preset_to_combobox(self, preset):
        self.comboBoxPresetLeft.addItem(preset)
        self.comboBoxPresetRight.addItem(preset)
        return

    def remove_preset_from_combobox(self, preset):
        index = self.comboBoxPresetLeft.findText(preset)
        self.comboBoxPresetLeft.removeItem(index)
        index = self.comboBoxPresetRight.findText(preset)
        self.comboBoxPresetRight.removeItem(index)
        return

    # This is only used to configure the initial state of the credential db buttons
    def initial_config_cred_db_buttons(self):
        db_file = pathlib.Path('credentials.db')
        if db_file.is_file():
            db_file_exists = True
        else:
            db_file_exists = False
        config_value = self.config['Credential Store']['credential_store_implementation']
        if (config_value == 'built_in') and db_file_exists:
            self.pushButtonLoadCredentialDatabase.setEnabled(True)
            self.pushButtonCreateCredentialDatabase.setEnabled(False)
            self.pushButtonDeleteCredentialDatabase.setEnabled(True)
        else:
            self.pushButtonLoadCredentialDatabase.setEnabled(False)
            self.pushButtonCreateCredentialDatabase.setEnabled(True)
            self.pushButtonDeleteCredentialDatabase.setEnabled(False)
        if config_value == 'read_only':
            self.pushButtonCreateCredentialDatabase.setEnabled(False)
            self.pushButtonLoadCredentialDatabase.setEnabled(True)
        if config_value == 'none':
            self.pushButtonCreateCredentialDatabase.setEnabled(False)
            self.pushButtonLoadCredentialDatabase.setEnabled(False)
        return

    # call this anytime a cred db is created, opened, or deleted to set all the buttons appropriately
    # (also looks at methods available in the cred db instance as well as config file settings.)
    def set_creddbbuttons(self):
        db_file = pathlib.Path('credentials.db')
        if db_file.is_file():
            db_file_exists = True
        else:
            db_file_exists = False
        config_value = self.config['Credential Store']['credential_store_implementation']

        if (config_value == 'built_in') and \
                (self.cred_db_authenticated is True) and\
                (hasattr(self.credentialstore, 'add_creds')):

            self.pushButtonCreatePresetLeft.setEnabled(True)
            self.pushButtonCreatePresetRight.setEnabled(True)

        else:
            self.pushButtonCreatePresetLeft.setEnabled(False)
            self.pushButtonCreatePresetRight.setEnabled(False)

        if (config_value == 'built_in') and \
                (self.cred_db_authenticated is True) and\
                (hasattr(self.credentialstore, 'update_creds')):

            self.pushButtonUpdatePresetLeft.setEnabled(True)
            self.pushButtonUpdatePresetRight.setEnabled(True)

        else:
            self.pushButtonUpdatePresetLeft.setEnabled(False)
            self.pushButtonUpdatePresetRight.setEnabled(False)

        if  (config_value == 'built_in') and \
                (self.cred_db_authenticated is True) and\
                (hasattr(self.credentialstore, 'delete_creds')):

            self.pushButtonDeletePresetLeft.setEnabled(True)
            self.pushButtonDeletePresetRight.setEnabled(True)

        else:
            self.pushButtonDeletePresetLeft.setEnabled(False)
            self.pushButtonDeletePresetRight.setEnabled(False)

        if (self.cred_db_authenticated is True) and\
                (config_value != 'none'):
            self.comboBoxPresetLeft.setEnabled(True)
            self.comboBoxPresetRight.setEnabled(True)
        else:
            self.comboBoxPresetLeft.setEnabled(False)
            self.comboBoxPresetRight.setEnabled(False)

        if (config_value == 'built_in'):
            if db_file_exists:
                self.pushButtonCreateCredentialDatabase.setEnabled(False)
                self.pushButtonDeleteCredentialDatabase.setEnabled(True)
            else:
                self.pushButtonCreateCredentialDatabase.setEnabled(True)
                self.pushButtonDeleteCredentialDatabase.setEnabled(False)
        else:
            self.pushButtonCreateCredentialDatabase.setEnabled(False)
            self.pushButtonDeleteCredentialDatabase.setEnabled(False)

        if db_file_exists or (config_value == 'read_only'):
            self.pushButtonLoadCredentialDatabase.setEnabled(True)
        else:
            self.pushButtonLoadCredentialDatabase.setEnabled(False)


        return

    def create_preset(self, comboBoxRegion, lineEditUserName, lineEditPassword, comboBoxPreset, side):
        logger.info('Creating preset in credential store.')
        sumoregion = str(comboBoxRegion.currentText())
        accesskeyid = str(lineEditUserName.text())
        accesskey = str(lineEditPassword.text())
        message = "Please type a name for the new preset."
        preset, result = QtWidgets.QInputDialog.getText(self, 'Enter preset name', message)
        if result:
            if self.credentialstore.name_exists(preset):
                self.errorbox('That name already exists in the credential database. Choose a new name or use "Update" to modify an existing entry.')
                return
            else:
                try:
                    self.credentialstore.add_creds(preset, sumoregion, accesskeyid, accesskey)
                    self.add_preset_to_combobox(preset)
                    # index = comboBoxRegion.findText(preset, QtCore.Qt.MatchFixedString)
                    # if index >= 0:
                    #     comboBoxRegion.setCurrentIndex(index)
                    self.load_preset(preset, comboBoxRegion, lineEditUserName, lineEditPassword, comboBoxPreset, side)
                except Exception as e:
                    logger.exception(e)
                return
        return

    def load_preset(self, preset, comboBoxRegion, lineEditUserName, lineEditPassword, comboBoxPreset, side):
        logger.info('Loading preset from credential store.')
        if preset:
            try:
                if self.credentialstore.name_exists(preset):
                    creds = self.credentialstore.get_creds(preset)
                    index = comboBoxPreset.findText(preset, QtCore.Qt.MatchFixedString)
                    if index >=0:
                        comboBoxPreset.setCurrentIndex(index)
                    index = comboBoxRegion.findText(creds['sumoregion'], QtCore.Qt.MatchFixedString)
                    if index >=0:
                        comboBoxRegion.setCurrentIndex(index)
                    lineEditUserName.setText(creds['accesskeyid'])
                    lineEditPassword.setText(creds['accesskey'])
                    # since we've changed the preset all of the stateful tabs need to be reset
                    # otherwise they will still be showing items from the previous preset
                    self.reset_stateful_objects(side=side)
                else:
                    raise Exception('That preset is not in the database.')
            except Exception as e:
                logger.exception(e)
                self.errorbox('Something went wrong\n\n' + str(e))
        else:
            print('preset evaluated false')

    def delete_preset(self, preset, comboBoxRegion, lineEditUserName, lineEditPassword, comboBoxPreset, side):
        logger.info('Deleting preset from credential store.')
        if self.credentialstore.name_exists(preset):
            try:
                result = self.credentialstore.delete_creds(preset)
                self.remove_preset_from_combobox(preset)
                preset = comboBoxPreset.currentText()
                # load the first preset in the list (if it's there)
                if preset:
                    self.load_preset(
                        preset,
                        comboBoxRegion,
                        lineEditUserName,
                        lineEditPassword,
                        comboBoxPreset,
                        side
                    )

            except Exception as e:
                logger.exception(e)
                self.errorbox('Something went wrong\n\n' + str(e))
        else:
            self.errorbox('Something went wrong. That preset does not exist in the database.')

    def update_preset(self, preset, sumoregion, accesskeyid, accesskey):
        logger.info('Updating preset in credential store.')
        if self.credentialstore.name_exists(preset):
            try:
                result = self.credentialstore.update_creds(preset, sumoregion, accesskeyid, accesskey)
            except Exception as e:
                logger.exception(e)
                self.errorbox('Something went wrong\n\n' + str(e))
        else:
            self.errorbox('Something went wrong. That preset does not exist in the database.')
        return


    # Start methods for Content Tab

    def findreplacecopycontent(self, ContentListWidgetFrom, ContentListWidgetTo, fromurl, fromid, fromkey, tourl, toid, tokey,
                    fromradioselected, toradioselected, todirectorylabel):

        logger.info("Copying Content")

        selecteditemsfrom = ContentListWidgetFrom.selectedItems()
        if len(selecteditemsfrom) > 0:  # make sure something was selected
            try:
                exportsuccessful = False
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                if (toradioselected == -2):  # Personal Folder Selected
                    contents = []
                    for selecteditem in selecteditemsfrom:
                        for child in ContentListWidgetFrom.currentcontent['children']:
                            if child['name'] == str(selecteditem.text()):
                                item_id = child['id']
                                contents.append(fromsumo.export_content_job_sync(item_id))
                                exportsuccessful = True
                elif toradioselected == -4:  # Admin Recommended Folders Selected
                    currentdir = ContentListWidgetTo.currentdirlist[-1]
                    if currentdir['id'] != 'TOP':
                        contents = []
                        for selecteditem in selecteditemsfrom:
                            for child in ContentListWidgetFrom.currentcontent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']
                                    contents.append(fromsumo.export_content_job_sync(item_id))
                                    exportsuccessful = True
            except Exception as e:
                logger.exception(e)
                self.errorbox('Source:Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
                return
            if exportsuccessful:
                categoriesfrom=[]
                for content in contents:
                    contentstring = json.dumps(content)
                    categoriesfrom = categoriesfrom + re.findall(r'\"_sourceCategory\s*=\s*\\?\"?([^\s\\|]*)', contentstring)
                uniquecategoriesfrom = list(set(categoriesfrom))  # dedupe the list
                try:
                    fromtime = str(QtCore.QDateTime.currentDateTime().addSecs(-3600).toString(QtCore.Qt.ISODate))
                    totime = str(QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))

                    query = r'* | count by _sourceCategory | fields _sourceCategory'
                    searchresults = tosumo.search_job_records_sync(query, fromTime=fromtime, toTime=totime, timeZone='UTC', byReceiptTime='false' )
                    categoriesto = []
                    for record in searchresults['records']:
                        categoriesto.append(record['map']['_sourcecategory'])
                    uniquecategoriesto = list(set(categoriesto))

                except Exception as e:
                    logger.exception(e)
                    self.errorbox('Destination:Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
                    return
                dialog = findReplaceCopyDialog(uniquecategoriesfrom, uniquecategoriesto)
                dialog.exec()
                dialog.show()
                if str(dialog.result()) == '1':
                    replacelist = dialog.getresults()
                    logger.info(replacelist)
                    if len(replacelist) > 0:
                        newcontents = []
                        for content in contents:
                            for entry in replacelist:

                                contentstring = json.dumps(content)
                                contentstring = contentstring.replace(str(entry['from']), str(entry['to']))
                                logger.info(contentstring)
                                newcontents.append(json.loads(contentstring))
                    else:
                        newcontents = contents
                    if (toradioselected == -2):  # Personal Folder Selected
                        try:
                            tofolderid = ContentListWidgetTo.currentcontent['id']
                            for newcontent in newcontents:
                                status = tosumo.import_content_job_sync(tofolderid, newcontent, adminmode=False)
                            self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected,
                                                       todirectorylabel)
                            return
                        except Exception as e:
                            logger.exception(e)
                            self.errorbox('Destination:Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
                            return
                    elif toradioselected == -4:  # Admin recommended Folder Selected
                        try:
                            tofolderid = ContentListWidgetTo.currentcontent['id']
                            for newcontent in newcontents:
                                status = tosumo.import_content_job_sync(tofolderid, newcontent, adminmode=True)
                            self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected,
                                                       todirectorylabel)
                        except Exception as e:
                            logger.exception(e)
                            self.errorbox('Destination:Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
                            return
                else:
                    return



        else:
            self.errorbox('You have not made any selections.')
            return
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
                        for child in ContentListWidgetFrom.currentcontent['children']:
                            if child['name'] == str(selecteditem.text()):
                                item_id = child['id']
                                content = fromsumo.export_content_job_sync(item_id)
                                tofolderid = ContentListWidgetTo.currentcontent['id']
                                status = tosumo.import_content_job_sync(tofolderid, content)
                                self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected, todirectorylabel)
                    return
                elif toradioselected == -4:  # Admin Recommended Folders Selected
                    currentdir = ContentListWidgetTo.currentdirlist[-1]
                    if currentdir['id'] != 'TOP':
                        for selecteditem in selecteditems:
                            for child in ContentListWidgetFrom.currentcontent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']
                                    content = fromsumo.export_content_job_sync(item_id)
                                    tofolderid = ContentListWidgetTo.currentcontent['id']
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
        return

    def create_folder(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        if ContentListWidget.updated == True:

            message = '''
        Please enter the name of the folder you wish to create:
            
                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Create Folder...', message)
            for item in ContentListWidget.currentcontent['children']:
                if item['name'] == str(text):
                    self.errorbox('That Directory Name Already Exists!')
                    return
            try:
                if radioselected == -2:  # if "Personal Folder" radio button is selected
                    logger.info("Creating New Folder in Personal Folder Tree")
                    sumo = SumoLogic(id, key, endpoint=url)
                    error = sumo.create_folder(str(text), str(ContentListWidget.currentcontent['id']))

                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                    return
                elif radioselected == -4:  # "Admin Folders" is selected
                    logger.info("Creating New Folder in Admin Recommended Folder Tree")
                    currentdir = ContentListWidget.currentdirlist[-1]
                    if currentdir['id'] != 'TOP':
                        sumo = SumoLogic(id, key, endpoint=url)
                        error = sumo.create_folder(str(text), str(ContentListWidget.currentcontent['id']), adminmode=True)

                        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Sorry, this tool in not currently capable of creating a top-level directory in the Admin Recommended folder due to API limitations. Creating sub-folders works fine. Suggested workaround is to make the top level folder in the SumoLogic UI and then use this tool to copy content into it. This should be fixed soon!')
                        return
            except Exception as e:
                logger.exception(e)
                self.errorbox('Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')

        else:
            self.errorbox("Please update the directory list before trying to create a new folder.")
        return

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

                            for child in ContentListWidget.currentcontent['children']:
                                if child['name'] == str(selecteditem.text()):
                                    item_id = child['id']

                            result = sumo.delete_content_job_sync(item_id)

                        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    elif radioselected == -4:  # "Admin Folders" is selected
                        sumo = SumoLogic(id, key, endpoint=url)
                        for selecteditem in selecteditems:

                            for child in ContentListWidget.currentcontent['children']:
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

        else:
            self.errorbox('You need to select something before you can delete it.')
        return

    def contentradiobuttonchanged(self, ContentListWidget,url, id, key, radioselected, directorylabel, pushButtonContentDelete):
        ContentListWidget.currentdirlist = []
        if radioselected == -2:
            pushButtonContentDelete.setEnabled(True)
        elif radioselected == -3:
            pushButtonContentDelete.setEnabled(False)
        else:
            pushButtonContentDelete.setEnabled(True)
        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
        return

    def updatecontentlist(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        sumo = SumoLogic(id, key, endpoint=url)
        if ContentListWidget.currentdirlist:
            currentdir = ContentListWidget.currentdirlist[-1]
        else:
            currentdir = {'name': None, 'id': 'TOP'}
        try:
            if (not ContentListWidget.currentcontent) or (currentdir['id'] == 'TOP'):
                if radioselected == -2:  # if "Personal Folder" radio button is selected
                    logger.info("Updating Personal Folder List")
                    ContentListWidget.currentcontent = sumo.get_personal_folder()

                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Personal Folder', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentcontent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Incorrect Credentials or Wrong Endpoint.')
                        return
                elif radioselected == -3:  # if "Global Folders" radio button is selected
                    logger.info("Updating Global Folder List")
                    ContentListWidget.currentcontent = sumo.get_global_folder_sync()

                    # Rename dict key from "data" to "children" for consistency
                    ContentListWidget.currentcontent['children'] = ContentListWidget.currentcontent.pop('data')
                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Global Folders', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentcontent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Incorrect Credentials or Wrong Endpoint.')
                        return
                else:  # "Admin Folders" must be selected
                    logger.info("Updating Admin Folder List")
                    ContentListWidget.currentcontent = sumo.get_admin_folder_sync()

                    # Rename dict key from "data" to "children" for consistency
                    ContentListWidget.currentcontent['children'] = ContentListWidget.currentcontent.pop('data')
                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Admin Recommended', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentcontent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                        return
                    else:
                        self.errorbox('Incorrect Credentials or Wrong Endpoint.')
                        return

            else:
                ContentListWidget.currentcontent = sumo.get_folder(currentdir['id'])
                self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
                return

        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials or Wrong Endpoint.')
            return
        return

    def doubleclickedcontentlist(self, item, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("Going Down One Content Folder")
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            for child in ContentListWidget.currentcontent['children']:
                if (child['name'] == item.text()) and (child['itemType'] == 'Folder'):
                    ContentListWidget.currentcontent = sumo.get_folder(child['id'])

                    dir = {'name': item.text(), 'id': child['id']}
                    ContentListWidget.currentdirlist.append(dir)

        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials or Wrong Endpoint.')
        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)
        return

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
                ContentListWidget.currentcontent = sumo.get_folder(parentdir['id'])

                self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                return
        except Exception as e:
            logger.exception(e)
            self.errorbox('Incorrect Credentials or Wrong Endpoint.')
        return

    def updatecontentlistwidget(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        try:
            ContentListWidget.clear()
            sumo = SumoLogic(id, key, endpoint=url)
            for object in ContentListWidget.currentcontent['children']:
                item_name = ''
                if radioselected == -3:
                    logger.info("Getting User info for Global Folder")
                    user_info = sumo.get_user(object['createdBy'])
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
            ContentListWidget.updated = True

        except Exception as e:
            logger.exception(e)
        return

    def backupcontent(self, ContentListWidget, url, id, key):
        logger.info("Backing Up Content")
        selecteditems = ContentListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url)
                for selecteditem in selecteditems:
                    for child in ContentListWidget.currentcontent['children']:
                        if child['name'] == str(selecteditem.text()):
                            item_id = child['id']
                            try:
                                content = sumo.export_content_job_sync(item_id)
                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(content, filepointer)
                                    message = message + str(selecteditem.text()) + r'.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.errorbox('Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
                                return
                self.infobox('Wrote files: \n\n' + message)
            else:
                self.errorbox("You don't have permissions to write to that directory")

        else:
            self.errorbox('No content selected.')
        return

    def restorecontent(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("Restoring Content")
        if ContentListWidget.updated == True:
            if 'id' in ContentListWidget.currentcontent:  # make sure the current folder has a folder id
                filter = "JSON (*.json)"
                filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(), filter)
                if len(filelist) > 0:
                    sumo = SumoLogic(id, key, endpoint=url)
                    for file in filelist:
                        try:
                            with open(file) as filepointer:
                                content = json.load(filepointer)


                        except Exception as e:
                            logger.exception(e)
                            self.errorbox("Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                            return
                        try:
                            folder_id = ContentListWidget.currentcontent['id']
                            if radioselected == -4:  # Admin Recommended Folders Selected
                                adminmode=True
                            else:
                                adminmode=False
                            sumo.import_content_job_sync(folder_id, content, adminmode=adminmode)
                        except Exception as e:
                            logger.exception(e)
                            self.errorbox('Incorrect Credentials, Wrong Endpoint, or Insufficient Privileges.')
                            return
                    self.updatecontentlist(ContentListWidget,url, id, key, radioselected, directorylabel)


            else:
                self.errorbox("You can't currently restore to the root Admin folder. This should be fixed soon. Suggested workaround is to restore to a child folder and then move the content using the Sumo Logic UI")
                return
        else:
            self.errorbox("Please update the directory list before restoring content")
        return
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
        return

            
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
        return


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
                        items[0].setForeground(QtGui.QBrush(QtCore.Qt.blue))
                    if collector['alive'] == False:
                        items[0].setData(6, QtGui.QFont("Arial",pointSize=10,italic=True))

            except Exception as e:
                logger.exception(e)
                self.errorbox('Incorrect Credentials or Wrong Endpoint.')

        else:
            self.errorbox('No user and/or password.')
        return

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
        return

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
        return

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
        return

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
                self.updatecollectorlist(CollectorListWidget, url, id, key)

        else:
            self.errorbox('No Collector Selected')
        return

    # This is broken and not connected to any button currently
    def restoresources(self):
        destinationcollector = self.listWidgetCollectorsRight.selectedItems()
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
        return

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
                    self.updatesourcelist(CollectorListWidget, SourceListWidget, url, id, key)

            else:
                self.errorbox('No Source(s) Selected')
        else:
            self.errorbox('You must select 1 and only 1 collector.')
        return
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
                except Exception as e:
                    self.errorbox("Failed to submit search job. Check credentials, endpoint, and query.")
                    logger.exception(e)
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

                            else:
                                self.errorbox('Search did not return any records.')
                    else:
                        self.errorbox('Search did not return any messages.')

            else:
                self.errorbox('Please enter a search.')
        else:
            self.errorbox('No user and/or password.')
        return
    # End Methods for Search Tab

    # Start Misc/Utility Methods
    def tabchange(self, index):
        if index == 0:
            self.comboBoxRegionRight.setEnabled(True)
            self.lineEditUserNameRight.setEnabled(True)
            self.lineEditPasswordRight.setEnabled(True)
        if index == 1:
            self.comboBoxRegionRight.setEnabled(True)
            self.lineEditUserNameRight.setEnabled(True)
            self.lineEditPasswordRight.setEnabled(True)
        if index == 2:
            self.comboBoxRegionRight.setEnabled(False)
            self.lineEditUserNameRight.setEnabled(False)
            self.lineEditPasswordRight.setEnabled(False)
        return

    # no longer called by __init__ since the credential store has been implemented
    def loadcredentials(self):
        logger.info("Looking for Credential File")
        # look to see if the credential file exists and load credentials if it does
        # fail if anything at all goes wrong
        if os.path.isfile(os.path.join(self.basedir, 'data/credentials.json')):
            try:
                with open(os.path.join(self.basedir, 'data/credentials.json'), 'r') as filepointer:
                    credentials = json.load(filepointer)
                self.lineEditUserNameLeft.setText(credentials['source']['user'])
                self.lineEditPasswordLeft.setText(credentials['source']['password'])
                self.lineEditUserNameRight.setText(credentials['destination']['user'])
                self.lineEditPasswordRight.setText(credentials['destination']['password'])
                logger.info("Found it! Creds will be populated.")
            except Exception as e:
                print("failed to load creds")
                logger.exception(e)
        else:
            logger.info("Didn't find it. :(  Creds will be blank.")
        return


    def errorbox(self, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText(message)
        msgBox.addButton(QtWidgets.QPushButton('OK'), QtWidgets.QMessageBox.RejectRole)
        ret = msgBox.exec_()
        return

    def infobox(self, message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Info')
        msgBox.setText(message)
        msgBox.addButton(QtWidgets.QPushButton('OK'), QtWidgets.QMessageBox.RejectRole)
        ret = msgBox.exec_()
        return

    def initModels(self):
        # Load API Endpoint List from file and create model for the comboboxes
        with open(os.path.join(self.basedir, 'data/apiurls.json'), 'r') as infile:
            self.loadedapiurls = json.load(infile)

        self.apiurlsmodel = QtGui.QStandardItemModel()
        for key in self.loadedapiurls:
            text_item = QtGui.QStandardItem(key)
            self.apiurlsmodel.appendRow(text_item)

        self.comboBoxRegionLeft.setModel(self.apiurlsmodel)
        self.comboBoxRegionRight.setModel(self.apiurlsmodel)

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
        return

    def init_and_load_config_file(self):

        config_file = pathlib.Path('sumotoolbox.ini')
        if not config_file.is_file():
            # If the config file doesn't exist then we need to create a new one. This should only happen
            # when running the pyinstaller executable version.
            # get the copy that's hidden inside the executable archive and copy it to the current dir
            source_file = pathlib.Path(self.basedir + '/data/sumotoolbox.ini')
            shutil.copy(str(source_file), str(config_file))
        self.config = configparser.ConfigParser()
        self.config.read(str(config_file))
        return

    # End Misc/Utility Methods

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = sumotoolbox()
    window.show()
    sys.exit(app.exec_())
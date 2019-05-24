__author__ = 'Tim MacDonald'

import sys
import json
import re
import time
import csv
import pytz
import os.path
from datetime import datetime
from tzlocal import get_localzone
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from sumologic import SumoLogic
import pprint
import pathlib
import os

# detect if in Pyinstaller package and build appropriate base directory path
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)

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

        # init all of the dialogs we'll be using


        # set up some variables we'll need later to do stuff

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
            str(self.LineEditLeftPassword.text())))

        self.listWidgetRightCollectors.itemSelectionChanged.connect(lambda: self.updatesourcelist(
            self.listWidgetRightCollectors,
            self.listWidgetRightSources,
            self.loadedapiurls[str(self.ComboBoxRightRegion.currentText())],
            str(self.LineEditRightUserName.text()),
            str(self.LineEditRightPassword.text())))

        # UI Buttons for Search API Tab
        self.pushButtonStartSearch.clicked.connect(lambda: self.runsearch(
            self.loadedapiurls[str(self.ComboBoxLeftRegion.currentText())],
            str(self.LineEditLeftUserName.text()),
            str(self.LineEditLeftPassword.text())
        ))

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

    def filterlistwidget(self, text):
        print(str(text))

    def loadcredentials(self):

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
            except Exception as e:
                print("failed to load creds")
                print(e)

    def getcollectorid(self, collectorname, url, id, key):
        sumo = SumoLogic(id, key, endpoint=url)
        sumocollectors = sumo.collectors()
        for sumocollector in sumocollectors:
            if sumocollector['name'] == collectorname:
                return sumocollector['id']

    def getsourceid(self, collectorid, sourcename, url, id, key):
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            sumosources = sumo.sources(collectorid)
            for sumosource in sumosources:
                if sumosource['name'] == sourcename:
                    return sumosource['id']
            return False
        except Exception as e:
            print(e)

    def updatecollectorlist(self, CollectorListWidget, url, id, key):
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
                print(e)
                self.errorbox('Incorrect Credentials.')

        else:
            self.errorbox('No user and/or password.')

    def updatesourcelist(self, CollectorListWidget, SourceListWidget, url, id, key):

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
                                            time.sleep(
                                                0.25)  # the Sumo Logic API only allows 4 calls per second so we must sleep .25 seconds between each call
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
            print(e)

    def backupcollector(self, CollectorListWidget, url, id, key):
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
                    time.sleep(.75) # we're making 3 calls to the Sumo API, there is a 4 call per second limit, so sleep .75 seconds
                    message = message + str(collectornameqstring.text()) + ' '
                self.infobox('Wrote files ' + message)
            else:
                self.errorbox("You don't have permissions to write to that directory")

        else:
            self.errorbox('No Source Collector Selected.')

    def deletecollectors(self, CollectorListWidget, url, id, key):
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
                        time.sleep(.50)
                    except Exception as e:
                        self.errorbox('Failed to delete collector: ' + str(collectornamesqstring.text()))
                        print(e)
                self.updatecollectorlist(CollectorListWidget, url, id, key)

        else:
            self.errorbox('No Collector Selected')

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
                print(e)

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
        collectornamesqstring = CollectorListWidget.selectedItems()
        if  len(collectornamesqstring) == 1:  # make sure something was selected
            collectorid = self.getcollectorid(str(collectornamesqstring[0].text()), url, id, key)
            time.sleep(.25)
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
                            time.sleep(.5)
                        except Exception as e:
                            self.errorbox('Failed to delete source: ' + str(sourcenameqstring.text()))
                            print(e)
                    self.updatesourcelist(CollectorListWidget, SourceListWidget, url, id, key)

            else:
                self.errorbox('No Source(s) Selected')
        else:
            self.errorbox('You must select 1 and only 1 collector.')

    def runsearch(self, url, id, key):

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
                        time.sleep(5)
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
                                        print(e)
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
                                            print(e)
                            else:
                                self.errorbox('Search did not return any records.')
                    else:
                        self.errorbox('Search did not return any messages.')
            else:
                self.errorbox('Please enter a search.')
        else:
            self.errorbox('No user and/or password.')

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = sumotoolbox()
    window.show()
    sys.exit(app.exec_())

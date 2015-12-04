__author__ = 'tim'

import sys
import json
import re
import time
import csv
import pytz
from datetime import datetime
from tzlocal import get_localzone
from PyQt4 import QtCore, QtGui, uic
from sumologic import SumoLogic

qtMainWindowUI = "sumotoolbox.ui" # Enter file here.
qtCollectorCopyDialogUI = "collectorcopy.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainWindowUI)

class sumotoolbox(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initModels()
        self.collectorcopyUI = uic.loadUi(qtCollectorCopyDialogUI)
        self.pushButtonUpdateListSource.clicked.connect(self.updatecollectorlistsource)
        self.pushButtonUpdateListDestination.clicked.connect(self.updatecollectorlistdestination)
        self.pushButtonCopyCollectorsToDest.clicked.connect(self.copysourcesfromsourcetodestinationdialog)
        self.pushButtonStartSearch.clicked.connect(self.runsearch)

    def updatecollectorlistsource(self):
        self.listWidgetSourceCollectors.clear()
        sourceurl = self.loadedapiurls[str(self.comboBoxSourceRegion.currentText())]
        sourceusername = str(self.SourceUserName.text())
        sourcepassword = str(self.SourcePassword.text())
        self.sourcecollectordict = {}
        regexprog = re.compile(r'\S+')
        if (re.match(regexprog,sourceusername) != None) and (re.match(regexprog,sourcepassword) != None):
            self.sumosource = SumoLogic(sourceusername, sourcepassword, endpoint=sourceurl)
            try:
                self.sourcecollectors = self.sumosource.collectors()
                for collector in self.sourcecollectors:
                    self.sourcecollectordict[collector['name']]=collector['id']

                for collector in self.sourcecollectordict:
                    self.listWidgetSourceCollectors.addItem(collector)

                self.listWidgetSourceCollectors.currentItemChanged.connect(self.updatesourcelistsource)
            except:
                self.errorbox('Incorrect Credentials.')
        else:
           self.errorbox('No user and/or password.')

    def updatecollectorlistdestination(self):
        self.listWidgetDestinationCollectors.clear()
        destinationurl = self.loadedapiurls[str(self.comboBoxDestinationRegion.currentText())]
        destinationusername = str(self.DestinationUserName.text())
        destinationpassword = str(self.DestinationPassword.text())
        self.destinationcollectordict = {}
        regexprog = re.compile(r'\S+')
        if (re.match(regexprog, destinationusername) is not None) and (re.match(regexprog,destinationpassword) is not None):
            self.sumodestination = SumoLogic(destinationusername, destinationpassword, endpoint=destinationurl)
            try:
                self.destinationcollectors = self.sumodestination.collectors()
                for collector in self.destinationcollectors:
                    self.destinationcollectordict[collector['name']]=collector['id']

                for collector in self.destinationcollectordict:
                    self.listWidgetDestinationCollectors.addItem(collector)

                self.listWidgetDestinationCollectors.currentItemChanged.connect(self.updatedestinationlistsource)
            except:
                self.errorbox('Incorrect Credentials.')
        else:
            self.errorbox('No user and/or password.')

    def updatesourcelistsource(self, currentcollector, prevcollector):

        self.listWidgetSourceSources.clear()
        if currentcollector != None:
            self.sourcesourcesdict = {}
            self.sourcesources = self.sumosource.sources(self.sourcecollectordict[str(currentcollector.text())])
            for source in self.sourcesources:
                self.sourcesourcesdict[source['name']]=''
            for source in self.sourcesourcesdict:
                self.listWidgetSourceSources.addItem(source)

    def updatedestinationlistsource(self, currentcollector, prevcollector):

        self.listWidgetDestinationSources.clear()
        if currentcollector != None:
            self.destinationsourcesdict = {}
            self.destinationsources = self.sumodestination.sources(self.destinationcollectordict[str(currentcollector.text())])
            for source in self.destinationsources:
                self.destinationsourcesdict[source['name']]=''
            for source in self.destinationsourcesdict:
                self.listWidgetDestinationSources.addItem(source)

    def copysourcesfromsourcetodestinationdialog(self):

        sourcecollector = self.listWidgetSourceCollectors.selectedItems()
        if len (sourcecollector) == 1:
            sourcecollector = sourcecollector[0].text()
            destinationcollector = self.listWidgetDestinationCollectors.selectedItems()
            if len(destinationcollector) == 1:

                destinationcollectorqstring = destinationcollector[0]
                destinationcollector = str(destinationcollector[0].text())
                sourcesources = self.listWidgetSourceSources.selectedItems()
                if len(sourcesources) > 0:
                    sourcelist = []
                    for source in sourcesources:
                        sourcelist.append(source.text())
                    message = "You are about to copy the following sources from collector \"" + sourcecollector + "\" to \"" + destinationcollector + "\". Is this correct? \n\n"
                    for source in sourcelist:
                        message = message + source + "\n"
                    self.collectorcopyUI.labelCollectorCopy.setText(message)
                    self.collectorcopyUI.dateTimeEdit.setMaximumDate(QtCore.QDate.currentDate())
                    self.collectorcopyUI.dateTimeEdit.setDate(QtCore.QDate.currentDate())
                    result = self.collectorcopyUI.exec_()
                    overridecollectiondate = self.collectorcopyUI.checkBoxOverrideCollectionStartTime.isChecked()
                    overridedate = self.collectorcopyUI.dateTimeEdit.dateTime()
                    overridedatemillis = long(overridedate.currentMSecsSinceEpoch())
                    if result:
                        for source in sourcelist:
                            for sumosource in self.sourcesources:
                                if sumosource['name'] == source:
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
                                        self.sumodestination.create_source(self.destinationcollectordict[destinationcollector], template)
                                    else:
                                        self.errorbox(source + ' already exists, skipping.')
                        self.updatedestinationlistsource(destinationcollectorqstring, destinationcollectorqstring)


                else:
                    self.errorbox('No Sources Selected.')
            else:
                self.errorbox('No Destination Collector Selected.')
        else:
            self.errorbox('No Source Collector Selected.')

    def runsearch(self):

        self.tableWidgetSearchResults.clear()
        selectedtimezone = str(self.comboBoxTimeZone.currentText())
        starttime = str(self.dateTimeEditSearchStartTime.dateTime().toString(QtCore.Qt.ISODate))
        endtime = str(self.dateTimeEditSearchEndTime.dateTime().toString(QtCore.Qt.ISODate))
        sourceurl = self.loadedapiurls[str(self.comboBoxSourceRegion.currentText())]
        sourceusername = str(self.SourceUserName.text())
        sourcepassword = str(self.SourcePassword.text())
        searchstring = str(self.plainTextEditSearch.toPlainText())
        regexprog = re.compile(r'\S+')
        jobsubmitted = False
        savetofile = self.checkBoxSaveSearch.isChecked()
        converttimefromepoch = self.checkBoxConvertTimeFromEpoch.isChecked()
        self.jobmessages = []
        self.jobrecords = []

        if (re.match(regexprog,sourceusername) != None) and (re.match(regexprog,sourcepassword) != None):
            self.sumosource = SumoLogic(sourceusername, sourcepassword, endpoint=sourceurl)

            if (re.match(regexprog, searchstring)) != None:
                try:
                    searchjob = self.sumosource.search_job(searchstring, starttime, endtime, selectedtimezone)
                    jobsubmitted = True
                except:
                    self.errorbox('Incorrect Credentials.')
                if jobsubmitted:
                    self.labelSearchResultCount.setText('0')
                    jobstatus = self.sumosource.search_job_status(searchjob)
                    nummessages = jobstatus['messageCount']
                    numrecords = jobstatus['recordCount']
                    self.labelSearchResultCount.setText(str(nummessages))
                    while jobstatus['state'] == 'GATHERING RESULTS':
                        time.sleep(5)
                        jobstatus = self.sumosource.search_job_status(searchjob)
                        numrecords = jobstatus['recordCount']
                        nummessages = jobstatus['messageCount']
                        self.labelSearchResultCount.setText(str(nummessages))
                    print jobstatus
                    if nummessages is not 0:

                        #return messages
                        if self.buttonGroupOutputType.checkedId() == -2:
                            iterations = nummessages // 10000 + 1
                            for iteration in range (1,iterations + 1):
                                messages = self.sumosource.search_job_messages(searchjob,limit=10000,offset=((iteration-1)*10000))
                                for message in messages['messages']:
                                    self.jobmessages.append(message)
                            self.tableWidgetSearchResults.setRowCount(len(self.jobmessages))
                            self.tableWidgetSearchResults.setColumnCount(2)
                            self.tableWidgetSearchResults.setHorizontalHeaderLabels(['time','_raw'])
                            index = 0
                            for message in self.jobmessages:
                                if converttimefromepoch:
                                    timezone = pytz.timezone(selectedtimezone)
                                    converteddatetime = datetime.fromtimestamp(float(message['map']['_messagetime']) / 1000, timezone)
                                    timestring = str(converteddatetime.strftime('%Y-%m-%d %H:%M:%S'))
                                    message['map']['_messagetime'] = timestring
                                self.tableWidgetSearchResults.setItem(index,0,QtGui.QTableWidgetItem(message['map']['_messagetime']))
                                self.tableWidgetSearchResults.setItem(index,1,QtGui.QTableWidgetItem(message['map']['_raw']))
                                index += 1
                            self.tableWidgetSearchResults.resizeRowsToContents()
                            self.tableWidgetSearchResults.resizeColumnsToContents()
                            if savetofile:
                                filename = QtGui.QFileDialog.getSaveFileName(self, 'Save CSV', '', selectedFilter='*.csv')
                                if filename:
                                    with open(filename,'wb') as csvfile:
                                        messagecsv = csv.DictWriter(csvfile,self.jobmessages[0]['map'].keys())
                                        messagecsv.writeheader()
                                        for entry in self.jobmessages:
                                            messagecsv.writerow(entry['map'])
                        #return records
                        if self.buttonGroupOutputType.checkedId() == -3:
                            iterations = numrecords // 10000 + 1
                            for iteration in range (1,iterations + 1):
                                records = self.sumosource.search_job_records(searchjob,limit=10000,offset=((iteration-1)*10000))
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
                            for record in self.jobrecords:
                                columnnum = 0
                                for fieldname in fieldnames:
                                    if converttimefromepoch and (fieldname == '_timeslice'):
                                        timezone = pytz.timezone(selectedtimezone)
                                        converteddatetime = datetime.fromtimestamp(float(record['map'][fieldname]) / 1000, timezone)
                                        timestring = str(converteddatetime.strftime('%Y-%m-%d %H:%M:%S'))
                                        #converteddatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(record['map']['_timeslice']) / 1000))
                                        record['map']['_timeslice'] = timestring
                                    self.tableWidgetSearchResults.setItem(index, columnnum, QtGui.QTableWidgetItem(record['map'][fieldname]))
                                    columnnum += 1
                                index += 1
                            self.tableWidgetSearchResults.resizeRowsToContents()
                            self.tableWidgetSearchResults.resizeColumnsToContents()
                            if savetofile:
                                filename = QtGui.QFileDialog.getSaveFileName(self, 'Save CSV', '', selectedFilter='*.csv')
                                if filename:
                                    with open(filename,'wb') as csvfile:
                                        recordcsv = csv.DictWriter(csvfile,self.jobrecords[0]['map'].keys())
                                        recordcsv.writeheader()
                                        for entry in self.jobrecords:
                                            recordcsv.writerow(entry['map'])
                    else:
                        self.errorbox('Search did not return any messages.')
            else:
                self.errorbox('Please enter a search.')
        else:
            self.errorbox('No user and/or password.')

    def errorbox(self, message):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText(message)
        msgBox.addButton(QtGui.QPushButton('OK'), QtGui.QMessageBox.RejectRole)
        ret = msgBox.exec_()

    def initModels(self):
        # Load API Endpoint List from file and create model for the comboboxes
        with open('apiurls.json', 'r') as infile:
            self.loadedapiurls=json.load(infile)

        self.apiurlsmodel = QtGui.QStandardItemModel()
        for key in self.loadedapiurls:
            text_item = QtGui.QStandardItem(key)
            self.apiurlsmodel.appendRow(text_item)

        self.comboBoxSourceRegion.setModel(self.apiurlsmodel)
        self.comboBoxDestinationRegion.setModel(self.apiurlsmodel)

        #Load Timezones and create model for timezone combobox

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
    app = QtGui.QApplication(sys.argv)
    window = sumotoolbox()
    window.show()
    sys.exit(app.exec_())
class_name = 'collector_tab'

from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import sys
import pathlib
import json
import re
from logzero import logger
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog

class restoreSourcesDialog(QtWidgets.QDialog):

    def __init__(self, sources_json, parent=None):
        super(restoreSourcesDialog, self).__init__(parent)
        self.objectlist = []
        self.setupUi(self, sources_json)

    def setupUi(self, rsd, sources_json):

        # setup static elements
        rsd.setObjectName("Restore Sources")
        rsd.resize(1150, 640)
        self.buttonBox = QtWidgets.QDialogButtonBox(rsd)
        self.buttonBox.setGeometry(QtCore.QRect(10, 600, 1130, 35))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBoxOkCancel")
        self.label = QtWidgets.QLabel(rsd)
        self.label.setGeometry(QtCore.QRect(20, 10, 1120, 140))
        self.label.setWordWrap(True)
        self.label.setObjectName("labelInstructions")
        self.scrollArea = QtWidgets.QScrollArea(rsd)
        self.scrollArea.setGeometry(QtCore.QRect(10, 150, 1130, 440))
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidget = QtWidgets.QWidget()
        self.scrollAreaWidgetContents = QtWidgets.QFormLayout()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")



        # Create 1 set of (checkbox, label, combobox per fromcategory


        for index, source in enumerate(sources_json):

            objectdict = {'checkbox': None, 'label': None}
            layout = QtWidgets.QHBoxLayout()
            objectdict['checkbox'] = QtWidgets.QCheckBox()
            objectdict['checkbox'].setGeometry(QtCore.QRect(0, 0, 20, 20))
            objectdict['checkbox'].setText("")
            objectdict['checkbox'].setObjectName("checkBox" + str(index))
            objectdict['checkbox'].setCheckState(2)
            layout.addWidget(objectdict['checkbox'])
            objectdict['label']= QtWidgets.QLabel()
            objectdict['label'].setGeometry(QtCore.QRect(0, 0, 480, 25))
            objectdict['label'].setObjectName("label" + str(index))
            objectdict['label'].setText(source['name'])
            layout.addWidget(objectdict['label'])

            self.objectlist.append(objectdict)
            self.scrollAreaWidgetContents.addRow(layout)

        self.scrollAreaWidget.setLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollArea.show()


        self.retranslateUi(rsd)
        self.buttonBox.accepted.connect(rsd.accept)
        self.buttonBox.rejected.connect(rsd.reject)
        QtCore.QMetaObject.connectSlotsByName(rsd)

    def retranslateUi(self, restoreSourcesDialog):
        _translate = QtCore.QCoreApplication.translate
        restoreSourcesDialog.setWindowTitle(_translate("Restore Sources", "Dialog"))
        self.label.setText(_translate("Restore Sources",
                                      "<html><head/><body<p>Select the sources you wish to restore:</p></body></html>"))

    def getresults(self):
        results = []
        for object in self.objectlist:
            if str(object['checkbox'].checkState()) == '2':
                results.append(object['label'].text())
        return results

class collector_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(collector_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Collectors'
        self.cred_usage = 'both'
        collector_ui = os.path.join(self.mainwindow.basedir, 'data/collector.ui')
        uic.loadUi(collector_ui, self)

        self.font = "Waree"
        self.font_size = 12
        self.load_icons()

        # UI Buttons for Collection API tab


        # Setup the search bars to work and to clear when update button is pushed
        self.lineEditCollectorSearchLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetCollectorsLeft,
            self.lineEditCollectorSearchLeft.text()
        ))

        self.lineEditCollectorSearchRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetCollectorsRight,
            self.lineEditCollectorSearchRight.text()
        ))

        #self.pushButtonUpdateListLeft.clicked.connect(self.lineEditCollectorSearchLeft.clear)
        #self.pushButtonUpdateListRight.clicked.connect(self.lineEditCollectorSearchRight.clear)

        #

        self.pushButtonUpdateListLeft.clicked.connect(lambda: self.update_collector_list(
            self.listWidgetCollectorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text()
        ))

        self.pushButtonUpdateListRight.clicked.connect(lambda: self.update_collector_list(
            self.listWidgetCollectorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupFilterRight,
            self.lineEditCollectorSearchRight.text()
        ))

        self.buttonGroupFilterLeft.buttonClicked.connect(lambda: self.update_collector_listwidget(
            self.listWidgetCollectorsLeft, 
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text()
        ))
        
        self.buttonGroupFilterRight.buttonClicked.connect(lambda: self.update_collector_listwidget(
            self.listWidgetCollectorsRight, 
            self.buttonGroupFilterRight,
            self.lineEditCollectorSearchRight.text()
        ))
        
        self.pushButtonCopySourcesLeftToRight.clicked.connect(lambda: self.copysources(
            self.listWidgetCollectorsLeft,
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesLeft,
            self.listWidgetSourcesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCopySourcesRightToLeft.clicked.connect(lambda: self.copysources(
            self.listWidgetCollectorsRight,
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesRight,
            self.listWidgetSourcesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupCollectorLeft.clicked.connect(lambda: self.backupcollector(
            self.listWidgetCollectorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupCollectorRight.clicked.connect(lambda: self.backupcollector(
            self.listWidgetCollectorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCollectorJSONLeft.clicked.connect(lambda: self.view_collector_JSON(
            self.listWidgetCollectorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonCollectorJSONRight.clicked.connect(lambda: self.view_collector_JSON(
            self.listWidgetCollectorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteCollectorLeft.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetCollectorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteCollectorRight.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetCollectorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteSourcesLeft.clicked.connect(lambda: self.deletesources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteSourcesRight.clicked.connect(lambda: self.deletesources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonRestoreSourcesLeft.clicked.connect(lambda: self.restoresources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRestoreSourcesRight.clicked.connect(lambda: self.restoresources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())

        ))

        self.pushButtonSourceJSONLeft.clicked.connect(lambda: self.view_source_JSON(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonSourceJSONRight.clicked.connect(lambda: self.view_source_JSON(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        # set up a signal to update the source list if a new collector is set
        self.listWidgetCollectorsLeft.itemSelectionChanged.connect(lambda: self.update_source_list(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.listWidgetCollectorsRight.itemSelectionChanged.connect(lambda: self.update_source_list(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))
        
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
            self.listWidgetCollectorsLeft.collectors = []
            self.listWidgetCollectorsLeft.clear()
            self.listWidgetSourcesLeft.clear()
            self.lineEditCollectorSearchLeft.clear()
            self.radioButtonFilterAllLeft.setChecked(True)

        if right:
            self.listWidgetCollectorsRight.collectors = []
            self.listWidgetCollectorsRight.clear()
            self.listWidgetSourcesRight.clear()
            self.lineEditCollectorSearchRight.clear()
            self.radioButtonFilterAllRight.setChecked(True)

    def load_icons(self):
        self.icons = {}
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/hosted_collector.svg'))
        self.icons['Hosted'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/installed_collector.svg'))
        self.icons['Installable'] = QtGui.QIcon(iconpath)

    def set_listwidget_filter(self, ListWidget, filtertext):
        for row in range(ListWidget.count()):
            item = ListWidget.item(row)
            widget = ListWidget.itemWidget(item)
            if filtertext:
                item.setHidden(not filtertext in item.text())
            else:
                item.setHidden(False)

    def getcollectorid(self, collectorname, url, id, key):
        logger.info("[Collectors] Getting Collector IDs")
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            sumocollectors = sumo.get_collectors_sync()

            for sumocollector in sumocollectors:
                if sumocollector['name'] == collectorname:
                    return sumocollector['id']
        except Exception as e:
            logger.exception(e)
        return

    def getsourceid(self, collectorid, sourcename, url, id, key):
        logger.info("[Collectors] Getting Source IDs")
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            sumosources = sumo.sources(collectorid)

            for sumosource in sumosources:
                if sumosource['name'] == sourcename:
                    return sumosource['id']
            return False
        except Exception as e:
            logger.exception(e)
        return

    def update_collector_list(self, CollectorListWidget, url, id, key, radiobuttongroup, filter_text):
        logger.info("[Collectors] Updating Collector List")
        regexprog = re.compile(r'\S+')  # make sure username and password have something in them
        if (re.match(regexprog, id) != None) and (re.match(regexprog, key) != None):
            # access the API with provided credentials
            sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
            try:
                CollectorListWidget.collectors = sumo.get_collectors_sync()  # get list of collectors
                self.update_collector_listwidget(CollectorListWidget, radiobuttongroup, filter_text)


            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('No user and/or password.')
        return

    def update_collector_listwidget(self, CollectorListWidget, radiobuttongroup, filter_text):
        CollectorListWidget.clear()  # clear the list first since it might already be populated
        for collector in CollectorListWidget.collectors:
            try:
                item = QtWidgets.QListWidgetItem(self.icons[collector['collectorType']], collector['name'])
            except Exception as e:
                item = QtWidgets.QListWidgetItem(collector['name'])
                logger.info(e)

            if (collector['collectorType'] == "Installable") and (collector['alive'] == False):
                item.setFont(QtGui.QFont(self.font, pointSize=self.font_size, italic=True))

            if radiobuttongroup.checkedId() == -2:  # Show all collectors
                CollectorListWidget.addItem(item)  # populate the list widget in the GUI
            elif radiobuttongroup.checkedId() == -3:  # Show only hosted collectors
                if collector['collectorType'] == "Hosted":
                    CollectorListWidget.addItem(item)  # populate the list widget in the GUI
            elif radiobuttongroup.checkedId() == -4:  # Show only installed collectors
                if collector['collectorType'] == "Installable":
                    CollectorListWidget.addItem(item)  # populate the list widget in the GUI
            elif radiobuttongroup.checkedId() == -5:  # Show only dead collectors
                if (collector['collectorType'] == "Installable") and (collector['alive'] == False ):
                    CollectorListWidget.addItem(item)  # populate the list widget in the GUI
            else:
                logger.info('[Collectors]Fell through conditions in update_list_widget')
        self.set_listwidget_filter(CollectorListWidget, filter_text)

    def update_source_list(self, CollectorListWidget, SourceListWidget, url, id, key):
        logger.info("[Collectors] Updating Source List")
        SourceListWidget.clear()  # clear the list first since it might already be populated
        collectors = CollectorListWidget.selectedItems()
        if (len(collectors) > 1) or (len(collectors) < 1):
            return
        else:
            collector = self.getcollectorid(collectors[0].text(), url, id, key)
            sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
            # populate the list of sources
            sources = sumo.sources(collector)
            for source in sources:
                SourceListWidget.addItem(source['name'])  # populate the display with sources
        return

    def copysources(self, CollectorListWidgetFrom, CollectorListWidgetTo, SourceListWidgetFrom, SourceListWidgetTo,
                    fromurl, fromid, fromkey, tourl, toid, tokey):
        logger.info("[Collectors] Copying Sources")
        try:
            fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
            sourcecollectorlist = CollectorListWidgetFrom.selectedItems()  # get the selected source collector
            if len(sourcecollectorlist) == 1:  # make sure there is a collector selected, otherwise bail
                sourcecollector = sourcecollectorlist[0].text()  # qstring to string conversion
                sourcecollectorid = self.getcollectorid(sourcecollector, fromurl, fromid, fromkey)
                destinationcollectorlist = CollectorListWidgetTo.selectedItems()  # get the selected dest collector
                if len(destinationcollectorlist) > 0:  # make sure there is a collector selected, otherwise bail
                    fromsources = SourceListWidgetFrom.selectedItems()  # get the selected sources
                    if len(fromsources) > 0:  # make sure at least one source is selected
                        fromsourcelist = []
                        for fromsource in fromsources:  # iterate through source names to build a warning message
                            fromsourcelist.append(fromsource.text())
                    else:
                        self.mainwindow.errorbox('No Sources Selected.')
                        return
                    destinationcollectorstring = ''
                    for destinationcollector in destinationcollectorlist:
                        destinationcollectorstring = destinationcollectorstring + destinationcollector.text() + ", "
                    message = "You are about to copy the following sources from collector \"" + sourcecollector + "\" to \"" + destinationcollectorstring + "\". Is this correct? \n\n"
                    for source in fromsourcelist:
                        message = message + source + "\n"
                    result = QtWidgets.QMessageBox.question(self, 'Really Copy?', message,
                                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                            QtWidgets.QMessageBox.No)  # bring up the copy dialog
                    if result:  # If they clicked "OK" rather than cancel
                        tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                        for destinationcollector in destinationcollectorlist:
                            destinationcollectorname = destinationcollector.text()
                            destinationcollectorid = self.getcollectorid(destinationcollectorname, tourl, toid,
                                                                         tokey)  # qstring to string conversion
                            sumosources = fromsumo.sources(sourcecollectorid)
                            for source in fromsourcelist:  # iterate through the selected sources and copy them
                                for sumosource in sumosources:
                                    if sumosource['name'] == source:
                                        if 'id' in sumosource:  # the API creates an ID so this must be deleted before sending
                                            del sumosource['id']
                                        if 'alive' in sumosource:
                                            del sumosource['alive']  # the API sets this itself so this must be deleted before sending
                                        template = {}
                                        template['source'] = sumosource  # the API expects a dict with a key called 'source'
                                        notduplicate = True
                                        sumotosourcelist = tosumo.sources(destinationcollectorid)
                                        for sumotosource in sumotosourcelist:
                                            if sumotosource['name'] == source:  # make sure the source doesn't already exist in the destination
                                                notduplicate = False
                                        if notduplicate:  # finally lets copy this thing
                                            tosumo.create_source(destinationcollectorid, template)
                                        else:
                                            self.mainwindow.errorbox(source + ' already exists, skipping.')
                        # call the update method for the dest collector since they have changed after the copy
                        if len(destinationcollectorlist) > 1:
                            self.mainwindow.infobox(
                                "Copy Complete. Please select an individual destination collector to see an updated source list.")

                        else:
                            self.update_source_list(CollectorListWidgetTo, SourceListWidgetTo, tourl, toid, tokey)


                else:
                    self.mainwindow.errorbox('You Must Select at Least 1 target.')
            else:
                self.mainwindow.errorbox('No Source Collector Selected.')
        except Exception as e:
            self.mainwindow.errorbox('Encountered a bug. Check the console output.')
            logger.exception(e)
        return

    def backupcollector(self, CollectorListWidget, url, id, key):
        logger.info("[Collectors] Backing Up Collector")
        collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
        if len(collectornamesqstring) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for collectornameqstring in collectornamesqstring:
                    collectorid = self.getcollectorid(str(collectornameqstring.text()), url, id, key)
                    savefilepath = pathlib.Path(savepath + r'/' + str(collectornameqstring.text()) + r'.collector.json')
                    savefilesourcespath = pathlib.Path(
                        savepath + r'/' + str(collectornameqstring.text()) + r'_sources' + r'.sources.json')

                    if savefilepath:
                        with savefilepath.open(mode='w') as filepointer:
                            collector, _ = sumo.get_collector_by_id(collectorid)
                            json.dump(collector, filepointer)
                    if savefilesourcespath:
                        with savefilesourcespath.open(mode='w') as filepointer:
                            json.dump(sumo.sources(collectorid), filepointer)
                    message = message + str(collectornameqstring.text()) + ' '
                self.mainwindow.infobox('Wrote files ' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No Source Collector Selected.')
        return

    def view_collector_JSON(self, CollectorListWidget, url, id, key):
        logger.info("[Collectors] Viewing Collector JSON")
        collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
        if len(collectornamesqstring) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for collectornameqstring in collectornamesqstring:
                    collector = sumo.get_collector_by_name_alternate(str(collectornameqstring.text()))
                    # sources = sumo.get_sources_sync(collector['id'])
                    json_text = json_text + json.dumps(collector, indent=4, sort_keys=True) + '\n\n'
                    # json_text = json_text + json.dumps(sources, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()
            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
        else:
            self.mainwindow.errorbox('No Collector Selected.')
        return

    def view_source_JSON(self, CollectorListWidget, SourceListWidget, url, id, key):
        logger.info("[Collectors] Viewing Source JSON")
        sourcenames = SourceListWidget.selectedItems()
        if len(sourcenames) > 0:  # make sure at least one source is selected
            try:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
                collectorname = str(collectornamesqstring[0].text())
                collector = sumo.get_collector_by_name_alternate(collectorname)
                sources = sumo.get_sources_sync(collector['id'])
                for sourcename in sourcenames:
                    for source in sources:
                        if str(sourcename.text()) == source['name']:
                            json_text = json_text + json.dumps(source, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('No Source Selected.')

    def deletecollectors(self, CollectorListWidget, url, id, key):
        logger.info("[Collectors] Deleting Collectors")
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
            if (result and (str(text) == 'DELETE')):
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for collectornameqstring in collectornamesqstring:
                    try:
                        collectorid = self.getcollectorid(str(collectornameqstring.text()), url, id, key)
                        sumo.delete_collector(collectorid)
                    except Exception as e:
                        self.mainwindow.errorbox('Failed to delete collector: ' + str(collectornamesqstring.text()))
                        logger.exception(e)
                self.update_collector_list(CollectorListWidget, url, id, key)

        else:
            self.mainwindow.errorbox('No Collector Selected')
        return

    def restoresources(self, CollectorListWidget, SourceListWidget, url, id, key):
        destinationcollectors = CollectorListWidget.selectedItems()
        if len(destinationcollectors) == 1:
            destinationcollectorqstring = destinationcollectors[0].text()
            destinationcollector = str(destinationcollectorqstring)
            destinationcollectorid = self.getcollectorid(destinationcollector, url, id, key)
            filter = "JSON (*.json)"
            restorefile, status = QtWidgets.QFileDialog.getOpenFileName(self, "Open file(s)...", os.getcwd(),
                                                                        filter)

            sources = None
            try:
                with open(restorefile) as data_file:
                    sources = json.load(data_file)
            except Exception as e:
                self.mainwindow.errorbox('Failed to load JSON file.')
                logger.exception(e)

            # a sources save file from the UI looks a little different than a save file from this tool, fix it here
            if sources:
                if 'sources' in sources:
                    sources = sources['sources']
                dialog = restoreSourcesDialog(sources)
                dialog.exec()
                dialog.show()
                if str(dialog.result()) == '1':
                    selectedsources = dialog.getresults()
                else:
                    return
                if len(selectedsources) > 0:
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selectedsource in selectedsources:
                        for sumosource in sources:
                            if sumosource['name'] == str(selectedsource):
                                if 'id' in sumosource:
                                    del sumosource['id']
                                if 'alive' in sumosource:
                                    del sumosource['alive']
                                template = {}
                                template['source'] = sumosource
                                sumo.create_source(
                                    destinationcollectorid, template)
                    self.update_source_list(CollectorListWidget, SourceListWidget, url, id, key)
                else:
                    self.mainwindow.errorbox('No sources selected for import.')
        else:
            self.mainwindow.errorbox('Please select 1 and only 1 collector to restore sources to.')
        return

    def deletesources(self, CollectorListWidget, SourceListWidget, url, id, key):
        logger.info("[Collectors] Deleting Sources")
        collectornamesqstring = CollectorListWidget.selectedItems()
        if len(collectornamesqstring) == 1:  # make sure something was selected
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
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for sourcenameqstring in sourcenamesqstring:
                        try:
                            sourceid = self.getsourceid(collectorid, str(sourcenameqstring.text()), url, id, key)
                            sumo.delete_source(collectorid, sourceid)
                        except Exception as e:
                            self.mainwindow.errorbox('Failed to delete source: ' + str(sourcenameqstring.text()))
                            logger.exception(e)
                    self.update_source_list(CollectorListWidget, SourceListWidget, url, id, key)

            else:
                self.mainwindow.errorbox('No Source(s) Selected')
        else:
            self.mainwindow.errorbox('You must select 1 and only 1 collector.')
        return


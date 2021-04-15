from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import pathlib
import json
from logzero import logger
from modules.shared import ShowTextDialog, exception_and_error_handling
from modules.tab_base_class import BaseTab


class_name = 'CollectorTab'


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
            objectdict['label'] = QtWidgets.QLabel()
            objectdict['label'].setGeometry(QtCore.QRect(0, 0, 480, 25))
            objectdict['label'].setObjectName("label" + str(index))
            if 'name' in source:
                objectdict['label'].setText(source['name'])
            elif 'config' in source:
                objectdict['label'].setText(source['config']['name'])
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


class CollectorTab(BaseTab):

    def __init__(self, mainwindow):
        super(CollectorTab, self).__init__(mainwindow)
        self.tab_name = 'Collectors'
        self.cred_usage = 'both'
        collector_ui = os.path.join(self.mainwindow.basedir, 'data/collector.ui')
        uic.loadUi(collector_ui, self)

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

        # self.pushButtonUpdateListLeft.clicked.connect(self.lineEditCollectorSearchLeft.clear)
        # self.pushButtonUpdateListRight.clicked.connect(self.lineEditCollectorSearchRight.clear)

        #

        self.pushButtonUpdateListLeft.clicked.connect(lambda: self.update_collector_list(
            self.listWidgetCollectorsLeft,
            self.mainwindow.get_current_creds('left'),
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text()
        ))

        self.pushButtonUpdateListRight.clicked.connect(lambda: self.update_collector_list(
            self.listWidgetCollectorsRight,
            self.mainwindow.get_current_creds('right'),
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
            self.mainwindow.get_current_creds('left'),
            self.mainwindow.get_current_creds('right')
        ))

        self.pushButtonCopySourcesRightToLeft.clicked.connect(lambda: self.copysources(
            self.listWidgetCollectorsRight,
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesRight,
            self.listWidgetSourcesLeft,
            self.mainwindow.get_current_creds('right'),
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonBackupCollectorLeft.clicked.connect(lambda: self.backupcollector(
            self.listWidgetCollectorsLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonBackupCollectorRight.clicked.connect(lambda: self.backupcollector(
            self.listWidgetCollectorsRight,
            self.mainwindow.get_current_creds('right')
        ))

        self.pushButtonCollectorJSONLeft.clicked.connect(lambda: self.view_collector_JSON(
            self.listWidgetCollectorsLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonCollectorJSONRight.clicked.connect(lambda: self.view_collector_JSON(
            self.listWidgetCollectorsRight,
            self.mainwindow.get_current_creds('right')
        ))

        self.pushButtonDeleteCollectorLeft.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetCollectorsLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonDeleteCollectorRight.clicked.connect(lambda: self.deletecollectors(
            self.listWidgetCollectorsRight,
            self.mainwindow.get_current_creds('right')
        ))

        self.pushButtonDeleteSourcesLeft.clicked.connect(lambda: self.deletesources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonDeleteSourcesRight.clicked.connect(lambda: self.deletesources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.get_current_creds('right')
        ))

        self.pushButtonRestoreSourcesLeft.clicked.connect(lambda: self.restoresources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonRestoreSourcesRight.clicked.connect(lambda: self.restoresources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.get_current_creds('right')

        ))

        self.pushButtonSourceJSONLeft.clicked.connect(lambda: self.view_source_JSON(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonSourceJSONRight.clicked.connect(lambda: self.view_source_JSON(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.get_current_creds('right')
        ))

        # set up a signal to update the source list if a new collector is set
        self.listWidgetCollectorsLeft.itemSelectionChanged.connect(lambda: self.update_source_list(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.mainwindow.get_current_creds('left')
        ))

        self.listWidgetCollectorsRight.itemSelectionChanged.connect(lambda: self.update_source_list(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.mainwindow.get_current_creds('right')
        ))

    def reset_stateful_objects(self, side='both'):
        left = None
        right = None
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

    def set_listwidget_filter(self, list_widget, filter_text):
        for row in range(list_widget.count()):
            item = list_widget.item(row)
            widget = list_widget.itemWidget(item)
            if filter_text:
                item.setHidden(not filter_text in item.text())
            else:
                item.setHidden(False)

    def getcollectorid(self, collectorname, creds):
        logger.info("[Collectors] Getting Collector IDs")
        sumo = self.mainwindow.sumo_from_creds(creds)
        try:
            sumocollectors = sumo.get_collectors_sync()

            for sumocollector in sumocollectors:
                if sumocollector['name'] == collectorname:
                    return sumocollector['id']
        except Exception as e:
            logger.exception(e)
        return

    def getsourceid(self, collectorid, sourcename, creds):
        logger.info("[Collectors] Getting Source IDs")
        sumo = self.mainwindow.sumo_from_creds(creds)
        try:
            sumosources = sumo.sources(collectorid)

            for sumosource in sumosources:
                if 'name' in sumosource and sumosource['name'] == sourcename:
                    return sumosource['id']
                elif 'config' in sumosource and sumosource['config']['name'] == sourcename:
                    return sumosource['id']
            return False
        except Exception as e:
            logger.exception(e)
        return

    @exception_and_error_handling
    def update_collector_list(self, CollectorListWidget, creds, radiobuttongroup, filter_text):
        logger.info("[Collectors] Updating Collector List")
        sumo = self.mainwindow.sumo_from_creds(creds)
        CollectorListWidget.collectors = sumo.get_collectors_sync()  # get list of collectors
        self.update_collector_listwidget(CollectorListWidget, radiobuttongroup, filter_text)


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
                if (collector['collectorType'] == "Installable") and (collector['alive'] == False):
                    CollectorListWidget.addItem(item)  # populate the list widget in the GUI
            else:
                logger.info('[Collectors]Fell through conditions in update_list_widget')
        self.set_listwidget_filter(CollectorListWidget, filter_text)

    @exception_and_error_handling
    def update_source_list(self, CollectorListWidget, SourceListWidget, creds):
        logger.info("[Collectors] Updating Source List")
        SourceListWidget.clear()  # clear the list first since it might already be populated
        collectors = CollectorListWidget.selectedItems()
        # if we have multiple collectors selected or none selected then don't try to populate the sources list
        if (len(collectors) > 1) or (len(collectors) < 1):
            return
        else:
            collector = self.getcollectorid(collectors[0].text(), creds)
            sumo = self.mainwindow.sumo_from_creds(creds)
            # populate the list of sources
            sources = sumo.sources(collector)
            for source in sources:
                if 'name' in source:
                    SourceListWidget.addItem(source['name'])  # populate the display with sources
                elif 'config' in source:
                    SourceListWidget.addItem(source['config']['name'])  # populate the display with C2C sources
        return

    @exception_and_error_handling
    def copysources(self, CollectorListWidgetFrom, CollectorListWidgetTo, SourceListWidgetFrom, SourceListWidgetTo,
                    from_creds, to_creds):
        logger.info("[Collectors] Copying Sources")
        from_sumo = self.mainwindow.sumo_from_creds(from_creds)
        sourcecollectorlist = CollectorListWidgetFrom.selectedItems()  # get the selected source collector
        if len(sourcecollectorlist) != 1: return  # make sure there is a single collector selected, otherwise bail
        sourcecollector = sourcecollectorlist[0].text()  # qstring to string conversion
        sourcecollectorid = self.getcollectorid(sourcecollector,
                                                from_creds)
        destinationcollectorlist = CollectorListWidgetTo.selectedItems()  # get the selected dest collector
        if len(destinationcollectorlist) < 1: return # make sure there is a collector selected, otherwise bail
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
            to_sumo = self.mainwindow.sumo_from_creds(to_creds)
            for destinationcollector in destinationcollectorlist:
                destinationcollectorname = destinationcollector.text()
                destinationcollectorid = self.getcollectorid(destinationcollectorname, to_creds)  # qstring to string conversion
                sumosources = from_sumo.sources(sourcecollectorid)
                for source in fromsourcelist:  # iterate through the selected sources and copy them
                    for sumosource in sumosources:
                        # if sumosource['name'] == source:
                        if ('name' in sumosource and source == sumosource['name']) or (
                                'config' in sumosource and source == sumosource['config']['name']):
                            if 'id' in sumosource:  # the API creates an ID so this must be deleted before sending
                                del sumosource['id']
                            if 'alive' in sumosource:
                                del sumosource[
                                    'alive']  # the API sets this itself so this must be deleted before sending
                            template = {}
                            template[
                                'source'] = sumosource  # the API expects a dict with a key called 'source'
                            notduplicate = True
                            sumotosourcelist = to_sumo.sources(destinationcollectorid)
                            for sumotosource in sumotosourcelist:
                                # make sure the source doesn't already exist in the destination
                                if ('name' in sumotosource and sumotosource['name'] == source) or (
                                        'config' in sumotosource and sumotosource['config']['name'] == source):
                                    notduplicate = False
                            if notduplicate:  # finally lets copy this thing
                                to_sumo.create_source(destinationcollectorid, template)
                            else:
                                self.mainwindow.errorbox(source + ' already exists, skipping.')
            # call the update method for the dest collector since they have changed after the copy
            if len(destinationcollectorlist) > 1:
                self.mainwindow.infobox(
                    "Copy Complete. Please select an individual destination collector to see an updated source list.")

            else:
                self.update_source_list(CollectorListWidgetTo, SourceListWidgetTo, to_creds)

    @exception_and_error_handling
    def backupcollector(self, CollectorListWidget, creds):
        logger.info("[Collectors] Backing Up Collector")
        collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
        if len(collectornamesqstring) < 1:  return # make sure something was selected
        savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
        if os.access(savepath, os.W_OK):
            message = ''
            sumo = self.mainwindow.sumo_from_creds(creds)
            for collectornameqstring in collectornamesqstring:
                collectorid = self.getcollectorid(str(collectornameqstring.text()), creds)
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

    @exception_and_error_handling
    def view_collector_JSON(self, CollectorListWidget, creds):
        logger.info("[Collectors] Viewing Collector JSON")
        collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
        if len(collectornamesqstring) < 1: return  # make sure something was selected
        sumo = self.mainwindow.sumo_from_creds(creds)
        json_text = ''
        for collectornameqstring in collectornamesqstring:
            collector = sumo.get_collector_by_name_alternate(str(collectornameqstring.text()))
            # sources = sumo.get_sources_sync(collector['id'])
            json_text = json_text + json.dumps(collector, indent=4, sort_keys=True) + '\n\n'
            # json_text = json_text + json.dumps(sources, indent=4, sort_keys=True) + '\n\n'
        self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
        self.json_window.show()

    @exception_and_error_handling
    def view_source_JSON(self, CollectorListWidget, SourceListWidget, creds):
        logger.info("[Collectors] Viewing Source JSON")
        sourcenames = SourceListWidget.selectedItems()
        if len(sourcenames) < 1: return  # make sure at least one source is selected
        sumo = self.mainwindow.sumo_from_creds(creds)
        json_text = ''
        collectornamesqstring = CollectorListWidget.selectedItems()  # get collectors sources have been selected
        collectorname = str(collectornamesqstring[0].text())
        collector = sumo.get_collector_by_name_alternate(collectorname)
        sources = sumo.get_sources_sync(collector['id'])
        for sourcename in sourcenames:
            for source in sources:
                if ('name' in source and str(sourcename.text()) == source['name']) or (
                        'config' in source and str(sourcename.text()) == source['config']['name']):
                    json_text = json_text + json.dumps(source, indent=4, sort_keys=True) + '\n\n'
        self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
        self.json_window.show()

    @exception_and_error_handling
    def deletecollectors(self, CollectorListWidget, creds):
        logger.info("[Collectors] Deleting Collectors")
        collectornamesqstring = CollectorListWidget.selectedItems()
        if len(collectornamesqstring) < 1: return # make sure something was selected
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
            sumo = self.mainwindow.sumo_from_creds(creds)
            for collectornameqstring in collectornamesqstring:
                collectorid = self.getcollectorid(str(collectornameqstring.text()), creds)
                sumo.delete_collector(collectorid)
            self.update_collector_list(CollectorListWidget, creds)

    @exception_and_error_handling
    def restoresources(self, CollectorListWidget, SourceListWidget, creds):
        destinationcollectors = CollectorListWidget.selectedItems()
        if len(destinationcollectors) != 1: return
        destinationcollectorqstring = destinationcollectors[0].text()
        destinationcollector = str(destinationcollectorqstring)
        destinationcollectorid = self.getcollectorid(destinationcollector, creds)
        filter = "JSON (*.json)"
        restorefile, status = QtWidgets.QFileDialog.getOpenFileName(self, "Open file(s)...", os.getcwd(), filter)
        sources = None
        with open(restorefile) as data_file:
            sources = json.load(data_file)
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
                sumo = self.mainwindow.sumo_from_creds(creds)
                for selectedsource in selectedsources:
                    for sumosource in sources:
                        if ('name' in sumosource and sumosource['name'] == str(selectedsource)) or ('config' in sumosource and sumosource['config']['name'] == str(selectedsource)):
                            if 'id' in sumosource:
                                del sumosource['id']
                            if 'alive' in sumosource:
                                del sumosource['alive']
                            template = {}
                            template['source'] = sumosource
                            sumo.create_source(
                                destinationcollectorid, template)
                self.update_source_list(CollectorListWidget, SourceListWidget, creds)
            else:
                self.mainwindow.errorbox('No sources selected for import.')

    @exception_and_error_handling
    def deletesources(self, CollectorListWidget, SourceListWidget, creds):
        logger.info("[Collectors] Deleting Sources")
        collectornamesqstring = CollectorListWidget.selectedItems()
        if len(collectornamesqstring) != 1: return  # make sure something was selected
        collectorid = self.getcollectorid(str(collectornamesqstring[0].text()), creds)
        sourcenamesqstring = SourceListWidget.selectedItems()
        if len(sourcenamesqstring) < 1: return  # make sure something was selected
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
            sumo = self.mainwindow.sumo_from_creds(creds)
            for sourcenameqstring in sourcenamesqstring:
                sourceid = self.getsourceid(collectorid, str(sourcenameqstring.text()), creds)
                sumo.delete_source(collectorid, sourceid)
            self.update_source_list(CollectorListWidget, SourceListWidget, creds)




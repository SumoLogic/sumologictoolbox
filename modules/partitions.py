from qtpy import QtWidgets, uic
import os
import sys
import pathlib
import json
from logzero import logger
from datetime import datetime, timezone
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog


class partitions_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(partitions_tab, self).__init__()
        self.mainwindow = mainwindow

        partitions_widget_ui = os.path.join(self.mainwindow.basedir, 'data/partitions.ui')
        uic.loadUi(partitions_widget_ui, self)

        self.pushButtonUpdatePartitionLeft.clicked.connect(lambda: self.update_partition_list(
            self.PartitionListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdatePartitionRight.clicked.connect(lambda: self.update_partition_list(
            self.PartitionListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonPartitionDecommissionLeft.clicked.connect(lambda: self.decommission_partition(
            self.PartitionListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonPartitionDecommissionRight.clicked.connect(lambda: self.decommission_partition(
            self.PartitionListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonPartitionCopyLeftToRight.clicked.connect(lambda: self.copy_partition(
            self.PartitionListWidgetLeft,
            self.PartitionListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonPartitionCopyRightToLeft.clicked.connect(lambda: self.copy_partition(
            self.PartitionListWidgetRight,
            self.PartitionListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonPartitionBackupLeft.clicked.connect(lambda: self.backup_partition(
            self.PartitionListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonPartitionBackupRight.clicked.connect(lambda: self.backup_partition(
            self.PartitionListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonPartitionJSONLeft.clicked.connect(lambda: self.view_json(
            self.PartitionListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonPartitionJSONRight.clicked.connect(lambda: self.view_json(
            self.PartitionListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonPartitionRestoreLeft.clicked.connect(lambda: self.restore_partition(
            self.PartitionListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonPartitionRestoreRight.clicked.connect(lambda: self.restore_partition(
            self.PartitionListWidgetRight,
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
            self.SVListWidgetLeft.clear()
            self.SVListWidgetLeft.currentcontent = {}

        if right:
            self.SVListWidgetRight.clear()
            self.SVListWidgetRight.currentcontent = {}

    def update_partition_list(self, PartitionListWidget, url, id, key):
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            logger.info("[Partitions]Updating Partition List")
            PartitionListWidget.currentcontent = sumo.get_partitions_sync()
            PartitionListWidget.clear()
            if len(PartitionListWidget.currentcontent) > 0:
                self.update_partition_listwidget(PartitionListWidget)
                return
        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def update_partition_listwidget(self, PartitionListWidget):
        try:
            PartitionListWidget.clear()
            PartitionListWidget.setSortingEnabled(True)
            for object in PartitionListWidget.currentcontent:
                if object['isActive']:
                    item_name = object['name']
                    PartitionListWidget.addItem(item_name)  # populate the list widget in the GUI
            PartitionListWidget.updated = True
        except Exception as e:
            logger.exception(e)
        return

    def decommission_partition(self, PartitionListWidget, url, id, key):
        logger.info("[Partitions]Decommissioning Partition(s)")
        selecteditems = PartitionListWidget.selectedItems()
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

                    sumo = SumoLogic(id, key, endpoint=url)
                    for selecteditem in selecteditems:
                        for object in PartitionListWidget.currentcontent:
                            if object['name'] == str(selecteditem.text()):
                                item_id = object['id']

                        result = sumo.decommission_partition(item_id)

                    self.update_partition_list(PartitionListWidget, url, id, key)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return

    def copy_partition(self, PartitionListWidgetFrom, PartitionListWidgetTo, fromurl, fromid, fromkey,
                            tourl, toid,
                            tokey):

        logger.info("[Partitions]Copying Partition(s)")
        try:
            selecteditems = PartitionListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                for selecteditem in selecteditems:
                    for object in PartitionListWidgetFrom.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            partitions_export = fromsumo.get_partition(item_id)
                            status = tosumo.create_partition(partitions_export['name'],
                                                             partitions_export['routingExpression'],
                                                             analytics_tier=partitions_export['analyticsTier'],
                                                             retention_period=partitions_export['retentionPeriod'],
                                                             is_compliant=partitions_export['isCompliant'])
                self.update_partition_list(PartitionListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_partition_list(PartitionListWidgetTo, tourl, toid, tokey)
        return

    def backup_partition(self, PartitionListWidget, url, id, key):
        logger.info("[Partitions]Backing Up Partition(s)")
        selecteditems = PartitionListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url)
                for selecteditem in selecteditems:
                    for object in PartitionListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            try:
                                export = sumo.get_partition(item_id)

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.partition.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(export, filepointer)
                                    message = message + str(selecteditem.text()) + r'.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                                return
                self.mainwindow.errorbox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No partition selected.')
        return

    def view_json(self, PartitionListWidget, url, id, key):
        logger.info("[Partitions]Viewing Partition(s) as JSON")
        selecteditems = PartitionListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in PartitionListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            fer = sumo.get_partition(item_id)
                            json_text = json_text + json.dumps(fer, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                return

        else:
            self.mainwindow.errorbox('No partition selected.')
        return

    def restore_partition(self, PartitionListWidget, url, id, key):
        logger.info("[Partitions]Restoring partitions(s)")
        if PartitionListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:
                sumo = SumoLogic(id, key, endpoint=url)
                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            partition_backup = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        status = sumo.create_partition(partition_backup['name'],
                                                       partition_backup['routingExpression'],
                                                       analytics_tier=partition_backup['analyticsTier'],
                                                       retention_period=partition_backup['retentionPeriod'],
                                                       is_compliant=partition_backup['isCompliant'])

                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_partition_list(PartitionListWidget, url, id, key)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the directory list before restoring content")
        return

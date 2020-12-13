class_name = 'saml_tab'


from qtpy import QtWidgets, uic
import os
import sys
import pathlib
import json
from logzero import logger
from datetime import datetime, timezone
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog, import_saml_config


class saml_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(saml_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'SAML'
        self.cred_usage = 'both'
        saml_widget_ui = os.path.join(self.mainwindow.basedir, 'data/saml.ui')
        uic.loadUi(saml_widget_ui, self)

        self.pushButtonUpdateSAMLLeft.clicked.connect(lambda: self.update_SAML_list(
            self.SAMLListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateSAMLRight.clicked.connect(lambda: self.update_SAML_list(
            self.SAMLListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonSAMLDeleteLeft.clicked.connect(lambda: self.delete_saml(
            self.SAMLListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonSAMLDeleteRight.clicked.connect(lambda: self.delete_saml(
            self.SAMLListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonSAMLCopyLeftToRight.clicked.connect(lambda: self.copy_saml(
            self.SAMLListWidgetLeft,
            self.SAMLListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonSAMLCopyRightToLeft.clicked.connect(lambda: self.copy_saml(
            self.SAMLListWidgetRight,
            self.SAMLListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonSAMLBackupLeft.clicked.connect(lambda: self.backup_saml(
            self.SAMLListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonSAMLBackupRight.clicked.connect(lambda: self.backup_saml(
            self.SAMLListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonSAMLJSONLeft.clicked.connect(lambda: self.view_json(
            self.SAMLListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonSAMLJSONRight.clicked.connect(lambda: self.view_json(
            self.SAMLListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonSAMLRestoreLeft.clicked.connect(lambda: self.restore_saml(
            self.SAMLListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonSAMLRestoreRight.clicked.connect(lambda: self.restore_saml(
            self.SAMLListWidgetRight,
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
            self.SAMLListWidgetLeft.clear()
            self.SAMLListWidgetLeft.currentcontent = {}
            self.SAMLListWidgetLeft.updated = False

        if right:
            self.SAMLListWidgetRight.clear()
            self.SAMLListWidgetRight.currentcontent = {}
            self.SAMLListWidgetRight.updated = False

    def update_SAML_list(self, SAMLListWidget, url, id, key):
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            logger.info("[SAML]Updating SAML config List")
            SAMLListWidget.currentcontent = sumo.get_saml_configs()
            SAMLListWidget.clear()
            self.update_SAML_listwidget(SAMLListWidget)
            return
        except Exception as e:
            logger.exception(e)
            SAMLListWidget.updated = False
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def update_SAML_listwidget(self, SAMLListWidget):
        try:
            SAMLListWidget.clear()
            SAMLListWidget.setSortingEnabled(True)
            for object in SAMLListWidget.currentcontent:
                item_name = object['configurationName']
                SAMLListWidget.addItem(item_name)  # populate the list widget in the GUI
            SAMLListWidget.updated = True
        except Exception as e:
            logger.exception(e)
            SAMLListWidget.updated = False
            SAMLListWidget.clear()

        return

    def delete_saml(self, SAMLListWidget, url, id, key):
        logger.info("[SAML]Deleting SAML config(s)")
        selecteditems = SAMLListWidget.selectedItems()
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

                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        for object in SAMLListWidget.currentcontent:
                            if object['configurationName'] == str(selecteditem.text()):
                                item_id = object['id']

                        result = sumo.delete_saml_config(item_id)

                    self.update_SAML_list(SAMLListWidget, url, id, key)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return

    def copy_saml(self, SAMLListWidgetFrom, SAMLListWidgetTo, fromurl, fromid, fromkey,
                            tourl, toid,
                            tokey):

        logger.info("[SAML]Copying SAML config(s)")
        try:
            selecteditems = SAMLListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                message = "You are about to copy the following item(s):\n\n"
                for selecteditem in selecteditems:
                    message = message + str(selecteditem.text()) + "\n"
                message = message + '''
                    This is exceedingly DANGEROUS!!!! 
                    Please be VERY, VERY, VERY sure you want to do this!
                    You could cross the streams if you copy the wrong thing(s).

                    If you are absolutely sure, type "COPY" in the box below.

                                        '''
                text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
                if (result and (str(text) == 'COPY')):
                    fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                    tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        for object in SAMLListWidgetFrom.currentcontent:
                            if object['configurationName'] == str(selecteditem.text()):
                                item_id = object['id']
                                saml_export = fromsumo.get_saml_config_by_id(item_id)
                                import_saml_config(saml_export, tosumo)
                                break
                    self.update_SAML_list(SAMLListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_SAML_list(SAMLListWidgetTo, tourl, toid, tokey)
        return

    def backup_saml(self, SAMLListWidget, url, id, key):
        logger.info("[SAML]Backing Up SAML config(s)")
        selecteditems = SAMLListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in SAMLListWidget.currentcontent:
                        if object['configurationName'] == str(selecteditem.text()):
                            item_id = object['id']
                            try:

                                export = sumo.get_saml_config_by_id(item_id)

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.saml.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(export, filepointer)
                                    message = message + str(selecteditem.text()) + r'.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                                return
                self.mainwindow.infobox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No content selected.')
        return

    def view_json(self, SAMLListWidget, url, id, key):
        logger.info("[SAML]Viewing SAML(s) as JSON")
        selecteditems = SAMLListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in SAMLListWidget.currentcontent:
                        if object['configurationName'] == str(selecteditem.text()):
                            item_id = object['id']
                            fer = sumo.get_saml_config_by_id(item_id)
                            json_text = json_text + json.dumps(fer, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                return

        else:
            self.mainwindow.errorbox('No FER selected.')
        return

    def restore_saml(self, SAMLListWidget, url, id, key):
        logger.info("[SAML]Restoring SAML config(s)")
        if SAMLListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            saml_export = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        import_saml_config(saml_export, sumo)

                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_SAML_list(SAMLListWidget, url, id, key)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the SAML config list before restoring a config")
        return

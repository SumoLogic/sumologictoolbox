class_name = 'field_extraction_rule_tab'

from qtpy import QtWidgets, uic
import os
import sys
import pathlib
import json
from logzero import logger
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog

class field_extraction_rule_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(field_extraction_rule_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Field Extraction Rules'
        self.cred_usage = 'both'
        self.left_right_fers = {'left':[], 'right': []}
        field_extraction_rule_widget_ui = os.path.join(self.mainwindow.basedir, 'data/field_extraction_rule.ui')
        uic.loadUi(field_extraction_rule_widget_ui, self)

        self.pushButtonUpdateFERLeft.clicked.connect(lambda: self.update_FER_list(
            self.FERListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            'left'
        ))

        self.pushButtonUpdateFERRight.clicked.connect(lambda: self.update_FER_list(
            self.FERListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            'right'
        ))

        self.pushButtonFERDeleteLeft.clicked.connect(lambda: self.delete_fer(
            self.FERListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonFERDeleteRight.clicked.connect(lambda: self.delete_fer(
            self.FERListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonFERCopyLeftToRight.clicked.connect(lambda: self.copy_fers(
            self.FERListWidgetLeft,
            self.FERListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonFERCopyRightToLeft.clicked.connect(lambda: self.copy_fers(
            self.FERListWidgetRight,
            self.FERListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonFERBackupLeft.clicked.connect(lambda: self.backup_fer(
            self.FERListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonFERBackupRight.clicked.connect(lambda: self.backup_fer(
            self.FERListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonFERJSONLeft.clicked.connect(lambda: self.view_json(
            self.FERListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonFERJSONRight.clicked.connect(lambda: self.view_json(
            self.FERListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonFERRestoreLeft.clicked.connect(lambda: self.restore_fer(
            self.FERListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonFERRestoreRight.clicked.connect(lambda: self.restore_fer(
            self.FERListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.buttonGroupContentLeft.buttonClicked.connect(lambda: self.update_FER_listwidgets(
            self.FERListWidgetLeft,
            self.FERListWidgetRight,
            self.buttonGroupContentLeft.checkedId(),
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
            self.FERListWidgetLeft.clear()
            self.FERListWidgetLeft.currentcontent = {}
            self.FERListWidgetLeft.updated = False


        if right:
            self.FERListWidgetRight.clear()
            self.FERListWidgetRight.currentcontent = {}
            self.FERListWidgetRight.updated = False

        return

    def update_FER_list(self, FERListWidget, url, id, key, side=None):
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            logger.info("[Field Extraction Rules]Updating FER List")
            FERListWidget.currentcontent = sumo.get_fers_sync()
            self.left_right_fers[side] = FERListWidget.currentcontent
            
            FERListWidget.clear()
            if len(FERListWidget.currentcontent) > 0:
                self.update_FER_listwidget(FERListWidget)
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def update_FER_listwidget(self, FERListWidget):
        try:
            FERListWidget.clear()
            FERListWidget.setSortingEnabled(True)
            for object in FERListWidget.currentcontent:
                item_name = object['name']
                FERListWidget.addItem(item_name)  # populate the list widget in the GUI

            FERListWidget.updated = True

        except Exception as e:
            logger.exception(e)
        return

    def update_FER_listwidgets(self, FERLisLefttWidget, FERLisRightWidget, radioselected):
        try:
            if not self.left_right_fers['left'] or not self.left_right_fers['right']:
                self.mainwindow.errorbox('You need need to update both left and right sides')
                return

            FERLisLefttWidget.clear()
            FERLisLefttWidget.setSortingEnabled(True)

            FERLisRightWidget.clear()
            FERLisRightWidget.setSortingEnabled(True)

            left_fers = {fer['name']: {'scope':fer['scope'], 'parseExpression': fer['parseExpression'], 'fieldNames': fer['fieldNames']} for fer in self.left_right_fers['left']}
            right_fers = {fer['name']: {'scope':fer['scope'], 'parseExpression': fer['parseExpression'], 'fieldNames': fer['fieldNames']} for fer in self.left_right_fers['right']}

            if radioselected == -2:
                for name in left_fers.keys():
                    FERLisLefttWidget.addItem(name)  # populate the list widget in the GUI

                FERLisLefttWidget.updated = True
                
                for name in right_fers.keys():
                    FERLisRightWidget.addItem(name)  # populate the list widget in the GUI

                FERLisRightWidget.updated = True

            elif radioselected == -3:
                for name in left_fers.keys():
                    if name not in right_fers.keys():
                        logger.info("The {} FER found in the left but not right side".format(name))
                        FERLisLefttWidget.addItem(name)  # populate the list widget in the GUI
                FERLisLefttWidget.updated = True
            
            elif radioselected == -4:
                for name in right_fers.keys():
                    if name not in left_fers.keys():
                        logger.info("The {} FER found in the right but not left side".format(name))
                        FERLisRightWidget.addItem(name)  # populate the list widget in the GUI
                FERLisRightWidget.updated = True

            elif radioselected == -5:
                for left_name, left_fer in left_fers.items():
                    if left_name in right_fers.keys():
                        left_scope = left_fer['scope']
                        left_parseExpression = left_fer['parseExpression']
                        left_fieldNames = left_fer['fieldNames']
                        right_scope = right_fers[left_name]['scope']
                        right_parseExpression = right_fers[left_name]['parseExpression']
                        right_fieldNames = right_fers[left_name]['fieldNames']

                        misMatchingFields = len([rfn for rfn, lfn in zip(left_fieldNames, right_fieldNames) if rfn != lfn])

                        if left_scope != right_scope or \
                        left_parseExpression != right_parseExpression or \
                        len(left_fieldNames) != len(right_fieldNames) or \
                        misMatchingFields > 0:
                            logger.info("The {} FER found in both however it differ in either scope, parse Expression or field Names".format(left_name))
                            FERLisLefttWidget.addItem(left_name)  # populate the list widget in the GUI
                            FERLisRightWidget.addItem(left_name)  # populate the list widget in the GUI
                FERLisLefttWidget.updated = True
                FERLisRightWidget.updated = True

        except Exception as e:
            logger.exception(e)
        return

    def delete_fer(self, FERListWidget, url, id, key):
        logger.info("[Field Extraction Rules]Deleting FER(s)")
        selecteditems = FERListWidget.selectedItems()
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
                        for object in FERListWidget.currentcontent:
                            if object['name'] == str(selecteditem.text()):
                                item_id = object['id']

                        result = sumo.delete_fer(item_id)

                    self.update_FER_list(FERListWidget, url, id, key)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return

    def process_fer(self, exported_fer):
        processed = {}
        processed['name'] = exported_fer['name']
        processed['scope'] = exported_fer['scope']
        processed['parseExpression'] = exported_fer['parseExpression']
        processed['enabled'] = 'false'

        return processed

    def copy_fers(self, FERListWidgetFrom, FERListWidgetTo, fromurl, fromid, fromkey,
                  tourl, toid,
                  tokey):

        logger.info("[Field Extraction Rules]Copying FER(s)")
        try:
            selecteditems = FERListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in FERListWidgetFrom.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            fer_export = fromsumo.get_fer(item_id)
                            status = tosumo.create_fer(fer_export['name'], fer_export['scope'],
                                                       fer_export['parseExpression'])
                self.update_FER_list(FERListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_FER_list(FERListWidgetTo, tourl, toid, tokey)
        return

    def backup_fer(self, FERListWidget, url, id, key):
        logger.info("[Field Extraction Rules]Backing Up FER(s)")
        selecteditems = FERListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in FERListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            try:
                                export = sumo.get_fer(item_id)

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.fer.json')
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
            self.mainwindow.errorbox('No FER selected.')
        return

    def view_json(self, FERListWidget, url, id, key):
        logger.info("[Field Extraction Rules]Viewing FER(s) as JSON")
        selecteditems = FERListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in FERListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            fer = sumo.get_fer(item_id)
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

    def restore_fer(self, FERListWidget, url, id, key):
        logger.info("[Field Extraction Rules]Restoring FER(s)")
        if FERListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            fer_backup = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        status = sumo.create_fer(fer_backup['name'], fer_backup['scope'], fer_backup['parseExpression'])

                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_FER_list(FERListWidget, url, id, key)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the directory list before restoring content")
        return

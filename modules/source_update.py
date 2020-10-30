from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import sys
import copy
import re
import pathlib
import json
from logzero import logger
from modules.sumologic import SumoLogic


class AddProcessingRuleDialog(QtWidgets.QDialog):

    def __init__(self):
        super(AddProcessingRuleDialog, self).__init__()
        self.rule_types = [ 'Include', 'Exclude', 'Hash', 'Mask']
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("ProcessingRule")
        self.intValidator = QtGui.QIntValidator()
        self.setWindowTitle('Create Processing Rule')

        self.qbtnok = QtWidgets.QDialogButtonBox.Ok

        self.qbtncancel = QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.addButton(self.qbtnok)
        self.buttonBox.addButton(self.qbtncancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.labelRuleName = QtWidgets.QLabel(Dialog)
        self.labelRuleName.setObjectName("RuleName")
        self.labelRuleName.setText('Rule Name:')
        self.lineEditRuleName = QtWidgets.QLineEdit(Dialog)
        self.lineEditRuleName.textChanged.connect(self.enable_ok_button)
        self.layoutRuleName = QtWidgets.QHBoxLayout()
        self.layoutRuleName.addWidget(self.labelRuleName)
        self.layoutRuleName.addWidget(self.lineEditRuleName)

        
        self.labelRuleType = QtWidgets.QLabel(Dialog)
        self.labelRuleType.setObjectName("RuleType")
        self.labelRuleType.setText('Rule Type:')
        self.comboBoxRuleType = QtWidgets.QComboBox(Dialog)
        for rule_type in self.rule_types:
            self.comboBoxRuleType.addItem(rule_type)
        self.layoutRuleType = QtWidgets.QHBoxLayout()
        self.layoutRuleType.addWidget(self.labelRuleType)
        self.layoutRuleType.addWidget(self.comboBoxRuleType)

        self.labelFilter = QtWidgets.QLabel(Dialog)
        self.labelFilter.setObjectName("Filter")
        self.labelFilter.setText('Filter:')
        self.lineEditFilter = QtWidgets.QLineEdit(Dialog)
        self.lineEditFilter.textChanged.connect(self.enable_ok_button)
        self.layoutFilter = QtWidgets.QHBoxLayout()
        self.layoutFilter.addWidget(self.labelFilter)
        self.layoutFilter.addWidget(self.lineEditFilter)

        self.labelMaskString = QtWidgets.QLabel(Dialog)
        self.labelMaskString.setObjectName("MaskString")
        self.labelMaskString.setText('MaskString:')
        self.lineEditMaskString = QtWidgets.QLineEdit(Dialog)
        self.lineEditMaskString.setDisabled(True)
        self.layoutMaskString = QtWidgets.QHBoxLayout()
        self.layoutMaskString.addWidget(self.labelMaskString)
        self.layoutMaskString.addWidget(self.lineEditMaskString)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.layoutRuleName)
        self.layout.addLayout(self.layoutRuleType)
        self.layout.addLayout(self.layoutFilter)
        self.layout.addLayout(self.layoutMaskString)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.comboBoxRuleType.currentTextChanged.connect(self.change_rule_type)

    def enable_ok_button(self):
        if (len(self.lineEditRuleName.text()) > 0) and (len(self.lineEditFilter.text()) > 0):
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

    def change_rule_type(self):
        if self.comboBoxRuleType.currentText() == 'Mask':
            self.lineEditMaskString.setEnabled(True)
        else:
            self.lineEditMaskString.setDisabled(True)

    def getresults(self):
        results = {}
        results['name'] = self.lineEditRuleName.text()
        results['regexp'] = self.lineEditFilter.text()
        results['filterType'] = self.comboBoxRuleType.currentText()
        if results['filterType'] == 'Mask':
            results['mask'] = self.lineEditMaskString.text()
        return results


class RemoveProcessingRuleDialog(QtWidgets.QDialog):

    def __init__(self, potential_rule_names_for_removal):
        super(RemoveProcessingRuleDialog, self).__init__()
        self.potential_rule_names_for_removal = potential_rule_names_for_removal
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("ProcessingRule")
        self.intValidator = QtGui.QIntValidator()
        self.setWindowTitle('Remove Processing Rule(s)')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.labelRuleName = QtWidgets.QLabel(Dialog)
        self.labelRuleName.setObjectName("Name")
        self.labelRuleName.setText('Choose Rule(s) to remove:')
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setAlternatingRowColors(False)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setSortingEnabled(True)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.labelRuleName)
        self.layout.addWidget(self.listWidget)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        for potential_rule_name_for_removal in self.potential_rule_names_for_removal:
            self.listWidget.addItem(potential_rule_name_for_removal)
        self.listWidget.clearSelection()

    def getresults(self):
        results = []
        for selected in self.listWidget.selectedItems():
            results.append(selected.text())
        return results


class source_update_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(source_update_tab, self).__init__()
        self.mainwindow = mainwindow

        source_update_ui = os.path.join(self.mainwindow.basedir, 'data/source_update.ui')
        uic.loadUi(source_update_ui, self)

        self.load_icons()
        self.reset_stateful_objects()
        self.font = "Waree"
        self.font_size = 12

        self.pushButtonRefresh.clicked.connect(lambda: self.update_source_list(
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonAddTargets.clicked.connect(self.add_targets)
        self.pushButtonRemoveTargets.clicked.connect(self.remove_targets)
        self.pushButtonClearTargets.clicked.connect(self.listWidgetTargets.clear)
        self.pushButtonAddRule.clicked.connect(self.add_rule)
        self.pushButtonRemoveRule.clicked.connect(self.remove_rule)
        self.pushButtonRemoveUpdate.clicked.connect(self.remove_update)
        self.pushButtonClearAllUpdates.clicked.connect(self.clear_all_updates)

        self.radioButtonRelative.toggled.connect(self.radio_button_toggled)
        self.radioButtonAbsolute.toggled.connect(self.radio_button_toggled)

        self.pushButtonApplyChanges.clicked.connect(lambda: self.apply_updates(
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUndoChanges.clicked.connect(lambda: self.undo_updates(
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        # Setup the search bars to work and to clear when update button is pushed
        self.lineEditSearchAvailableSources.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetSources,
            self.lineEditSearchAvailableSources.text()
        ))

        self.lineEditSearchTargets.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetTargets,
            self.lineEditSearchTargets.text()
        ))

    def radio_button_toggled(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            if radio_button.text() == "Relative":
                self.clear_all_updates()
                self.pushButtonRemoveRule.setEnabled(True)
            elif radio_button.text() == "Absolute":
                reply = QtWidgets.QMessageBox.question(self, 'Clear remove rules?',
                                                       'Entering absolute mode will clear all updates that remove rules. Continue?)',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.clear_all_updates()
                    self.pushButtonRemoveRule.setEnabled(False)
                if reply == QtWidgets.QMessageBox.No:
                    self.radioButtonRelative.setChecked(True)

    def reset_stateful_objects(self, side='both'):

        if side == 'both':
            left = True

        if side == 'left':
            left = True

        if side == 'right':
            left = False

        if left:

            self.listWidgetSources.clear()
            self.listWidgetTargets.clear()
            self.listWidgetUpdates.clear()
            self.sources = {}
            self.collectors = []
            self.addrules = []
            self.removerules = []
            self.undolist = []
            self.addrules = []
            self.removerules = []
            self.lineEditSearchAvailableSources.clear()
            self.lineEditSearchTargets.clear()
            self.radioButtonRelative.setChecked(True)
            self.pushButtonUndoChanges.setEnabled(False)

    def set_listwidget_filter(self, ListWidget, filtertext):
        for row in range(ListWidget.count()):
            item = ListWidget.item(row)
            widget = ListWidget.itemWidget(item)
            if filtertext:
                item.setHidden(not filtertext in item.text())
            else:
                item.setHidden(False)

    def getcollectorid(self, collectorname, url, id, key):
        logger.info("[Source Update] Getting Collector IDs")
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            sumocollectors = sumo.get_collectors_sync()

            for sumocollector in sumocollectors:
                if sumocollector['name'] == collectorname:
                    return sumocollector['id']
        except Exception as e:
            logger.exception(e)
        return

    def getsourceid(self, collectorid, sourcename, url, id, key):
        logger.info("[Source Update] Getting Source IDs")
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

    def update_source_list(self, url, id, key):
        logger.info("[Source Update] Updating Source List (this could take a while.)")
        self.listWidgetSources.clear()
        self.sources = {}
        sumo = SumoLogic(id, key, endpoint=url)

        try:
            collectors = sumo.get_collectors_sync()
            for index, collector in enumerate(collectors):
                sources = sumo.get_sources_sync(collector['id'])
                for source in sources:
                    #create a dict to lookup source ID by display name
                    itemname = '[' + collector['name'] + "]" + " " + source['name']
                    self.sources[itemname] = [{'collector_id': collector['id'], 'source_id': source['id']}]
                    #create a list of sources with the same source category
                    if 'category' in source:
                        itemname = '[_sourceCategory=' + source['category'] + ']'
                        if itemname in self.sources:
                            self.sources[itemname].append({'collector_id': collector['id'], 'source_id': source['id']})
                        else:
                            self.sources[itemname] = [{'collector_id': collector['id'], 'source_id': source['id']}]
                    #Create a list of sources with the same field=value
                    if source['fields']:
                        for key, value in source['fields'].items():
                            entry = "[" + str(key) + '=' + str(value) + "]"
                            if entry in self.sources:
                                self.sources[entry].append({'collector_id': collector['id'], 'source_id': source['id']})
                            else:
                                self.sources[entry] = [{'collector_id': collector['id'], 'source_id': source['id']}]

                collectors[index]['sources'] = sources

            self.collectors = collectors
            self.update_source_list_widget()

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

    def update_source_list_widget(self):
        logger.info("[Source Update] Updating Source List Widget.")
        self.listWidgetSources.clear()
        for sourcename in self.sources:
            item = QtWidgets.QListWidgetItem(sourcename)
            if "_sourceCategory=" in item.text():
                item.setForeground(QtGui.QColor('#008080'))
            elif "=" in item.text():
                item.setForeground(QtGui.QColor('#FE019A'))
            self.listWidgetSources.addItem(item)

    def view_json(self):
        logger.info("[Source Update] Viewing Selected Source")
        item_text = ''
        window_title = 'JSON Source'
        selecteditems = self.listWidgetSources.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            for selecteditem in selecteditems:
                if not self.listWidgetTargets.findItems(selecteditem.text(), QtCore.Qt.MatchExactly):
                    newItem = QtWidgets.QListWidgetItem(selecteditem)
                    self.listWidgetTargets.addItem(newItem)

    def add_targets(self):
        logger.info("[Source Update] Adding Sources to Target List")
        selecteditems = self.listWidgetSources.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            for selecteditem in selecteditems:
                if not self.listWidgetTargets.findItems(selecteditem.text(), QtCore.Qt.MatchExactly):
                    newItem = QtWidgets.QListWidgetItem(selecteditem)
                    self.listWidgetTargets.addItem(newItem)

    def remove_targets(self):
        logger.info("[Source Update] Removing Sources from Target List")
        selectedItems = self.listWidgetTargets.selectedItems()
        if len(selectedItems) > 0:  # make sure something was selected
            for selectedItem in selectedItems:
                item_index = self.listWidgetTargets.row(selectedItem)
                self.listWidgetTargets.takeItem(item_index)

    def add_rule(self):
        logger.info("[Source Update] Adding new rule to update list.")
        dialog = AddProcessingRuleDialog()
        dialog.exec()
        dialog.show()

        if str(dialog.result()) == '1':
            filter = dialog.getresults()
            if filter['name'] not in self.get_item_names_from_listWidget(self.listWidgetUpdates):
                self.addrules.append(filter)
                item = QtWidgets.QListWidgetItem(self.icons['plus'], filter['name'])
                self.listWidgetUpdates.addItem(item)  # populate the list widget in the GUI
            else:
                self.mainwindow.errorbox('Duplicate rule name. Rule not added.')
        dialog.close()

    def remove_rule(self):
        logger.info("[Source Update] Add remove rule to update list.")
        filter_name_list = []
        filter_list = self.get_filter_list_from_listWidgetTarget()
        for filter in filter_list:
            filter_name_list.append(filter['name'])
        filter_name_list= list(set(filter_name_list))
        dialog = RemoveProcessingRuleDialog(filter_name_list)
        dialog.exec()
        dialog.show()

        if str(dialog.result()) == '1':
            filter_names_to_remove = dialog.getresults()
            for filter_name_to_remove in filter_names_to_remove:
                self.removerules.append(filter_name_to_remove)
                item = QtWidgets.QListWidgetItem(self.icons['minus'], filter_name_to_remove)
                self.listWidgetUpdates.addItem(item)  # populate the list widget in the GUI
        dialog.close()

    def remove_update(self):
        logger.info("[Source Update] Clearing update from update list.")
        selectedItems = self.listWidgetUpdates.selectedItems()
        if len(selectedItems) > 0:  # make sure something was selected
            for selectedItem in selectedItems:
                item_index = self.listWidgetUpdates.row(selectedItem)
                item = self.listWidgetUpdates.takeItem(item_index)
                self.removerules.remove(item.text())



    def clear_all_updates(self):
        logger.info("[Source Update] Clearing all updates from update list.")
        self.listWidgetUpdates.clear()
        self.addrules = []
        self.removerules = []

    def apply_updates(self, url, id, key):
        logger.info("[Source Update] Applying updates from update list.")
        overwrite_rules = False
        if self.radioButtonRelative.isChecked():
            overwrite_rules = False
        elif self.radioButtonAbsolute.isChecked():
            overwrite_rules = True

        target_source_ids = self.get_source_id_list_from_listWidgetTarget()
        if len(target_source_ids) > 0:
            if (len(self.addrules) + len(self.removerules)) > 0:
                result = QtWidgets.QMessageBox.question(self,
                                                        'Continue?',
                                                        'Are you sure you want to apply these updates?',
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.No)
                if result:
                    self.undolist = []
                    try:
                        sumo = SumoLogic(id, key, endpoint=url)
                        for target_source_id in target_source_ids:
                            etag, current_source = sumo.get_source_with_etag(target_source_id['collector_id'], target_source_id['source_id'])
                            self.undolist.append({'collector_id': target_source_id['collector_id'],
                                                  'source_id': target_source_id['source_id'],
                                                  'source': copy.deepcopy(current_source)})
                            if overwrite_rules:
                                current_source['source']['filters'] = []
                            for removerule in self.removerules:
                                for index, filter in enumerate(current_source['source']['filters']):
                                    if filter['name'] == removerule:
                                        current_source['source']['filters'].pop(index)
                                        break
                            for addrule in self.addrules:
                                current_source['source']['filters'].append(addrule)
                            sumo.update_source(target_source_id['collector_id'], current_source, etag)
                        self.mainwindow.infobox('Your update completed successfully.')
                        self.pushButtonUndoChanges.setEnabled(True)
                        self.listWidgetTargets.clear()
                        self.update_source_list(url, id, key)


                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong, rolling back changes:\n\n' + str(e))
                        self.undo_updates(url, id, key)


            else:
                self.mainwindow.errorbox('No updates defined. Please add at least one update to apply.')
                return
        else:
            self.mainwindow.errorbox('Target list is empty. Please select at least one target to update.')
            return

    def undo_updates(self, url, id, key):
        logger.info("[Source Update] Undoing updates.")
        try:
            sumo = SumoLogic(id, key, endpoint=url)
            for undo in self.undolist:
                etag, current_source = sumo.get_source_with_etag(undo['collector_id'],
                                                                 undo['source_id'])
                current_source['source']['filters'] = undo['source']['source']['filters']
                sumo.update_source(undo['collector_id'], current_source, etag)
            self.pushButtonUndoChanges.setEnabled(False)
            self.mainwindow.infobox('Undo was successful.')
            self.update_source_list(url, id, key)

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            self.update_source_list(url, id, key)

    def get_item_names_from_listWidget(self, listWidget):
        item_name_list = []
        for index in range(listWidget.count()):
            item_name_list.append(listWidget.item(index).text())
        return item_name_list

    def get_source_id_list_from_listWidgetTarget(self):
        source_list = []
        for target in self.get_item_names_from_listWidget(self.listWidgetTargets):
            if target in self.sources:
                source_list = source_list + self.sources[target]
        #  get a unique list, no duplicates. Thanks Stackoverflow!
        source_list = list(map(dict, set(tuple(sorted(d.items())) for d in source_list)))
        return source_list

    def get_filter_list_from_listWidgetTarget(self):
        filter_list = []
        source_id_list = self.get_source_id_list_from_listWidgetTarget()
        for source_id in source_id_list:
            for collector in self.collectors:
                if collector['id'] == source_id['collector_id']:
                    for source in collector['sources']:
                        if source['id'] == source_id['source_id']:
                            for filter in source['filters']:
                                filter_list.append(filter)
        return filter_list

    def load_icons(self):
        logger.info("[Source Update] Loading Icons")
        self.icons = {}
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/plus_sign.svg'))
        self.icons['plus'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/minus_sign.svg'))
        self.icons['minus'] = QtGui.QIcon(iconpath)
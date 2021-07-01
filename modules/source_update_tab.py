from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import copy
import sys
import pathlib
import json
from logzero import logger
from modules.multithreading import Worker, ProgressDialog

class_name = 'source_update_tab'


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
        self.tab_name = 'Source Update'
        self.cred_usage = 'left'
        source_update_ui = os.path.join(self.mainwindow.basedir, 'data/source_update.ui')
        uic.loadUi(source_update_ui, self)

        self.load_icons()
        self.reset_stateful_objects()
        self.font = "Waree"
        self.font_size = 12
        self.pushButtonRefresh.clicked.connect(lambda: self.update_source_list(
            self.mainwindow.get_current_creds('left')))

        self.pushButtonAddTargets.clicked.connect(self.add_targets)
        self.pushButtonRemoveTargets.clicked.connect(self.remove_targets)
        self.pushButtonClearTargets.clicked.connect(self.listWidgetTargets.clear)
        self.pushButtonChangeSourceCategory.clicked.connect(self.change_source_category)
        # self.pushButtonAddField.clicked.connect(self.add_field)
        # self.pushButtonRemoveField.clicked.connect(self.remove_field)
        self.pushButtonAddRule.clicked.connect(self.add_rule)
        self.pushButtonRemoveRule.clicked.connect(self.remove_rule)
        self.pushButtonRemoveUpdate.clicked.connect(self.remove_update)
        self.pushButtonClearAllUpdates.clicked.connect(self.clear_all_updates)
        self.radioButtonRelative.toggled.connect(self.radio_button_toggled)
        self.radioButtonAbsolute.toggled.connect(self.radio_button_toggled)

        self.pushButtonApplyChanges.clicked.connect(lambda: self.apply_updates(
            self.mainwindow.get_current_creds('left')))

        self.pushButtonUndoChanges.clicked.connect(lambda: self.undo_updates(
            self.mainwindow.get_current_creds('left')))

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
            self.new_source_category = None
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

    def get_sources(self, collector_name, collector_id, creds):
        sumo = self.mainwindow.sumo_from_creds(creds)
        source_dict = {}
        try:
            sources = sumo.get_sources_sync(collector_id)
            for source in sources:
                # create a dict to lookup source ID by display name
                if 'name' in source:
                    itemname = '[' + collector_name + "]" + " " + source['name']
                elif 'name' in source['config']:
                    itemname = '[' + collector_name + "]" + " " + source['config']['name']
                source_dict[itemname] = [{'collector_id': collector_id, 'source_id': source['id']}]
                # create a list of sources with the same source category
                if 'category' in source:
                    itemname = '[_sourceCategory=' + source['category'] + ']'
                    if itemname in source_dict:
                        source_dict[itemname].append({'collector_id': collector_id, 'source_id': source['id']})
                    else:
                        source_dict[itemname] = [{'collector_id': collector_id, 'source_id': source['id']}]
                # Create a list of sources with the same field=value
                if 'fields' in source and source['fields']:
                    for key, value in source['fields'].items():
                        entry = "[" + str(key) + '=' + str(value) + "]"
                        if entry in source_dict:
                            source_dict[entry].append({'collector_id': collector_id, 'source_id': source['id']})
                        else:
                            source_dict[entry] = [{'collector_id': collector_id, 'source_id': source['id']}]
                elif 'config' in source and source['config']['fields']:
                    for key, value in source['config']['fields'].items():
                        entry = "[" + str(key) + '=' + str(value) + "]"
                        if entry in source_dict:
                            source_dict[entry].append({'collector_id': collector_id, 'source_id': source['id']})
                        else:
                            source_dict[entry] = [{'collector_id': collector_id, 'source_id': source['id']}]
                
            return {'collector': collector_name,
                    'sources': sources,
                    'source_dict': source_dict,
                    'num_messages': None,
                    'status': 'SUCCESS',
                    'line_number': None,
                    'exception': None}
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            lineno = tb.tb_lineno
            return {'collector': collector_name,
                    'sources': sources,
                    'source_dict': source_dict,
                    'num_messages': None,
                    'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)}

    def merge_source_results(self, result):

        if result['status'] == 'FAIL':
            self.mainwindow.threadpool.clear()
            logger.info(result['exception'])
            self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
            return None
        collector = next(c for c in self.collectors if c['name'] == result['collector'])
        collector['sources'] = result['sources']
        self.sources = {**self.sources, **result['source_dict']}
        logger.debug(json.dumps(result))
        self.update_source_list_widget()

    def update_source_list(self, creds):
        logger.info("[Source Update] Updating Source List (this could take a while.)")
        self.listWidgetSources.clear()
        self.sources = {}
        sumo = self.mainwindow.sumo_from_creds(creds)

        try:
            self.collectors = sumo.get_collectors_sync()
            num_collectors = len(self.collectors)
            self.progress = ProgressDialog('Getting all sources...', 0, num_collectors, self.mainwindow.threadpool, self.mainwindow)
            self.workers = []

            for index, collector in enumerate(self.collectors):
                logger.debug(f'Creating get_sources thread for collector {collector["name"]}')
                self.workers.append(Worker(self.get_sources,
                                      collector['name'],
                                      collector['id'],
                                      creds))
                self.workers[index].signals.finished.connect(self.progress.increment)
                self.workers[index].signals.result.connect(self.merge_source_results)
                self.mainwindow.threadpool.start(self.workers[index])

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

    def update_source_list_widget(self):
        logger.debug("[Source Update] Updating Source List Widget.")
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

    def change_source_category(self):
        logger.info("[Source Update] Adding new _sourceCategory change to update list.")
        if not (self.listWidgetUpdates.findItems('_sourceCategory', QtCore.Qt.MatchContains)):
            sc, ok = QtWidgets.QInputDialog.getText(self, 'Change Source Category', 'New Source Category:')
            if ok:
                self.new_source_category = str(sc)
                item_text = '_sourceCategory=' + self.new_source_category
                item = QtWidgets.QListWidgetItem(self.icons['change'], item_text)
                item.itemtype = 'ChangeSourceCategory'
                self.listWidgetUpdates.addItem(item)  # populate the list widget in the GUI
        else:
            self.mainwindow.errorbox("You've already specified a new source Category.")


    def add_field(self):
        pass

    def remove_field(self):
        pass

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
                item.itemtype = 'NewRule'
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
                item.itemtype = 'RemoveRule'
                self.listWidgetUpdates.addItem(item)  # populate the list widget in the GUI
        dialog.close()

    def remove_update(self):
        logger.info("[Source Update] Clearing update from update list.")
        selectedItems = self.listWidgetUpdates.selectedItems()
        if len(selectedItems) > 0:  # make sure something was selected
            for selectedItem in selectedItems:
                item_index = self.listWidgetUpdates.row(selectedItem)
                item = self.listWidgetUpdates.takeItem(item_index)
                if item.itemtype == 'ChangeSourceCategory':
                    self.new_source_category = None
                elif item.itemtype == 'RemoveRule':
                    self.removerules.remove(item.text())
                elif item.itemtype == 'NewRule':
                    for i in range(len(self.addrules)):
                        if self.addrules[i]['name'] == item.text():
                            del self.addrules[i]

    def clear_all_updates(self):
        logger.info("[Source Update] Clearing all updates from update list.")
        self.listWidgetUpdates.clear()
        self.addrules = []
        self.removerules = []
        self.new_source_category = None
    
    def apply_update(self, collector_id, source_id, overwrite_rules, creds):
        sumo = self.mainwindow.sumo_from_creds(creds)
        try:
            etag, current_source = sumo.get_source_with_etag(collector_id,
                                                             source_id)
            self.undolist.append({'collector_id': collector_id,
                                  'source_id': source_id,
                                  'source': copy.deepcopy(current_source)})
            if overwrite_rules:
                if 'filters' in current_source['source']:
                    current_source['source']['filters'] = []
                elif 'config' in current_source['source']:
                    current_source['source']['config']['filters'] = []
                else:
                    assert 'Source JSON does not match known schema'
            for removerule in self.removerules:
                if 'filters' in current_source['source']:
                    for index, filter in enumerate(current_source['source']['filters']):
                        if filter['name'] == removerule:
                            current_source['source']['filters'].pop(index)
                            break

            for addrule in self.addrules:
                # C2C sources do not currently support filters as of 1/5/2021
                # Revisit this when filter support is added for filters in the future
                if 'filters' in current_source['source']:
                    current_source['source']['filters'].append(addrule)

            if self.new_source_category:
                if 'name' in current_source['source']:
                    current_source['source']['category'] = self.new_source_category
                elif 'name' in current_source['source']['config']:
                    current_source['source']['config']['category'] = self.new_source_category
            sumo.update_source(collector_id, current_source, etag)
            return {'status': 'SUCCESS',
                    'line_number': None,
                    'exception': None,
                    'creds': creds
                    }
        except Exception as e:
            _, _, tb = sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }
            
    def merge_updates(self, result):
        if result['status'] == 'SUCCESS':
            self.num_successful_updates += 1
        else:
            self.mainwindow.threadpool.clear()
            logger.info(result['exception'])
            self.mainwindow.errorbox('Something went wrong, rolling back changes:\n\n' + result['exception'])
            self.undo_updates(result['id'], result['key'], result['url'])
        if self.num_successful_updates == self.num_source_updates:
            self.mainwindow.infobox('Your update completed successfully.')
            self.pushButtonUndoChanges.setEnabled(True)
            self.listWidgetTargets.clear()
            self.update_source_list(result['creds'])


    def apply_updates(self, creds):
        logger.info("[Source Update] Applying updates from update list.")
        overwrite_rules = False
        if self.radioButtonRelative.isChecked():
            overwrite_rules = False
        elif self.radioButtonAbsolute.isChecked():
            overwrite_rules = True

        target_source_ids = self.get_source_id_list_from_listWidgetTarget()
        if len(target_source_ids) > 0:
            if (len(self.addrules) > 0) or (len(self.removerules) > 0) or self.new_source_category:
                result = QtWidgets.QMessageBox.question(self,
                                                        'Continue?',
                                                        'Are you sure you want to apply these updates?',
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.No)
                if result:
                    self.undolist = []
                    try:
                        self.num_successful_updates = 0
                        self.num_source_updates = len(target_source_ids)

                        self.progress = ProgressDialog('Applying updates...', 0, self.num_source_updates, self.mainwindow.threadpool,
                                                       self.mainwindow)
                        self.workers = []
                        for index, target_source_id in enumerate(target_source_ids):
                            logger.debug(f'Creating apply_update thread for source {target_source_id}')
                            self.workers.append(Worker(self.apply_update,
                                                       target_source_id['collector_id'],
                                                       target_source_id['source_id'],
                                                       overwrite_rules,
                                                       creds))
                            self.workers[index].signals.finished.connect(self.progress.increment)
                            self.workers[index].signals.result.connect(self.merge_updates)
                            self.mainwindow.threadpool.start(self.workers[index])

                    except Exception as e:
                        logger.exception(e)

            else:
                self.mainwindow.errorbox('No updates defined. Please add at least one update to apply.')
                return
        else:
            self.mainwindow.errorbox('Target list is empty. Please select at least one target to update.')
            return

    def undo_update(self, undo, creds):
            try:
                sumo = self.mainwindow.sumo_from_creds(creds)
                etag, current_source = sumo.get_source_with_etag(undo['collector_id'],
                                                                 undo['source_id'])
                current_source = undo['source']
                sumo.update_source(undo['collector_id'], current_source, etag)
                return {'status': 'SUCCESS',
                        'line_number': None,
                        'exception': None,
                        'creds': creds
                        }
            except Exception as e:
                _, _, tb = sys.exc_info()
                lineno = tb.tb_lineno
                return {'status': 'FAIL',
                        'line_number': lineno,
                        'exception': str(e)
                        }

    def merge_undos(self, result):
        if result['status'] == 'SUCCESS':
            self.num_successful_undos += 1
        else:
            self.mainwindow.threadpool.clear()
            logger.info(result['exception'])
            self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
        if self.num_successful_undos == self.num_undos:
            self.mainwindow.infobox('Your undo completed successfully.')
            self.pushButtonUndoChanges.setEnabled(False)
            self.listWidgetTargets.clear()
            self.update_source_list(result['creds'])

    def undo_updates(self, creds):
        logger.info("[Source Update] Undoing updates.")
        try:
            self.num_undos = len(self.undolist)
            self.num_successful_undos = 0
            self.progress = ProgressDialog('Undoing updates...', 0, self.num_undos, self.mainwindow.threadpool,
                                           self.mainwindow)
            self.workers = []
            for index, undo in enumerate(self.undolist):
                logger.debug(f'Creating undo thread for source {undo}')
                self.workers.append(Worker(self.undo_update,
                                           undo,
                                           creds))
                self.workers[index].signals.finished.connect(self.progress.increment)
                self.workers[index].signals.result.connect(self.merge_undos)
                self.mainwindow.threadpool.start(self.workers[index])

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            self.update_source_list(creds)

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
                            if 'filters' in source:
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
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/change.svg'))
        self.icons['change'] = QtGui.QIcon(iconpath)

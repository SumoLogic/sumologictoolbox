from qtpy import QtCore, QtGui, QtWidgets, uic
from modules.multithreading import Worker, ProgressDialog
from modules.shared import ShowTextDialog, exception_and_error_handling
from modules.filesystem_adapter import FilesystemAdapter
import pathlib
import json
import re
import os
from logzero import logger

class_name = 'baseTab'


class FindReplaceCopyDialog(QtWidgets.QDialog):

    def __init__(self, fromcategories, tocategories, parent=None):
        super(FindReplaceCopyDialog, self).__init__(parent)
        self.objectlist = []
        self.setup_ui(self, fromcategories, tocategories)

    def setup_ui(self, Dialog, fromcategories, tocategories):

        # setup static elements
        Dialog.setObjectName("FindReplaceCopy")
        Dialog.setMinimumWidth(700)
        Dialog.setWindowTitle('Dynamically Replace Source Category Strings')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # set up the list of destination categories to populate into the comboboxes
        itemmodel = QtGui.QStandardItemModel()
        for tocategory in tocategories:
            text_item = QtGui.QStandardItem(str(tocategory))
            itemmodel.appendRow(text_item)
        itemmodel.sort(0)
        self.layoutSelections = QtWidgets.QGridLayout()
        self.labelReplace = QtWidgets.QLabel()
        self.labelReplace.setText("Replace")
        self.layoutSelections.addWidget(self.labelReplace, 0, 0)
        self.labelOriginal = QtWidgets.QLabel()
        self.labelOriginal.setText("Original Source Category")
        self.layoutSelections.addWidget(self.labelOriginal, 0, 1)
        self.labelReplaceWith = QtWidgets.QLabel()
        self.labelReplaceWith.setText("With:")
        self.layoutSelections.addWidget(self.labelReplaceWith, 0, 2)

        # Create 1 set of (checkbox, label, combobox per fromcategory
        for index, fromcategory in enumerate(fromcategories):

            objectdict = {'checkbox': None, 'label': None, 'combobox': None}

            objectdict['checkbox'] = QtWidgets.QCheckBox()
            objectdict['checkbox'].setObjectName("checkBox" + str(index))
            objectdict['checkbox'].setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.layoutSelections.addWidget(objectdict['checkbox'], index + 1, 0)
            objectdict['label']= QtWidgets.QLabel()
            objectdict['label'].setObjectName("comboBox" + str(index))
            objectdict['label'].setText(fromcategory)
            objectdict['label'].setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.layoutSelections.addWidget(objectdict['label'], index + 1, 1)
            objectdict['combobox'] = QtWidgets.QComboBox()
            objectdict['combobox'].setObjectName("comboBox" + str(index))
            objectdict['combobox'].setModel(itemmodel)
            objectdict['combobox'].setEditable(True)
            objectdict['combobox'].setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.layoutSelections.addWidget(objectdict['combobox'], index + 1, 2)
            self.objectlist.append(objectdict)

        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setLayout(self.layoutSelections)

        # Creata a vertical scroll area with a grid layout inside with label headers

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidget(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        #self.scrollArea.setFixedHeight(400)
        self.scrollArea.setMaximumHeight(500)
        self.scrollArea.setMinimumWidth(700)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def getresults(self):
        results = []
        for object in self.objectlist:
            if str(object['checkbox'].checkState()) == '2':
                objectdata = { 'from': str(object['label'].text()), 'to': str(object['combobox'].currentText())}
                results.append(objectdata)
        return results


class BaseTab(QtWidgets.QWidget):

    def __init__(self, mainwindow):
        super(BaseTab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Base'
        self.cred_usage = 'both'

        # Override the font
        self.font = "Waree"
        self.font_size = 12

        # things needed for multithreading
        self.workers = []
        self.num_successful_threads = 0

        self.load_icons()

    def reset_stateful_objects(self, side='both'):
        self.left = None
        self.right = None
        if side == 'both':
            self.left = True
            self.right = True
        if side == 'left':
            self.left = True
            self.right = False
        if side == 'right':
            self.left = False
            self.right = True

        self.left_creds = self.mainwindow.get_current_creds('left')
        self.right_creds = self.mainwindow.get_current_creds('right')

    def load_icons(self):
        self.icons = {}
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(icon_path)

    def set_listwidget_filter(self, list_widget, filter_text):
        for row in range(list_widget.count()):
            item = list_widget.item(row)
            if filter_text:
                item.setHidden(not filter_text in item.text())
            else:
                item.setHidden(False)

    # Thanks Stackoverflow. Yoink!
    def find_keys(self, obj, key):
        """Pull all values of specified key from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        results = extract(obj, arr, key)
        return results

    def _find_replace_specific_key_and_value(self, obj, key, old_value, new_value):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    obj[k] = self._find_replace_specific_key_and_value(v, key, old_value, new_value)
                elif k == key and v == old_value:
                    obj[k] = new_value
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                obj[index] = self._find_replace_specific_key_and_value(item, key, old_value, new_value)
        return obj

    def recurse_replace_query_strings(self, query_string_replacement_list, exported_json):

        if exported_json['type'] == "SavedSearchWithScheduleSyncDefinition":
            for query_string_replacement in query_string_replacement_list:
                if query_string_replacement['from'] in exported_json['search']['queryText']:
                    exported_json['search']['queryText'] = exported_json['search']['queryText'].replace(
                        str(query_string_replacement['from']),
                        str(query_string_replacement['to']))
                    break
            return exported_json

        elif exported_json['type'] == "DashboardSyncDefinition":
            for panelnum, panel in enumerate(exported_json['panels'], start=0):

                if panel['viewerType'] == "metrics":  # there can be multiple query strings so we have an extra loop here
                    for querynum, metrics_query in enumerate(panel['metricsQueries'], start=0):
                        for query_string_replacement in query_string_replacement_list:
                            if query_string_replacement['from'] in metrics_query['query']:
                                metrics_query['query'] = metrics_query['query'].replace(
                                    str(query_string_replacement['from']),
                                    str(query_string_replacement['to']))
                                break
                        panel['metricsQueries'][querynum] = metrics_query

                else:  # if panel is a log panel
                    for query_string_replacement in query_string_replacement_list:
                        if query_string_replacement['from'] in panel['queryString']:
                            panel['queryString'] = panel['queryString'].replace(
                                str(query_string_replacement['from']),
                                str(query_string_replacement['to']))
                            break
                exported_json['panels'][panelnum] = panel
            return exported_json

        elif exported_json['type'] == "DashboardV2SyncDefinition":  # if it's a new style dashboard
            for panelnum, panel in enumerate(exported_json['panels'], start=0):
                for querynum, query in enumerate(panel['queries']):
                    for query_string_replacement in query_string_replacement_list:
                        if query_string_replacement['from'] in query['queryString']:
                            query['queryString'] = query['queryString'].replace(
                                str(query_string_replacement['from']),
                                str(query_string_replacement['to']))
                            break
                    panel['queries'][querynum] = query
                exported_json['panels'][panelnum] = panel
            return exported_json
        elif exported_json['type'] == "FolderSyncDefinition":
            children = []
            for object in exported_json['children']:
                children.append(self.recurse_replace_query_strings(query_string_replacement_list, object))
            exported_json['children'] = children
            return exported_json

    def clear_filters(self, list_widget):
        pass

    @exception_and_error_handling
    def update_item_list(self, list_widget, adapter, path_label=None):
        mode_param = {'mode': list_widget.mode}
        merged_params = {**list_widget.params, **mode_param}
        contents = adapter.list(params=merged_params)
        logger.debug(f'[Tab Base Class] Updating item list, got: {contents}')
        self.update_list_widget(list_widget, adapter, contents, path_label=path_label)
        self.clear_filters(list_widget)

    def create_list_widget_item(self, item):
        item_name = str(item['name'])
        if ('contentType' in item) and (item['contentType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        elif ('itemType' in item) and (item['itemType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        else:
            list_item = QtWidgets.QListWidgetItem(item_name)
        return list_item

    def update_list_widget(self, list_widget, adapter, payload, path_label=None):
        try:
            list_widget.clear()
            count = 0
            for item in payload:
                list_item = self.create_list_widget_item(item)
                # attach the details about the item to the entry in listwidget, this makes life much easier
                list_item.details = item
                list_widget.addItem(list_item)  # populate the list widget in the GUI with no icon (fallthrough)
                count += 1
            if path_label:
                path_label.setText(adapter.get_current_path())
            list_widget.updated = True
        except Exception as e:
            list_widget.clear()
            list_widget.updated = False
            logger.exception(e)
        return

    @exception_and_error_handling
    def find_replace_metadata(self, adapter, payload):
        logger.debug(f"[{self.tab_name}] Replacing Metadata")
        source_metadata = []
        for item in payload:
            # find all the keys in our item that contain queries
            query_list = self.find_keys(item, 'queryText')
            query_list = query_list + self.find_keys(item, 'query')
            query_list = query_list + self.find_keys(item, 'queryString')
            # extract the source category from our list of queries
            for query in query_list:
                source_metadata = source_metadata + re.findall(r'_sourceCategory\s*=\s*\\?\"?([^\s^")]*)\"?',
                                                              query)
            # de-duplicate the list of source categories
            unique_source_metadata = list(set(source_metadata))
            # if the destination is a Sumo Instance then query for available metadata tags
            if adapter.is_sumo_adapter():
                fromtime = str(QtCore.QDateTime.currentDateTime().addSecs(-3600).toString(QtCore.Qt.ISODate))
                totime = str(QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
                # We query the destination org to get a sample of active source categories
                query = r'* | count by _sourceCategory | fields _sourceCategory'
                results = adapter.sumo_search_records(query, from_time=fromtime, to_time=totime,
                                                             timezone='UTC', by_receipt_time=False)
                records = results['payload']
                destination_metadata = []
                for record in records:
                    logger.debug(f'Found Source Category:{record}')
                    destination_metadata.append(record['map']['_sourcecategory'])
                unique_destination_metadata = list(set(destination_metadata))
            # if the destination is not a Sumo instance then leave the destination metadata tag list empty
            else:
                unique_destination_metadata = []
            dialog = FindReplaceCopyDialog(unique_source_metadata, unique_destination_metadata)
            dialog.exec()
            dialog.show()
            if str(dialog.result()) == '1':
                replacelist = dialog.getresults()
                logger.debug(f'Metadata replacement list: {replacelist}')
                dialog.close()
                if len(replacelist) > 0:
                    new_payload = []
                    for item in payload:
                        new_payload.append(self.recurse_replace_query_strings(replacelist, item))
                else:
                    new_payload = payload
                return new_payload
            else:
                return []

    @exception_and_error_handling
    def begin_copy_content(self,
                           source_list_widget,
                           destination_list_widget,
                           source_adapter,
                           destination_adapter,
                           params):
        selected_items = source_list_widget.selectedItems()
        num_selected_items = len(selected_items)
        if num_selected_items < 1: return # make sure something was selected
        logger.debug(f"[{self.tab_name}] Exporting Item(s) {selected_items}")
        self.num_threads = num_selected_items
        self.num_successful_threads = 0
        self.copy_export_results = []
        self.export_progress = ProgressDialog('Exporting items...', 0, self.num_threads, self.mainwindow.threadpool, self.mainwindow)
        self.workers = []
        base_params = {'destination_list_widget': destination_list_widget,
                       'destination_adapter': destination_adapter,
                       'read_mode': source_list_widget.mode,
                       'write_mode': destination_list_widget.mode}
        merged_params = {**base_params, **params}
        merged_params = {**merged_params, **source_list_widget.params}
        for index, selected_item in enumerate(selected_items):
            if 'id' in selected_item.details:
                item_id = selected_item.details['id']
            else:
                item_id = None
            logger.debug(f"Creating copy thread for item {selected_item.details['name']}")
            self.workers.append(Worker(source_adapter.export_item,
                                       selected_item.details['name'],
                                       item_id,
                                       params=merged_params
                                       ))
            self.workers[index].signals.finished.connect(self.export_progress.increment)
            self.workers[index].signals.result.connect(self.merge_begin_copy_results)
            self.mainwindow.threadpool.start(self.workers[index])
        return

    def merge_begin_copy_results(self, result):
        if result['status'] == 'SUCCESS':
            self.num_successful_threads += 1
            self.copy_export_results.append(result['payload'])
        else:
            self.mainwindow.threadpool.clear()
            logger.info(f"ERROR: {result['exception']} on line: {result['line_number']}")
            self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
        if self.num_successful_threads == self.num_threads:
                if result['params']['replace_source_categories']:
                    item_list = self.find_replace_metadata(result['params']['destination_adapter'], self.copy_export_results)
                else:
                    item_list = self.copy_export_results
                if len(item_list) == 0: return
                logger.debug(f"[{self.tab_name}] Importing Item(s)")
                self.num_threads = len(item_list)
                self.num_successful_threads = 0
                self.copy_export_results = []
                self.import_progress = ProgressDialog('Importing items...', 0, self.num_threads, self.mainwindow.threadpool,
                                               self.mainwindow)
                self.workers = []
                for index, item in enumerate(item_list):
                    if 'name' in item:
                        logger.debug(f"Creating copy thread for item {item['name']}")
                    self.workers.append(Worker(result['params']['destination_adapter'].import_item,
                                               item['name'],
                                               item,
                                               params=result['params']
                                               ))
                    self.workers[index].signals.finished.connect(self.import_progress.increment)
                    self.workers[index].signals.result.connect(self.merge_results_update_target)
                    self.mainwindow.threadpool.start(self.workers[index])

    def merge_results_update_target(self, result):
        if result['status'] == 'SUCCESS':
            self.num_successful_threads += 1
        else:
            self.mainwindow.threadpool.clear()
            logger.info(f"ERROR: {result['exception']} on line: {result['line_number']}")
            self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
        if self.num_successful_threads == self.num_threads:
                self.update_item_list(result['params']['destination_list_widget'], result['adapter'])

    @exception_and_error_handling
    def delete_item(self, list_widget, adapter):

        selected_items = list_widget.selectedItems()
        if len(selected_items) < 1: return  # make sure something was selected
        logger.debug(f"[{self.tab_name}] Deleting Item(s) {selected_items}")
        message = "You are about to delete the following item(s):\n\n"
        for selected_item in selected_items:
            message = message + str(selected_item.text()) + "\n"
        message = message + '''
This is exceedingly DANGEROUS!!!! 
Please be VERY, VERY, VERY sure you want to do this!
You could lose quite a bit of work if you delete the wrong thing(s).

If you are absolutely sure, type "DELETE" in the box below.

                '''
        text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
        if (result and (str(text) == 'DELETE')):
            self.num_threads = len(selected_items)
            self.num_successful_threads = 0
            self.progress = ProgressDialog('Deleting items...', 0, self.num_threads, self.mainwindow.threadpool,
                                           self.mainwindow)
            self.workers = []
            params = {'destination_list_widget': list_widget,
                      'destination_adapter': adapter,
                      'mode': list_widget.mode}
            for index, selected_item in enumerate(selected_items):
                item_name = selected_item.details['name']
                if 'id' in selected_item.details:
                    item_id = selected_item.details['id']
                else:
                    item_id = None
                logger.debug(f"Creating delete thread for item {item_name}")
                self.workers.append(Worker(adapter.delete,
                                           item_name,
                                           item_id,
                                           params=params))
                self.workers[index].signals.finished.connect(self.progress.increment)
                self.workers[index].signals.result.connect(self.merge_results_update_target)
                self.mainwindow.threadpool.start(self.workers[index])

    @exception_and_error_handling
    def view_json(self, list_widget, adapter):
        selected_items = list_widget.selectedItems()
        if len(selected_items) < 1: return  # make sure something was selected
        logger.debug(f"[Content] Viewing JSON {selected_items}")
        self.num_threads = len(selected_items)
        self.num_successful_threads = 0
        self.progress = ProgressDialog('Viewing items...', 0, self.num_threads, self.mainwindow.threadpool, self.mainwindow)
        self.json_text = ''
        self.workers = []
        params = {'read_mode': list_widget.mode,
                  'list_widget': list_widget}
        for index, selected_item in enumerate(selected_items):
            item_name = selected_item.details['name']
            if 'id' in selected_item.details:
                item_id = selected_item.details['id']
            else:
                item_id = None
            logger.debug(f"Creating view thread for item {item_name}")
            self.workers.append(Worker(adapter.get,
                                       item_name,
                                       item_id,
                                       params=params))
            self.workers[index].signals.finished.connect(self.progress.increment)
            self.workers[index].signals.result.connect(self.merge_view_json_results)
            self.mainwindow.threadpool.start(self.workers[index])

    def merge_view_json_results(self, result):
        if result['status'] == 'SUCCESS':
            self.num_successful_threads += 1
            self.json_text = self.json_text + json.dumps(result['payload'], indent=4, sort_keys=True) + '\n\n'
        else:
            self.mainwindow.threadpool.clear()
            logger.info(f"ERROR: {result['exception']} on line: {result['line_number']}")
            self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
        if self.num_successful_threads == self.num_threads:
            self.json_window = ShowTextDialog('JSON', self.json_text, self.mainwindow.basedir)
            self.json_window.show()

    @exception_and_error_handling
    def create_folder(self, list_widget, adapter):
        if list_widget.updated:
            message = '''
        Please enter the name of the folder you wish to create:

                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Create Folder...', message)
            if result:
                for item in list_widget.selectedItems():
                    if item.details['name'] == str(text):
                        self.mainwindow.errorbox('That Directory Name Already Exists!')
                        return False
                logger.debug(f"[{self.tab_name}] Creating New Folder {str(text)}")
                params = {'mode': list_widget.mode}
                result = adapter.create_folder(str(text), list_widget, params=params)
                if result:
                    self.update_item_list(list_widget, adapter)
                    return True
                else:
                    return False

    @exception_and_error_handling
    def double_clicked_item(self, list_widget, adapter, item,  path_label=None):
        logger.debug(f"[{self.tab_name}] Going Down One Folder {str(item.details['name'])}")
        mode_param = {'mode': list_widget.mode}
        merged_params = {**list_widget.params, **mode_param}
        result = adapter.down(item.details['name'], params=merged_params)
        if result:
            self.update_item_list(list_widget, adapter,  path_label=path_label)

    @exception_and_error_handling
    def go_to_parent_dir(self, list_widget, adapter,  path_label=None):
        if list_widget.updated:
            mode_param = {'mode': list_widget.mode}
            merged_params = {**list_widget.params, **mode_param}
            result = adapter.up(params=merged_params)
            if result:
                logger.debug(f"[{self.tab_name}] Going Up One folder")
                self.update_item_list(list_widget, adapter,  path_label=path_label)


class StandardTab(BaseTab):

    def __init__(self, mainwindow, copy_override=False):
        super(StandardTab, self).__init__(mainwindow)
        standard_tab_ui = os.path.join(self.mainwindow.basedir, 'data/standard_tab.ui')
        uic.loadUi(standard_tab_ui, self)
        self.listWidgetLeft.filter = self.lineEditSearchLeft
        self.listWidgetRight.filter = self.lineEditSearchRight

        self.pushButtonUpdateLeft.clicked.connect(lambda: self.update_item_list(
            self.listWidgetLeft,
            self.left_adapter,
            path_label=self.labelPathLeft
        ))

        self.pushButtonUpdateRight.clicked.connect(lambda: self.update_item_list(
            self.listWidgetRight,
            self.right_adapter,
            path_label=self.labelPathRight
        ))

        self.pushButtonParentDirLeft.clicked.connect(lambda: self.go_to_parent_dir(
            self.listWidgetLeft,
            self.left_adapter,
            path_label=self.labelPathLeft
        ))

        self.pushButtonParentDirRight.clicked.connect(lambda: self.go_to_parent_dir(
            self.listWidgetRight,
            self.right_adapter,
            path_label=self.labelPathRight
        ))

        self.lineEditSearchLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetLeft,
            self.lineEditSearchLeft.text()
        ))

        self.lineEditSearchRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetRight,
            self.lineEditSearchRight.text()
        ))
        
        self.listWidgetLeft.itemDoubleClicked.connect(lambda item: self.double_clicked_item(
            self.listWidgetLeft,
            self.left_adapter,
            item,
            path_label=self.labelPathLeft
        ))

        self.listWidgetRight.itemDoubleClicked.connect(lambda item: self.double_clicked_item(
            self.listWidgetRight,
            self.right_adapter,
            item,
            path_label=self.labelPathRight
        ))

        self.pushButtonNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.listWidgetLeft,
            self.left_adapter
        ))

        self.pushButtonNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.listWidgetRight,
            self.right_adapter
        ))

        self.pushButtonDeleteLeft.clicked.connect(lambda: self.delete_item(
            self.listWidgetLeft,
            self.left_adapter
        ))

        self.pushButtonDeleteRight.clicked.connect(lambda: self.delete_item(
            self.listWidgetRight,
            self.right_adapter
        ))

        if not copy_override:
            self.pushButtonCopyLeftToRight.clicked.connect(lambda: self.begin_copy_content(
                self.listWidgetLeft,
                self.listWidgetRight,
                self.left_adapter,
                self.right_adapter,
                {'replace_source_categories': False}
            ))

            self.pushButtonCopyRightToLeft.clicked.connect(lambda: self.begin_copy_content(
                self.listWidgetRight,
                self.listWidgetLeft,
                self.right_adapter,
                self.left_adapter,
                {'replace_source_categories': False}
            ))

        self.pushButtonJSONLeft.clicked.connect(lambda: self.view_json(
            self.listWidgetLeft,
            self.left_adapter
        ))

        self.pushButtonJSONRight.clicked.connect(lambda: self.view_json(
            self.listWidgetRight,
            self.right_adapter
        ))

    def clear_filters(self, list_widget):
        list_widget.filter.clear()

    def reset_stateful_objects(self, side='both'):
        super(StandardTab, self).reset_stateful_objects(side=side)
        if self.left:
            self.listWidgetLeft.clear()
            self.listWidgetLeft.currentcontent = {}
            self.listWidgetLeft.updated = False
            self.listWidgetLeft.mode = None
            self.labelPathLeft.clear()
            self.lineEditSearchLeft.clear()
            if self.left_creds['service'] == "FILESYSTEM:":
                self.pushButtonParentDirLeft.setEnabled(True)
                self.pushButtonNewFolderLeft.setEnabled(True)
                self.left_adapter = FilesystemAdapter(self.left_creds, 'left', self.mainwindow)
            elif ':' not in self.left_creds['service']:
                self.pushButtonParentDirLeft.setEnabled(False)
                self.pushButtonNewFolderLeft.setEnabled(False)

        if self.right:
            self.listWidgetRight.clear()
            self.listWidgetRight.currentcontent = {}
            self.listWidgetRight.updated = False
            self.listWidgetRight.mode = None
            self.labelPathRight.clear()
            self.lineEditSearchRight.clear()
            if self.right_creds['service'] == "FILESYSTEM:":
                self.pushButtonParentDirRight.setEnabled(True)
                self.pushButtonNewFolderRight.setEnabled(True)
                self.right_adapter = FilesystemAdapter(self.right_creds, 'right', self.mainwindow)
            if ':' not in self.right_creds['service']:
                self.pushButtonParentDirRight.setEnabled(False)
                self.pushButtonNewFolderRight.setEnabled(False)


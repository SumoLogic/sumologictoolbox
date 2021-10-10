from qtpy import QtGui, QtWidgets, uic
import os
import pathlib
import json
from logzero import logger
from modules.shared import exception_and_error_handling
from modules.filesystem_adapter import FilesystemAdapter


class ItemSelector(QtWidgets.QWidget):

    class ItemNameInput(QtWidgets.QDialog):

        def __init__(self, mainwindow, name='', extension=''):
            super().__init__()
            self.mainwindow = mainwindow
            item_name_input_ui = os.path.join(self.mainwindow.basedir, 'data/item_name_input.ui')
            uic.loadUi(item_name_input_ui, self)
            self.lineEditName.setText(name)
            self.labelExtension.setText(extension)

        def get_results(self):
            if self.exec_() == QtWidgets.QDialog.Accepted:
                # get all values
                val = self.lineEditName.text()
                return val
            else:
                return None

    def __init__(self, mainwindow, util_buttons_on=False, file_filter='', multi_select=False, enable_sumo=False):
        super().__init__()
        self.mainwindow = mainwindow
        self.load_icons()
        self.set_file_filter(file_filter)
        item_selector_ui = os.path.join(self.mainwindow.basedir, 'data/item_selector.ui')
        uic.loadUi(item_selector_ui, self)
        self.presets = self.mainwindow.list_presets_with_creds()
        self.comboBoxPreset.addItem('FILESYSTEM:')
        for preset in self.presets:
            if enable_sumo:
                self.comboBoxPreset.addItem(preset['name'])
            else:
                if ":" in preset['sumoregion']:
                    self.comboBoxPreset.addItem(preset['name'])
        if util_buttons_on:
            self.frameUtilButtons.show()
        else:
            self.frameUtilButtons.hide()
        self.set_multi_select(multi_select)
        self.preset_changed()
        self.comboBoxPreset.currentTextChanged.connect(self.preset_changed)
        self.lineEditSearch.textChanged.connect(lambda filter_text: self.set_listwidget_filter(filter_text))
        self.pushButtonUpdate.clicked.connect(lambda: self.update_file_list())
        self.pushButtonParentDir.clicked.connect(lambda: self.go_to_parent_dir())
        self.listWidget.itemDoubleClicked.connect(lambda item: self.double_clicked_file(item))

    def detect_item_type(self, item):
        if 'collectorType' in item:
            return 'sumocollector'
        elif 'source' in item:
            return 'sumosource'
        elif 'type' in item:
            if (item['type'] == "SavedSearchWithScheduleSyncDefinition")\
                or (item['type'] == "Folder")\
                or (item['type'] == "DashboardSyncDefinition")\
                or (item['type'] == "LookupTableSyncDefinition")\
                or (item['type'] == "DashboardV2SyncDefinition"):
                    return 'sumocontent'
            elif (item['type'] == "MonitorsLibraryMonitorExport")\
                or (item['type'] == "MonitorsLibraryFolderExport"):
                    return 'sumomonitor'
            elif 'connectionSubtype' in item:
                return 'sumoconnection'
        elif 'users' in item:
            return 'sumorole'
        elif 'roleIds' in item:
            return 'sumouser'
        elif 'startTime' in item and 'indexName' in item:
            return 'sumoscheduledview'
        elif 'authnRequestUrl' in item:
            return 'sumosamlconfig'
        elif 'fieldNames' in item:
            return 'sumofer'
        elif 'analyticsTier' in item:
            return 'sumopartition'
        elif 'data' in item and 'input' in item['data'] and 'output' in item['data']:
            return 'sumomapping'
        elif 'ruleId' in item:
            return 'sumorule'
        elif 'ruleIds' in item and 'ordered' in item:
            return 'sumocustominsight'
        elif 'sumoPackageVersion' in item:
            return 'sumopackage'
        else:
            return None

    def get_selected_item_names(self):
        names = []
        items = self.listWidget.selectedItems()
        for item in items:
            names.append(item.text())
        return names

    def get_selected_items(self):
        item_names = self.get_selected_item_names()
        items = []
        try:
            for item_name in item_names:
                # come back later and add support for item_ids
                item_data = self.adapter.export_item(item_name, None)['payload']
                item_type = self.detect_item_type(item_data)
                if item_type:
                    items.append({'item_name': item_name, 'item_type': item_type, 'item_data': item_data})
                else:
                    logger.info(f"Couldn't detect item type for item: {item_name}")
                    logger.debug(f"Item data:\n{item_data}")
            return items
        except Exception as e:
            raise e

    def input_item_name(self, name: str, extension: str):
        input_dialog = self.ItemNameInput(self.mainwindow, name=name, extension=extension)
        name = input_dialog.get_results()
        return name

    def write_item(self, item, name='', extension='', ask=True):
        if not name or ask:
            pre_populated_text = '' + str(name)
            name = self.input_item_name(pre_populated_text, extension)
        if name:
            params = {}
            params['extension'] = str(extension)
            logger.info(f'Writing sumo package:{name}')
            result = self.adapter.import_item(name, item, params=params)
            self.update_file_list()

    def set_multi_select(self, bool):
        if bool:
            self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def set_listwidget_filter(self, filter_text:str):
        for row in range(self.listWidget.count()):
            item = self.listWidget.item(row)
            if filter_text:
                item.setHidden(not filter_text in item.text())
            else:
                item.setHidden(False)

    def clear_listwidget_filter(self):
        self.lineEditSearch.clear()

    def show_git_buttons(self):
        self.frameRepo.show()
        self.pushButtonCommit.setVisible(True)
        self.pushButtonPush.setVisible(True)
        self.pushButtonPull.setVisible(True)

    def hide_git_buttons(self):
        self.frameRepo.hide()
        self.pushButtonCommit.setVisible(False)
        self.pushButtonPush.setVisible(False)
        self.pushButtonPull.setVisible(False)

    def show_util_buttons(self):
        self.frameUtilButtons.show()

    def hide_util_buttons(self):
        self.frameUtilButtons.hide()

    def set_file_filter(self, file_filter):
        self.file_filter = file_filter
        self.params = {'extension': self.file_filter}

    def load_icons(self):
        self.icons = {}
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(icon_path)
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/json.svg'))
        self.icons['JSON'] = QtGui.QIcon(icon_path)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/dashboard.svg'))
        self.icons['content'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/user.svg'))
        self.icons['user'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/role.svg'))
        self.icons['role'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/partition.svg'))
        self.icons['partition'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/sv.svg'))
        self.icons['sv'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/fer.svg'))
        self.icons['fer'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/monitor.svg'))
        self.icons['monitor'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/saml.svg'))
        self.icons['saml'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/connection.svg'))
        self.icons['connection'] = QtGui.QIcon(iconpath)

    def preset_changed(self):
        selected_preset_name = self.comboBoxPreset.currentText()
        self.listWidget.updated = False
        self.listWidget.clear()
        self.clear_listwidget_filter()
        self.hide_git_buttons()
        if selected_preset_name == 'FILESYSTEM:':
            self.adapter = FilesystemAdapter(None, 'left', self.mainwindow)
        else:
            self.show_git_buttons()

    def create_listwidget_item(self, item):
        item_name = str(item['name'])
        if ('contentType' in item) and (item['contentType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        elif ('itemType' in item) and (item['itemType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        else:
            list_item = QtWidgets.QListWidgetItem(self.icons['JSON'], item_name)
        list_item.name = item_name
        list_item.path = self.adapter.get_current_path()
        return list_item

    @exception_and_error_handling
    def update_file_list(self):
        contents = self.adapter.list(params=self.params)
        logger.debug(f'[Package Editor] Updating item list, got: {contents}')
        self.update_file_listwidget(contents)

    def update_file_listwidget(self, payload):
        try:
            self.listWidget.clear()
            count = 0
            for item in payload:
                list_item = self.create_listwidget_item(item)
                # attach the details about the item to the entry in listwidget, this makes life much easier
                list_item.details = item
                self.listWidget.addItem(
                    list_item)  # populate the list widget in the GUI with no icon (fallthrough)
                count += 1

                self.labelDirectoryPath.setText(self.adapter.get_current_path())
            self.listWidget.updated = True
        except Exception as e:
            self.listWidget.clear()
            self.listWidget.updated = False
            logger.exception(e)
        return

    @exception_and_error_handling
    def double_clicked_file(self, item):
        if self.listWidget.updated:
            logger.debug(f"[Package Editor] Going Down One Folder {str(item.details['name'])}")
            result = self.adapter.down(item.details['name'], params=self.params)
            if result:
                self.update_file_list()

    @exception_and_error_handling
    def go_to_parent_dir(self):
        if self.listWidget.updated:
            result = self.adapter.up(params=self.params)
            if result:
                logger.debug(f"[Package Editor] Going Up One folder")
                self.update_file_list()
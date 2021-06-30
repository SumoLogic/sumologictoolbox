from modules.filesystem_adapter import FilesystemAdapter
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pathlib
import os
from modules.shared import exception_and_error_handling
from logzero import logger


class SumoListWidgetItem(QtWidgets.QListWidgetItem):

    def __init__(self, preset, path):
        super().__init__()
        self.preset = preset
        self.path = path
        self.attributes = []
        self.widget = QtWidgets.QWidget()


class ContentWidget(QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super(ContentWidget, self).__init__(parent)
        self.create_widget(name)

    def create_widget(self, name):
        self.widget_layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(name)
        self.widget_layout.addWidget(self.label)

        self.checkbox_org_share = QtWidgets.QCheckBox("Share RO with Org")
        self.checkbox_org_share.setStyleSheet("QCheckBox::indicator"
                                              "{"
                                              "border : 1px solid grey;"
                                              "}")
        self.widget_layout.addWidget(self.checkbox_org_share)
        self.checkbox_admin_share = QtWidgets.QCheckBox("Share RW with Admin")
        self.widget_layout.addWidget(self.checkbox_admin_share)
        self.widget_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.widget_layout.addStretch()
        self.setLayout(self.widget_layout)




class ContentListWidgetItem(SumoListWidgetItem):

    def __init__(self, preset, path):
        super().__init__(preset, path)
        self.share_ro_global = True
        self.share_rw_admin = False
        self.widget = ContentWidget('test')

        # build


class PackageEditor(QtWidgets.QDialog):

    def __init__(self, mainwindow):
        super(PackageEditor, self).__init__()
        self.mainwindow = mainwindow
        self.presets = self.mainwindow.list_presets_with_creds()
        package_editor_ui = os.path.join(self.mainwindow.basedir, 'data/package_editor.ui')
        uic.loadUi(package_editor_ui, self)
        self.comboBoxPreset.addItem('FILESYSTEM:')
        for preset in self.presets:
            if ":" in preset['sumoregion'] and preset['sumoregion'] != "MULTI:":
                self.comboBoxPreset.addItem(preset['name'])
        self.params = {'extension': '.json'}
        self.load_icons()
        self.preset_changed()
        self.pushButtonUpdate.clicked.connect(lambda: self.update_item_list())
        self.pushButtonParentDir.clicked.connect(lambda: self.go_to_parent_dir())
        self.listWidgetConfigs.itemDoubleClicked.connect(lambda item: self.double_clicked_item(item))

        #testing
        test_item = QtWidgets.QListWidgetItem()
        test_widget = ContentWidget('test')
        test_item.setSizeHint(test_widget.sizeHint())
        self.listWidgetPackages.addItem(test_item)
        self.listWidgetPackages.setItemWidget(test_item, test_widget)

    def load_icons(self):
        self.icons = {}
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(icon_path)
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/json.svg'))
        self.icons['JSON'] = QtGui.QIcon(icon_path)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/dashboard.svg'))
        self.icons['Dashboard'] = QtGui.QIcon(iconpath)

    def preset_changed(self):
        selected_preset_name = self.comboBoxPreset.currentText()
        self.listWidgetConfigs.updated = False
        if selected_preset_name == 'FILESYSTEM:':
            self.adapter = FilesystemAdapter(None, 'left', self.mainwindow)

    def create_list_widget_item(self, item):
        item_name = str(item['name'])
        if ('contentType' in item) and (item['contentType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        elif ('itemType' in item) and (item['itemType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        else:
            list_item = QtWidgets.QListWidgetItem(self.icons['JSON'], item_name)
        return list_item

    @exception_and_error_handling
    def update_item_list(self):
        contents = self.adapter.list(params=self.params)
        logger.debug(f'[Create Orgs Dialog] Updating item list, got: {contents}')
        self.update_list_widget(contents)

    def update_list_widget(self, payload):
        try:
            self.listWidgetConfigs.clear()
            count = 0
            for item in payload:
                list_item = self.create_list_widget_item(item)
                # attach the details about the item to the entry in listwidget, this makes life much easier
                list_item.details = item
                self.listWidgetConfigs.addItem(list_item)  # populate the list widget in the GUI with no icon (fallthrough)
                count += 1

                self.labelDirectoryPath.setText(self.adapter.get_current_path())
            self.listWidgetConfigs.updated = True
        except Exception as e:
            self.listWidgetConfigs.clear()
            self.listWidgetConfigs.updated = False
            logger.exception(e)
        return

    @exception_and_error_handling
    def double_clicked_item(self, item):
        if self.listWidgetConfigs.updated:
            logger.debug(f"[Create Orgs Dialog] Going Down One Folder {str(item.details['name'])}")
            result = self.adapter.down(item.details['name'], params=self.params)
            if result:
                self.update_item_list()

    @exception_and_error_handling
    def go_to_parent_dir(self):
        if self.listWidgetConfigs.updated:
            result = self.adapter.up(params=self.params)
            if result:
                logger.debug(f"[Create Orgs Dialog] Going Up One folder")
                self.update_item_list()

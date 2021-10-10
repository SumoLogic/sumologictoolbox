import json
from modules.item_selector import ItemSelector
from modules.package import SumoPackage
from qtpy import QtCore, QtGui, QtWidgets, uic
import pathlib
import os
from logzero import logger


class PackageEditor(QtWidgets.QDialog):

    def __init__(self, mainwindow):
        super(PackageEditor, self).__init__()
        self.mainwindow = mainwindow
        package_editor_ui = os.path.join(self.mainwindow.basedir, 'data/package_editor.ui')
        uic.loadUi(package_editor_ui, self)
        self.load_icons()
        self.init_package()
        self.selector = ItemSelector(self.mainwindow, file_filter='.json', multi_select=True)
        self.verticalLayoutSelector.insertWidget(0, self.selector)
        self.textEditItemData.setAcceptRichText(False)
        self.textEditItemData.setReadOnly(True)
        self.pushButtonAddToPackage.clicked.connect(self.add_items_to_package)
        self.listWidgetPackageItems.itemClicked.connect(lambda item: self.display_item_options(item))
        self.tableWidgetProperties.cellChanged.connect(lambda row, column: self.update_item_config(row, column))
        self.pushButtonRemove.clicked.connect(self.remove_item_from_package)
        self.pushButtonClearAll.clicked.connect(self.init_package)
        self.pushButtonSavePackage.clicked.connect(self.save_package)
        self.pushButtonLoadPackage.clicked.connect(self.load_package)


    def load_icons(self):
        self.icons = {}
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(icon_path)
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/json.svg'))
        self.icons['JSON'] = QtGui.QIcon(icon_path)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/dashboard.svg'))
        self.icons['sumocontent'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/user.svg'))
        self.icons['sumouser'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/role.svg'))
        self.icons['sumorole'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/partition.svg'))
        self.icons['sumopartition'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/sv.svg'))
        self.icons['sumoscheduledview'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/fer.svg'))
        self.icons['sumofer'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/monitor.svg'))
        self.icons['sumomonitor'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/saml.svg'))
        self.icons['sumosamlconfig'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/connection.svg'))
        self.icons['sumoconnection'] = QtGui.QIcon(iconpath)

    def save_package(self):
        if not self.current_package.is_empty():
            package = self.current_package.package_export()
            self.selector.write_item(package, extension='.sumopackage.json')

    def load_package(self):
        items = self.selector.get_selected_items()
        if len(items) == 1 and items[0]['item_type'] == 'sumopackage':
            logger.debug(f'Loading Package: {items[0]}')
            self.current_package = SumoPackage(package_data=items[0]['item_data'])
        self.update_item_listwidget()

    def remove_item_from_package(self):
        self.current_package.package_items.remove(self.current_entry)
        self.update_item_listwidget()
        self.tableWidgetProperties.clear()
        self.textEditItemData.setPlainText('')

    def init_package(self):
        self.current_package = SumoPackage()
        self.current_entry = None
        self.update_item_listwidget()
        self.tableWidgetProperties.clear()
        self.textEditItemData.setPlainText('')

    def update_item_listwidget(self):
        self.listWidgetPackageItems.clear()
        for entry in self.current_package.package_items:
            item = QtWidgets.QListWidgetItem()
            item.setText(entry.item_name)
            item.setIcon(self.icons[entry.item_type])
            item.entry = entry
            self.listWidgetPackageItems.addItem(item)

    def display_item_options(self, item):
        self.current_entry = item.entry
        self.textEditItemData.setPlainText(json.dumps(self.current_entry.item_data, indent=4, sort_keys=True))
        self.tableWidgetProperties.clear()
        self.tableWidgetProperties.setRowCount(0)
        self.tableWidgetProperties.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem('Attribute'))
        self.tableWidgetProperties.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem('Value'))
        for index, item_option in enumerate(self.current_entry.item_options):
            self.tableWidgetProperties.insertRow(self.tableWidgetProperties.rowCount())
            # Add the name of the option
            item = QtWidgets.QTableWidgetItem(item_option['option_display_name'])
            self.tableWidgetProperties.setItem(self.tableWidgetProperties.rowCount() - 1, 0, item)
            # Add the checkbox
            item = QtWidgets.QTableWidgetItem()
            # link the actual option dict back to this temporary entry so we can reference it when the checkbox
            # is clicked
            item.option_index = index
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            if item_option['value']:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tableWidgetProperties.setItem(self.tableWidgetProperties.rowCount() - 1, 1, item)
            
    def update_item_config(self, row, column):
        item = self.tableWidgetProperties.item(row, column)
        if 'option_index' in (dir(item)):
            if item.checkState() == 2:
                self.current_entry.set_option_value(item.option_index, True)
            else:
                self.current_entry.set_option_value(item.option_index, False)

    def add_items_to_package(self):
        items = self.selector.get_selected_items()
        self.current_package.add_items(items)
        self.update_item_listwidget()


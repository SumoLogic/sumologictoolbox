import json
from modules.item_selector import ItemSelector
from modules.package import SumoPackage
from qtpy import QtCore, QtGui, QtWidgets, uic
import pathlib
import os
from logzero import logger


class PackageDeploy(QtWidgets.QDialog):

    def __init__(self, mainwindow):
        super(PackageDeploy, self).__init__()
        self.mainwindow = mainwindow
        package_deploy_ui = os.path.join(self.mainwindow.basedir, 'data/package_deploy.ui')
        uic.loadUi(package_deploy_ui, self)
        self.load_icons()
        self.selector = ItemSelector(self.mainwindow, file_filter='.sumopackage.json', multi_select=False)
        self.verticalLayoutSelector.insertWidget(0, self.selector)
        self.populate_preset_listwidget()
        self.pushButtonSelectAll.clicked.connect(lambda: self.set_presets_checkstate(QtCore.Qt.Checked))
        self.pushButtonSelectNone.clicked.connect(lambda: self.set_presets_checkstate(QtCore.Qt.Unchecked))
        self.lineEditSearch.textChanged.connect(lambda filter_text: self.set_listwidget_filter(filter_text))

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

    def load_package(self):
        items = self.selector.get_selected_items()
        if len(items) == 1 and items[0]['item_type'] == 'sumopackage':
            logger.debug(f'Loading Package: {items[0]}')
            self.current_package = SumoPackage(package_data=items[0]['item_data'])


    def populate_preset_listwidget(self):
        presets = self.mainwindow.list_presets_with_creds()
        for preset in presets:
            item = QtWidgets.QListWidgetItem(preset['name'])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setBackground(QtGui.QColor(60, 60, 60))
            item.name = preset['name']
            item.sumoregion = preset['sumoregion']
            item.accesskeyid = preset['accesskeyid']
            item.accesskey = preset['accesskey']
            self.listWidgetPresets.addItem(item)

    def set_presets_checkstate(self, state):
        for item in [self.listWidgetPresets.item(i) for i in range(self.listWidgetPresets.count())]:
            item.setCheckState(state)

    def set_listwidget_filter(self, filter_text: str):
        for row in range(self.listWidgetPresets.count()):
            item = self.listWidgetPresets.item(row)
            if filter_text:
                item.setHidden(not filter_text in item.text())
            else:
                item.setHidden(False)




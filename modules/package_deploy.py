import json
from modules.item_selector import ItemSelector
from modules.shared import exception_and_error_handling
from modules.package import SumoPackage
from modules.multithreading import ProgressDialog, Worker
from modules.sumologic import SumoLogic
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
        self.selector = ItemSelector(self.mainwindow, file_filter='.sumopackage.json', multi_select=False)
        self.verticalLayoutSelector.insertWidget(0, self.selector)
        self.populate_preset_listwidget()
        self.pushButtonSelectAll.clicked.connect(lambda: self.set_presets_checkstate(QtCore.Qt.Checked))
        self.pushButtonSelectNone.clicked.connect(lambda: self.set_presets_checkstate(QtCore.Qt.Unchecked))
        self.lineEditSearch.textChanged.connect(lambda filter_text: self.set_listwidget_filter(filter_text))
        self.pushButtonDeployPackage.clicked.connect(self.deploy_package)

    def load_package(self):
        items = self.selector.get_selected_items()
        if len(items) == 1 and items[0]['item_type'] == 'sumopackage':
            logger.debug(f'Loading Package: {items[0]}')
            self.package = SumoPackage(package_data=items[0]['item_data'])
            return True
        else:
            return False

    def deploy_package(self):
        if self.load_package():
            selected_presets = self.get_selected_presets()
            verify = QtWidgets.QMessageBox.question(self,
                                                    'Verify Deploy',
                                                    'Are you sure you want to deploy this package? There is no undo.',
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if verify == QtWidgets.QMessageBox.No:
                return
            logger.debug(f"[Package Deploy] Deploying package to {[selected_preset['name'] for selected_preset in selected_presets]}")
            self.num_threads = len(selected_presets)
            self.num_finished_threads = 0
            self.deploy_results = []
            self.export_progress = ProgressDialog('Deploying package...', 0, self.num_threads, self.mainwindow.threadpool,
                                                  self.mainwindow)
            self.workers = []
            for index, selected_preset in enumerate(selected_presets):
                logger.debug(f"Creating copy thread for item {selected_preset['name']}")
                sumo = SumoLogic(selected_preset['accesskeyid'],
                                 selected_preset['accesskey'],
                                 endpoint=self.mainwindow.endpoint_lookup(selected_preset['sumoregion']))
                self.workers.append(Worker(self.package.deploy,
                                           selected_preset['name'],
                                           sumo))
                self.workers[index].signals.finished.connect(self.export_progress.increment)
                self.workers[index].signals.result.connect(self.merge_deploy_package_results)
                self.mainwindow.threadpool.start(self.workers[index])

    def merge_deploy_package_results(self, result):

        self.deploy_results.append(result)
        self.num_finished_threads += 1
        if self.num_finished_threads == self.num_threads:
            # Build fancy results dialog later, log results for now.
            logger.info(f'Package deploy complete. Results:\n {self.deploy_results}')
            self.mainwindow.infobox("Package deploy is complete. Check the log file for results.")

    def populate_preset_listwidget(self):
        presets = self.mainwindow.list_presets_with_creds()
        for preset in presets:
            item = QtWidgets.QListWidgetItem(preset['name'])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setBackground(QtGui.QColor(60, 60, 60))
            item.data = preset
            self.listWidgetPresets.addItem(item)

    def set_presets_checkstate(self, state):
        for item in [self.listWidgetPresets.item(i) for i in range(self.listWidgetPresets.count())]:
            item.setCheckState(state)

    def get_selected_presets(self):
        selected_presets = [self.listWidgetPresets.item(i).data for i in range(self.listWidgetPresets.count()) if self.listWidgetPresets.item(i).checkState() == QtCore.Qt.Checked]
        return selected_presets

    def set_listwidget_filter(self, filter_text: str):
        for row in range(self.listWidgetPresets.count()):
            item = self.listWidgetPresets.item(row)
            if filter_text:
                item.setHidden(not filter_text in item.text())
            else:
                item.setHidden(False)




from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os
import pathlib
import json
from logzero import logger
from modules.shared import ShowTextDialog, exception_and_error_handling
from modules.tab_base_class import BaseTab
from modules.filesystem_adapter import FilesystemAdapter
from modules.adapter import SumoCollectorAdapter, SumoSourceAdapter
from modules.multithreading import Worker, ProgressDialog


class_name = 'CollectorTab'


class CollectorTab(BaseTab):

    def __init__(self, mainwindow):
        super(CollectorTab, self).__init__(mainwindow)
        self.tab_name = 'Collectors'
        self.cred_usage = 'both'
        collector_ui = os.path.join(self.mainwindow.basedir, 'data/collector.ui')
        uic.loadUi(collector_ui, self)
        self.listWidgetCollectorsLeft.params = {'extension': 'nothing'}
        self.listWidgetCollectorsRight.params = {'extension': 'nothing'}
        self.listWidgetSourcesLeft.params = {'extension': '.sumosource.json'}
        self.listWidgetSourcesRight.params = {'extension': '.sumosource.json'}
        self.listWidgetCollectorsLeft.mode = None
        self.listWidgetCollectorsRight.mode = None
        self.listWidgetSourcesLeft.mode = None
        self.listWidgetSourcesRight.mode = None

        # UI Buttons for Collection API tab

        # Setup the search bars to work and to clear when update button is pushed
        self.lineEditCollectorSearchLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetCollectorsLeft,
            self.lineEditCollectorSearchLeft.text()
        ))

        self.lineEditCollectorSearchRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetCollectorsRight,
            self.lineEditCollectorSearchRight.text()
        ))

        self.pushButtonParentDirLeft.clicked.connect(lambda: self.go_to_parent_dir(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.left_collector_adapter,
            self.left_source_adapter,
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text(),
            path_label=self.labelPathLeft
        ))

        self.pushButtonParentDirRight.clicked.connect(lambda: self.go_to_parent_dir(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.right_collector_adapter,
            self.right_source_adapter,
            self.buttonGroupFilterRight,
            self.lineEditCollectorSearchRight.text(),
            path_label=self.labelPathRight
        ))

        self.listWidgetCollectorsLeft.itemDoubleClicked.connect(lambda item: self.double_clicked_item(
            item,
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.left_collector_adapter,
            self.left_source_adapter,
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text(),
            path_label=self.labelPathLeft
        ))

        self.listWidgetCollectorsRight.itemDoubleClicked.connect(lambda item: self.double_clicked_item(
            item,
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.right_collector_adapter,
            self.right_source_adapter,
            self.buttonGroupFilterRight,
            self.lineEditCollectorSearchRight.text(),
            path_label=self.labelPathRight
        ))

        self.pushButtonNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.left_collector_adapter,
            self.left_source_adapter,
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text(),
            path_label=self.labelPathLeft
        ))

        self.pushButtonNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.right_collector_adapter,
            self.right_source_adapter,
            self.buttonGroupFilterRight,
            self.lineEditCollectorSearchRight.text(),
            path_label=self.labelPathRight
        ))

        self.pushButtonUpdateListLeft.clicked.connect(lambda: self.update_collector_list(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.left_collector_adapter,
            self.left_source_adapter,
            self.buttonGroupFilterLeft,
            self.lineEditCollectorSearchLeft.text(),
            path_label=self.labelPathLeft
        ))

        self.pushButtonUpdateListRight.clicked.connect(lambda: self.update_collector_list(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.right_collector_adapter,
            self.right_source_adapter,
            self.buttonGroupFilterRight,
            self.lineEditCollectorSearchRight.text(),
            path_label=self.labelPathRight
        ))

        self.buttonGroupFilterLeft.buttonClicked.connect(lambda: self.update_collector_listwidget(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.buttonGroupFilterLeft,
            self.left_collector_adapter,
            self.left_source_adapter
        ))

        self.buttonGroupFilterRight.buttonClicked.connect(lambda: self.update_collector_listwidget(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.buttonGroupFilterRight,
            self.right_collector_adapter,
            self.right_source_adapter
        ))

        self.pushButtonCopySourcesLeftToRight.clicked.connect(lambda: self.copy_sources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesLeft,
            self.listWidgetSourcesRight,
            self.right_collector_adapter,
            self.left_source_adapter,
            self.right_source_adapter
        ))

        self.pushButtonCopySourcesRightToLeft.clicked.connect(lambda: self.copy_sources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesRight,
            self.listWidgetSourcesLeft,
            self.left_collector_adapter,
            self.right_source_adapter,
            self.left_source_adapter
        ))

        self.pushButtonCollectorJSONLeft.clicked.connect(lambda: self.view_json(
            self.listWidgetCollectorsLeft,
            self.left_collector_adapter
        ))

        self.pushButtonCollectorJSONRight.clicked.connect(lambda: self.view_json(
            self.listWidgetCollectorsRight,
            self.right_collector_adapter
        ))

        self.pushButtonDeleteCollectorLeft.clicked.connect(lambda: self.delete_item(
            self.listWidgetCollectorsLeft,
            self.left_collector_adapter
        ))

        self.pushButtonDeleteCollectorRight.clicked.connect(lambda: self.delete_item(
            self.listWidgetCollectorsRight,
            self.right_collector_adapter
        ))

        self.pushButtonDeleteSourcesLeft.clicked.connect(lambda: self.delete_sources(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.left_source_adapter
        ))

        self.pushButtonDeleteSourcesRight.clicked.connect(lambda: self.delete_sources(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.right_source_adapter
        ))

        self.pushButtonSourceJSONLeft.clicked.connect(lambda: self.view_source_json(
            self.listWidgetSourcesLeft,
            self.left_source_adapter
        ))

        self.pushButtonSourceJSONRight.clicked.connect(lambda: self.view_source_json(
            self.listWidgetSourcesRight,
            self.right_source_adapter
        ))

        # set up a signal to update the source list if a new collector is set
        self.listWidgetCollectorsLeft.itemSelectionChanged.connect(lambda: self.update_source_list(
            self.listWidgetCollectorsLeft,
            self.listWidgetSourcesLeft,
            self.left_source_adapter
        ))

        self.listWidgetCollectorsRight.itemSelectionChanged.connect(lambda: self.update_source_list(
            self.listWidgetCollectorsRight,
            self.listWidgetSourcesRight,
            self.right_source_adapter
        ))

    def reset_stateful_objects(self, side='both'):
        super(CollectorTab, self).reset_stateful_objects(side=side)
        if self.left:
            self.listWidgetCollectorsLeft.collectors = []
            self.listWidgetCollectorsLeft.update = False
            self.listWidgetSourcesLeft.update = False
            self.listWidgetSourcesLeft.collector_id = None
            self.listWidgetCollectorsLeft.clear()
            self.listWidgetSourcesLeft.clear()
            self.lineEditCollectorSearchLeft.clear()
            self.radioButtonFilterAllLeft.setChecked(True)
            self.labelPathLeft.clear()
            self.radioButtonFilterAllLeft.setEnabled(False)
            self.radioButtonFilterHostedLeft.setEnabled(False)
            self.radioButtonFilterInstalledLeft.setEnabled(False)
            self.radioButtonFilterDeadLeft.setEnabled(False)
            if self.left_creds['service'] == "FILESYSTEM:":
                self.pushButtonParentDirLeft.setEnabled(True)
                self.pushButtonNewFolderLeft.setEnabled(True)
                self.left_collector_adapter = FilesystemAdapter(self.left_creds, 'left', self.mainwindow)
                self.left_source_adapter = FilesystemAdapter(self.left_creds, 'left', self.mainwindow)
            elif ':' not in self.left_creds['service']:
                self.pushButtonParentDirLeft.setEnabled(False)
                self.pushButtonNewFolderLeft.setEnabled(False)
                self.radioButtonFilterAllLeft.setEnabled(True)
                self.radioButtonFilterHostedLeft.setEnabled(True)
                self.radioButtonFilterInstalledLeft.setEnabled(True)
                self.radioButtonFilterDeadLeft.setEnabled(True)
                self.left_collector_adapter = SumoCollectorAdapter(self.left_creds, 'left', self.mainwindow)
                self.left_source_adapter = SumoSourceAdapter(self.left_creds, 'left', self.mainwindow)
        if self.right:
            self.listWidgetCollectorsRight.collectors = []
            self.listWidgetCollectorsRight.update = False
            self.listWidgetSourcesRight.update = False
            self.listWidgetSourcesRight.collector_id = None
            self.listWidgetCollectorsRight.clear()
            self.listWidgetSourcesRight.clear()
            self.lineEditCollectorSearchRight.clear()
            self.radioButtonFilterAllRight.setChecked(True)
            self.labelPathRight.clear()
            self.radioButtonFilterAllRight.setEnabled(False)
            self.radioButtonFilterHostedRight.setEnabled(False)
            self.radioButtonFilterInstalledRight.setEnabled(False)
            self.radioButtonFilterDeadRight.setEnabled(False)
            if self.right_creds['service'] == "FILESYSTEM:":
                self.pushButtonParentDirRight.setEnabled(True)
                self.pushButtonNewFolderRight.setEnabled(True)
                self.right_collector_adapter = FilesystemAdapter(self.right_creds, 'right', self.mainwindow)
                self.right_source_adapter = FilesystemAdapter(self.right_creds, 'right', self.mainwindow)
            elif ':' not in self.right_creds['service']:
                self.radioButtonFilterAllRight.setEnabled(True)
                self.radioButtonFilterHostedRight.setEnabled(True)
                self.radioButtonFilterInstalledRight.setEnabled(True)
                self.radioButtonFilterDeadRight.setEnabled(True)
                self.pushButtonParentDirRight.setEnabled(False)
                self.pushButtonNewFolderRight.setEnabled(False)
                self.right_collector_adapter = SumoCollectorAdapter(self.right_creds, 'right', self.mainwindow)
                self.right_source_adapter = SumoSourceAdapter(self.right_creds, 'right', self.mainwindow)

    def load_icons(self):
        super(CollectorTab, self).load_icons()
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/hosted_collector.svg'))
        self.icons['Hosted'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/installed_collector.svg'))
        self.icons['Installable'] = QtGui.QIcon(iconpath)

    @exception_and_error_handling
    def double_clicked_item(self, item, collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=None):
        logger.debug(f"[{self.tab_name}] Going Down One Folder {str(item.details['name'])}")
        result = collector_adapter.down(item.details['name'], params=collector_list_widget.params)
        if result:
            self.update_collector_list(collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=path_label)


    @exception_and_error_handling
    def go_to_parent_dir(self, collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=None):
        if collector_list_widget.updated:
            result = collector_adapter.up(params=collector_list_widget.params)
            if result:
                logger.debug(f"[{self.tab_name}] Going Up One folder")
                self.update_collector_list(collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=path_label)

    @exception_and_error_handling
    def create_folder(self, collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=None):
        if collector_list_widget.updated:
            message = '''
        Please enter the name of the folder you wish to create:

                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Create Folder...', message)
            if result:
                for item in collector_list_widget.selectedItems():
                    if item.details['name'] == str(text):
                        self.mainwindow.errorbox('That Directory Name Already Exists!')
                        return False
                logger.debug(f"[{self.tab_name}] Creating New Folder {str(text)}")

                result = collector_adapter.create_folder(str(text), collector_list_widget)
                if result:
                    self.update_collector_list(collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=path_label)
                    return True
                else:
                    return False

    @exception_and_error_handling
    def update_collector_list(self, collector_list_widget, source_list_widget, collector_adapter, source_adapter, radiobuttongroup, filter_text, path_label=None):
        logger.debug("[Collectors] Updating Collector List")
        collector_list_widget.collectors = collector_adapter.list(params=collector_list_widget.params)  # get list of collectors
        if path_label:
            path_label.setText(collector_adapter.get_current_path())
        self.update_collector_listwidget(collector_list_widget, source_list_widget, radiobuttongroup, collector_adapter, source_adapter)
        self.set_listwidget_filter(collector_list_widget, filter_text)

    def update_collector_listwidget(self, collector_list_widget, source_list_widget, radiobuttongroup, collector_adapter, source_adapter):
        collector_list_widget.clear()  # clear the list first since it might already be populated
        for collector in collector_list_widget.collectors:
            if collector_adapter.is_sumo_adapter() and 'collectorType' in collector:
                item = QtWidgets.QListWidgetItem(self.icons[collector['collectorType']], collector['name'])
            else:
                item = QtWidgets.QListWidgetItem(self.icons['Folder'], collector['name'])
            if 'id' in collector:
                item.id = collector['id']
            item.details = collector
            if collector_adapter.is_sumo_adapter() and 'collectorType' in collector:
                if (collector['collectorType'] == "Installable") and (collector['alive'] == False):
                    item.setFont(QtGui.QFont(self.font, pointSize=self.font_size, italic=True))
                if radiobuttongroup.checkedId() == -2:  # Show all collectors
                    collector_list_widget.addItem(item)  # populate the list widget in the GUI
                elif radiobuttongroup.checkedId() == -3:  # Show only hosted collectors
                    if collector['collectorType'] == "Hosted":
                        collector_list_widget.addItem(item)  # populate the list widget in the GUI
                elif radiobuttongroup.checkedId() == -4:  # Show only installed collectors
                    if collector['collectorType'] == "Installable":
                        collector_list_widget.addItem(item)  # populate the list widget in the GUI
                elif radiobuttongroup.checkedId() == -5:  # Show only dead collectors
                    if (collector['collectorType'] == "Installable") and (collector['alive'] == False):
                        collector_list_widget.addItem(item)  # populate the list widget in the GUI
                else:
                    logger.info('[Collectors]Fell through conditions in update_list_widget')
            else:  # we aren't pulling from a sumo adapter, populate the directory list and populate the source list widget
                collector_list_widget.addItem(item)

        if not collector_adapter.is_sumo_adapter():
            source_adapter.set_current_path_list(collector_adapter.get_current_path_list())
            sources = source_adapter.list(params=source_list_widget.params)
            source_list_widget.collector_id = None
            self.update_source_listwidget(source_list_widget, sources)
        collector_list_widget.updated = True


    @exception_and_error_handling
    def update_source_list(self, collector_list_widget, source_list_widget, adapter):
        logger.debug("[Collectors] Updating Source List")
        source_list_widget.clear()  # clear the list first since it might already be populated
        collectors = collector_list_widget.selectedItems()
        # if we have multiple collectors selected or none selected then don't try to populate the sources list
        if adapter.is_sumo_adapter() and ((len(collectors) > 1) or (len(collectors) < 1)):
            return
        else:
            # populate the list of sources
            if adapter.is_sumo_adapter() and hasattr(collectors[0], 'id'):  # there won't be an ID if it's not from a sumo adapter (i.e. if it comes from a file)
                collector_name = str(collectors[0].text())
                params = {'collector_id': collectors[0].id}
                merged_params = {**params, **source_list_widget.params}
                sources = adapter.list(params=merged_params)
                source_list_widget.collector_id = collectors[0].id
                self.update_source_listwidget(source_list_widget, sources)
            else:

                sources = adapter.list(params=source_list_widget.params)
                self.update_source_listwidget(source_list_widget, sources)

    def update_source_listwidget(self, source_list_widget, sources):
        source_list_widget.clear()
        for source in sources:
            logger.debug(f'Adding source to list widget: {source}')
            if 'itemType' in source and source['itemType'] == 'Folder':
                continue
            else:
                logger.debug(f'Adding source to list widget: {source}')
                if 'name' in source:
                    item = QtWidgets.QListWidgetItem(source['name'])
                    item.details = source
                    source_list_widget.addItem(item)  # populate the display with sources
                elif 'config' in source:
                    item = QtWidgets.QListWidgetItem(source['config']['name'])
                    item.details = source
                    source_list_widget.addItem(item)  # populate the display with C2C sources
        source_list_widget.updated = True

    @exception_and_error_handling
    def copy_sources(self, to_collector_list_widget, from_source_list_widget, to_source_list_widget,
                     to_collector_adapter, from_source_adapter, to_source_adapter):
        logger.info("[Collectors] Copying Sources")
        selected_sources = from_source_list_widget.selectedItems()
        selected_target_collectors = to_collector_list_widget.selectedItems()
        num_selected_items = len(selected_sources)
        num_selected_target_collectors = len(selected_target_collectors)
        if num_selected_items < 1 and (num_selected_target_collectors < 1 or not to_source_adapter.is_sumo_adapter()): return  # make sure something was selected
        exported_sources = []
        logger.debug(f"[{self.tab_name}] Exporting Item(s) {selected_sources}")
        base_params = {'mode': from_source_list_widget.mode,
                       'source_collector_id': from_source_list_widget.collector_id}
        merged_params = {**base_params, **to_source_list_widget.params}
        # export the sources
        for selected_source in selected_sources:
            if 'id' in selected_source.details:
              item_id = selected_source.details['id']
            else:
             item_id = None
            logger.debug(f"Exporting {selected_source.details['name']}")
            exported_sources.append(from_source_adapter.export_item(
                selected_source.details['name'],
                item_id,
                params=merged_params
            ))
        # import the sources to the target collector(s)
        if to_source_adapter.is_sumo_adapter():
            for selected_target_collector in selected_target_collectors:
                collector_id = selected_target_collector.details['id']
                base_params = {'mode': to_source_list_widget.mode,
                               'dest_collector_id': collector_id}
                merged_params = {**base_params, **to_source_list_widget.params}
                for exported_source in exported_sources:
                    logger.debug(f"Importing {exported_source['payload']['source']['name']}")
                    to_source_adapter.import_item(exported_source['payload']['source']['name'],
                                                  exported_source['payload'],
                                                  to_source_list_widget,
                                                  params=merged_params
                                                  )
        else: # not a sumologic collector a the destination
            for exported_source in exported_sources:
                logger.debug(f"Importing {exported_source['payload']['source']['name']}")
                to_source_adapter.import_item(exported_source['payload']['source']['name'],
                                              exported_source['payload'],
                                              to_source_list_widget,
                                              params=to_source_list_widget.params
                                              )
        # update the target
        self.update_source_list(to_collector_list_widget,
                                to_source_list_widget,
                                to_source_adapter)
        if len(selected_target_collectors) > 1:
            self.mainwindow.infobox('Copy Complete.')

    # The following multi-threaded code causes segfaults when copying to multiple collectors so it is
    # disabled. Will re-enable and fix soon (hopefully!)
    #
    # @exception_and_error_handling
    # def copy_sources(self, to_collector_list_widget, from_source_list_widget, to_source_list_widget,
    #                  to_collector_adapter, from_source_adapter, to_source_adapter):
    #     logger.info("[Collectors] Copying Sources")
    #     selected_sources = from_source_list_widget.selectedItems()
    #     num_selected_items = len(selected_sources)
    #     if num_selected_items < 1: return  # make sure something was selected
    #     logger.debug(f"[{self.tab_name}] Exporting Item(s) {selected_sources}")
    #     self.num_threads = num_selected_items
    #     self.num_successful_threads = 0
    #     self.copy_export_results = []
    #     self.export_progress = ProgressDialog('Exporting items...', 0, self.num_threads, self.mainwindow.threadpool,
    #                                           self.mainwindow)
    #     self.workers = []
    #     base_params = {'to_collector_list_widget': to_collector_list_widget,
    #                    'to_source_list_widget': to_source_list_widget,
    #                    'from_source_adapter': from_source_adapter,
    #                    'to_collector_adapter': to_collector_adapter,
    #                    'to_source_adapter': to_source_adapter,
    #                    'mode': to_source_list_widget.mode,
    #                    'source_collector_id': from_source_list_widget.collector_id}
    #     merged_params = {**base_params, **to_source_list_widget.params}
    #     for index, selected_item in enumerate(selected_sources):
    #         if 'id' in selected_item.details:
    #             item_id = selected_item.details['id']
    #         else:
    #             item_id = None
    #         logger.debug(f"Creating copy thread for item {selected_item.details['name']}")
    #         self.workers.append(Worker(from_source_adapter.export_item,
    #                                    selected_item.details['name'],
    #                                    item_id,
    #                                    params=merged_params
    #                                    ))
    #         self.workers[index].signals.finished.connect(self.export_progress.increment)
    #         self.workers[index].signals.result.connect(lambda result: self.merge_copy_sources(result))
    #         self.mainwindow.threadpool.start(self.workers[index])
    #     return
    #
    # @QtCore.pyqtSlot()
    # def merge_copy_sources(self, result):
    #     if result['status'] == 'SUCCESS':
    #         self.num_successful_threads += 1
    #         self.copy_export_results.append(result['payload'])
    #     else:
    #         self.mainwindow.threadpool.clear()
    #         logger.info(f"ERROR: {result['exception']} on line: {result['line_number']}")
    #         self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
    #     if self.num_successful_threads == self.num_threads:
    #         item_list = self.copy_export_results
    #         if len(item_list) == 0: return
    #         logger.debug(f"[{self.tab_name}] Importing Item(s)")
    #
    #         self.num_successful_threads = 0
    #         self.copy_export_results = []
    #         self.workers = []
    #         if result['params']['to_collector_adapter'].is_sumo_adapter():
    #             selected_target_collectors = result['params']['to_collector_list_widget'].selectedItems()
    #             self.num_threads = len(item_list) * len(selected_target_collectors)
    #             self.import_progress = ProgressDialog('Importing items...', 0, self.num_threads,
    #                                                   self.mainwindow.threadpool,
    #                                                   self.mainwindow)
    #             for selected_target_collector in selected_target_collectors:
    #                 target_collector_id = selected_target_collector.details['id']
    #                 logger.debug(f'Target Collector ID for Import: {target_collector_id}')
    #                 for index, item in enumerate(item_list):
    #                     if 'name' in item['source']:
    #                         logger.debug(f"Creating import thread for item {item['source']['name']}")
    #
    #                     result['params']['dest_collector_id'] = target_collector_id
    #                     logger.debug(f'Importing {item["source"]["name"]} for collector {result["params"]["dest_collector_id"]}')
    #                     self.workers.append(Worker(result['params']['to_source_adapter'].import_item,
    #                                                item['source']['name'],
    #                                                item,
    #                                                result['params']['to_source_list_widget'],
    #                                                params=result['params']
    #                                                ))
    #                     self.workers[index].signals.finished.connect(self.import_progress.increment)
    #                     self.workers[index].signals.result.connect(self.custom_merge_results_update_target)
    #                     self.mainwindow.threadpool.start(self.workers[index])
    #         else:
    #             pass

    def custom_merge_results_update_target(self, result):
        if result['status'] == 'SUCCESS':
            self.num_successful_threads += 1
        else:
            self.mainwindow.threadpool.clear()
            # logger.info(f"ERROR: {result['exception']} on line: {result['line_number']}")
            self.mainwindow.errorbox('Something went wrong:\n\n' + result['exception'])
        if self.num_successful_threads == self.num_threads:
            self.update_source_list(result['params']['to_collector_list_widget'],
                                    result['params']['to_source_list_widget'],
                                    result['params']['to_source_adapter'])


    @exception_and_error_handling
    def view_source_json(self, list_widget, adapter):
        selected_items = list_widget.selectedItems()
        if len(selected_items) < 1: return  # make sure something was selected
        logger.debug(f"[Content] Viewing JSON {selected_items}")
        self.num_threads = len(selected_items)
        self.num_successful_threads = 0
        self.progress = ProgressDialog('Viewing items...', 0, self.num_threads, self.mainwindow.threadpool, self.mainwindow)
        self.json_text = ''
        self.workers = []
        params = {'mode': list_widget.mode,
                  'source_collector_id': list_widget.collector_id}
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


    @exception_and_error_handling
    def delete_sources(self, collector_list_widget, source_list_widget, adapter):

        selected_collectors = collector_list_widget.selectedItems()
        if len(selected_collectors) != 1 and adapter.is_sumo_adapter(): return  # make sure something was selected
        collector_id = source_list_widget.collector_id
        selected_sources = source_list_widget.selectedItems()
        if len(selected_sources) < 1: return  # make sure something was selected
        logger.debug(f"[Collectors] Deleting Sources {selected_sources}")
        message = "You are about to delete the following source(s):\n\n"
        for selected_source in selected_sources:
            message = message + str(selected_source.text()) + "\n"
        message = message + '''
This could be exceedingly DANGEROUS!!!! 
Please be VERY, VERY, VERY sure you want to do this!

If you are absolutely sure, type "DELETE" in the box below.

                '''
        text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
        if (result and (str(text) == 'DELETE')):
            self.num_threads = len(selected_sources)
            self.num_successful_threads = 0
            self.progress = ProgressDialog('Deleting items...', 0, self.num_threads, self.mainwindow.threadpool,
                                           self.mainwindow)
            self.workers = []
            params = {'to_source_list_widget': source_list_widget,
                      'to_collector_list_widget': collector_list_widget,
                      'to_source_adapter': adapter,
                      'mode': source_list_widget.mode,
                      'collector_id': collector_id}
            for index, selected_source in enumerate(selected_sources):
                item_name = selected_source.details['name']
                if 'id' in selected_source.details:
                    item_id = selected_source.details['id']
                else:
                    item_id = None
                logger.debug(f"Creating delete thread for item {item_name}")
                self.workers.append(Worker(adapter.delete,
                                           item_name,
                                           item_id,
                                           source_list_widget,
                                           params=params))
                self.workers[index].signals.finished.connect(self.progress.increment)
                self.workers[index].signals.result.connect(self.custom_merge_results_update_target)
                self.mainwindow.threadpool.start(self.workers[index])




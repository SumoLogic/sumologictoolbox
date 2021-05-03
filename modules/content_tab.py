from qtpy import QtGui, QtWidgets, uic
import os
import pathlib
from logzero import logger
from modules.adapter import SumoContentAdapter
from modules.tab_base_class import BaseTab
from modules.filesystem_adapter import FilesystemAdapter

class_name = 'ContentTab'


class ContentTab(BaseTab):

    def __init__(self, mainwindow):
        super(ContentTab, self).__init__(mainwindow)
        self.tab_name = 'Content'
        self.cred_usage = 'both'
        content_widget_ui = os.path.join(self.mainwindow.basedir, 'data/content.ui')
        uic.loadUi(content_widget_ui, self)
        # set up some variables to identify the content list widgets. This is read by some of the content methods
        # to determine proper course of action
        self.contentListWidgetLeft.side = 'left'
        self.contentListWidgetRight.side = 'right'
        self.contentListWidgetLeft.params = {'extension': '.sumocontent.json'}
        self.contentListWidgetRight.params = {'extension': '.sumocontent.json'}
        self.reset_stateful_objects()

        # Content Pane Signals
        # Left Side
        self.pushButtonUpdateContentLeft.clicked.connect(lambda: self.update_item_list(
            self.contentListWidgetLeft,
            self.left_adapter,
            self.contentCurrentDirLabelLeft
        ))

        self.contentListWidgetLeft.itemDoubleClicked.connect(lambda item: self.double_clicked_item(
            self.contentListWidgetLeft,
            self.left_adapter,
            item,
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonParentDirContentLeft.clicked.connect(lambda: self.go_to_parent_dir(
            self.contentListWidgetLeft,
            self.left_adapter,
            self.contentCurrentDirLabelLeft
        ))

        self.buttonGroupContentLeft.buttonClicked.connect(lambda: self.content_radio_button_changed(
            self.contentListWidgetLeft,
            self.left_adapter,
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetLeft,
            self.left_adapter
        ))

        self.pushButtonContentDeleteLeft.clicked.connect(lambda: self.delete_item(
            self.contentListWidgetLeft,
            self.left_adapter
        ))

        self.pushButtonContentCopyLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.left_adapter,
            self.right_adapter,
            {'replace_source_categories': False, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

        self.pushButtonContentFindReplaceCopyLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.left_adapter,
            self.right_adapter,
            {'replace_source_categories': True, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

        # Right Side
        self.pushButtonUpdateContentRight.clicked.connect(lambda: self.update_item_list(
            self.contentListWidgetRight,
            self.right_adapter,
            self.contentCurrentDirLabelRight
        ))

        self.contentListWidgetRight.itemDoubleClicked.connect(lambda item: self.double_clicked_item(
            self.contentListWidgetRight,
            self.right_adapter,
            item,
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonParentDirContentRight.clicked.connect(lambda: self.go_to_parent_dir(
            self.contentListWidgetRight,
            self.right_adapter,
            self.contentCurrentDirLabelRight
        ))

        self.buttonGroupContentRight.buttonClicked.connect(lambda: self.content_radio_button_changed(
            self.contentListWidgetRight,
            self.right_adapter,
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetRight,
            self.right_adapter
        ))

        self.pushButtonContentDeleteRight.clicked.connect(lambda: self.delete_item(
            self.contentListWidgetRight,
            self.right_adapter
        ))

        self.pushButtonContentCopyRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.right_adapter,
            self.left_adapter,
            {'replace_source_categories': False, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

        self.pushButtonContentFindReplaceCopyRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.right_adapter,
            self.left_adapter,
            {'replace_source_categories': True, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

        self.pushButtonContentViewJSONLeft.clicked.connect(lambda: self.view_json(
            self.contentListWidgetLeft,
            self.left_adapter
        ))

        self.pushButtonContentViewJSONRight.clicked.connect(lambda: self.view_json(
            self.contentListWidgetRight,
            self.right_adapter
        ))

    def reset_stateful_objects(self, side='both'):
        left = None
        right = None
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
            self.contentListWidgetLeft.clear()
            self.contentListWidgetLeft.updated = False
            self.radioButtonPersonalLeft.setEnabled(False)
            self.radioButtonGlobalLeft.setEnabled(False)
            self.radioButtonAdminLeft.setEnabled(False)
            left_creds = self.mainwindow.get_current_creds('left')
            if left_creds['service'] == "FILESYSTEM:":
                self.left_adapter = FilesystemAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)
            elif ':' not in left_creds['service']:
                self.radioButtonPersonalLeft.setEnabled(True)
                self.radioButtonGlobalLeft.setEnabled(True)
                self.radioButtonAdminLeft.setEnabled(True)
                self.left_adapter = SumoContentAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)
            self.radioButtonPersonalLeft.setChecked(True)
            self.contentListWidgetLeft.mode = "personal"
            self.contentCurrentDirLabelLeft.clear()


        if right:
            self.contentListWidgetRight.clear()
            self.contentListWidgetRight.updated = False
            self.radioButtonPersonalRight.setEnabled(False)
            self.radioButtonGlobalRight.setEnabled(False)
            self.radioButtonAdminRight.setEnabled(False)
            right_creds = self.mainwindow.get_current_creds('right')
            if right_creds['service'] == "FILESYSTEM:":
                self.right_adapter = FilesystemAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)
            elif ':' not in right_creds['service']:
                self.radioButtonPersonalRight.setEnabled(True)
                self.radioButtonGlobalRight.setEnabled(True)
                self.radioButtonAdminRight.setEnabled(True)
                self.right_adapter = SumoContentAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)
            self.radioButtonPersonalRight.setChecked(True)
            self.contentListWidgetRight.mode = "personal"
            self.contentCurrentDirLabelRight.clear()

    def load_icons(self):
        self.icons = {}
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/dashboard.svg'))
        self.icons['Dashboard'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/logsearch.svg'))
        self.icons['Search'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/scheduledsearch.svg'))
        self.icons['scheduledsearch'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/correlationrules.svg'))
        self.icons['Rule'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/informationmodel.svg'))
        self.icons['Model'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/lookuptable.svg'))
        self.icons['Lookups'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/parser.svg'))
        self.icons['Parser'] = QtGui.QIcon(iconpath)
        return

    def content_radio_button_changed(self, content_list_widget, adapter, radio_selected, path_label=None):
        content_list_widget.currentdirlist = []
        if radio_selected == -2:
            content_list_widget.mode = "personal"
        elif radio_selected == -3:
            content_list_widget.mode = "global"
        elif radio_selected == -4:
            content_list_widget.mode = "admin"
        self.update_item_list(content_list_widget, adapter, path_label=path_label)
        return

    def toggle_content_buttons(self, side, state):
        if side == 'left':
            self.pushButtonContentCopyRightToLeft.setEnabled(state)
            self.pushButtonContentFindReplaceCopyRightToLeft.setEnabled(state)
            self.pushButtonContentNewFolderLeft.setEnabled(state)
            self.pushButtonContentDeleteLeft.setEnabled(state)
        elif side == 'right':
            self.pushButtonContentCopyLeftToRight.setEnabled(state)
            self.pushButtonContentFindReplaceCopyLeftToRight.setEnabled(state)
            self.pushButtonContentNewFolderRight.setEnabled(state)
            self.pushButtonContentDeleteRight.setEnabled(state)


    def create_list_widget_item(self, item):
        item_name = str(item['name'])
        if item['itemType'] == 'Folder':
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        elif item['itemType'] == 'Search':
            list_item = QtWidgets.QListWidgetItem(self.icons['Search'], item_name)
        elif item['itemType'] == 'Dashboard' or item['itemType'] == 'Report':
            list_item = QtWidgets.QListWidgetItem(self.icons['Dashboard'], item_name)
        elif item['itemType'] == 'Lookups':
            list_item = QtWidgets.QListWidgetItem(self.icons['Lookups'], item_name)
        else:
            list_item = QtWidgets.QListWidgetItem(item_name)
        return list_item

    def update_list_widget(self, list_widget, adapter, payload, path_label=None):
        try:
            list_widget.clear()
            for item in payload:
                list_item = self.create_list_widget_item(item)
                # attach the details about the item to the entry in listwidget, this makes life much easier
                list_item.details = item
                list_widget.addItem(list_item)  # populate the list widget in the GUI with no icon (fallthrough)
            if path_label:
                path_label.setText(adapter.get_current_path())
            if adapter.at_top_of_hierarchy() and list_widget.mode == 'global':
                self.toggle_content_buttons(list_widget.side, False)
            else:
                self.toggle_content_buttons(list_widget.side, True)
            list_widget.updated = True
        except Exception as e:
            list_widget.clear()
            list_widget.updated = False
            logger.exception(e)
        return



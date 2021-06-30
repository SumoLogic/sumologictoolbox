from qtpy import QtGui, QtWidgets
import pathlib
from logzero import logger
from modules.adapter import SumoContentAdapter
from modules.tab_base_class import StandardTab


class_name = 'ContentTab'


class ContentTab(StandardTab):

    def __init__(self, mainwindow):
        super(ContentTab, self).__init__(mainwindow)
        self.tab_name = 'Content'
        self.cred_usage = 'both'

        # set up some variables to identify the content list widgets. This is read by some of the content methods
        # to determine proper course of action
        self.listWidgetLeft.params = {'extension': '.sumocontent.json'}
        self.listWidgetRight.params = {'extension': '.sumocontent.json'}
        self.listWidgetLeft.side = "left"
        self.listWidgetRight.side = "right"
        self.QRadioButtonLeftPersonalFolders = QtWidgets.QRadioButton('Personal')
        self.QRadioButtonLeftPersonalFolders.setChecked(True)
        self.QRadioButtonLeftGlobalFolders = QtWidgets.QRadioButton('Global')
        self.QRadioButtonLeftAdminFolders = QtWidgets.QRadioButton('Admin Recommended')
        self.QRadioButtonGroupLeft = QtWidgets.QButtonGroup()
        self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftPersonalFolders, 0)
        self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftGlobalFolders, 1)
        self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftAdminFolders, 2)
        self.horizontalLayoutTopPushButtonsLeft.insertWidget(3, self.QRadioButtonLeftPersonalFolders)
        self.horizontalLayoutTopPushButtonsLeft.insertWidget(4, self.QRadioButtonLeftGlobalFolders)
        self.horizontalLayoutTopPushButtonsLeft.insertWidget(5, self.QRadioButtonLeftAdminFolders)

        self.QRadioButtonRightPersonalFolders = QtWidgets.QRadioButton('Personal')
        self.QRadioButtonRightPersonalFolders.setChecked(True)
        self.QRadioButtonRightGlobalFolders = QtWidgets.QRadioButton('Global')
        self.QRadioButtonRightAdminFolders = QtWidgets.QRadioButton('Admin Recommended')
        self.QRadioButtonGroupRight = QtWidgets.QButtonGroup()
        self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightPersonalFolders, 0)
        self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightGlobalFolders, 1)
        self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightAdminFolders, 2)
        self.horizontalLayoutTopPushButtonsRight.insertWidget(3, self.QRadioButtonRightPersonalFolders)
        self.horizontalLayoutTopPushButtonsRight.insertWidget(4, self.QRadioButtonRightGlobalFolders)
        self.horizontalLayoutTopPushButtonsRight.insertWidget(5, self.QRadioButtonRightAdminFolders)

        self.checkBoxIncludeConnections = QtWidgets.QCheckBox()
        self.checkBoxIncludeConnections.setChecked(True)
        self.checkBoxIncludeConnections.setText("Include\nConnections")
        self.verticalLayoutCenterButton.insertWidget(3, self.checkBoxIncludeConnections)
        self.checkBoxIncludeConnections.show()

        self.toggle_include_roles()
        self.reset_stateful_objects()

        self.QRadioButtonGroupLeft.buttonClicked.connect(lambda: self.radio_button_changed(
            self.listWidgetLeft,
            self.left_adapter,
            self.QRadioButtonGroupLeft.checkedId(),
            self.labelPathLeft
        ))

        self.QRadioButtonGroupRight.buttonClicked.connect(lambda: self.radio_button_changed(
            self.listWidgetRight,
            self.right_adapter,
            self.QRadioButtonGroupRight.checkedId(),
            self.labelPathRight
        ))

        self.checkBoxIncludeConnections.stateChanged.connect(self.toggle_include_roles)

    def toggle_include_roles(self):
        self.listWidgetLeft.params['include_connections'] = self.checkBoxIncludeConnections.isChecked()
        self.listWidgetRight.params['include_connections'] = self.checkBoxIncludeConnections.isChecked()

    def reset_stateful_objects(self, side='both'):
        super(ContentTab, self).reset_stateful_objects(side=side)
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
            self.QRadioButtonLeftPersonalFolders.setEnabled(False)
            self.QRadioButtonLeftGlobalFolders.setEnabled(False)
            self.QRadioButtonLeftAdminFolders.setEnabled(False)
            # FindReplaceCopy Requires a Sumo Org as the Destination so it can query source categories
            # turn it off by default
            self.left_find_replace_copy_on = False
            self.pushButtonFindReplaceCopyRightToLeft.setEnabled(False)

            if ':' not in self.left_creds['service']:
                self.pushButtonParentDirLeft.setEnabled(True)
                self.pushButtonNewFolderLeft.setEnabled(True)
                self.QRadioButtonLeftPersonalFolders.setEnabled(True)
                self.QRadioButtonLeftGlobalFolders.setEnabled(True)
                self.QRadioButtonLeftAdminFolders.setEnabled(True)
                # FindReplaceCopy Requires a Sumo Org as the Destination so it can query source categories
                # turn it on since that's true
                self.left_find_replace_copy_on = True
                self.pushButtonFindReplaceCopyRightToLeft.setEnabled(True)
                self.left_adapter = SumoContentAdapter(self.left_creds, 'left', self.mainwindow)
            self.listWidgetLeft.mode = "personal"

        if right:

            self.QRadioButtonRightPersonalFolders.setEnabled(False)
            self.QRadioButtonRightGlobalFolders.setEnabled(False)
            self.QRadioButtonRightAdminFolders.setEnabled(False)
            # FindReplaceCopy Requires a Sumo Org as the Destination so it can query source categories
            # turn it off by default
            self.right_find_replace_copy_on = False
            self.pushButtonFindReplaceCopyLeftToRight.setEnabled(False)

            if ':' not in self.right_creds['service']:
                self.pushButtonParentDirRight.setEnabled(True)
                self.pushButtonNewFolderRight.setEnabled(True)
                self.QRadioButtonRightPersonalFolders.setEnabled(True)
                self.QRadioButtonRightGlobalFolders.setEnabled(True)
                self.QRadioButtonRightAdminFolders.setEnabled(True)
                # FindReplaceCopy Requires a Sumo Org as the Destination so it can query source categories
                # turn it on since that's true
                self.right_find_replace_copy_on = True
                self.pushButtonFindReplaceCopyLeftToRight.setEnabled(True)
                self.right_adapter = SumoContentAdapter(self.right_creds, 'right', self.mainwindow)
            self.listWidgetRight.mode = "personal"

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

    def radio_button_changed(self, list_widget, adapter, radio_selected, path_label=None):
        list_widget.currentdirlist = []
        if radio_selected == 0:
            list_widget.mode = "personal"
        elif radio_selected == 1:
            list_widget.mode = "global"
        elif radio_selected == 2:
            list_widget.mode = "admin"
        self.update_item_list(list_widget, adapter, path_label=path_label)
        return

    def toggle_content_buttons(self, side, state):
        if side == 'left':
            self.pushButtonCopyRightToLeft.setEnabled(state)
            self.pushButtonNewFolderLeft.setEnabled(state)
            self.pushButtonDeleteLeft.setEnabled(state)
            if self.left_find_replace_copy_on:
                self.pushButtonFindReplaceCopyRightToLeft.setEnabled(state)
        elif side == 'right':
            self.pushButtonCopyLeftToRight.setEnabled(state)
            self.pushButtonNewFolderRight.setEnabled(state)
            self.pushButtonDeleteRight.setEnabled(state)
            if self.right_find_replace_copy_on:
                self.pushButtonFindReplaceCopyLeftToRight.setEnabled(state)

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



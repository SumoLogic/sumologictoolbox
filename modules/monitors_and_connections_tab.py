import pathlib
from qtpy import QtGui, QtWidgets
from modules.adapter import SumoConnectionAdapter, SumoMonitorAdapter
from modules.tab_base_class import DoubleTab

class_name = 'MonitorsAndConnectionsTab'


class MonitorsAndConnectionsTab(DoubleTab):

    def __init__(self, mainwindow):
        super(MonitorsAndConnectionsTab, self).__init__(mainwindow, top_copy_override=True)
        self.tab_name = 'Monitors and Connections'
        self.cred_usage = 'both'

        self.load_icons()

        # customize UI
        self.labelTopLeft.setText("Monitors:")
        self.labelTopRight.setText("Monitors:")
        self.labelBottomLeft.setText("Connections:")
        self.labelBottomRight.setText("Connections:")
        self.checkBoxIncludeConnects = QtWidgets.QCheckBox()
        self.checkBoxIncludeConnects.setChecked(False)
        self.checkBoxIncludeConnects.setText("Include\nConnections")
        self.verticalLayoutCenterButton.insertWidget(3, self.checkBoxIncludeConnects)
        self.checkBoxIncludeConnects.show()

        # Connect the UI buttons to methods

        self.pushButtonCopyTopLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetTopLeft,
            self.listWidgetTopRight,
            self.left_top_adapter,
            self.right_top_adapter,
            {'replace_source_categories': False, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

        self.pushButtonCopyTopRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetTopRight,
            self.listWidgetTopLeft,
            self.right_top_adapter,
            self.left_top_adapter,
            {'replace_source_categories': False, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

    def reset_stateful_objects(self, side='both'):
        super(MonitorsAndConnectionsTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.pushButtonParentDirLeft.setEnabled(True)
                self.pushButtonNewFolderLeft.setEnabled(True)
                self.left_top_adapter = SumoMonitorAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)
                self.left_bottom_adapter = SumoConnectionAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.pushButtonParentDirRight.setEnabled(True)
                self.pushButtonNewFolderRight.setEnabled(True)
                self.right_top_adapter = SumoMonitorAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)
                self.right_bottom_adapter = SumoConnectionAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)

    def load_icons(self):
        self.icons = {}
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(icon_path)
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/monitor.svg'))
        self.icons['Monitor'] = QtGui.QIcon(icon_path)

    def create_list_widget_item(self, item):
        item_name = str(item['name'])
        if ('contentType' in item) and (item['contentType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        elif ('contentType' in item) and (item['contentType'] == 'Monitor'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Monitor'], item_name)
        else:
            list_item = QtWidgets.QListWidgetItem(item_name)
        return list_item


import pathlib
from qtpy import QtGui, QtWidgets
from modules.adapter import SumoMonitorAdapter
from modules.tab_base_class import StandardTab

class_name = 'MonitorsTab'


class MonitorsTab(StandardTab):

    def __init__(self, mainwindow):
        super(MonitorsTab, self).__init__(mainwindow)
        self.tab_name = 'Monitors'
        self.cred_usage = 'both'

        # customize UI
        self.checkBoxIncludeConnects = QtWidgets.QCheckBox()
        self.checkBoxIncludeConnects.setChecked(False)
        self.checkBoxIncludeConnects.setText("Include\nConnections")
        self.verticalLayoutCenterButton.insertWidget(3, self.checkBoxIncludeConnects)
        self.checkBoxIncludeConnects.show()
        self.listWidgetLeft.params = {'extension': '.sumomonitor.json'}
        self.listWidgetRight.params = {'extension': '.sumomonitor.json'}

        # Connect the UI buttons to methods

        self.pushButtonCopyLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetLeft,
            self.listWidgetRight,
            self.left_adapter,
            self.right_adapter,
            {'replace_source_categories': False, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

        self.pushButtonCopyRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetRight,
            self.listWidgetLeft,
            self.right_adapter,
            self.left_adapter,
            {'replace_source_categories': False, 'include_connections': self.checkBoxIncludeConnects.isChecked()}
        ))

    def reset_stateful_objects(self, side='both'):
        super(MonitorsTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.pushButtonParentDirLeft.setEnabled(True)
                self.pushButtonNewFolderLeft.setEnabled(True)
                self.left_adapter = SumoMonitorAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)


        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.pushButtonParentDirRight.setEnabled(True)
                self.pushButtonNewFolderRight.setEnabled(True)
                self.right_adapter = SumoMonitorAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)

    def load_icons(self):
        super(MonitorsTab, self).load_icons()
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


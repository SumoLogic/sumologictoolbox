class_name = 'monitors_and_connections_tab'

import json
import os
import pathlib

from logzero import logger
from qtpy import QtGui, QtWidgets, uic

from modules.shared import ShowTextDialog
from modules.sumologic import SumoLogic
from modules.shared import import_monitors_with_connections, export_monitor_and_connections, import_monitors_without_connections

class monitors_and_connections_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):
        super(monitors_and_connections_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Monitors and Connections'
        self.cred_usage = 'both'
        monitors_and_connections_widget_ui = os.path.join(self.mainwindow.basedir, 'data/monitors_and_connections.ui')
        uic.loadUi(monitors_and_connections_widget_ui, self)

        self.load_icons()
        self.reset_stateful_objects()

        # Connect the UI buttons to methods

        # Connect Update Buttons
        self.pushButtonUpdateMonitorsLeft.clicked.connect(lambda: self.update_monitors_list(
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft
        ))

        self.pushButtonUpdateMonitorsRight.clicked.connect(lambda: self.update_monitors_list(
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))

        self.listWidgetMonitorsLeft.itemDoubleClicked.connect(lambda item: self.doubleclickedmonitorlist(
            item,
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft
        ))
        
        self.listWidgetMonitorsRight.itemDoubleClicked.connect(lambda item: self.doubleclickedmonitorlist(
            item,
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))

        self.pushButtonParentDirMonitorsLeft.clicked.connect(lambda: self.parentdirmonitorlist(
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft
        ))
        self.pushButtonParentDirMonitorsRight.clicked.connect(lambda: self.parentdirmonitorlist(
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))
        # Connect Search Bars
        self.lineEditSearchMonitorsLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetMonitorsLeft,
            self.lineEditSearchMonitorsLeft.text()
        ))

        self.lineEditSearchMonitorsRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetMonitorsRight,
            self.lineEditSearchMonitorsRight.text()
        ))

        self.lineEditSearchConnectionsLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetConnectionsLeft,
            self.lineEditSearchConnectionsLeft.text()
        ))

        self.lineEditSearchConnectionsRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetConnectionsRight,
            self.lineEditSearchConnectionsRight.text()
        ))

        self.pushButtonCopyMonitorLeftToRight.clicked.connect(lambda: self.copy_monitor(
            self.listWidgetMonitorsLeft,
            self.listWidgetMonitorsRight,
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))

        self.pushButtonCopyMonitorRightToLeft.clicked.connect(lambda: self.copy_monitor(
            self.listWidgetMonitorsRight,
            self.listWidgetMonitorsLeft,
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft
        ))

        self.pushButtonMonitorNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft
        ))

        self.pushButtonMonitorNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))

        self.pushButtonBackupMonitorLeft.clicked.connect(lambda: self.backup_monitor(
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupMonitorRight.clicked.connect(lambda: self.backup_monitor(
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonMonitorJSONLeft.clicked.connect(lambda: self.view_monitor_json(
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonMonitorJSONRight.clicked.connect(lambda: self.view_monitor_json(
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonRestoreMonitorLeft.clicked.connect(lambda: self.restore_monitor(
            self.listWidgetMonitorsLeft,
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft
        ))

        self.pushButtonRestoreMonitorRight.clicked.connect(lambda: self.restore_monitor(
            self.listWidgetMonitorsRight,
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))

        self.pushButtonDeleteMonitorLeft.clicked.connect(lambda: self.delete_monitor(
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.labelMonitorPathLeft

        ))

        self.pushButtonDeleteMonitorRight.clicked.connect(lambda: self.delete_monitor(
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.labelMonitorPathRight
        ))

        self.pushButtonUpdateConnectionsLeft.clicked.connect(lambda: self.update_connection_list(
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateConnectionsRight.clicked.connect(lambda: self.update_connection_list(
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))
        
        self.pushButtonCopyConnectionLeftToRight.clicked.connect(lambda: self.copy_connection(
            self.listWidgetConnectionsLeft,
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCopyConnectionRightToLeft.clicked.connect(lambda: self.copy_connection(
            self.listWidgetConnectionsRight,
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupConnectionLeft.clicked.connect(lambda: self.backup_connection(
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupConnectionRight.clicked.connect(lambda: self.backup_connection(
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonConnectionJSONLeft.clicked.connect(lambda: self.view_connection_json(
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonConnectionJSONRight.clicked.connect(lambda: self.view_connection_json(
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonRestoreConnectionLeft.clicked.connect(lambda: self.restore_connection(
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRestoreConnectionRight.clicked.connect(lambda: self.restore_connection(
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteConnectionLeft.clicked.connect(lambda: self.delete_connection(
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteConnectionRight.clicked.connect(lambda: self.delete_connection(
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

    def reset_stateful_objects(self, side='both'):

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
            self.listWidgetMonitorsLeft.clear()
            self.listWidgetMonitorsLeft.currentcontent = {}
            self.listWidgetMonitorsLeft.currentdirlist = []
            self.listWidgetMonitorsLeft.updated = False
            self.listWidgetConnectionsLeft.clear()
            self.listWidgetConnectionsLeft.currentcontent = {}
            self.listWidgetConnectionsLeft.updated = False

        if right:
            self.listWidgetMonitorsRight.clear()
            self.listWidgetMonitorsRight.currentcontent = {}
            self.listWidgetMonitorsRight.currentdirlist = []
            self.listWidgetMonitorsRight.updated = False
            self.listWidgetConnectionsRight.clear()
            self.listWidgetConnectionsRight.currentcontent = {}
            self.listWidgetConnectionsRight.updated = False

    def load_icons(self):
        self.icons = {}
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/monitor.svg'))
        self.icons['Monitor'] = QtGui.QIcon(iconpath)

    def set_listwidget_filter(self, ListWidget, filtertext):
        for row in range(ListWidget.count()):
            item = ListWidget.item(row)
            widget = ListWidget.itemWidget(item)
            if filtertext:
                item.setHidden(not filtertext in item.text())
            else:
                item.setHidden(False)

    def update_monitors_list(self, MonitorsListWidget, url, id, key, directorylabel):
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        logger.info("[Monitors and Connections]Updating Monitors List")
        if MonitorsListWidget.currentdirlist:
            currentdir = MonitorsListWidget.currentdirlist[-1]
        else:
            currentdir = {'name': None, 'id': 'TOP'}
        try:
            if (not MonitorsListWidget.currentcontent) or (currentdir['id'] == 'TOP'):
                MonitorsListWidget.currentdirlist = []
                dir = {'name': '/', 'id': 'TOP'}
                MonitorsListWidget.currentdirlist.append(dir)
                MonitorsListWidget.currentcontent = sumo.get_monitor_folder_root()
                self.updatemonitorlistwidget(MonitorsListWidget, directorylabel)
                return
            else:
                MonitorsListWidget.currentcontent = sumo.get_monitor(currentdir['id'])
                self.updatemonitorlistwidget(MonitorsListWidget, directorylabel)
                return

        except Exception as e:
            MonitorsListWidget.updated = False
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def doubleclickedmonitorlist(self, item, MonitorListWidget, url, id, key, directorylabel):
        logger.info("[Monitors and Connections] Going Down One Monitor Folder")
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            for child in MonitorListWidget.currentcontent['children']:
                if (child['name'] == item.text()) and (child['contentType'] == 'Folder'):
                    MonitorListWidget.currentcontent = sumo.get_monitor(child['id'])
                    dir = {'name': item.text(), 'id': child['id']}
                    MonitorListWidget.currentdirlist.append(dir)
                    self.update_monitors_list(MonitorListWidget, url, id, key, directorylabel)
                    break

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def parentdirmonitorlist(self, MonitorListWidget, url, id, key, directorylabel):
        if MonitorListWidget.updated:
            logger.info("[Monitors and Connections] Going Up One Monitor Folder")
            sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
            currentdir = MonitorListWidget.currentdirlist[-1]
            if currentdir['id'] != 'TOP':
                parentdir = MonitorListWidget.currentdirlist[-2]
            else:
                return
            try:

                if parentdir['id'] == 'TOP':
                    MonitorListWidget.currentdirlist = []
                    self.update_monitors_list(MonitorListWidget, url, id, key, directorylabel)
                    return

                else:
                    MonitorListWidget.currentdirlist.pop()
                    MonitorListWidget.currentcontent = sumo.get_monitor(parentdir['id'])
                    self.update_monitors_list(MonitorListWidget, url, id, key, directorylabel)
                    return
                
            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

            return

    def updatemonitorlistwidget(self, MonitorListWidget, directorylabel):
        try:
            MonitorListWidget.clear()
            for object in MonitorListWidget.currentcontent['children']:
                item_name = ''
                item_name = item_name + object['name']
                if object['contentType'] == 'Folder':
                    item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
                    #item.setIcon(self.icons['Folder'])
                    MonitorListWidget.addItem(item)  # populate the list widget in the GUI
                elif object['contentType'] == 'Monitor':
                    item = QtWidgets.QListWidgetItem(self.icons['Monitor'], item_name)
                    #item.setIcon(self.icons['Monitor'])
                    MonitorListWidget.addItem(item)  # populate the list widget in the GUI
                else:
                    MonitorListWidget.addItem(item_name)  # populate the list widget in the GUI with no icon (fallthrough)

            # build the string to show the current directory
            dirname = ''
            for dir in MonitorListWidget.currentdirlist:
                dirname = dirname + '/' + str(dir['name'])
            directorylabel.setText(dirname)
            MonitorListWidget.updated = True

        except Exception as e:
            MonitorListWidget.clear()
            MonitorListWidget.updated = False
            logger.exception(e)
        return

    def create_folder(self, MonitorListWidget, url, id, key, directorylabel):
        if MonitorListWidget.updated == True:

            message = '''
        Please enter the name of the folder you wish to create:

                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Create Folder...', message)
            if result:
                for item in MonitorListWidget.currentcontent['children']:
                    if item['name'] == str(text):
                        self.mainwindow.errorbox('That Directory Name Already Exists!')
                        return
                try:

                    logger.info("[Monitors and Connections]Creating New Monitor Folder")
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    parent_id = MonitorListWidget.currentcontent['id']
                    error = sumo.create_monitor_folder(parent_id, text)
                    self.update_monitors_list(MonitorListWidget, url, id, key, directorylabel)
                    return

                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox("Please update the directory list before trying to create a new folder.")
        return
    
    def view_monitor_json(self, MonitorListWidget, url, id, key):
        logger.info("[Monitors and Connections]Viewing Monitor(s) JSON")
        selecteditems = MonitorListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in MonitorListWidget.currentcontent['children']:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            user = sumo.export_monitor(item_id)
                            json_text = json_text + json.dumps(user, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                return
        else:
            self.mainwindow.errorbox('No monitor selected.')
        return

    def copy_monitor(self, MonitorListWidgetFrom, MonitorListWidgetTo, ConnectionListWidgetTo, fromurl, fromid, fromkey,
                  tourl, toid, tokey, directory_label):

        # Need to add check if user already exists and interactively ask if any missing roles should be created 
        logger.info("[Monitors and Connections]Copying Monitor(s)")
        try:
            selecteditems = MonitorListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in MonitorListWidgetFrom.currentcontent['children']:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                    monitor = export_monitor_and_connections(item_id, fromsumo)
                    for index, connection in enumerate(monitor['connections']):
                        monitor['connections'][index]['type'] = str(connection['type']).replace('Connection',
                                                                                               'Definition')
                    parent_id = MonitorListWidgetTo.currentcontent['id']
                    if self.checkBoxCopyRestoreConnections.isChecked():
                        import_monitors_with_connections(parent_id, monitor, tosumo)
                    else:
                        import_monitors_without_connections(parent_id, monitor, tosumo)

                            
                self.update_monitors_list(MonitorListWidgetTo, tourl, toid, tokey, directory_label)
                self.update_connection_list(ConnectionListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_monitors_list(MonitorListWidgetTo, tourl, toid, tokey, directory_label)
            self.update_connection_list(ConnectionListWidgetTo, tourl, toid, tokey)
        return

    def backup_monitor(self, MonitorListWidget, url, id, key):
        logger.info("[Monitors and Connections]Backing Up Monitors(s)")
        selecteditems = MonitorListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in MonitorListWidget.currentcontent['children']:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            try:
                                export = export_monitor_and_connections(item_id, sumo)
                                for index, connection in enumerate(export['connections']):
                                    export['connections'][index]['type'] = str(connection['type']).replace('Connection', 'Definition')

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.monitor.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(export, filepointer)
                                    message = message + str(selecteditem.text()) + r'.monitor.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                                return
                self.mainwindow.infobox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No monitor selected.')
        return



    def restore_monitor(self, MonitorListWidget, ConnectionListWidget, url, id, key, directory_label):
        logger.info("[Monitors and Connections]Restoring Monitor(s)")
        if MonitorListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:

                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            monitor = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                        parent_id = MonitorListWidget.currentcontent['id']
                        if self.checkBoxCopyRestoreConnections.isChecked():
                            import_monitors_with_connections(parent_id ,monitor, sumo)
                        else:
                            import_monitors_without_connections(parent_id, monitor, sumo)



                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_connection_list(ConnectionListWidget, url, id, key)
                self.update_monitors_list(MonitorListWidget, url, id, key, directorylabel=directory_label)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the monitor list before restoring content")
        return

    def delete_monitor(self, MonitorListWidget, url, id, key, directorylabel):
        logger.info("[Monitors and Connections]Deleting Monitor(s)")
        selecteditems = MonitorListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            message = "You are about to delete the following item(s):\n\n"
            for selecteditem in selecteditems:
                message = message + str(selecteditem.text()) + "\n"
            message = message + '''
    This is exceedingly DANGEROUS!!!! 
    Please be VERY, VERY, VERY sure you want to do this!
    You could lose quite a bit of work if you delete the wrong thing(s).

    If you are absolutely sure, type "DELETE" in the box below.

                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text) == 'DELETE')):
                try:

                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        for object in MonitorListWidget.currentcontent['children']:
                            if object['name'] == str(selecteditem.text()):
                                item_id = object['id']

                        result = sumo.delete_monitor(item_id)

                    self.update_monitors_list(MonitorListWidget, url, id, key, directorylabel)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return
    
    def update_connection_list(self, ConnectionListWidget, url, id, key):
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            logger.info("[Monitors and Connections]Updating Connection List")
            ConnectionListWidget.currentcontent = sumo.get_connections_sync()
            ConnectionListWidget.clear()
            if len(ConnectionListWidget.currentcontent) > 0:
                self.update_connection_listwidget(ConnectionListWidget)
                return

        except Exception as e:
            
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def update_connection_listwidget(self, ConnectionListWidget):
        try:
            ConnectionListWidget.clear()
            ConnectionListWidget.setSortingEnabled(True)
            for object in ConnectionListWidget.currentcontent:
                item_name = object['name']
                ConnectionListWidget.addItem(item_name)  # populate the list widget in the GUI

            ConnectionListWidget.updated = True

        except Exception as e:
            ConnectionListWidget.clear()
            ConnectionListWidget.updated = True
            logger.exception(e)
        return
    
    def copy_connection(self, ConnectionListWidgetFrom, ConnectionListWidgetTo, fromurl, fromid, fromkey,
                  tourl, toid, tokey):

        logger.info("[Monitors and Connections]Copying Connection(s)")
        try:
            selecteditems = ConnectionListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in ConnectionListWidgetFrom.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            connection_id = object['id']
                            connection_type = object['type']
                            connection = fromsumo.get_connection(connection_id, connection_type)
                            connection['type'] = str(connection['type']).replace('Connection', 'Definition')
                            status = tosumo.create_connection(connection)
                self.update_connection_list(ConnectionListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_connection_list(ConnectionListWidgetTo, tourl, toid, tokey)
        return

    def backup_connection(self, ConnectionListWidget, url, id, key):
        logger.info("[Monitors and Connections]Backing Up Connection(s)")
        selecteditems = ConnectionListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    for object in ConnectionListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            item_type = object['type']
                            try:
                                export = sumo.get_connection(item_id, item_type)
                                export['type'] = str(export['type']).replace('Connection', 'Definition')

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.connection.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(export, filepointer)
                                    message = message + str(selecteditem.text()) + r'.connection.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                                return
                self.mainwindow.infobox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No connection selected.')
        return

    def view_connection_json(self, ConnectionListWidget, url, id, key):
        logger.info("[Monitors and Connections]Viewing Connection(s) JSON")
        selecteditems = ConnectionListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in ConnectionListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            connection_id = object['id']
                            connection_type = object['type']
                            connection = sumo.get_connection(connection_id, connection_type)
                            json_text = json_text + json.dumps(connection, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                return
        else:
            self.mainwindow.errorbox('No connection selected.')
        return

    def restore_connection(self, ConnectionListWidget, url, id, key):
        logger.info("[Users and Roles]Restoring Role(s)")
        if ConnectionListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            connection_backup = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        status = sumo.create_connection(connection_backup)

                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_connection_list(ConnectionListWidget, url, id, key)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the directory list before restoring content")
        return

    def delete_connection(self, ConnectionListWidget, url, id, key):
        logger.info("[Monitors and Connections]Deleting Connection(s)")
        selecteditems = ConnectionListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            message = "You are about to delete the following item(s):\n\n"
            for selecteditem in selecteditems:
                message = message + str(selecteditem.text()) + "\n"
            message = message + '''
    This is exceedingly DANGEROUS!!!! 
    Please be VERY, VERY, VERY sure you want to do this!
    You could lose quite a bit of work if you delete the wrong thing(s).

    If you are absolutely sure, type "DELETE" in the box below.

                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text) == 'DELETE')):
                try:

                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        for object in ConnectionListWidget.currentcontent:
                            if object['name'] == str(selecteditem.text()):
                                item_id = object['id']
                                item_type = object['type']

                        result = sumo.delete_connection(item_id, item_type)

                    self.update_connection_list(ConnectionListWidget, url, id, key)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return
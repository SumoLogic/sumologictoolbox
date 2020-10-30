from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import sys
import re
import pathlib
import json
from logzero import logger
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog


class monitors_and_connections_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):
        super(monitors_and_connections_tab, self).__init__()
        self.mainwindow = mainwindow

        monitors_and_connections_widget_ui = os.path.join(self.mainwindow.basedir, 'data/monitors_and_connections.ui')
        uic.loadUi(monitors_and_connections_widget_ui, self)

        # Connect the UI buttons to methods

        # Connect Update Buttons
        self.pushButtonUpdateMonitorsAndConnectionsLeft.clicked.connect(lambda: self.update_monitors_and_connections_lists(
            self.listWidgetMonitorsLeft,
            self.listWidgetConnectionsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateMonitorsAndConnectionsRight.clicked.connect(lambda: self.update_monitors_and_connections_lists(
            self.listWidgetMonitorsRight,
            self.listWidgetConnectionsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
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
            str(self.mainwindow.lineEditPasswordRight.text())
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
            str(self.mainwindow.lineEditPasswordLeft.text())
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
            self.listWidgetConnectionsLeft,
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRestoreMonitorRight.clicked.connect(lambda: self.restore_monitor(
            self.listWidgetConnectionsRight,
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteMonitorLeft.clicked.connect(lambda: self.delete_monitor(
            self.listWidgetConnectionsLeft,
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteMonitorRight.clicked.connect(lambda: self.delete_monitor(
            self.listWidgetConnectionsRight,
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCopyConnectionLeftToRight.clicked.connect(lambda: self.copy_connection(
            self.listWidgetConnectionsLeft,
            self.listWidgetConnectionsRight,
            self.listWidgetMonitorsRight,
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
            self.listWidgetMonitorsLeft,
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
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRestoreConnectionRight.clicked.connect(lambda: self.restore_connection(
            self.listWidgetConnectionsRight,
            self.listWidgetMonitorsRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteConnectionLeft.clicked.connect(lambda: self.delete_connection(
            self.listWidgetConnectionsLeft,
            self.listWidgetMonitorsLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteConnectionRight.clicked.connect(lambda: self.delete_connection(
            self.listWidgetConnectionsRight,
            self.listWidgetMonitorsRight,
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
            self.listWidgetMonitorsLeft.updated = False
            self.listWidgetRolesLeft.clear()
            self.listWidgetRolesLeft.currentcontent = {}
            self.listWidgetRolesLeft.updated = False

        if right:
            self.listWidgetMonitorsRight.clear()
            self.listWidgetMonitorsRight.currentcontent = {}
            self.listWidgetMonitorsRight.updated = False
            self.listWidgetRolesRight.clear()
            self.listWidgetRolesRight.currentcontent = {}
            self.listWidgetRolesRight.updated = False

    def set_listwidget_filter(self, ListWidget, filtertext):
        for row in range(ListWidget.count()):
            item = ListWidget.item(row)
            widget = ListWidget.itemWidget(item)
            if filtertext:
                item.setHidden(not filtertext in item.text())
            else:
                item.setHidden(False)

    def update_users_and_roles_lists(self, UserListWidget, RoleListWidget, url, id, key):
        sumo = SumoLogic(id, key, endpoint=url)
        try:
            logger.info("[Users and Roles]Updating Users and Roles Lists")
            UserListWidget.currentcontent = sumo.get_users_sync()
            RoleListWidget.currentcontent = sumo.get_roles_sync()
            self.update_users_and_roles_listwidgets(UserListWidget, RoleListWidget)
            return
        except Exception as e:
            UserListWidget.updated = False
            RoleListWidget.updated = False
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def update_users_and_roles_listwidgets(self, UserListWidget, RoleListWidget):
        try:
            UserListWidget.clear()
            RoleListWidget.clear()
            UserListWidget.setSortingEnabled(True)
            for object in UserListWidget.currentcontent:
                item_name = object['firstName'] + ' ' + object['lastName']
                UserListWidget.addItem(item_name)  # populate the list widget in the GUI
            UserListWidget.updated = True
            for object in RoleListWidget.currentcontent:
                item_name = object['name']
                RoleListWidget.addItem(item_name)  # populate the list widget in the GUI
            RoleListWidget.updated = True

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

    def copy_user(self, UserListWidgetFrom, UserListWidgetTo, RoleListWidgetTo, fromurl, fromid, fromkey,
                  tourl, toid, tokey):

        # Need to add check if user already exists and interactively ask if any missing roles should be created 
        logger.info("[Users and Roles]Copying User(s)")
        try:
            selecteditems = UserListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                for selecteditem in selecteditems:
                    for object in UserListWidgetFrom.currentcontent:
                        if object['firstName'] + ' ' + object['lastName'] == str(selecteditem.text()):
                            user_id = object['id']
                            user = fromsumo.get_user_and_roles(user_id)
                            # print('unmodified user: ' + str(user))
                            dest_roles = tosumo.get_roles_sync()
                            for source_role in user['roles']:
                                role_already_exists_in_dest = False
                                source_role_id = source_role['id']
                                for dest_role in dest_roles:
                                    if dest_role['name'] == source_role['name']:
                                        role_already_exists_in_dest = True
                                        dest_role_id = dest_role['id']
                                if role_already_exists_in_dest:
                                    # print('found role at target: ' + source_role['name'])
                                    user['roleIds'].append(dest_role_id)
                                    user['roleIds'].remove(source_role_id)
                                else:
                                    source_role['users'] = []
                                    tosumo.create_role(source_role)
                                    updated_dest_roles = tosumo.get_roles_sync()
                                    for updated_dest_role in updated_dest_roles:
                                        if updated_dest_role['name'] == source_role['name']:
                                            user['roleIds'].append(updated_dest_role['id'])
                                    user['roleIds'].remove(source_role_id)
                                    # print('Did not find role at target. Added role:' + source_role['name'])
                            # print('modified user: ' + str(user))
                            tosumo.create_user(user['firstName'], user['lastName'], user['email'], user['roleIds'])

                self.update_users_and_roles_lists(UserListWidgetTo, RoleListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_users_and_roles_lists(UserListWidgetTo, RoleListWidgetTo, tourl, toid, tokey)
        return

    def backup_user(self, UserListWidget, url, id, key):
        logger.info("[Users and Roles]Backing Up User(s)")
        selecteditems = UserListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url)
                for selecteditem in selecteditems:
                    for object in UserListWidget.currentcontent:
                        if object['firstName'] + ' ' + object['lastName'] == str(selecteditem.text()):
                            user_id = object['id']
                            try:
                                export = sumo.get_user_and_roles(user_id)

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.user.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(export, filepointer)
                                    message = message + str(selecteditem.text()) + r'.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                                return
                self.mainwindow.infobox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No user selected.')
        return

    def view_user_json(self, UserListWidget, url, id, key):
        logger.info("[Users and Roles]Viewing User(s) JSON")
        selecteditems = UserListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in UserListWidget.currentcontent:
                        if object['firstName'] + ' ' + object['lastName'] == str(selecteditem.text()):
                            user_id = object['id']
                            user = sumo.get_user(user_id)
                            json_text = json_text + json.dumps(user, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                return
        else:
            self.mainwindow.errorbox('No user selected.')
        return

    def restore_user(self, RoleListWidget, UserListWidget, url, id, key):
        logger.info("[Users and Roles]Restoring User(s)")
        if UserListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:
                sumo = SumoLogic(id, key, endpoint=url)
                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            user = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        dest_roles = sumo.get_roles_sync()
                        for source_role in user['roles']:
                            role_already_exists_in_dest = False
                            source_role_id = source_role['id']
                            for dest_role in dest_roles:
                                if dest_role['name'] == source_role['name']:
                                    role_already_exists_in_dest = True
                                    dest_role_id = dest_role['id']
                            if role_already_exists_in_dest:
                                # print('found role at target: ' + source_role['name'])
                                user['roleIds'].append(dest_role_id)
                                user['roleIds'].remove(source_role_id)
                            else:
                                source_role['users'] = []
                                sumo.create_role(source_role)
                                updated_dest_roles = sumo.get_roles_sync()
                                for updated_dest_role in updated_dest_roles:
                                    if updated_dest_role['name'] == source_role['name']:
                                        user['roleIds'].append(updated_dest_role['id'])
                                user['roleIds'].remove(source_role_id)
                                # print('Did not find role at target. Added role:' + source_role['name'])
                            # print('modified user: ' + str(user))
                        sumo.create_user(user['firstName'], user['lastName'], user['email'], user['roleIds'])

                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_users_and_roles_lists(UserListWidget, RoleListWidget, url, id, key)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the directory list before restoring content")
        return

    def delete_user(self, RoleListWidget, UserListWidget, url, id, key):
        logger.info("[Users and Roles]Deleting User(s)")
        selecteditems = UserListWidget.selectedItems()
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

                    sumo = SumoLogic(id, key, endpoint=url)
                    for selecteditem in selecteditems:
                        for object in UserListWidget.currentcontent:
                            if object['firstName'] + ' ' + object['lastName'] == str(selecteditem.text()):
                                item_id = object['id']

                        result = sumo.delete_user(item_id)

                    self.update_users_and_roles_lists(UserListWidget, RoleListWidget, url, id, key)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return

    def copy_role(self, RoleListWidgetFrom, RoleListWidgetTo, UserListWidgetTo, fromurl, fromid, fromkey,
                  tourl, toid, tokey):

        logger.info("[Users and Roles]Copying Role(s)")
        try:
            selecteditems = RoleListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl)
                for selecteditem in selecteditems:
                    for object in RoleListWidgetFrom.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            role_id = object['id']
                            role = fromsumo.get_role(role_id)
                            status = tosumo.create_role(role)
                self.update_users_and_roles_lists(UserListWidgetTo, RoleListWidgetTo, tourl, toid, tokey)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:' + str(e))
            self.update_users_and_roles_lists(UserListWidgetTo, RoleListWidgetTo, tourl, toid, tokey)
        return

    def backup_role(self, RoleListWidget, url, id, key):
        logger.info("[Users and Roles]Backing Up Role(s)")
        selecteditems = RoleListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url)
                for selecteditem in selecteditems:
                    for object in RoleListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            item_id = object['id']
                            try:
                                export = sumo.get_role(item_id)

                                savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.role.json')
                                if savefilepath:
                                    with savefilepath.open(mode='w') as filepointer:
                                        json.dump(export, filepointer)
                                    message = message + str(selecteditem.text()) + r'.json' + '\n'
                            except Exception as e:
                                logger.exception(e)
                                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                                return
                self.mainwindow.infobox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No content selected.')
        return

    def view_role_json(self, RoleListWidget, url, id, key):
        logger.info("[Users and Roles]Viewing Roles(s) JSON")
        selecteditems = RoleListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            try:
                sumo = SumoLogic(id, key, endpoint=url)
                json_text = ''
                for selecteditem in selecteditems:
                    for object in RoleListWidget.currentcontent:
                        if object['name'] == str(selecteditem.text()):
                            role_id = object['id']
                            role = sumo.get_role(role_id)
                            json_text = json_text + json.dumps(role, indent=4, sort_keys=True) + '\n\n'
                self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
                self.json_window.show()

            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                return
        else:
            self.mainwindow.errorbox('No role selected.')
        return

    def restore_role(self, RoleListWidget, UserListWidget, url, id, key):
        logger.info("[Users and Roles]Restoring Role(s)")
        if RoleListWidget.updated == True:

            filter = "JSON (*.json)"
            filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                      filter)
            if len(filelist) > 0:
                sumo = SumoLogic(id, key, endpoint=url)
                for file in filelist:
                    try:
                        with open(file) as filepointer:
                            role_backup = json.load(filepointer)
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox(
                            "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                        return
                    try:
                        role_backup['users'] = []
                        status = sumo.create_role(role_backup)

                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.update_users_and_roles_lists(UserListWidget, RoleListWidget, url, id, key)


            else:
                self.mainwindow.errorbox("Please select at least one file to restore.")
                return
        else:
            self.mainwindow.errorbox("Please update the directory list before restoring content")
        return

    def delete_role(self, RoleListWidget, UserListWidget, url, id, key):
        logger.info("[Users and Roles]Deleting Role(s)")
        selecteditems = RoleListWidget.selectedItems()
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

                    sumo = SumoLogic(id, key, endpoint=url)
                    for selecteditem in selecteditems:
                        for object in RoleListWidget.currentcontent:
                            if object['name'] == str(selecteditem.text()):
                                item_id = object['id']

                        result = sumo.delete_role(item_id)

                    self.update_users_and_roles_lists(UserListWidget, RoleListWidget, url, id, key)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return
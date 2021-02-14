from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import sys
import re
import pathlib
import json
from logzero import logger
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog, export_user_and_roles, import_user_and_roles

class_name = 'users_and_roles_tab'


class users_and_roles_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):
        super(users_and_roles_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Users and Roles'
        self.cred_usage = 'both'
        users_and_roles_widget_ui = os.path.join(self.mainwindow.basedir, 'data/users_and_roles.ui')
        uic.loadUi(users_and_roles_widget_ui, self)
        self.listWidgetUsersLeft.side = 'Left'
        self.listWidgetUsersRight.side = 'Right'
        self.listWidgetRolesLeft.side = 'Left'
        self.listWidgetRolesRight.side = 'Right'

        # Connect the UI buttons to methods

        # Connect Update Buttons
        self.pushButtonUpdateUsersAndRolesLeft.clicked.connect(lambda: self.update_users_and_roles_lists(
            self.listWidgetUsersLeft,
            self.listWidgetRolesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateUsersAndRolesRight.clicked.connect(lambda: self.update_users_and_roles_lists(
            self.listWidgetUsersRight,
            self.listWidgetRolesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        # Connect Search Bars
        self.lineEditSearchUsersLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetUsersLeft,
            self.lineEditSearchUsersLeft.text()
        ))

        self.lineEditSearchUsersRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetUsersRight,
            self.lineEditSearchUsersRight.text()
        ))

        self.lineEditSearchRolesLeft.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetRolesLeft,
            self.lineEditSearchRolesLeft.text()
        ))

        self.lineEditSearchRolesRight.textChanged.connect(lambda: self.set_listwidget_filter(
            self.listWidgetRolesRight,
            self.lineEditSearchRolesRight.text()
        ))

        self.pushButtonCopyUserLeftToRight.clicked.connect(lambda: self.copy_user(
            self.listWidgetUsersLeft,
            self.listWidgetUsersRight,
            self.listWidgetRolesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCopyUserRightToLeft.clicked.connect(lambda: self.copy_user(
            self.listWidgetUsersRight,
            self.listWidgetUsersLeft,
            self.listWidgetRolesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupUserLeft.clicked.connect(lambda: self.backup_user(
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupUserRight.clicked.connect(lambda: self.backup_user(
            self.listWidgetUsersRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonUserJSONLeft.clicked.connect(lambda: self.view_user_json(
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUserJSONRight.clicked.connect(lambda: self.view_user_json(
            self.listWidgetUsersRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonRestoreUserLeft.clicked.connect(lambda: self.restore_user(
            self.listWidgetRolesLeft,
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRestoreUserRight.clicked.connect(lambda: self.restore_user(
            self.listWidgetRolesRight,
            self.listWidgetUsersRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteUserLeft.clicked.connect(lambda: self.delete_user(
            self.listWidgetRolesLeft,
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteUserRight.clicked.connect(lambda: self.delete_user(
            self.listWidgetRolesRight,
            self.listWidgetUsersRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCopyRoleLeftToRight.clicked.connect(lambda: self.copy_role(
            self.listWidgetRolesLeft,
            self.listWidgetRolesRight,
            self.listWidgetUsersRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonCopyRoleRightToLeft.clicked.connect(lambda: self.copy_role(
            self.listWidgetRolesRight,
            self.listWidgetRolesLeft,
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupRoleLeft.clicked.connect(lambda: self.backup_role(
            self.listWidgetRolesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonBackupRoleRight.clicked.connect(lambda: self.backup_role(
            self.listWidgetRolesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonRoleJSONLeft.clicked.connect(lambda: self.view_role_json(
            self.listWidgetRolesLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRoleJSONRight.clicked.connect(lambda: self.view_role_json(
            self.listWidgetRolesRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonRestoreRoleLeft.clicked.connect(lambda: self.restore_role(
            self.listWidgetRolesLeft,
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonRestoreRoleRight.clicked.connect(lambda: self.restore_role(
            self.listWidgetRolesRight,
            self.listWidgetUsersRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text())
        ))

        self.pushButtonDeleteRoleLeft.clicked.connect(lambda: self.delete_role(
            self.listWidgetRolesLeft,
            self.listWidgetUsersLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonDeleteRoleRight.clicked.connect(lambda: self.delete_role(
            self.listWidgetRolesRight,
            self.listWidgetUsersRight,
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
            self.listWidgetUsersLeft.clear()
            self.listWidgetUsersLeft.currentcontent = {}
            self.listWidgetUsersLeft.updated = False
            self.listWidgetRolesLeft.clear()
            self.listWidgetRolesLeft.currentcontent = {}
            self.listWidgetRolesLeft.updated = False

        if right:
            self.listWidgetUsersRight.clear()
            self.listWidgetUsersRight.currentcontent = {}
            self.listWidgetUsersRight.updated = False
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
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        try:
            logger.info("[Users and Roles] Updating Users and Roles Lists")
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
                item = QtWidgets.QListWidgetItem(item_name)
                item.details = object
                UserListWidget.addItem(item)  # populate the list widget in the GUI
                if UserListWidget.side == 'Left':
                    self.set_listwidget_filter(
                        UserListWidget,
                        self.lineEditSearchUsersLeft.text()
                    )
                elif UserListWidget.side == 'Right':
                    self.set_listwidget_filter(
                        UserListWidget,
                        self.lineEditSearchUsersRight.text()
                    )
            UserListWidget.updated = True
            for object in RoleListWidget.currentcontent:
                item_name = object['name']
                item = QtWidgets.QListWidgetItem(item_name)
                item.details = object
                RoleListWidget.addItem(item)  # populate the list widget in the GUI
                if RoleListWidget.side == 'Left':
                    self.set_listwidget_filter(
                        RoleListWidget,
                        self.lineEditSearchRolesLeft.text()
                    )
                elif RoleListWidget.side == 'Right':
                    self.set_listwidget_filter(
                        RoleListWidget,
                        self.lineEditSearchRolesRight.text()
                    )
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
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    user_id = selecteditem.details['id']
                    user_and_roles = export_user_and_roles(user_id, fromsumo)
                    result = import_user_and_roles(user_and_roles, tosumo)

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
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    user_id = selecteditem.details['id']
                    try:
                        export = export_user_and_roles(user_id, sumo)

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
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for selecteditem in selecteditems:
                    user_id = selecteditem.details['id']
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
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
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
                        result = import_user_and_roles(user, sumo)

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

                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        item_id = selecteditem.details['id']
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
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    role_id = selecteditem.details['id']
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
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    item_id = selecteditem.details['id']
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
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                json_text = ''
                for selecteditem in selecteditems:
                    role_id = selecteditem.details['id']
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
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
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
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        item_id = selecteditem.details['id']
                        result = sumo.delete_role(item_id)
                    self.update_users_and_roles_lists(UserListWidget, RoleListWidget, url, id, key)
                    return

                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return

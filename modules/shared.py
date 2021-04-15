from qtpy import QtWidgets, QtGui
from logzero import logger
import pathlib
from functools import wraps
from datetime import datetime, timezone


class ShowTextDialog(QtWidgets.QDialog):

    def __init__(self, title, text, base_dir):
        super(ShowTextDialog, self).__init__()
        self.title = title
        self.text = text
        self.setMinimumSize(600, 600)
        self.last_search = "Up"
        self.icons = {}
        iconpath = str(pathlib.Path(base_dir + '/data/arrow-up.svg'))
        self.icons['ArrowUp'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(base_dir + '/data/arrow-down.svg'))
        self.icons['ArrowDown'] = QtGui.QIcon(iconpath)
        self.setupUi(self)
        self.searchbox.textChanged.connect(lambda: self.search(
            self.searchbox.text()
        ))
        self.searchup.clicked.connect(lambda: self.search_up(
            self.searchbox.text()
        ))
        self.searchdown.clicked.connect(lambda: self.search_down(
            self.searchbox.text()
        ))

    def setupUi(self, Dialog):
        Dialog.setObjectName("JSONDisplay")
        self.setWindowTitle(self.title)

        self.searchlayout = QtWidgets.QHBoxLayout()
        self.searchbox = QtWidgets.QLineEdit()
        self.searchbox.setPlaceholderText('Search')
        self.searchlayout.addWidget(self.searchbox)
        self.searchup = QtWidgets.QPushButton()
        self.searchup.setIcon(self.icons['ArrowUp'])
        self.searchlayout.addWidget(self.searchup)
        self.searchdown = QtWidgets.QPushButton()
        self.searchdown.setIcon(self.icons['ArrowDown'])
        self.searchlayout.addWidget(self.searchdown)
        self.textedit = QtWidgets.QTextEdit()
        self.textedit.setText(self.text)
        # self.textedit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.textedit.setReadOnly(True)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.searchlayout)
        self.layout.addWidget(self.textedit)
        self.setLayout(self.layout)

    def search(self, search_text):
        self.textedit.textCursor().clearSelection()
        if self.last_search == 'Up':
            search_result = self.textedit.find(search_text)
            if search_result:
                self.last_search = 'Down'
            else:
                search_result = self.textedit.find(search_text, QtGui.QTextDocument.FindBackward)
                self.last_search = 'Up'

    def search_down(self, search_text):
        search_result = self.textedit.find(search_text)

    def search_up(self, search_text):
        search_result = self.textedit.find(search_text, QtGui.QTextDocument.FindBackward)


# functions that are shared by multiple tabs. These are mostly import/export functions that will be used by their own
# tab (import monitors is used by the monitor tab for instance) and also be used by the orgs tab, when deploying config
# to a newly provisioned org.

def errorbox(message):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText(message)
    msgBox.addButton(QtWidgets.QPushButton('OK'), QtWidgets.QMessageBox.RejectRole)
    ret = msgBox.exec_()
    return

def infobox(message):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle('Info')
    msgBox.setText(message)
    msgBox.addButton(QtWidgets.QPushButton('OK'), QtWidgets.QMessageBox.RejectRole)
    ret = msgBox.exec_()
    return

def exception_and_error_handling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(e)
            errorbox('Something went wrong:\n\n' + str(e))
    return wrapper

# Recursively find all instances of a key in a dict/list object. Thanks Stackoverflow. Yoink!
def find_keys(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


# Recursively find all instances of a key in a dict/list object and replace the value with a new value IF it
# matches the old value
def find_replace_specific_key_and_value(obj, key, old_value, new_value):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict,list)):
                obj[k] = find_replace_specific_key_and_value(v, key, old_value, new_value)
            elif k == key and v == old_value:
                obj[k] = new_value
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            obj[index] = find_replace_specific_key_and_value(item, key, old_value, new_value)
    return obj


def find_replace_keys(obj, key, new_value):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                obj[k] = new_value
            elif isinstance(v, (dict,list)):
                obj[k] = find_replace_keys(v, key, new_value)

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            obj[index] = find_replace_keys(item, key, new_value)
    return obj



# This call gets the monitor(s) and then all connections used by that monitor. This is useful for exporting or copying a
# monitor to a new org. This is a bit messy due to the requirement to specify connectionType in the get_connection
# method.
def export_monitor(self, item_id, sumo):
    # export the monitor/folder (the easy part)
    monitor = sumo.export_monitor(str(item_id))
    # find every connectionId key in the exported JSON
    connection_ids = find_keys(monitor, 'connectionId')
    # we're going to attach all the connection dependencies to this object so create an empty list
    monitor['connections'] = []
    # get a list of current connections (we have to do this because we need the connection type to export the connection)
    connections = sumo.get_connections_sync()
    # iterate through the connection IDs we found in the monitor
    for connection_id in connection_ids:
        # and iterate through list of all connections in the org
        for connection in connections:
            # if we find a match export the connection and attach it to the monitor JSON
            if connection['id'] == connection_id:
                exported_connection = export_connection(None, connection_id, sumo)
                monitor['connections'].append(exported_connection)
                break
    return monitor


def import_monitor(self, parent_id, monitor, sumo, include_connection=False):
    if include_connection:
        connection_lookups = []
        org_connection_list = sumo.get_connections_sync()
        for monitor_connection in monitor['connections']:
            connection_found = False
            # iterate through the connections already in the org, if any of them match the name of the exported connection
            # then take note of it's connectionId and which name it pairs with
            while not connection_found:
                for org_connection in org_connection_list:
                    if monitor_connection['name'] == org_connection['name']:
                        connection_lookups_entry = {'name': monitor_connection['name'],
                                                   'old_id': monitor_connection['id'],
                                                   'new_id': org_connection['id']}
                        connection_lookups.append(connection_lookups_entry)
                        connection_found =True
                        break
                if not connection_found:
                    result = import_connection(None, monitor_connection, sumo)
                    org_connection_list = sumo.get_connections_sync()

        for connection_lookup in connection_lookups:
            monitor = find_replace_specific_key_and_value(monitor, 'connectionId', connection_lookup['old_id'], connection_lookup['new_id'])
        for index, connection in enumerate(monitor['connections']):
            monitor['connections'][index]['type'] = str(connection['type']).replace('Connection',
                                                                                    'Definition')
        result = sumo.import_monitor(parent_id, monitor)
    else:
        monitor = find_replace_keys(monitor, 'notifications', [])
        result = sumo.import_monitor(parent_id, monitor)

    return result


def export_connection(self, connection_id, sumo):
    connections = sumo.get_connections_sync()
    for connection in connections:
        if connection['id'] == connection_id:
            connection_type = connection['type']
            return sumo.get_connection(connection_id, connection_type)


def import_connection(self, connection, sumo):
    connection['type'] = str(connection['type']).replace('Connection', 'Definition')
    status = sumo.create_connection(connection)
    return status


def export_saml_config(self, item_id, sumo):
    return sumo.get_saml_config_by_id(item_id)


def import_saml_config(self, saml_export, sumo):
    # Hacky stuff to get create to work
    if 'spInitiatedLoginPath' in saml_export: del saml_export['spInitiatedLoginPath']
    if 'authnRequestUrl' in saml_export: del saml_export['authnRequestUrl']
    saml_export['spInitiatedLoginEnabled'] = False
    # End Hacky stuff
    status = sumo.create_saml_config(saml_export)


def export_user(self, user_id, sumo):
    user = sumo.get_user(str(user_id))
    user['roles'] = []
    for role_id in user['roleIds']:
        role = export_role(None, role_id, sumo)
        user['roles'].append(role)
    return user


def import_user(self, user, sumo, include_roles=False):
    dest_role_id = None
    dest_roles = sumo.get_roles_sync()
    if include_roles:
        for source_role in user['roles']:
            role_already_exists_in_dest = False
            source_role_id = source_role['id']
            for dest_role in dest_roles:
                if dest_role['name'] == source_role['name']:
                    role_already_exists_in_dest = True
                    dest_role_id = dest_role['id']
            if role_already_exists_in_dest:
                user['roleIds'].append(dest_role_id)
                user['roleIds'].remove(source_role_id)
            else:
                import_role(None, source_role, sumo)
                updated_dest_roles = sumo.get_roles_sync()
                for updated_dest_role in updated_dest_roles:
                    if updated_dest_role['name'] == source_role['name']:
                        user['roleIds'].append(updated_dest_role['id'])
                user['roleIds'].remove(source_role_id)
        result = sumo.create_user(user['firstName'], user['lastName'], user['email'], user['roleIds'])
    else:
        #  if the user is an admin or analyst find that ID in the list of roles from the destination org
        #  and add it to the new role list
        new_role_list = []
        for source_role in user['roles']:
            if source_role['name'] == 'Administrator':
                for dest_role in dest_roles:
                    if dest_role['name'] == 'Administrator':
                        new_role_list.append(dest_role['id'])
            if source_role['name'] == 'Analyst':
                for dest_role in dest_roles:
                    if dest_role['name'] == 'Analyst':
                        new_role_list.append(dest_role['id'])
        #  at this point hopefully we should have at least one new role for the user. If not make them
        #  an analyst
        if not(len(new_role_list) > 0):
            for dest_role in dest_roles:
                if dest_role['name'] == 'Analyst':
                    new_role_list.append(dest_role['id'])
        user['roleIds'] = new_role_list
        result = sumo.create_user(user['firstName'], user['lastName'], user['email'], user['roleIds'])
    return result


def export_role(self, role_id, sumo):
    return sumo.get_role(str(role_id))


def import_role(self, role, sumo):
    role['users'] = []
    return sumo.create_role(role)

def export_fer(self, fer_id, sumo):
    return sumo.get_fer(fer_id)

def import_fer(self, fer, sumo):
    return sumo.create_fer(fer)

def export_scheduled_view(self, sv_id, sumo):
    return sumo.get_scheduled_view(sv_id)

def import_scheduled_view(self, sv, sumo, use_current_date=True):
    if use_current_date:
        sv['startTime'] = str(datetime.now(timezone.utc).astimezone().isoformat())
    return sumo.create_scheduled_view(sv)


def export_content(self, item_id, sumo, adminmode):

    content = sumo.export_content_job_sync(item_id, adminmode=adminmode)
    connection_ids = find_keys(content, 'webhookId')
    content['connections'] = []
    connections = sumo.get_connections_sync()
    for connection_id in connection_ids:
        # and iterate through list of all connections in the org
        for connection in connections:
            # if we find a match export the connection and attach it to the monitor JSON
            if connection['id'] == connection_id:
                connection_type = connection['type']
                exported_connection = export_connection(connection_id, sumo)
                content['connections'].append(exported_connection)
                break
    return content


def import_content(self, content, folder_id, sumo, adminmode, include_connections=False):
    if include_connections:
        connection_lookups = []
        org_connection_list = sumo.get_connections_sync()
        for content_connection in content['connections']:
            connection_found = False
            # iterate through the connections already in the org, if any of them match the name of the exported connection
            # then take note of it's connectionId and which name it pairs with
            while not connection_found:
                for org_connection in org_connection_list:
                    if content_connection['name'] == org_connection['name']:
                        connection_lookups_entry = {'name': content_connection['name'],
                                                    'old_id': content_connection['id'],
                                                    'new_id': org_connection['id']}
                        connection_lookups.append(connection_lookups_entry)
                        connection_found = True
                        break
                if not connection_found:
                    result = import_connection(content_connection, sumo)
                    org_connection_list = sumo.get_connections_sync()

        for connection_lookup in connection_lookups:
            content = find_replace_specific_key_and_value(content, 'webhookId', connection_lookup['old_id'],
                                                          connection_lookup['new_id'])
        result = sumo.import_content_job_sync(folder_id, content, adminmode=adminmode)
    else:
        content = find_replace_keys(content, 'searchSchedule', None)
        result = sumo.import_content_job_sync(folder_id, content, adminmode=adminmode)
    return result


def export_partition(self, item_id, sumo):
    return sumo.get_partition(item_id)


def import_partition(self, payload, sumo):
    return sumo.create_partition(payload)











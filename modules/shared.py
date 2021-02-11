
from qtpy import QtWidgets, QtGui, QtCore
import pathlib

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


# functions that are shared by multiple tabs. These are mostly import/export functions that will be used by their own tab
# (import monitors is used by the monitor tab for instance) and also be used by the orgs tab, when deploying config
# to a newly provisioned org.

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

# This call gets the monitor(s) and then all connections used by that monitor. This is useful for exporting or copying a monitor
# to a new org. This is a bit messy due to the requirement to specify connectionType in the get_connection method.
def export_monitor_and_connections(item_id, sumo):
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
                connection_type = connection['type']
                exported_connection = sumo.get_connection(connection_id, connection_type)
                monitor['connections'].append(exported_connection)
                break
    return monitor

def import_monitors_with_connections(parent_id, monitor, sumo):

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
                result = sumo.create_connection(monitor_connection)
                org_connection_list = sumo.get_connections_sync()

    for connection_lookup in connection_lookups:
        monitor = find_replace_specific_key_and_value(monitor, 'connectionId', connection_lookup['old_id'], connection_lookup['new_id'])
    result = sumo.import_monitor(parent_id, monitor)

def import_monitors_without_connections(parent_id, monitor, sumo):
    monitor = find_replace_keys(monitor, 'notifications', [])
    result = sumo.import_monitor(parent_id, monitor)

def import_saml_config(saml_export, sumo):
    # Hacky stuff to get create to work
    if 'spInitiatedLoginPath' in saml_export: del saml_export['spInitiatedLoginPath']
    if 'authnRequestUrl' in saml_export: del saml_export['authnRequestUrl']
    saml_export['spInitiatedLoginEnabled'] = False
    # End Hacky stuff
    status = sumo.create_saml_config(saml_export)

def content_item_to_permissions(sumo, content, isTopLevel=False, adminmode=False):
    folders = []
    if isinstance(content, dict):
        if 'id' in content and 'name' in content and 'itemType' in content:
            id = content['id']
            name = content['name']
            itemType = content['itemType']
            permissions = sumo.get_permissions(id,explicit_only=True,adminmode=adminmode)
            currentPath = sumo.get_item_path(id, adminmode=adminmode)['path']
            details = {'id': id, 'name': name, 'itemType': itemType, 'path': currentPath,'permissions': permissions['explicitPermissions']}
            folders.append(details)

            if itemType == 'Folder' and 'children' in content and len(content['children']) > 0:
                for child in content['children']:
                    if child['itemType'] == 'Folder':
                        child = sumo.get_folder(child['id'], adminmode=adminmode)
                    folders = folders + content_item_to_permissions(sumo, child, adminmode=adminmode)

    elif isinstance(content, list):
        for index, item in enumerate(content):
            folders = folders + content_item_to_permissions(sumo,item, adminmode=adminmode)

    return folders















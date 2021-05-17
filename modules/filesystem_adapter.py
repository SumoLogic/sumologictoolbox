from modules.adapter import Adapter
import pathlib
import ntpath
import os
import json
import platform
from logzero import logger
import string
if platform.system() == 'Windows':
    from ctypes import windll


class FilesystemAdapter(Adapter):

    def __init__(self, creds, side, log_level='info'):
        super(FilesystemAdapter, self).__init__(None, side, log_level=log_level)
        self.configured = True
        self._go_to_default_dir()
        self.list_windows_drives = False

    def get_windows_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_lowercase:
            if bitmask & 1:
                drive_dict = {'name': str(letter),
                             'itemType': 'Drive'}
                drives.append(drive_dict)
            bitmask >>= 1
        return drives

    def at_top_of_hierarchy(self):
        #  we must be at root if the id list is empty
        #return not self.current_path_list
        return len(self.current_path_list) <= 1

    def _generate_path_string(self, prefix=""):
        path_string = str(prefix)
        if platform.system() == "Windows":
            for directory in self.current_path_list:
                path_string = path_string + f"{directory}\\"
        else:
            for directory in self.current_path_list:
                path_string = path_string + f"{directory}/"
        return path_string

    def _go_to_default_dir(self):
        home_dir = pathlib.Path.home()
        self._reset_path()
        path_list = list(home_dir.parts)
        self.current_path_list = path_list
        self._update_path_string()

    def list(self, params=None):
        item_list = []
        item_list.extend(self._get_folders())
        if self.list_windows_drives and platform.system() == "Windows":
            return self.get_windows_drives()
        elif params is not None and 'extension' in params:
            filter = '*' + str(params['extension'])
            item_list.extend(self._get_files(filter))
        else:
            item_list.extend(self._get_files('*'))
        return item_list

    def _get_files(self, filter):
        file_list = []
        path = pathlib.Path(str(self.get_current_path()))
        logger.debug(f'Getting files that match: {filter}')
        files = path.glob(filter)
        for file in files:
            if file.is_file():
                _, file_name = ntpath.split(file)
                file_dict = {'name': file_name,
                             'itemType': 'File'}
                file_list.append(file_dict)
        return file_list

    def _get_folders(self):
        folder_list = []
        for path in pathlib.Path(self.get_current_path()).iterdir():
            if path.is_dir():
                folder_name = os.path.basename(path)
                logger.debug(f"[Filesystem Adapter] Found folder {folder_name} in {os.path.dirname(path)}")
                folder_dict = {'name': folder_name,
                               'itemType': 'Folder'}
                folder_list.append(folder_dict)
        return folder_list

    def up(self, params=None):
        if self.at_top_of_hierarchy() and platform.system() == "Windows":
            logger.debug(f"[Filesystem Adapter] Detected Windows top of hierarchy. Setting flag to list drive letters. ")
            self.list_windows_drives = True
            self._remove_dir_from_path()
            return True
        elif self.at_top_of_hierarchy():
            return False
        else:
            self._remove_dir_from_path()
            return True

    def down(self, folder_name, params=None):
        if self.list_windows_drives and platform.system() == "Windows":
            folder_name = folder_name + ":"
            self._add_dir_to_path(folder_name)
            logger.debug(f"[Filesystem Adapter] Detected Windows top of hierarchy. Selecting drive. New path is {self.get_current_path()} ")
            self.list_windows_drives = False
            return True
        else:
            path = pathlib.Path(self.get_current_path(), folder_name)
            if path.is_dir():
                self._add_dir_to_path(folder_name)
                logger.debug(f'New path: {self.get_current_path()}')
                return True
            else:
                return False

    def create_folder(self, folder_name, list_widget, params=None):
        try:
            path = pathlib.Path(self.get_current_path(), folder_name)
            logger.debug(f"Creating filesystem folder: {str(path)}")
            path.mkdir()
            return {'status': 'SUCCESS',
                    'result': True,
                    'adapter': self,
                    'params': params,
                    'list_widget': list_widget}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, item_name, payload, list_widget, params=None):
        try:
            file_name = str(item_name) + str(params['extension'])
            file_name = file_name.replace('/', '-')
            save_file_path = pathlib.Path(self.get_current_path(), file_name)
            logger.debug(f'Writing to file: {str(save_file_path)}')
            with save_file_path.open('w', encoding='UTF-8') as f:
                json.dump(payload, f)
            return {'status': 'SUCCESS',
                    'result': True,
                    'adapter': self,
                    'params': params,
                    'list_widget': list_widget}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def get(self, item_name, item_id, params=None):
        try:
            file_name = item_name
            save_file_path = pathlib.Path(self.get_current_path(), file_name)
            logger.debug(f'Reading from file: {str(save_file_path)}')
            with save_file_path.open(encoding='UTF-8') as f:
                contents = json.load(f)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': contents,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, item_name, item_id, params=None):
        return self.get(item_name, item_id, params=params)

    def import_item(self, item_name, payload, list_widget,  params=None):
        return self.put(item_name, payload, list_widget, params=params)

    def delete(self, item_name, item_id, list_widget, params=None):
        try:
            path = pathlib.Path(self.get_current_path(), item_name)
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()
            return {'status': 'SUCCESS',
                    'result': None,
                    'adapter': self,
                    'params': params,
                    'list_widget': list_widget}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }
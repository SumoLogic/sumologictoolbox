from modules.adapter import Adapter
import pathlib
import ntpath

class FilesystemAdapter(Adapter):

    def __init__(self, creds, side, log_level='info'):
        super(FilesystemAdapter, self).__init__(None, side, log_level=log_level)
        self.configured = True
        self._go_to_default_dir()

    def _go_to_default_dir(self):
        home_dir = pathlib.Path.home()
        self._reset_path()
        path_list = list(home_dir.parts)
        self.current_path_list = path_list
        self._update_path_string()

    def list(self, mode, params=None):
        item_list = []
        if params is not None and 'filter' in params:
            filter = params['filter']
        else:
            filter = "*"
        print(self.path_string)
        path = pathlib.Path(str(self.get_current_path()))
        items = path.glob(filter)
        folder = ""
        for item in items:
            folder, filename = ntpath.split(item)
            print(f"{folder} {filename}")
            item_dict = {'name': str(filename)}
            item_list.append(item_dict)
        self.path_string = folder
        self._update_path_string()
        return item_list

    def up(self, mode, params=None):
        return False

    def down(self, mode, folder_name, params=None):
        return False

    def create_folder(self, mode, folder_name, list_widget, params=None):
        return False

    def put(self, mode, item_name, payload, list_widget, params=None):
        return False

    def get(self, mode, item_name, item_id, params=None):
        return False

    def export_item(self, mode, item_name, item_id, params=None):
        return False

    def import_item(self, mode, item_name, payload, list_widget,  params=None):
        return False

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        return False



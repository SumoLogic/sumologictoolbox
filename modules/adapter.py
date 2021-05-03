class Adapter:

    import sys

    def __init__(self, creds, side, log_level='info'):
        self.current_path_list = []
        self.log_level = log_level
        self.path_string = ""
        self.configured = False
        self.sumo_adapter = False
        self.side = side

    def is_configured(self):
        return self.configured

    def is_sumo_adapter(self):
        return self.sumo_adapter

    def list(self, mode, params=None):
        return False

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

    def get_current_path(self):
        return self.path_string

    def _reset_path(self):
        self.current_path_list = []

    def _update_path_string(self, prefix=""):
        self.path_string = self._generate_path_string(prefix=prefix)

    def _generate_path_string(self, prefix=""):
        path_string = str(prefix)
        for directory in self.current_path_list:
            path_string = path_string + f"{directory}/"
        return path_string

    def _add_dir_to_path(self, directory):
        self.current_path_list.append(str(directory))
        self._update_path_string()

    def _remove_dir_from_path(self):
        self.current_path_list.pop()
        self._update_path_string()

    def at_top_of_hierarchy(self):
        #  we must be at root if the id list is empty
        return not self.current_path_list

    def _find_keys(self, obj, key):
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

    def _find_replace_keys(self, obj, key, new_value):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    obj[k] = new_value
                elif isinstance(v, (dict, list)):
                    obj[k] = self._find_replace_keys(v, key, new_value)

        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                obj[index] = self._find_replace_keys(item, key, new_value)
        return obj

    def _find_replace_specific_key_and_value(self, obj, key, old_value, new_value):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    obj[k] = self._find_replace_specific_key_and_value(v, key, old_value, new_value)
                elif k == key and v == old_value:
                    obj[k] = new_value
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                obj[index] = self._find_replace_specific_key_and_value(item, key, old_value, new_value)
        return obj

class SumoAdapter(Adapter):

    from modules.sumologic import SumoLogic
    from logzero import logger

    def __init__(self, creds, side, log_level='info'):
        super(SumoAdapter, self).__init__(creds, side)
        self.log_level=log_level
        self.sumo = self.sumo_from_creds(creds)
        self.sumo_adapter = True
        self.configured = True
        # try:
        #     self.sumo.get_account_contract()
        #     self.sumo_adapter = True
        #     self.configured = True
        # except Exception as e:
        #     self.configured = False
        #     self.logger.info(f'Failed to validate adapter: {str(e)}')

    def sumo_from_creds(self, creds):
        return self.SumoLogic(creds['id'],
                              creds['key'],
                              endpoint=creds['url'],
                              log_level=self.log_level)

    def sumo_search_records(self, query, from_time=None, to_time=None, timezone='UTC', by_receipt_time=False, params=None):
        try:
            results = self.sumo.search_job_records_sync(query,
                                                        fromTime=from_time,
                                                        toTime=to_time,
                                                        timeZone=timezone,
                                                        byReceiptTime=by_receipt_time)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': results,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def sumo_search_messages(self, query, from_time=None, to_time=None, timezone='UTC', by_receipt_time=False, params=None):
        try:
            results = self.sumo.search_job_messages_sync(query,
                                                        fromTime=from_time,
                                                        toTime=to_time,
                                                        timeZone=timezone,
                                                        byReceiptTime=by_receipt_time)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': results,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }


class SumoHierarchyAdapter(SumoAdapter):

    def __init__(self, creds, side, log_level='info'):
        super(SumoHierarchyAdapter, self).__init__(creds, side, log_level=log_level)
        self.current_path_id_list = []
        self.current_path_contents = {}

    def _add_dir_id_to_path(self, directory_id):
        self.current_path_id_list.append(str(directory_id))

    def _remove_dir_id_from_path(self):
        self.current_path_id_list.pop()

    def _reset_dir_id_path(self):
        self.current_path_id_list = []

    def _get_current_directory_id(self):
        if len(self.current_path_id_list) > 0:
            return self.current_path_id_list[-1]
        else:
            return False

    def _get_current_path_contents(self, mode):
        return []

    def list(self, mode, params=None):
        self.current_path_contents = self._get_current_path_contents(mode)
        return self.current_path_contents

    def up(self, mode, params=None):
        if self.at_top_of_hierarchy():
            return False
        else:
            self._remove_dir_id_from_path()
            self._remove_dir_from_path()
            self.current_path_contents = self._get_current_path_contents(mode)
            return True

    def down(self, mode, item_name, params=None):
        item = None
        self.logger.debug(f'[down] mode: {mode}')
        self.logger.debug(f'[down] item_name: {item_name}')
        for content in self._get_current_path_contents(mode):
            if content['name'] == str(item_name):
                item = content
                break
        self.logger.debug(f'[down] item: {item}')
        if 'itemType' in item:
            type_field = item['itemType']
        elif 'contentType' in item:
            type_field = item['contentType']
        else:
            type_field = None
        if item is not None and 'folder' in str(type_field).lower():
            self._add_dir_to_path(str(item_name))
            self._add_dir_id_to_path(item['id'])
            self.current_path_contents = self._get_current_path_contents(mode)
            return True
        else:
            return False


class SumoContentAdapter(SumoHierarchyAdapter):

    from modules.shared import import_content, export_content

    def __init__(self, creds, side, log_level='info'):
        super(SumoContentAdapter, self).__init__(creds, side, log_level=log_level)
        self.last_mode = ''
        self.current_path_contents = {}

    def _self_update_path_string_from_mode(self, mode):
        if mode == "personal":
            self._update_path_string(prefix='/Personal/')
        elif mode == "global":
            self._update_path_string(prefix='/Global/')
        elif mode == "admin":
            self._update_path_string(prefix='/Admin Recommended/')

    def _determine_admin_mode(self, mode):
        if mode == "personal":
            return False
        if mode == "global" or mode == "admin":
            return True

    def _get_current_path_contents(self, mode):
        contents = {}
        if self.last_mode is not mode:
            mode_switch = True
        else:
            mode_switch = False
        self.logger.debug(f'[_get_current_path_contents] mode: {mode}')
        self.logger.debug(f'[_get_current_path_contents] current path: {self.get_current_path()}')
        self.logger.debug(f'[_get_current_path_contents] current path: {self._get_current_directory_id()}')

        if mode == "personal":
            if mode_switch or self.at_top_of_hierarchy():
                contents = self.sumo.get_personal_folder()
                self._reset_path()
                self._reset_dir_id_path()
                self._add_dir_id_to_path(contents['id'])
            else:
                contents = self.sumo.get_folder(self._get_current_directory_id(), adminmode=self._determine_admin_mode(mode))
        if mode == "global":
            if mode_switch or self.at_top_of_hierarchy():
                contents = self.sumo.get_global_folder_sync(adminmode=True)
                self._reset_path()
                self._reset_dir_id_path()
                self._add_dir_id_to_path('TOP')
            else:
                contents = self.sumo.get_folder(self._get_current_directory_id(), adminmode=self._determine_admin_mode(mode))
        if mode == "admin":
            if mode_switch or self.at_top_of_hierarchy():
                contents = self.sumo.get_admin_folder_sync(adminmode=True)
                self._reset_path()
                self._reset_dir_id_path()
                self._add_dir_id_to_path(contents['id'])
            else:
                contents = self.sumo.get_folder(self._get_current_directory_id(), adminmode=self._determine_admin_mode(mode))
        self._self_update_path_string_from_mode(mode)
        self.last_mode = mode
        if 'children' in contents:
            return contents['children']
        if 'data' in contents:
            return contents['data']
        else:
            return False

    def create_folder(self, mode, folder_name, list_widget, params=None):
        adminmode = self._determine_admin_mode(mode)
        try:
            result = self.sumo.create_folder(folder_name, self._get_current_directory_id(), adminmode=adminmode)
            self.current_path_contents = self._get_current_path_contents(mode)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'result': result,
                    'list_widget': list_widget}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                }

    def get(self, mode, item_name, item_id, params=None):
        try:
            content = {}
            adminmode = self._determine_admin_mode(mode)
            for item in self.current_path_contents:
                if item['name'] == item_name:
                    if item['itemType'] == 'Folder':
                        content = self.sumo.get_folder(item_id, adminmode=adminmode)
                    else:
                        content = self.sumo.export_content_job_sync(item_id, adminmode=adminmode)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': content,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        adminmode = self._determine_admin_mode(mode)
        try:
            content = self.export_content(item_id, self.sumo, adminmode=adminmode)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': content,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        adminmode = self._determine_admin_mode(mode)
        try:
            current_dir_id = self._get_current_directory_id()
            if 'include_connections' not in params:
                raise Exception("You must pass a boolean 'include_connections' parameter.")
            else:
                include_connections = params['include_connections']
            result = self.import_content(payload,
                                         current_dir_id,
                                         self.sumo,
                                         adminmode=adminmode,
                                         include_connections=include_connections)
            return {'status': 'SUCCESS',
                    'result': result,
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

    def put(self, mode, item_name, payload, list_widget, params=None):
        return self.import_item(mode, item_name, payload, list_widget, params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        adminmode = self._determine_admin_mode(mode)
        try:
            result = self.sumo.delete_content_job_sync(item_id, adminmode=adminmode)
            return {'status': 'SUCCESS',
                    'result': result,
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


class SumoConnectionAdapter(SumoAdapter):

    from modules.shared import import_connection, export_connection

    def __init__(self, creds, side, log_level='info'):
        super(SumoConnectionAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        self.current_path_contents = self.sumo.get_connections_sync()
        return self.current_path_contents

    def get(self, mode, item_name, item_id, params=None):
        try:
            payload = None
            for connection in self.current_path_contents:
                if connection['id'] == item_id:
                    connection_type = connection['type']
                    payload = self.sumo.get_connection(item_id, connection_type)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': payload,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            connection = self.export_connection(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': connection,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_connection(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            connection_type = None
            connections = self.sumo.get_connections_sync()
            for connection in connections:
                if connection['id'] == item_id:
                    connection_type = connection['type']
                    result = self.sumo.delete_connection(item_id, connection_type)
                    return {'status': 'SUCCESS',
                            'result': result,
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


class SumoUserAdapter(SumoAdapter):

    from modules.shared import import_user, export_user

    def __init__(self, creds, side, log_level='info'):
        super(SumoUserAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        users = self.sumo.get_users_sync()
        for index, user in enumerate(users):
            users[index]['name'] = f"{user['firstName']} {user['lastName']}"
        return users

    def get(self, mode, item_name, item_id, params=None):
        try:
            user = self.sumo.get_user(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': user,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            user = self.export_user(item_id, self.sumo)
            user['name'] = f"{user['firstName']} {user['lastName']}"
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': user,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_user(payload, self.sumo, include_roles=params['include_roles'])
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            result = self.sumo.delete_user(item_id)
            return {'status': 'SUCCESS',
                    'result': result,
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


class SumoRoleAdapter(SumoAdapter):

    from modules.shared import import_role, export_role

    def __init__(self, creds, side, log_level='info'):
        super(SumoRoleAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        roles = self.sumo.get_roles_sync()
        return roles

    def get(self, mode, item_name, item_id, params=None):
        try:
            role = self.sumo.get_role(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': role,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            role = self.export_role(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': role,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_role(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            result = self.sumo.delete_role(item_id)
            return {'status': 'SUCCESS',
                    'result': result,
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


class SumoFERAdapter(SumoAdapter):

    from modules.shared import import_fer, export_fer

    def __init__(self, creds, side, log_level='info'):
        super(SumoFERAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        fers = self.sumo.get_fers_sync()
        return fers

    def get(self, mode, item_name, item_id, params=None):
        try:
            fer = self.sumo.get_fer(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': fer,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            fer = self.export_fer(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': fer,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_fer(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)


class SumoScheduledViewAdapter(SumoAdapter):

    from modules.shared import import_scheduled_view, export_scheduled_view

    def __init__(self, creds, side, log_level='info'):
        super(SumoScheduledViewAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        scheduled_views = self.sumo.get_scheduled_views_sync()
        for index, scheduled_view in enumerate(scheduled_views):
            scheduled_views[index]['name'] = scheduled_view['indexName']

        return scheduled_views

    def get(self, mode, item_name, item_id, params=None):
        try:
            scheduled_view = self.sumo.get_scheduled_view(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': scheduled_view,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            scheduled_view = self.export_scheduled_view(item_id, self.sumo)
            scheduled_view['name'] = scheduled_view['indexName']
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': scheduled_view,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_scheduled_view(payload, self.sumo, use_current_date=params['use_current_date'])
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            result = self.sumo.disable_scheduled_view(item_id)
            return {'status': 'SUCCESS',
                    'result': result,
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


class SumoMonitorAdapter(SumoHierarchyAdapter):

    from modules.shared import import_monitor, export_monitor

    def __init__(self, creds, side, log_level='info'):
        super(SumoMonitorAdapter, self).__init__(creds, side, log_level=log_level)
        self.last_mode = ''
        self.current_path_contents = {}

    def _get_current_path_contents(self, mode):
        self.logger.debug(f'[_get_current_path_contents] mode: {mode}')
        self.logger.debug(f'[_get_current_path_contents] current path: {self.get_current_path()}')
        self.logger.debug(f'[_get_current_path_contents] current path: {self._get_current_directory_id()}')
        if self.at_top_of_hierarchy():
            contents = self.sumo.get_monitor_folder_root()
            self._reset_path()
            self._reset_dir_id_path()
            self._add_dir_id_to_path(contents['id'])
        else:
            contents = self.sumo.get_monitor(self._get_current_directory_id())
        self._update_path_string()
        if 'children' in contents:
            return contents['children']
        else:
            return False

    def create_folder(self, mode, folder_name, list_widget, params=None):
        try:
            result = self.sumo.create_monitor_folder(self._get_current_directory_id(), folder_name)
            self.current_path_contents = self._get_current_path_contents(mode)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'result': result,
                    'list_widget': list_widget}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                }

    def get(self, mode, item_name, item_id, params=None):
        try:
            content = self.sumo.get_monitor(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': content,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            monitor = self.export_monitor(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': monitor,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def import_item(self, mode, item_name, payload, list_widget, params=None):

        try:
            current_dir_id = self._get_current_directory_id()
            result = self.import_monitor(current_dir_id, payload, self.sumo, include_connection=params['include_connections'])
            return {'status': 'SUCCESS',
                    'result': result,
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

    def put(self, mode, item_name, payload, list_widget, params=None):
        return self.import_item(mode, item_name, payload, list_widget, params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            result = self.sumo.delete_monitor(item_id)
            return {'status': 'SUCCESS',
                    'result': result,
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


class SumoPartitionAdapter(SumoAdapter):

    from modules.shared import import_partition, export_partition

    def __init__(self, creds, side, log_level='info'):
        super(SumoPartitionAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        active_partitions = []
        partitions = self.sumo.get_partitions_sync()
        for partition in partitions:
            if partition['isActive']:
                active_partitions.append(partition)
        return active_partitions

    def get(self, mode, item_name, item_id, params=None):
        try:
            partition = self.sumo.get_partition(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': partition,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            partition = self.export_partition(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': partition,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_partition(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            result = self.sumo.decommission_partition(item_id)
            return {'status': 'SUCCESS',
                    'result': result,
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

class SumoSAMLAdapter(SumoAdapter):

    from modules.shared import import_saml_config, export_saml_config

    def __init__(self, creds, side, log_level='info'):
        super(SumoSAMLAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, mode, params=None):
        saml_configs = self.sumo.get_saml_configs()
        for index, saml_config in enumerate(saml_configs):
            saml_configs[index]['name'] = saml_config['configurationName']
        return saml_configs

    def get(self, mode, item_name, item_id, params=None):
        try:
            saml_config = self.sumo.get_saml_config_by_id(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': saml_config,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, mode, item_name, item_id, params=None):
        try:
            saml_config = self.export_saml_config(item_id, self.sumo)
            saml_config['name'] = saml_config['configurationName']
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': saml_config,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, mode, item_name, payload, list_widget, params=None):
        try:
            result = self.import_saml_config(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
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

    def import_item(self, mode, item_name, payload, list_widget, params=None):
        return self.put(mode, item_name, payload, list_widget, params=params)

    def delete(self, mode, item_name, item_id, list_widget, params=None):
        try:
            result = self.sumo.delete_saml_config(item_id)
            return {'status': 'SUCCESS',
                    'result': result,
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






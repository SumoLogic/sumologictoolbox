from modules.adapter import SumoAdapter


class SumoRuleAdapter(SumoAdapter):
    def __init__(self, creds, side, log_level='info'):
        super(SumoRuleAdapter, self).__init__(creds, side, log_level=log_level)

    def list(self, params=None):
        return self.sumo.get_sources_sync(collector_id)

    def get(self, item_name, item_id, params=None):
        try:
            collector_id = params['collector_id']
            source = self.sumo.get_source(collector_id, item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': source,
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

    def put(self, item_name, payload, list_widget, params=None):
        try:
            collector_id = params['collector_id']
            result = self.sumo.create_source(collector_id, payload)
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

    def import_item(self, item_name, payload, list_widget, params=None):
        return self.put(item_name, payload, list_widget, params=params)

    def delete(self, item_name, item_id, list_widget, params=None):
        try:
            collector_id = params['collector_id']
            result = self.sumo.delete_source(collector_id, item_id)
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

from modules.adapter import SumoAdapter


class SumoCustomInsightAdapter(SumoAdapter):

    from modules.shared import import_custom_insight, export_custom_insight

    def __init__(self, creds, side, mainwindow):
        super(SumoCustomInsightAdapter, self).__init__(creds, side, mainwindow)

    def list(self, params=None):
        return self.sumo.get_custom_insights_sync()

    def get(self, item_name, item_id, params=None):
        try:
            custom_insight = self.sumo.get_custom_insight(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': custom_insight,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, item_name, item_id, params=None):
        try:
            custom_insight = self.export_custom_insight(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': custom_insight,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, item_name, payload, list_widget, params=None):
        try:
            result = self.import_custom_insight(payload, self.sumo)
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
            result = self.sumo.delete_custom_insight(item_id)
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


class SumoRuleAdapter(SumoAdapter):

    from modules.shared import import_rule, export_rule

    def __init__(self, creds, side, mainwindow):
        super(SumoRuleAdapter, self).__init__(creds, side, mainwindow)

    def list(self,  params=None):
        if 'query' in params:
            query = params['query']
        else:
            query = ''
        return self.sumo.get_rules_sync(query)

    def get(self, item_name, item_id, params=None):
        try:
            rule = self.export_rule(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': rule,
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
            result = self.import_rule(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
                    'adapter': self,
                    'params': params,
                    'list_widget': list_widget}
        except Exception as e:
            print(str(e))
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
            result = self.sumo.delete_rule(item_id)
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


class SumoLogMappingAdapter(SumoAdapter):

    from modules.shared import import_log_mapping, export_log_mapping

    def __init__(self, creds, side, mainwindow):
        super(SumoLogMappingAdapter, self).__init__(creds, side, mainwindow)

    def list(self,  params=None):
        if 'query' in params:
            query = params['query']
        else:
            query = ''
        return self.sumo.get_log_mappings_sync(query)

    def get(self, item_name, item_id, params=None):
        try:
            mapping = self.sumo.get_log_mapping(item_id)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': mapping,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def export_item(self, item_name, item_id, params=None):
        try:
            mapping = self.export_log_mapping(item_id, self.sumo)
            return {'status': 'SUCCESS',
                    'adapter': self,
                    'payload': mapping,
                    'params': params}
        except Exception as e:
            _, _, tb = self.sys.exc_info()
            lineno = tb.tb_lineno
            return {'status': 'FAIL',
                    'line_number': lineno,
                    'exception': str(e)
                    }

    def put(self, item_name, payload, list_widget, params=None):
        try:
            result = self.import_log_mapping(payload, self.sumo)
            return {'status': 'SUCCESS',
                    'result': result,
                    'adapter': self,
                    'params': params,
                    'list_widget': list_widget}
        except Exception as e:
            print(str(e))
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
            result = self.sumo.delete_log_mapping(item_id)
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
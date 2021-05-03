from modules.adapter import SumoConnectionAdapter
from modules.tab_base_class import StandardTab

class_name = 'ConnectionsTab'


class ConnectionsTab(StandardTab):

    def __init__(self, mainwindow):
        super(ConnectionsTab, self).__init__(mainwindow)
        self.tab_name = 'Connections'
        self.cred_usage = 'both'

        # customize UI
        self.listWidgetLeft.params = {'extension': '.sumoconnection.json'}
        self.listWidgetRight.params = {'extension': '.sumoconnection.json'}


    def reset_stateful_objects(self, side='both'):
        super(ConnectionsTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoConnectionAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoConnectionAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)



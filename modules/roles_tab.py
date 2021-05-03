from modules.adapter import SumoRoleAdapter
from modules.tab_base_class import StandardTab

class_name = 'RolesTab'


class RolesTab(StandardTab):

    def __init__(self, mainwindow):
        super(RolesTab, self).__init__(mainwindow)
        self.tab_name = 'Roles'
        self.cred_usage = 'both'

        # customize UI
        self.listWidgetLeft.params = {'extension': '.sumorole.json'}
        self.listWidgetRight.params = {'extension': '.sumorole.json'}

    def reset_stateful_objects(self, side='both'):
        super(RolesTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoRoleAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoRoleAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)
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
            if ':' not in self.left_creds['service']:
                self.left_adapter = SumoRoleAdapter(self.left_creds, 'left', self.mainwindow)

        if self.right:
            if ':' not in self.right_creds['service']:
                self.right_adapter = SumoRoleAdapter(self.right_creds, 'right', self.mainwindow)
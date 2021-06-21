from qtpy import QtWidgets
from modules.adapter import SumoUserAdapter
from modules.tab_base_class import StandardTab

class_name = 'UsersTab'


class UsersTab(StandardTab):

    def __init__(self, mainwindow):
        super(UsersTab, self).__init__(mainwindow)
        self.tab_name = 'Users'
        self.cred_usage = 'both'

        # customize UI
        self.checkBoxIncludeRoles = QtWidgets.QCheckBox()
        self.checkBoxIncludeRoles.setChecked(True)
        self.checkBoxIncludeRoles.setText("Include\nRoles")
        self.verticalLayoutCenterButton.insertWidget(3, self.checkBoxIncludeRoles)
        self.checkBoxIncludeRoles.show()
        self.listWidgetLeft.params = {'extension': '.sumouser.json'}
        self.listWidgetRight.params = {'extension': '.sumouser.json'}


        # Connect the UI buttons to methods

        self.pushButtonCopyLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetLeft,
            self.listWidgetRight,
            self.left_adapter,
            self.right_adapter,
            {'replace_source_categories': False, 'include_roles': self.checkBoxIncludeRoles.isChecked()}
        ))

        self.pushButtonCopyRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetRight,
            self.listWidgetLeft,
            self.right_adapter,
            self.left_adapter,
            {'replace_source_categories': False, 'include_roles': self.checkBoxIncludeRoles.isChecked()}
        ))

    def reset_stateful_objects(self, side='both'):
        super(UsersTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoUserAdapter(left_creds, 'left', self.mainwindow)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoUserAdapter(right_creds, 'right', self.mainwindow)




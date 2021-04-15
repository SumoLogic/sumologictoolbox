from qtpy import QtWidgets
import os
from modules.adapter import SumoUserAdapter, SumoRoleAdapter
from modules.tab_base_class import DoubleTab

class_name = 'UsersAndRolesTab'


class UsersAndRolesTab(DoubleTab):

    def __init__(self, mainwindow):
        super(UsersAndRolesTab, self).__init__(mainwindow, top_copy_override=True)
        self.tab_name = 'Users and Roles'
        self.cred_usage = 'both'

        # customize UI
        self.labelTopLeft.setText("Users:")
        self.labelTopRight.setText("Users:")
        self.labelBottomLeft.setText("Roles:")
        self.labelBottomRight.setText("Roles:")
        self.checkBoxIncludeRoles = QtWidgets.QCheckBox()
        self.checkBoxIncludeRoles.setChecked(True)
        self.checkBoxIncludeRoles.setText("Include\nRoles")
        self.verticalLayoutCenterButton.insertWidget(3, self.checkBoxIncludeRoles)
        self.checkBoxIncludeRoles.show()

        # Connect the UI buttons to methods

        self.pushButtonCopyTopLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetTopLeft,
            self.listWidgetTopRight,
            self.left_top_adapter,
            self.right_top_adapter,
            {'replace_source_categories': False, 'include_roles': self.checkBoxIncludeRoles.isChecked()}
        ))

        self.pushButtonCopyTopRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.listWidgetTopRight,
            self.listWidgetTopLeft,
            self.right_top_adapter,
            self.left_top_adapter,
            {'replace_source_categories': False, 'include_roles': self.checkBoxIncludeRoles.isChecked()}
        ))

    def reset_stateful_objects(self, side='both'):
        super(UsersAndRolesTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_top_adapter = SumoUserAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)
                self.left_bottom_adapter = SumoRoleAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_top_adapter = SumoUserAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)
                self.right_bottom_adapter = SumoRoleAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)



from qtpy import QtWidgets, uic
import os
from modules.adapter import SumoScheduledViewAdapter
from modules.tab_base_class import StandardTab

class_name = 'ScheduledViewTab'


class ScheduledViewTab(StandardTab):

    def __init__(self, mainwindow):
        super(ScheduledViewTab, self).__init__(mainwindow, copy_override=True)
        self.tab_name = 'Scheduled Views'
        self.cred_usage = 'both'
        self.useCurrentDate = QtWidgets.QCheckBox()
        self.useCurrentDate.setChecked(True)
        self.useCurrentDate.setText("Use Current\nDate")
        self.verticalLayoutCenterButton.insertWidget(3, self.useCurrentDate)
        self.useCurrentDate.show()

        self.pushButtonCopyLeftToRight.clicked.connect(lambda: self.begin_copy_content(
            self.ListWidgetLeft,
            self.ListWidgetRight,
            self.left_adapter,
            self.right_adapter,
            {'replace_source_categories': False, 'use_current_date': self.useCurrentDate.isChecked()}
        ))

        self.pushButtonCopyRightToLeft.clicked.connect(lambda: self.begin_copy_content(
            self.ListWidgetRight,
            self.ListWidgetLeft,
            self.right_adapter,
            self.left_adapter,
            {'replace_source_categories': False, 'use_current_date': self.useCurrentDate.isChecked()}
        ))


    def reset_stateful_objects(self, side='both'):
        super(ScheduledViewTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoScheduledViewAdapter(left_creds, 'left', log_level=self.mainwindow.log_level)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoScheduledViewAdapter(right_creds, 'right', log_level=self.mainwindow.log_level)

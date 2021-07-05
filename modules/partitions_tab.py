from modules.tab_base_class import StandardTab
from modules.adapter import SumoPartitionAdapter


class_name = 'PartitionsTab'


class PartitionsTab(StandardTab):

    def __init__(self, mainwindow):
        super(PartitionsTab, self).__init__(mainwindow)
        self.tab_name = 'Partitions'
        self.cred_usage = 'both'
        self.listWidgetLeft.params = {'extension': '.sumopartition.json'}
        self.listWidgetRight.params = {'extension': '.sumopartition.json'}

    def reset_stateful_objects(self, side='both'):
        super(PartitionsTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoPartitionAdapter(left_creds, 'left', self.mainwindow)
        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoPartitionAdapter(right_creds, 'right', self.mainwindow)
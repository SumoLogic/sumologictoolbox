from modules.tab_base_class import StandardTab
from modules.csiem_adapter import SumoCustomInsightAdapter


class_name = 'CustomInsightTab'


class CustomInsightTab(StandardTab):

    def __init__(self, mainwindow):
        super(CustomInsightTab, self).__init__(mainwindow)
        self.tab_name = 'Custom Insights'
        self.cred_usage = 'both'
        self.listWidgetLeft.params = {'extension': '.sumocustominsight.json'}
        self.listWidgetRight.params = {'extension': '.sumocustominsight.json'}

    def reset_stateful_objects(self, side='both'):
        super(CustomInsightTab, self).reset_stateful_objects(side=side)
        if self.left:

            if ':' not in self.left_creds['service']:
                self.left_adapter = SumoCustomInsightAdapter(self.left_creds, 'left', self.mainwindow)

        if self.right:

            if ':' not in self.right_creds['service']:
                self.right_adapter = SumoCustomInsightAdapter(self.right_creds, 'right', self.mainwindow)
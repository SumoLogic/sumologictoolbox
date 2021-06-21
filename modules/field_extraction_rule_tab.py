from modules.tab_base_class import StandardTab
from modules.adapter import SumoFERAdapter


class_name = 'FieldExtractionRuleTab'


class FieldExtractionRuleTab(StandardTab):

    def __init__(self, mainwindow):
        super(FieldExtractionRuleTab, self).__init__(mainwindow)
        self.tab_name = 'Field Extraction Rules'
        self.cred_usage = 'both'
        self.listWidgetLeft.params = {'extension': '.sumofer.json'}
        self.listWidgetRight.params = {'extension': '.sumofer.json'}

    def reset_stateful_objects(self, side='both'):
        super(FieldExtractionRuleTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoFERAdapter(left_creds, 'left', self.mainwindow)

        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoFERAdapter(right_creds, 'right', self.mainwindow)






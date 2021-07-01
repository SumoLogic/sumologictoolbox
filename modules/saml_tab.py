from modules.tab_base_class import StandardTab
from modules.adapter import SumoSAMLAdapter

class_name = 'SAMLTab'


class SAMLTab(StandardTab):

    def __init__(self, mainwindow):
        super(SAMLTab, self).__init__(mainwindow)
        self.tab_name = 'SAML'
        self.cred_usage = 'both'
        self.listWidgetLeft.params = {'extension': '.sumosamlconfig.json'}
        self.listWidgetRight.params = {'extension': '.sumosamlconfig.json'}
        self.verticalLayoutCenterButton.removeWidget(self.pushButtonFindReplaceCopyLeftToRight)
        self.verticalLayoutCenterButton.removeWidget(self.pushButtonFindReplaceCopyRightToLeft)

    def reset_stateful_objects(self, side='both'):
        super(SAMLTab, self).reset_stateful_objects(side=side)
        if self.left:
            left_creds = self.mainwindow.get_current_creds('left')
            if ':' not in left_creds['service']:
                self.left_adapter = SumoSAMLAdapter(left_creds, 'left', self.mainwindow)
        if self.right:
            right_creds = self.mainwindow.get_current_creds('right')
            if ':' not in right_creds['service']:
                self.right_adapter = SumoSAMLAdapter(right_creds, 'right', self.mainwindow)

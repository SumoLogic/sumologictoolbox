from modules.tab_base_class import StandardTab
from modules.csiem_adapter import SumoRuleAdapter


class_name = 'RulesTab'


class RulesTab(StandardTab):

    def __init__(self, mainwindow):
        super(RulesTab, self).__init__(mainwindow)
        self.tab_name = 'Rules'
        self.cred_usage = 'both'
        self.listWidgetLeft.params = {'extension': '.sumorule.json',
                                      'query': 'ruleSource:"user"'}
        self.listWidgetRight.params = {'extension': '.sumorule.json',
                                       'query': 'ruleSource:"user"'}

    #     self.QRadioButtonLeftAllRules = QtWidgets.QRadioButton('All')
    #     self.QRadioButtonLeftCustomRules = QtWidgets.QRadioButton('Custom')
    #     self.QRadioButtonLeftCustomRules.setChecked(True)
    #     self.QRadioButtonLeftOTBRules = QtWidgets.QRadioButton('OTB')
    #     self.QRadioButtonLeftProtoRules = QtWidgets.QRadioButton('Proto')
    #     self.QRadioButtonGroupLeft = QtWidgets.QButtonGroup()
    #     self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftAllRules, 0)
    #     self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftCustomRules, 1)
    #     self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftOTBRules, 2)
    #     self.QRadioButtonGroupLeft.addButton(self.QRadioButtonLeftProtoRules, 3)
    #     self.horizontalLayoutTopPushButtonsLeft.insertWidget(3, self.QRadioButtonLeftAllRules)
    #     self.horizontalLayoutTopPushButtonsLeft.insertWidget(4, self.QRadioButtonLeftCustomRules)
    #     self.horizontalLayoutTopPushButtonsLeft.insertWidget(5, self.QRadioButtonLeftOTBRules)
    #     self.horizontalLayoutTopPushButtonsLeft.insertWidget(6, self.QRadioButtonLeftProtoRules)
    #     self.QRadioButtonRightAllRules = QtWidgets.QRadioButton('All')
    #     self.QRadioButtonRightCustomRules = QtWidgets.QRadioButton('Custom')
    #     self.QRadioButtonRightCustomRules.setChecked(True)
    #     self.QRadioButtonRightOTBRules = QtWidgets.QRadioButton('OTB')
    #     self.QRadioButtonRightProtoRules = QtWidgets.QRadioButton('Proto')
    #     self.QRadioButtonGroupRight = QtWidgets.QButtonGroup()
    #     self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightAllRules, 0)
    #     self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightCustomRules, 1)
    #     self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightOTBRules, 2)
    #     self.QRadioButtonGroupRight.addButton(self.QRadioButtonRightProtoRules, 3)
    #     self.horizontalLayoutTopPushButtonsRight.insertWidget(3, self.QRadioButtonRightAllRules)
    #     self.horizontalLayoutTopPushButtonsRight.insertWidget(4, self.QRadioButtonRightCustomRules)
    #     self.horizontalLayoutTopPushButtonsRight.insertWidget(5, self.QRadioButtonRightOTBRules)
    #     self.horizontalLayoutTopPushButtonsRight.insertWidget(6, self.QRadioButtonRightProtoRules)
    #
    #     self.QRadioButtonGroupLeft.buttonClicked.connect(lambda: self.radio_button_changed(
    #         self.listWidgetLeft,
    #         self.left_adapter,
    #         self.QRadioButtonGroupLeft.checkedId(),
    #         self.labelPathLeft
    #     ))
    #
    #     self.QRadioButtonGroupRight.buttonClicked.connect(lambda: self.radio_button_changed(
    #         self.listWidgetRight,
    #         self.right_adapter,
    #         self.QRadioButtonGroupRight.checkedId(),
    #         self.labelPathRight
    #     ))
    #
    # def radio_button_changed(self, list_widget, adapter, button_id, path_label):
    #     if button_id == 0:
    #         list_widget.params['query'] = ''
    #     if button_id == 1:
    #         list_widget.params['query'] = 'ruleSource:"user"'
    #     if button_id == 2:
    #         list_widget.params['query'] = 'ruleSource:"sumo"'
    #     if button_id == 3:
    #         list_widget.params['query'] = 'isPrototype:"true"'
    #     self.update_item_list(list_widget, adapter, path_label=path_label)

    def reset_stateful_objects(self, side='both'):
        super(RulesTab, self).reset_stateful_objects(side=side)

        if self.left:
            # self.QRadioButtonLeftAllRules.setEnabled(False)
            # self.QRadioButtonLeftCustomRules.setEnabled(False)
            # self.QRadioButtonLeftOTBRules.setEnabled(False)
            # self.QRadioButtonLeftProtoRules.setEnabled(False)
            if ':' not in self.left_creds['service']:
                # self.QRadioButtonLeftAllRules.setEnabled(True)
                # self.QRadioButtonLeftCustomRules.setEnabled(True)
                # self.QRadioButtonLeftOTBRules.setEnabled(True)
                # self.QRadioButtonLeftProtoRules.setEnabled(True)
                self.left_adapter = SumoRuleAdapter(self.left_creds, 'left', self.mainwindow)

        if self.right:
            # self.QRadioButtonRightAllRules.setEnabled(False)
            # self.QRadioButtonRightCustomRules.setEnabled(False)
            # self.QRadioButtonRightOTBRules.setEnabled(False)
            # self.QRadioButtonRightProtoRules.setEnabled(False)
            if ':' not in self.right_creds['service']:
                # self.QRadioButtonRightAllRules.setEnabled(True)
                # self.QRadioButtonRightCustomRules.setEnabled(True)
                # self.QRadioButtonRightOTBRules.setEnabled(True)
                # self.QRadioButtonRightProtoRules.setEnabled(True)
                self.right_adapter = SumoRuleAdapter(self.right_creds, 'right', self.mainwindow)

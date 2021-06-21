class_name = 'organizations_tab'

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os
from logzero import logger
import pathlib
from modules.shared import exception_and_error_handling
from modules.filesystem_adapter import FilesystemAdapter
from modules.sumologic_orgs import SumoLogic_Orgs


class CreateOrUpdateOrgDialog(QtWidgets.QDialog):

    def __init__(self, deployments, mainwindow, org_details=None, trials_enabled=False):
        super(CreateOrUpdateOrgDialog, self).__init__()
        self.deployments = deployments
        self.mainwindow = mainwindow
        self.adapter = None
        self.presets = self.mainwindow.list_presets_with_creds()
        self.intValidator = QtGui.QIntValidator()
        self.available_org_licenses = ["Paid"]
        if trials_enabled and not org_details:
            self.available_org_licenses.append("Trial")
        self.org_details = org_details
        org_details_ui = os.path.join(self.mainwindow.basedir, 'data/org_details.ui')
        uic.loadUi(org_details_ui, self)
        self.params = {'extension': '.json'}
        self.setupUi()
        self.load_icons()
        self.preset_changed()

    def setupUi(self):

        self.lineEditContinuousIngest.setValidator(self.intValidator)
        self.lineEditFrequentIngest.setValidator(self.intValidator)
        self.lineEditInfrequentIngest.setValidator(self.intValidator)
        self.lineEditMetricsIngest.setValidator(self.intValidator)
        self.lineEditTracingIngest.setValidator(self.intValidator)
        for deployment in self.deployments:
            self.comboBoxDeployment.addItem(deployment['deploymentId'].strip())
        for license in self.available_org_licenses:
            self.comboBoxPlan.addItem(license.strip())
        self.comboBoxPreset.addItem('FILESYSTEM:')
        for preset in self.presets:
            if ":" in preset['sumoregion'] and preset['sumoregion'] != "MULTI:":
                self.comboBoxPreset.addItem(preset['name'])
        self.configure_org_toggle()

        # Connect UI Element Signals

        self.checkBoxConfigureOrg.stateChanged.connect(self.configure_org_toggle)
        self.pushButtonUpdate.clicked.connect(lambda: self.update_item_list())
        self.pushButtonParentDir.clicked.connect(lambda: self.go_to_parent_dir())
        self.listWidgetConfigs.itemDoubleClicked.connect(lambda item: self.double_clicked_item(item))

        if self.org_details:
            self.comboBoxDeployment.setEnabled(False)
            self.checkBoxCreatePreset.setEnabled(False)
            self.checkBoxConfigureOrg.setEnabled(False)
            self.lineEditOrgName.setText(self.org_details['organizationName'])
            self.lineEditOrgName.setReadOnly(True)
            self.lineEditEmail.setText(self.org_details['email'])
            self.lineEditEmail.setReadOnly(True)
            self.lineEditOwnerFirst.setText(self.org_details['firstName'])
            self.lineEditOwnerFirst.setReadOnly(True)
            self.lineEditOwnerLast.setText(self.org_details['lastName'])
            self.lineEditOwnerLast.setReadOnly(True)
            index = self.comboBoxPlan.findText(self.org_details['subscription']['plan']['planName'],
                                                      QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.comboBoxPlan.setCurrentIndex(index)
            if str(self.comboBoxPlan.currentText()) == "Paid":
                self.comboBoxPlan.setEditable(False)

            self.lineEditContinuousIngest.setText(str(self.org_details['subscription']['baselines']['continuousIngest']))
            self.lineEditFrequentIngest.setText(str(self.org_details['subscription']['baselines']['frequentIngest']))
            self.lineEditInfrequentIngest.setText(str(self.org_details['subscription']['baselines']['infrequentIngest']))
            self.lineEditMetricsIngest.setText(str(self.org_details['subscription']['baselines']['metrics']))
            self.lineEditTracingIngest.setText(str(self.org_details['subscription']['baselines']['tracingIngest']))

        else:
            self.lineEditContinuousIngest.setText('0')
            self.lineEditFrequentIngest.setText('0')
            self.lineEditInfrequentIngest.setText('0')
            self.lineEditMetricsIngest.setText('0')
            self.lineEditTracingIngest.setText('0')

    def load_icons(self):
        self.icons = {}
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(icon_path)
        icon_path = str(pathlib.Path(self.mainwindow.basedir + '/data/json.svg'))
        self.icons['JSON'] = QtGui.QIcon(icon_path)


    def configure_org_toggle(self):
        check_state = self.checkBoxConfigureOrg.checkState()
        self.comboBoxPreset.setEnabled(check_state)
        self.pushButtonUpdate.setEnabled(check_state)
        self.pushButtonParentDir.setEnabled(check_state)

    def preset_changed(self):
        selected_preset_name = self.comboBoxPreset.currentText()
        self.listWidgetConfigs.updated = False
        if selected_preset_name == 'FILESYSTEM:':
            self.adapter = FilesystemAdapter(None, 'left', self.mainwindow)

    def create_list_widget_item(self, item):
        item_name = str(item['name'])
        if ('contentType' in item) and (item['contentType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        elif ('itemType' in item) and (item['itemType'] == 'Folder'):
            list_item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
        else:
            list_item = QtWidgets.QListWidgetItem(self.icons['JSON'], item_name)
        return list_item

    @exception_and_error_handling
    def update_item_list(self):
        contents = self.adapter.list(params=self.params)
        logger.debug(f'[Create Orgs Dialog] Updating item list, got: {contents}')
        self.update_list_widget(contents)

    def update_list_widget(self, payload):
        try:
            self.listWidgetConfigs.clear()
            count = 0
            for item in payload:
                list_item = self.create_list_widget_item(item)
                # attach the details about the item to the entry in listwidget, this makes life much easier
                list_item.details = item
                self.listWidgetConfigs.addItem(list_item)  # populate the list widget in the GUI with no icon (fallthrough)
                count += 1

                self.labelDirectoryPath.setText(self.adapter.get_current_path())
            self.listWidgetConfigs.updated = True
        except Exception as e:
            self.listWidgetConfigs.clear()
            self.listWidgetConfigs.updated = False
            logger.exception(e)
        return

    @exception_and_error_handling
    def double_clicked_item(self, item):
        if self.listWidgetConfigs.updated:
            logger.debug(f"[Create Orgs Dialog] Going Down One Folder {str(item.details['name'])}")
            result = self.adapter.down(item.details['name'], params=self.params)
            if result:
                self.update_item_list()

    @exception_and_error_handling
    def go_to_parent_dir(self):
        if self.listWidgetConfigs.updated:
            result = self.adapter.up(params=self.params)
            if result:
                logger.debug(f"[Create Orgs Dialog] Going Up One folder")
                self.update_item_list()

    def getresults(self):

        results = {'organizationName': str(self.lineEditOrgName.text()),
                   'firstName': str(self.lineEditOwnerFirst.text()),
                   'lastName': str(self.lineEditOwnerLast.text()),
                   'email': str(self.lineEditEmail.text()),
                   'deploymentId': str(self.comboBoxDeployment.currentText()),
                   'baselines': {}
                   }
        results['baselines']['continuousIngest'] = str(self.lineEditContinuousIngest.text())
        results['baselines']['frequentIngest'] = str(self.lineEditFrequentIngest.text())
        results['baselines']['infrequentIngest'] = str(self.lineEditInFrequentIngest.text())
        results['baselines']['metrics'] = self.lineEditMetricsIngest.text()
        results['baselines']['tracingIngest'] = self.lineEditTracingIngest.text()
        if not self.org_details:
            results['create_preset'] = self.createPresetCheckbox.isChecked()
            # results['write_creds_to_file'] = self.writeCredsToFileCheckbox.isChecked()
        return results


class organizations_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(organizations_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Organizations'
        self.cred_usage = 'left'
        collector_ui = os.path.join(self.mainwindow.basedir, 'data/organizations.ui')
        uic.loadUi(collector_ui, self)

        #self.font = "Waree"
        #self.font_size = 12

        # UI Buttons for Organizations API tab

        self.pushButtonGetOrgs.clicked.connect(lambda: self.update_org_list(
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonCreateOrg.clicked.connect(lambda: self.create_org(
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonCancelSubscription.clicked.connect(lambda: self.cancel_subscription(
            self.tableWidgetOrgs.selectedItems(),
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonUpdateSubscription.clicked.connect(lambda: self.update_subscription(
            self.tableWidgetOrgs.selectedItems(),
            self.mainwindow.get_current_creds('left')
        ))

        self.tableWidgetOrgs.itemDoubleClicked.connect(self.row_doubleclicked)

    def row_doubleclicked(self, qtablewidgetitem):
        selected = self.tableWidgetOrgs.selectedItems()
        row_dict = self.create_dict_from_qtable_row(selected)

    def create_dict_from_qtable_row(self, list_of_qtableitems):
        row_dict = {}
        for qtableitem in list_of_qtableitems:
            column_number = qtableitem.column()
            key = self.tableWidgetOrgs.horizontalHeaderItem(column_number).text()
            row_dict[key] = qtableitem.text()
        return row_dict

    def reset_stateful_objects(self, side='both'):

        self.tableWidgetOrgs.clearContents()
        self.tableWidgetOrgs.raw_orgs =[]
        self.tableWidgetOrgs.horizontalHeader().hide()
        self.tableWidgetOrgs.setRowCount(0)
        parent_deployment = str(self.mainwindow.comboBoxRegionLeft.currentText().lower())
        id = str(self.mainwindow.lineEditUserNameLeft.text())
        key = str(self.mainwindow.lineEditPasswordLeft.text())
        self.pushButtonGetOrgs.setEnabled(True)
        self.checkBoxShowActive.setEnabled(True)
        self.pushButtonCreateOrg.setEnabled(True)
        self.pushButtonUpdateSubscription.setEnabled(True)
        self.pushButtonCancelSubscription.setEnabled(True)

        # try:
        #     sumo_mam = SumoLogic_Orgs(id, key, parent_deployment, log_level=self.mainwindow.log_level)
        #     test = sumo_mam.get_deployments()
        #     logger.info('Current org has Multi Org Management enabled.')
        # except Exception as e:
        #     logger.info('Current org does not have Multi Org Management enabled.')
        #     logger.debug('Exception calling Orgs API: {}'.format(str(e)))
        #     self.pushButtonGetOrgs.setEnabled(False)
        #     self.checkBoxShowActive.setEnabled(False)
        #     self.pushButtonCreateOrg.setEnabled(False)
        #     self.pushButtonUpdateSubscription.setEnabled(False)
        #     self.pushButtonCancelSubscription.setEnabled(False)



    def update_org_list(self, creds):
        logger.debug("[Organizations] Getting Updated Org List")
        if self.checkBoxShowActive.isChecked():
            status_filter= "Active"
        else:
            status_filter= "All"
        try:

            sumo_mam = SumoLogic_Orgs(creds['id'],
                                      creds['key'],
                                      str(creds['service']).lower(),
                                      log_level=self.mainwindow.log_level)
            self.tableWidgetOrgs.raw_orgs = sumo_mam.get_orgs_sync(status_filter=status_filter)
            self.update_org_table_widget()

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            self.reset_stateful_objects('left')
            return

    def update_org_table_widget(self):
        logger.debug("[Organizations] Updating Org Table Widget")
        self.tableWidgetOrgs.clear()
        orgs = []
        for raw_org in self.tableWidgetOrgs.raw_orgs:
            org = { 'Org Name': raw_org['organizationName'],
                    'Org ID': raw_org['orgId'],
                    'Owner Email': raw_org['email'],
                    'Credits': raw_org['subscription']['credits'],
                    'License': raw_org['subscription']['plan']['planName'],
                    'Status': raw_org['subscription']['status'],
                    'Continuous Ingest': raw_org['subscription']['baselines']['continuousIngest'],
                    #'Continuous Storage': raw_org['subscription']['baselines']['continuousStorage'],
                    'Frequent Ingest': raw_org['subscription']['baselines']['frequentIngest'],
                    #'Frequent Storage': raw_org['subscription']['baselines']['frequentStorage'],
                    'Infrequent Ingest': raw_org['subscription']['baselines']['infrequentIngest'],
                    #'Infrequent Storage': raw_org['subscription']['baselines']['infrequentStorage'],
                    #'CSE Ingest': raw_org['subscription']['baselines']['cseIngest'],
                    #'CSE Storage': raw_org['subscription']['baselines']['cseStorage'],
                    'Metrics': raw_org['subscription']['baselines']['metrics'],
                    'Tracing': raw_org['subscription']['baselines']['tracingIngest']
                    }
            orgs.append(org)

        if len(orgs) > 0:
            numrows = len(orgs)
            self.tableWidgetOrgs.setRowCount(numrows)
            numcolumns = len(orgs[0])
            self.tableWidgetOrgs.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidgetOrgs.setColumnCount(numcolumns)
            self.tableWidgetOrgs.horizontalHeader().show()
            self.tableWidgetOrgs.setHorizontalHeaderLabels((list(orgs[0].keys())))

            for row in range(numrows):
                for column in range(numcolumns):
                    entry = (list(orgs[row].values())[column])
                    item = QtWidgets.QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, entry)
                    self.tableWidgetOrgs.setItem(row, column, item)

        else:
            self.mainwindow.errorbox('No orgs to display.')

    def create_org(self, creds):
        logger.debug("[Organizations]Creating Org")


        try:
            sumo_mam = SumoLogic_Orgs(creds['id'],
                                      creds['key'],
                                      str(creds['service']).lower(),
                                      log_level=self.mainwindow.log_level)
            deployments = sumo_mam.get_deployments()
            org_info = sumo_mam.get_parent_org_info()
            trials_enabled = org_info['isEligibleForTrialOrgs']



        except Exception as e:
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            logger.exception(e)
            return

        dialog = CreateOrUpdateOrgDialog(deployments, self.mainwindow, trials_enabled=trials_enabled)
        dialog.exec()
        dialog.show()

        if str(dialog.result()) == '1':
            org_details = dialog.getresults()

            try:

                response = sumo_mam.create_org(org_details)
                dialog.close()

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                dialog.close()
                return

            # if org_details['create_preset']:
            #     self.mainwindow.create_preset_non_interactive(response_dict['organizationName'],
            #                                                   response_dict['deploymentId'],
            #                                                   response_dict['accessKey']['id'],
            #                                                   response_dict['accessKey']['key']
            #                                                   )
            # if org_details['write_creds_to_file']:
            #     savepath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save Credentials Location')
            #     file = pathlib.Path(savepath + r'/' + str(response_dict['organizationName'] + r'.user.json'))
            #     try:
            #         with open(str(file), 'w') as filepointer:
            #             json.dump(response_dict, filepointer)
            #
            #     except Exception as e:
            #         self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            #         logger.exception(e)
            #     #  secure the credentials file
            #     os.chmod(file, 600)
            self.update_org_list(creds)

        else:
            return

    def cancel_subscription(self, selected_row, creds):
        if len(selected_row) > 0:
            logger.debug("[Organizations] Canceling Subscription")
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_mam = SumoLogic_Orgs(creds['id'],
                                          creds['key'],
                                          str(creds['service']).lower(),
                                          log_level=self.mainwindow.log_level)
                sumo_mam.deactivate_org(row_dict['Org ID'])

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                return

            self.update_org_list(creds)
            return
        else:
            self.mainwindow.errorbox('Nothing Selected')

    def update_subscription(self, selected_row, creds):
        if len(selected_row) > 0:
            logger.debug("[Organizations] Updating Subscription")
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_mam = SumoLogic_Orgs(creds['id'],
                                          creds['key'],
                                          str(creds['service']).lower(),
                                          log_level=self.mainwindow.log_level)
                org_details = sumo_mam.get_org_details(row_dict['Org ID'])
                deployments = sumo_mam.get_deployments()
                org_info = sumo_mam.get_parent_org_info()
                trials_enabled = org_info['isEligibleForTrialOrgs']

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                return

            dialog = CreateOrUpdateOrgDialog(deployments, self.mainwindow, org_details=org_details, trials_enabled=trials_enabled)
            dialog.exec()
            dialog.show()

            if str(dialog.result()) == '1':
                org_update_details = dialog.getresults()
                try:

                    response = sumo_mam.update_org(org_details['orgId'], org_update_details['baselines'])
                except Exception as e:
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                    logger.exception(e)
                    dialog.close()

                dialog.close()
                self.update_org_list(creds)


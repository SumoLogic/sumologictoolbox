from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import re
from logzero import logger
from modules.sumologic_orgs import SumoLogicOrgs
from modules.sumologic import SumoLogic
from modules.package_editor import PackageEditor
from modules.package_deploy import PackageDeploy
from modules.package import SumoPackage
from modules.filesystem_adapter import FilesystemAdapter
from modules.item_selector import ItemSelector

class_name = 'OrganizationsTab'


class CreateOrUpdateOrgDialog(QtWidgets.QDialog):

    def __init__(self, mainwindow, org_details=None):
        super(CreateOrUpdateOrgDialog, self).__init__()
        self.mainwindow = mainwindow
        self.package = None
        self.is_update = bool(org_details)
        create_org_dialog_ui = os.path.join(self.mainwindow.basedir, 'data/org_details.ui')
        uic.loadUi(create_org_dialog_ui, self)
        self.selector = ItemSelector(self.mainwindow, file_filter='.sumopackage.json')
        self.verticalLayoutSelector.insertWidget(0, self.selector)
        self.intValidator = QtGui.QIntValidator()
        self.available_org_licenses = ["Paid"]

        self.org_details = org_details
        if org_details:
            logger.debug(f'Org Details: {self.org_details}')

        self.parent_org_creds = self.mainwindow.get_current_creds('left')
        self.parent_org_sumo = self.mainwindow.sumo_from_creds(self.parent_org_creds)
        self.sumo_mam = SumoLogicOrgs(self.parent_org_creds['id'],
                                      self.parent_org_creds['key'],
                                      str(self.parent_org_creds['service']).lower(),
                                      log_level=self.mainwindow.log_level)

        self.deployments = []
        try:
            self.deployments = self.sumo_mam.get_deployments()
            self.parent_org_info = self.sumo_mam.get_parent_org_info()
            self.user_info = self.parent_org_sumo.whoami()
            trials_enabled = self.parent_org_info['isEligibleForTrialOrgs']
            if trials_enabled and not org_details:
                self.available_org_licenses.append("Trial")
        except Exception as e:
            logger.info(f'Failed to get org details. {e}')
            self.mainwindow.errorbox("Couldn't get parent org details. Have you selected the credentials for a parent org?")
        self.setupUi()
        self.subdomain_toggle()

    def setupUi(self):
        self.lineEditContinuousIngest.setValidator(self.intValidator)
        self.lineEditFrequentIngest.setValidator(self.intValidator)
        self.lineEditInfrequentIngest.setValidator(self.intValidator)
        self.lineEditMetricsIngest.setValidator(self.intValidator)
        self.lineEditTracingIngest.setValidator(self.intValidator)
        for deployment in self.deployments:
            self.comboBoxDeployment.insertItem(0, deployment['deploymentId'].strip())
        self.comboBoxDeployment.model().sort(0)
        self.comboBoxDeployment.setCurrentIndex(0)
        for license in self.available_org_licenses:
            self.comboBoxPlan.addItem(license.strip())

        # Connect UI Element Signals
        self.comboBoxPlan.currentIndexChanged.connect(self.plan_changed)
        self.checkBoxConfigureOrg.stateChanged.connect(self.configure_org_toggle)
        self.checkBoxSubdomain.stateChanged.connect(self.subdomain_toggle)
        self.checkBoxCreatePreset.stateChanged.connect(self.configure_org_toggle)
        self.pushButtonSelectPackage.clicked.connect(self.load_package)

        # Connect Fields to Validator
        self.lineEditOrgName.textChanged.connect(self.validate_field_contents)
        self.lineEditEmail.textChanged.connect(self.validate_field_contents)
        self.lineEditOwnerFirst.textChanged.connect(self.validate_field_contents)
        self.lineEditOwnerLast.textChanged.connect(self.validate_field_contents)
        self.lineEditContinuousIngest.textChanged.connect(self.validate_field_contents)
        self.lineEditFrequentIngest.textChanged.connect(self.validate_field_contents)
        self.lineEditInfrequentIngest.textChanged.connect(self.validate_field_contents)
        self.lineEditMetricsIngest.textChanged.connect(self.validate_field_contents)
        self.lineEditTracingIngest.textChanged.connect(self.validate_field_contents)
        self.lineEditSubdomain.textChanged.connect(self.validate_field_contents)
        self.lineEditConfigureOrg.textChanged.connect(self.validate_field_contents)

        if self.is_update: # we're updating an existing org

            self.buttonBox.accepted.connect(self.update_org)
            self.comboBoxDeployment.setEnabled(False)
            index = self.comboBoxDeployment.findText(self.org_details['deploymentId'],
                                               QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.comboBoxDeployment.setCurrentIndex(index)
            self.checkBoxCreatePreset.setEnabled(False)
            self.checkBoxConfigureOrg.setEnabled(False)
            self.checkBoxSubdomain.setEnabled(False)
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


        else:  # We're creating a new org
            # Set the default license type to "Trial" for new orgs
            index = self.comboBoxPlan.findText('Trial',
                                               QtCore.Qt.MatchFixedString)
            self.comboBoxPlan.setCurrentIndex(index)
            # Map the OK button to the "create_org" method.
            self.buttonBox.accepted.connect(self.create_org)

        # once everything is populated execute the state change methods to set everything correctly based on values
        self.subdomain_toggle()
        self.plan_changed()

    def plan_changed(self):
        if self.comboBoxPlan.currentText() == 'Trial':
            self.lineEditContinuousIngest.setText('5')
            self.lineEditContinuousIngest.setEnabled(False)
            self.lineEditFrequentIngest.setText('5')
            self.lineEditFrequentIngest.setEnabled(False)
            self.lineEditInfrequentIngest.setText('5')
            self.lineEditInfrequentIngest.setEnabled(False)
            self.lineEditMetricsIngest.setText('5000')
            self.lineEditTracingIngest.setText('0')
        else:
            self.lineEditContinuousIngest.setEnabled(True)
            self.lineEditFrequentIngest.setEnabled(True)
            self.lineEditInfrequentIngest.setEnabled(True)
            if self.is_update:
                # Populate the UI with existing plan values
                self.lineEditContinuousIngest.setText(
                    str(self.org_details['subscription']['baselines']['continuousIngest']))
                self.lineEditFrequentIngest.setText(
                    str(self.org_details['subscription']['baselines']['frequentIngest']))
                self.lineEditInfrequentIngest.setText(
                    str(self.org_details['subscription']['baselines']['infrequentIngest']))
                self.lineEditMetricsIngest.setText(str(self.org_details['subscription']['baselines']['metrics']))
                self.lineEditTracingIngest.setText(str(self.org_details['subscription']['baselines']['tracingIngest']))
            else:
                self.lineEditContinuousIngest.setText('1')
                self.lineEditFrequentIngest.setText('0')
                self.lineEditInfrequentIngest.setText('0')
                self.lineEditMetricsIngest.setText('0')
                self.lineEditTracingIngest.setText('0')

    def configure_org_toggle(self):
        config_org = self.checkBoxConfigureOrg.checkState()
        create_subdomain = self.checkBoxSubdomain.checkState()
        create_preset = self.checkBoxCreatePreset.checkState()
        self.validate_field_contents()
        if config_org:
            self.frameSelector.show()
        else:
            self.frameSelector.hide()
            self.lineEditConfigureOrg.setText('')
            self.resize(588, 564)
            self.adjustSize()
        if config_org or create_subdomain or create_preset:
            self.lineEditEmail.setEnabled(False)
            self.lineEditEmail.setText(self.user_info['email'])
            self.lineEditOwnerFirst.setEnabled(False)
            self.lineEditOwnerFirst.setText(self.user_info['firstName'])
            self.lineEditOwnerLast.setEnabled(False)
            self.lineEditOwnerLast.setText(self.user_info['lastName'])
        else:
            self.lineEditEmail.setEnabled(True)
            self.lineEditEmail.clear()
            self.lineEditOwnerFirst.setEnabled(True)
            self.lineEditOwnerFirst.clear()
            self.lineEditOwnerLast.setEnabled(True)
            self.lineEditOwnerLast.clear()

    def subdomain_toggle(self):
        check_state = self.checkBoxSubdomain.checkState()
        self.lineEditSubdomain.setEnabled(check_state)
        if not check_state:
            self.lineEditSubdomain.clear()
        self.configure_org_toggle()

    def preset_changed(self):
        selected_preset_name = self.comboBoxPreset.currentText()
        if selected_preset_name == 'FILESYSTEM:':
            self.adapter = FilesystemAdapter(None, 'left', self.mainwindow)

    def load_package(self):
        items = self.selector.get_selected_items()
        if len(items) == 1:
            logger.info(f'Loading package: {items[0]}')
            self.package = SumoPackage(package_data=items[0]['item_data'])
            self.lineEditConfigureOrg.setText(items[0]['item_name'])

    def create_org(self):
        logger.debug("[Organizations]Creating Org")
        org_details = self.getresults()

        try:
            create_org_results = self.sumo_mam.create_org(org_details)
        except Exception as e:
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            logger.exception(e)
            return

        child_org_id = create_org_results['orgId']
        logger.debug(f"Created new child org: {child_org_id}")
        config_org = self.checkBoxConfigureOrg.checkState()
        create_subdomain = self.checkBoxSubdomain.checkState()
        create_preset = self.checkBoxCreatePreset.checkState()

        if config_org or create_subdomain or create_preset:

            create_access_key_results = self.sumo_mam.create_access_key('sumotoolbox', child_org_id)
            child_org_name = org_details['organizationName']
            child_access_id = create_access_key_results['id']
            child_access_key = create_access_key_results['key']
            child_deployment = org_details['deploymentId']
            child_sumo = SumoLogic(child_access_id,
                                   child_access_key,
                                   endpoint=self.mainwindow.endpoint_lookup(child_deployment),
                                   log_level=self.mainwindow.log_level)

            if create_preset:
                self.mainwindow.create_preset_non_interactive(child_org_name,
                                                              child_deployment,
                                                              child_access_id,
                                                              child_access_key
                                                              )

            if create_subdomain:
                subdomain = self.lineEditSubdomain.text()
                try:
                    result = child_sumo.create_account_subdomain(subdomain)
                except Exception as e:
                    logger.exception(e)
            if config_org:
                self.package.log_items()
                result = self.package.deploy(child_org_name, child_sumo)
                logger.info(f'Package deploy attempted. Results: {result}')
            self.accept()

    def update_org(self):
        org_details_new = self.getresults()
        org_id = self.org_details['orgId']
        try:
            response = self.sumo_mam.update_org(org_id, org_details_new['baselines'])
            self.accept()
        except Exception as e:
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            logger.exception(e)
            self.reject()

    def validate_field_contents(self):
        email_validation_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        field_contents = self.getresults()
        org_name_is_populated = bool(field_contents['organizationName'])
        account_owner_name_is_populated = bool(field_contents['firstName']) and bool(field_contents['lastName'])
        account_owner_email_is_populated = bool(re.fullmatch(email_validation_regex, field_contents['email']))
        if field_contents['baselines']['continuousIngest']:
            continous_ingest_validated = bool(int(field_contents['baselines']['continuousIngest']) > 0)
        else:
            continous_ingest_validated = False
        if field_contents['baselines']['frequentIngest']:
            frequent_ingest_validated = bool(int(field_contents['baselines']['frequentIngest']) >= 0)
        else:
            frequent_ingest_validated = False
        if field_contents['baselines']['infrequentIngest']:
            infrequent_ingest_validated = bool(int(field_contents['baselines']['infrequentIngest']) >= 0)
        else:
            infrequent_ingest_validated = False
        if field_contents['baselines']['metrics']:
            metrics_ingest_validated = bool(int(field_contents['baselines']['metrics']) >= 0)
        else:
            metrics_ingest_validated = False
        if field_contents['baselines']['tracingIngest']:
            tracing_ingest_validated = bool(int(field_contents['baselines']['tracingIngest']) >= 0)
        else:
            tracing_ingest_validated = False
        if self.checkBoxSubdomain.checkState():
            subdomain_is_populated_or_unchecked = bool(self.lineEditSubdomain.text())
        else:
            subdomain_is_populated_or_unchecked = True
        if self.checkBoxConfigureOrg.checkState():
            configure_org_is_populated_or_unchecked = bool(self.lineEditConfigureOrg.text())
        else:
            configure_org_is_populated_or_unchecked = True

        ready_to_go = bool(org_name_is_populated
                           and account_owner_name_is_populated
                           and account_owner_email_is_populated
                           and continous_ingest_validated
                           and frequent_ingest_validated
                           and infrequent_ingest_validated
                           and metrics_ingest_validated
                           and tracing_ingest_validated
                           and subdomain_is_populated_or_unchecked
                           and configure_org_is_populated_or_unchecked)

        ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        if ready_to_go:
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

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
        results['baselines']['infrequentIngest'] = str(self.lineEditInfrequentIngest.text())
        results['baselines']['metrics'] = self.lineEditMetricsIngest.text()
        results['baselines']['tracingIngest'] = self.lineEditTracingIngest.text()
        if self.comboBoxPlan.currentText() == "Trial":
            results['trialPlanPeriod'] = 45
        return results


class OrganizationsTab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(OrganizationsTab, self).__init__()
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

        self.pushButtonCreateOrg.clicked.connect(self.create_org)

        self.pushButtonCancelSubscription.clicked.connect(lambda: self.cancel_subscription(
            self.tableWidgetOrgs.selectedItems(),
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonUpdateSubscription.clicked.connect(lambda: self.update_subscription(
            self.tableWidgetOrgs.selectedItems(),
            self.mainwindow.get_current_creds('left')
        ))

        self.pushButtonPackageEditor.clicked.connect(self.package_editor)
        self.pushButtonPackageDeploy.clicked.connect(self.package_deploy)
        self.tableWidgetOrgs.itemDoubleClicked.connect(self.row_doubleclicked)

    def package_editor(self):
        dialog = PackageEditor(self.mainwindow)
        dialog.exec()
        dialog.show()
        dialog.close()

    def package_deploy(self):
        dialog = PackageDeploy(self.mainwindow)
        dialog.exec()
        dialog.show()
        dialog.close()

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

    def update_org_list(self, creds):
        logger.debug("[Organizations] Getting Updated Org List")
        if self.checkBoxShowActive.isChecked():
            status_filter= "Active"
        else:
            status_filter= "All"
        try:

            sumo_mam = SumoLogicOrgs(creds['id'],
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

    def cancel_subscription(self, selected_row, creds):
        if len(selected_row) > 0:
            verify = QtWidgets.QMessageBox.question(self,
                                                    'Verify Org Cancellation',
                                                    'Are you sure you want to cancel this org? There is no undo.',
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if verify == QtWidgets.QMessageBox.No:
                return
            logger.debug("[Organizations] Canceling Subscription")
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_mam = SumoLogicOrgs(creds['id'],
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

    def create_org(self):
        parent_org_creds = self.mainwindow.get_current_creds('left')
        if parent_org_creds['id'] and parent_org_creds['key']:
            dialog = CreateOrUpdateOrgDialog(self.mainwindow)
            result = dialog.exec()
            if result:
                self.update_org_list(self.mainwindow.get_current_creds('left'))

    def update_subscription(self, selected_row, creds):
        if len(selected_row) > 0:
            logger.debug("[Organizations] Updating Subscription")
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_mam = SumoLogicOrgs(creds['id'],
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

            dialog = CreateOrUpdateOrgDialog(self.mainwindow, org_details=org_details)
            result = dialog.exec()
            if result:
                self.update_org_list(creds)


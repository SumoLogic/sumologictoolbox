class_name = 'organizations_tab'

from qtpy import QtCore, QtGui, QtWidgets, uic
import os
from logzero import logger
import pathlib
import json
from modules.sumologic_orgs import SumoLogic_Orgs

class CreateOrUpdateOrgDialog(QtWidgets.QDialog):

    def __init__(self, deployments, org_details=None, trials_enabled=False):
        super(CreateOrUpdateOrgDialog, self).__init__()
        self.deployments = deployments
        self.available_org_licenses = ["Paid"]
        if trials_enabled and not org_details:
            self.available_org_licenses.append("Trial")
        self.org_details = org_details
        self.setupUi(self)




    def setupUi(self, Dialog):
        Dialog.setObjectName("CreateOrg")
        self.intValidator = QtGui.QIntValidator()
        self.setWindowTitle('Enter Org Details')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.labelOrgName = QtWidgets.QLabel(Dialog)
        self.labelOrgName.setObjectName("OrgName")
        self.labelOrgName.setText('Organization Name:')
        self.lineEditOrgName = QtWidgets.QLineEdit(Dialog)

        self.layoutOrgName = QtWidgets.QHBoxLayout()
        self.layoutOrgName.addWidget(self.labelOrgName)
        self.layoutOrgName.addWidget(self.lineEditOrgName)

        self.labelEmail = QtWidgets.QLabel(Dialog)
        self.labelEmail.setObjectName("Email")
        self.labelEmail.setText('Registration Email:')
        self.lineEditEmail = QtWidgets.QLineEdit(Dialog)
        self.layoutEmail = QtWidgets.QHBoxLayout()
        self.layoutEmail.addWidget(self.labelEmail)
        self.layoutEmail.addWidget(self.lineEditEmail)

        self.labelFirstName = QtWidgets.QLabel(Dialog)
        self.labelFirstName.setObjectName("FirstName")
        self.labelFirstName.setText('First Name:')
        self.lineEditFirstName = QtWidgets.QLineEdit(Dialog)
        self.layoutFirstName = QtWidgets.QHBoxLayout()
        self.layoutFirstName.addWidget(self.labelFirstName)
        self.layoutFirstName.addWidget(self.lineEditFirstName)

        self.labelLastName = QtWidgets.QLabel(Dialog)
        self.labelLastName.setObjectName("LastName")
        self.labelLastName.setText('Last Name:')
        self.lineEditLastName = QtWidgets.QLineEdit(Dialog)
        self.layoutLastName = QtWidgets.QHBoxLayout()
        self.layoutLastName.addWidget(self.labelLastName)
        self.layoutLastName.addWidget(self.lineEditLastName)

        self.labelDeployment = QtWidgets.QLabel(Dialog)
        self.labelDeployment.setObjectName("Deployment")
        self.labelDeployment.setText('Deployment:')
        self.comboBoxDeployment = QtWidgets.QComboBox(Dialog)
        for deployment in self.deployments:
            self.comboBoxDeployment.addItem(deployment['deploymentId'].strip())
        self.layoutDeployment = QtWidgets.QHBoxLayout()
        self.layoutDeployment.addWidget(self.labelDeployment)
        self.layoutDeployment.addWidget(self.comboBoxDeployment)

        self.labelLicenseType = QtWidgets.QLabel(Dialog)
        self.labelLicenseType.setObjectName("LicenseType")
        self.labelLicenseType.setText('License Type:')
        self.comboBoxLicenseType = QtWidgets.QComboBox(Dialog)
        for license in self.available_org_licenses:
            self.comboBoxLicenseType.addItem(license.strip())
        self.layoutLicenseType = QtWidgets.QHBoxLayout()
        self.layoutLicenseType.addWidget(self.labelLicenseType)
        self.layoutLicenseType.addWidget(self.comboBoxLicenseType)

        self.labelTrialLength = QtWidgets.QLabel(Dialog)
        self.labelTrialLength.setObjectName('TrialLength')
        self.labelTrialLength.setText('Trial Length')
        self.lineEditTrialLength = QtWidgets.QLineEdit(Dialog)

        # Temporarily Disabled for V1 of Orgs. Trial length is fixed at 45 days
        self.lineEditTrialLength.setText('45')
        self.lineEditTrialLength.setReadOnly(True)

        self.layoutTrialLength = QtWidgets.QHBoxLayout()
        self.layoutTrialLength.addWidget(self.labelTrialLength)
        self.layoutTrialLength.addWidget(self.lineEditTrialLength)
        
        if self.org_details:
            self.lineEditOrgName.setText(self.org_details['organizationName'])
            self.lineEditOrgName.setReadOnly(True)
            self.lineEditEmail.setText(self.org_details['email'])
            self.lineEditEmail.setReadOnly(True)
            self.lineEditFirstName.setText(self.org_details['firstName'])
            self.lineEditFirstName.setReadOnly(True)
            self.lineEditLastName.setText(self.org_details['lastName'])
            self.lineEditLastName.setReadOnly(True)
            index = self.comboBoxLicenseType.findText(self.org_details['subscription']['plan']['planName'],
                                                      QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.comboBoxLicenseType.setCurrentIndex(index)
            self.comboBoxLicenseType.setEditable(False)

        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.layoutOrgName)
        self.layout.addLayout(self.layoutEmail)
        self.layout.addLayout(self.layoutFirstName)
        self.layout.addLayout(self.layoutLastName)
        self.layout.addLayout(self.layoutDeployment)
        self.layout.addLayout(self.layoutLicenseType)
        self.layout.addLayout(self.layoutTrialLength)

        # Continuous
        self.labelContinuousTierIngest = QtWidgets.QLabel(Dialog)
        self.labelContinuousTierIngest.setObjectName("ContinuousTierIngest")
        self.labelContinuousTierIngest.setText('Continuous Tier Ingest (0 - 1,000,000 GB/day):')
        self.lineEditContinuousTierIngest = QtWidgets.QLineEdit(Dialog)

        self.lineEditContinuousTierIngest.setValidator(self.intValidator)
        self.layoutContinuousTierIngest = QtWidgets.QHBoxLayout()
        self.layoutContinuousTierIngest.addWidget(self.labelContinuousTierIngest)
        self.layoutContinuousTierIngest.addWidget(self.lineEditContinuousTierIngest)

        self.labelContinuousTierStorage = QtWidgets.QLabel(Dialog)
        self.labelContinuousTierStorage.setObjectName("ContinuousTierStorage")
        self.labelContinuousTierStorage.setText('Continuous Tier Storage (0 - 1,000,000 GB):')
        self.lineEditContinuousTierStorage = QtWidgets.QLineEdit(Dialog)

        self.lineEditContinuousTierStorage.setValidator(self.intValidator)
        self.layoutContinuousTierStorage = QtWidgets.QHBoxLayout()
        self.layoutContinuousTierStorage.addWidget(self.labelContinuousTierStorage)
        self.layoutContinuousTierStorage.addWidget(self.lineEditContinuousTierStorage)
        
        # Frequent
        self.labelFrequentTierIngest = QtWidgets.QLabel(Dialog)
        self.labelFrequentTierIngest.setObjectName("FrequentTierIngest")
        self.labelFrequentTierIngest.setText('Frequent Tier Ingest (0 - 1,000,000 GB/day):')
        self.lineEditFrequentTierIngest = QtWidgets.QLineEdit(Dialog)

        self.lineEditFrequentTierIngest.setValidator(self.intValidator)
        self.layoutFrequentTierIngest = QtWidgets.QHBoxLayout()
        self.layoutFrequentTierIngest.addWidget(self.labelFrequentTierIngest)
        self.layoutFrequentTierIngest.addWidget(self.lineEditFrequentTierIngest)

        self.labelFrequentTierStorage = QtWidgets.QLabel(Dialog)
        self.labelFrequentTierStorage.setObjectName("FrequentTierStorage")
        self.labelFrequentTierStorage.setText('Frequent Tier Storage (0 - 1,000,000 GB):')
        self.lineEditFrequentTierStorage = QtWidgets.QLineEdit(Dialog)

        self.lineEditFrequentTierStorage.setValidator(self.intValidator)
        self.layoutFrequentTierStorage = QtWidgets.QHBoxLayout()
        self.layoutFrequentTierStorage.addWidget(self.labelFrequentTierStorage)
        self.layoutFrequentTierStorage.addWidget(self.lineEditFrequentTierStorage)
        
        # Infrequent
        
        self.labelInFrequentTierIngest = QtWidgets.QLabel(Dialog)
        self.labelInFrequentTierIngest.setObjectName("InFrequentTierIngest")
        self.labelInFrequentTierIngest.setText('InFrequent Tier Ingest (0 - 1,000,000 GB/day):')
        self.lineEditInFrequentTierIngest = QtWidgets.QLineEdit(Dialog)

        self.lineEditInFrequentTierIngest.setValidator(self.intValidator)
        self.layoutInFrequentTierIngest = QtWidgets.QHBoxLayout()
        self.layoutInFrequentTierIngest.addWidget(self.labelInFrequentTierIngest)
        self.layoutInFrequentTierIngest.addWidget(self.lineEditInFrequentTierIngest)

        self.labelInFrequentTierStorage = QtWidgets.QLabel(Dialog)
        self.labelInFrequentTierStorage.setObjectName("InFrequentTierStorage")
        self.labelInFrequentTierStorage.setText('InFrequent Tier Storage (0 - 1,000,000 GB):')
        self.lineEditInFrequentTierStorage = QtWidgets.QLineEdit(Dialog)

        self.lineEditInFrequentTierStorage.setValidator(self.intValidator)
        self.layoutInFrequentTierStorage = QtWidgets.QHBoxLayout()
        self.layoutInFrequentTierStorage.addWidget(self.labelInFrequentTierStorage)
        self.layoutInFrequentTierStorage.addWidget(self.lineEditInFrequentTierStorage)

        # Metrics
        self.labelMetrics = QtWidgets.QLabel(Dialog)
        self.labelMetrics.setObjectName("Metrics")
        self.labelMetrics.setText('Metrics Ingest (0 - 100,000 DPM):')
        self.lineEditMetrics = QtWidgets.QLineEdit(Dialog)

        self.lineEditMetrics.setValidator(self.intValidator)
        self.layoutMetrics = QtWidgets.QHBoxLayout()
        self.layoutMetrics.addWidget(self.labelMetrics)
        self.layoutMetrics.addWidget(self.lineEditMetrics)

        # CSE
        
        self.labelCSEIngest = QtWidgets.QLabel(Dialog)
        self.labelCSEIngest.setObjectName("CSEIngest")
        self.labelCSEIngest.setText('CSE Ingest (0 - 1,000,000 GB/day):')
        self.lineEditCSEIngest = QtWidgets.QLineEdit(Dialog)

        self.lineEditCSEIngest.setValidator(self.intValidator)
        self.layoutCSEIngest = QtWidgets.QHBoxLayout()
        self.layoutCSEIngest.addWidget(self.labelCSEIngest)
        self.layoutCSEIngest.addWidget(self.lineEditCSEIngest)

        self.labelCSEStorage = QtWidgets.QLabel(Dialog)
        self.labelCSEStorage.setObjectName("CSEStorage")
        self.labelCSEStorage.setText('CSE Storage (0 - 1,000,000 GB):')
        self.lineEditCSEStorage = QtWidgets.QLineEdit(Dialog)

        self.lineEditCSEStorage.setValidator(self.intValidator)
        self.layoutCSEStorage = QtWidgets.QHBoxLayout()
        self.layoutCSEStorage.addWidget(self.labelCSEStorage)
        self.layoutCSEStorage.addWidget(self.lineEditCSEStorage)

        if self.org_details:

            self.lineEditContinuousTierIngest.setText(str(self.org_details['subscription']['baselines']['continuousIngest']))
            self.lineEditContinuousTierStorage.setText(str(self.org_details['subscription']['baselines']['continuousStorage']))
            self.lineEditFrequentTierIngest.setText(str(self.org_details['subscription']['baselines']['frequentIngest']))
            self.lineEditFrequentTierStorage.setText(str(self.org_details['subscription']['baselines']['frequentStorage']))
            self.lineEditInFrequentTierIngest.setText(str(self.org_details['subscription']['baselines']['infrequentIngest']))
            self.lineEditInFrequentTierStorage.setText(str(self.org_details['subscription']['baselines']['infrequentStorage']))
            self.lineEditCSEIngest.setText(str(self.org_details['subscription']['baselines']['cseIngest']))
            self.lineEditCSEStorage.setText(str(self.org_details['subscription']['baselines']['cseStorage']))
            self.lineEditMetrics.setText(str(self.org_details['subscription']['baselines']['metrics']))

        else:
            self.lineEditContinuousTierIngest.setText('0')
            self.lineEditContinuousTierStorage.setText('0')
            self.lineEditFrequentTierIngest.setText('0')
            self.lineEditFrequentTierStorage.setText('0')
            self.lineEditInFrequentTierIngest.setText('0')
            self.lineEditInFrequentTierStorage.setText('0')
            self.lineEditMetrics.setText('0')
            self.lineEditCSEIngest.setText('0')
            self.lineEditCSEStorage.setText('0')

            
        self.layout.addLayout(self.layoutContinuousTierIngest)
        self.layout.addLayout(self.layoutContinuousTierStorage)
        self.layout.addLayout(self.layoutFrequentTierIngest)
        self.layout.addLayout(self.layoutFrequentTierStorage)
        self.layout.addLayout(self.layoutInFrequentTierIngest)
        self.layout.addLayout(self.layoutInFrequentTierStorage)
        self.layout.addLayout(self.layoutMetrics)
        self.layout.addLayout(self.layoutCSEIngest)
        self.layout.addLayout(self.layoutCSEStorage)
        self.createPresetCheckbox = QtWidgets.QCheckBox("Create Credential Preset")
        self.createPresetCheckbox.setChecked(True)
        self.writeCredsToFileCheckbox = QtWidgets.QCheckBox("Write Credentials to File")
        self.writeCredsToFileCheckbox.setChecked(False)
        if not self.org_details:
            self.layoutCheckboxes = QtWidgets.QHBoxLayout()
            self.layoutCheckboxes.addWidget(self.createPresetCheckbox)
            self.layoutCheckboxes.addWidget(self.writeCredsToFileCheckbox)
            self.layout.addLayout(self.layoutCheckboxes)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        return
            
    def getresults(self):

        results = {'organizationName': str(self.lineEditOrgName.text()),
                   'firstName': str(self.lineEditFirstName.text()),
                   'lastName': str(self.lineEditLastName.text()),
                   'email': str(self.lineEditEmail.text()),
                   'deploymentId': str(self.comboBoxDeployment.currentText()),
                   'baselines': {}
                   }
        results['baselines']['continuousIngest'] = str(self.lineEditContinuousTierIngest.text())
        results['baselines']['continuousStorage'] = str(self.lineEditContinuousTierStorage.text())
        results['baselines']['frequentIngest'] = str(self.lineEditFrequentTierIngest.text())
        results['baselines']['frequentStorage'] = str(self.lineEditFrequentTierStorage.text())
        results['baselines']['infrequentIngest'] = str(self.lineEditInFrequentTierIngest.text())
        results['baselines']['infrequentStorage'] = str(self.lineEditInFrequentTierStorage.text())
        results['baselines']['metrics'] = self.lineEditMetrics.text()
        results['baselines']['cseIngest'] = str(self.lineEditCSEIngest.text())
        results['baselines']['cseStorage'] = str(self.lineEditCSEStorage.text())
        if self.comboBoxLicenseType.currentText() == 'Trial':
            results['trialPlanPeriod'] = str(self.lineEditTrialLength.text())
        if not self.org_details:
            results['create_preset'] = self.createPresetCheckbox.isChecked()
            results['write_creds_to_file'] = self.writeCredsToFileCheckbox.isChecked()
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
            str(self.mainwindow.comboBoxRegionLeft.currentText().lower()),
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
        ))

        self.pushButtonCreateOrg.clicked.connect(lambda: self.create_org(
            str(self.mainwindow.comboBoxRegionLeft.currentText().lower()),
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
        ))

        self.pushButtonCancelSubscription.clicked.connect(lambda: self.cancel_subscription(
            self.tableWidgetOrgs.selectedItems(),
            str(self.mainwindow.comboBoxRegionLeft.currentText().lower()),
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateSubscription.clicked.connect(lambda: self.update_subscription(
            self.tableWidgetOrgs.selectedItems(),
            str(self.mainwindow.comboBoxRegionLeft.currentText().lower()),
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
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
        try:
            sumo_mam = SumoLogic_Orgs(id, key, parent_deployment, log_level=self.mainwindow.log_level)
            test = sumo_mam.get_deployments()
            logger.info('Current org has Multi Org Management enabled.')
        except Exception as e:
            logger.info('Current org does not have Multi Org Management enabled.')
            logger.debug('Exception calling Orgs API: {}'.format(str(e)))
            self.pushButtonGetOrgs.setEnabled(False)
            self.checkBoxShowActive.setEnabled(False)
            self.pushButtonCreateOrg.setEnabled(False)
            self.pushButtonUpdateSubscription.setEnabled(False)
            self.pushButtonCancelSubscription.setEnabled(False)



    def update_org_list(self, parent_deployment, id, key):
        logger.info("[Organizations] Getting Updated Org List")
        if self.checkBoxShowActive.isChecked():
            status_filter= "Active"
        else:
            status_filter= "All"
        try:

            sumo_mam = SumoLogic_Orgs(id, key, parent_deployment, log_level=self.mainwindow.log_level)
            self.tableWidgetOrgs.raw_orgs = sumo_mam.get_orgs_sync(status_filter=status_filter)
            self.update_org_table_widget()

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            self.reset_stateful_objects('left')
            return

    def update_org_table_widget(self):
        logger.info("[Organizations] Updating Org Table Widget")
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
                    'Continuous Storage': raw_org['subscription']['baselines']['continuousStorage'],
                    'Frequent Ingest': raw_org['subscription']['baselines']['frequentIngest'],
                    'Frequent Storage': raw_org['subscription']['baselines']['frequentStorage'],
                    'Infrequent Ingest': raw_org['subscription']['baselines']['infrequentIngest'],
                    'Infrequent Storage': raw_org['subscription']['baselines']['infrequentStorage'],
                    #'CSE Ingest': raw_org['subscription']['baselines']['cseIngest'],
                    #'CSE Storage': raw_org['subscription']['baselines']['cseStorage'],
                    'Metrics': raw_org['subscription']['baselines']['metrics']
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

    def create_org(self, parent_deployment, id, key):
        logger.info("[Organizations]Creating Org")


        try:
            sumo_orgs = SumoLogic_Orgs(id, key, parent_deployment, log_level=self.mainwindow.log_level)
            deployments = sumo_orgs.get_deployments()
            org_info = sumo_orgs.get_parent_org_info()
            trials_enabled = org_info['isEligibleForTrialOrgs']



        except Exception as e:
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            logger.exception(e)
            return

        dialog = CreateOrUpdateOrgDialog(deployments, trials_enabled=trials_enabled)
        dialog.exec()
        dialog.show()

        if str(dialog.result()) == '1':
            org_details = dialog.getresults()

            try:

                response = sumo_orgs.create_org(org_details)
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
            self.update_org_list(parent_deployment, id, key)

        else:
            return

    def cancel_subscription(self, selected_row, parent_deployment, id, key):
        if len(selected_row) > 0:
            logger.info("[Organizations] Canceling Subscription")
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_orgs = SumoLogic_Orgs(id, key, parent_deployment=parent_deployment)
                sumo_orgs.deactivate_org(row_dict['Org ID'])

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                return

            self.update_org_list(parent_deployment, id, key)
            return
        else:
            self.mainwindow.errorbox('Nothing Selected')

    def update_subscription(self, selected_row, parent_deployment, id, key):
        if len(selected_row) > 0:
            logger.info("[Organizations] Updating Subscription")
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_orgs = SumoLogic_Orgs(id, key, parent_deployment)
                org_details = sumo_orgs.get_org_details(row_dict['Org ID'])
                deployments = sumo_orgs.get_deployments()
                org_info = sumo_orgs.get_parent_org_info()
                trials_enabled = org_info['isEligibleForTrialOrgs']

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                return

            dialog = CreateOrUpdateOrgDialog(deployments, org_details=org_details, trials_enabled=trials_enabled)
            dialog.exec()
            dialog.show()

            if str(dialog.result()) == '1':
                org_update_details = dialog.getresults()
                try:

                    response = sumo_orgs.update_org(org_details['orgId'], org_update_details['baselines'])
                except Exception as e:
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                    logger.exception(e)
                    dialog.close()

                dialog.close()
                self.update_org_list(parent_deployment, id, key)


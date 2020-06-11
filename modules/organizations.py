from qtpy import QtCore, QtGui, QtWidgets, uic
import os
from logzero import logger
import pathlib
import json
from modules.sumologic_mam import SumoLogic_MAM

class CreateOrUpdateOrgDialog(QtWidgets.QDialog):

    def __init__(self, deployments, subscription_type, subscription_update=False, org_details=None):
        super(CreateOrUpdateOrgDialog, self).__init__()
        self.deployments = deployments

        self.product_names = ["SUMO-CF-TRIAL",
                              "SUMO-CF-FREE",
                              "SUMO-CF-PRO",
                              "SUMO-CF-ENT",
                              "SUMO-ESS",
                              "SUMO-ENT-OPS",
                              "SUMO-ENT-SEC",
                              "SUMO-ENT-SUI"
                              ]
        self.subscription_type = subscription_type
        self.subscription_update = subscription_update
        self.org_details = org_details
        self.setupUi(self)




    def setupUi(self, Dialog):
        Dialog.setObjectName("CreateOrg")
        #Dialog.resize(320, 366)
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
            self.comboBoxDeployment.addItem(deployment['deploymentName'].strip())
        self.layoutDeployment = QtWidgets.QHBoxLayout()
        self.layoutDeployment.addWidget(self.labelDeployment)
        self.layoutDeployment.addWidget(self.comboBoxDeployment)

        self.labelProductName = QtWidgets.QLabel(Dialog)
        self.labelProductName.setObjectName("ProductName")
        self.labelProductName.setText('Product Name:')
        self.comboBoxProductName = QtWidgets.QComboBox(Dialog)
        for product_name in self.product_names:
            self.comboBoxProductName.addItem(product_name.strip())
        self.layoutProductName = QtWidgets.QHBoxLayout()
        self.layoutProductName.addWidget(self.labelProductName)
        self.layoutProductName.addWidget(self.comboBoxProductName)

        self.labelStartDate = QtWidgets.QLabel(Dialog)
        self.labelStartDate.setObjectName("StartDate")
        self.labelStartDate.setText('Start Date (UTC):')
        self.DateTimeStartDate = QtWidgets.QDateTimeEdit()
        self.DateTimeStartDate.setCalendarPopup(True)
        self.DateTimeStartDate.setDateTime(QtCore.QDateTime.currentDateTime().toUTC())
        self.layoutStartDate = QtWidgets.QHBoxLayout()
        self.layoutStartDate.addWidget(self.labelStartDate)
        self.layoutStartDate.addWidget(self.DateTimeStartDate)

        if self.subscription_update:
            self.lineEditOrgName.setText(self.org_details['organizationName'])
            self.lineEditOrgName.setReadOnly(True)
            self.lineEditEmail.setText(self.org_details['email'])
            self.lineEditEmail.setReadOnly(True)
            self.lineEditFirstName.setText(self.org_details['firstName'])
            self.lineEditFirstName.setReadOnly(True)
            self.lineEditLastName.setText(self.org_details['lastName'])
            self.lineEditLastName.setReadOnly(True)
            index = self.comboBoxProductName.findText(self.org_details['subscription']['productName'],
                                                      QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.comboBoxProductName.setCurrentIndex(index)
            self.comboBoxProductName.setEditable(False)

        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.layoutOrgName)
        self.layout.addLayout(self.layoutEmail)
        self.layout.addLayout(self.layoutFirstName)
        self.layout.addLayout(self.layoutLastName)
        self.layout.addLayout(self.layoutDeployment)
        self.layout.addLayout(self.layoutProductName)
        self.layout.addLayout(self.layoutStartDate)

        if self.subscription_type == 'CreditsSubscription':

            self.labelCredits = QtWidgets.QLabel(Dialog)
            self.labelCredits.setObjectName("Credits")
            self.labelCredits.setText('Credits (40,000 -  1,000,000):')
            self.lineEditCredits = QtWidgets.QLineEdit(Dialog)

            self.lineEditCredits.setValidator(self.intValidator)
            if self.subscription_update:
                self.lineEditCredits.setText(str(self.org_details['usage']['usageCreditUnits']))  # Best guess as I don't know what org details returns for Credits licenses yet
            else:
                self.lineEditCredits.setText('40000')

            self.layoutCredits = QtWidgets.QHBoxLayout()
            self.layoutCredits.addWidget(self.labelCredits)
            self.layoutCredits.addWidget(self.lineEditCredits)
            self.layout.addLayout(self.layoutCredits)
            self.createPresetCheckbox = QtWidgets.QCheckBox("Create Credential Preset")
            self.createPresetCheckbox.setChecked(True)
            self.writeCredsToFileCheckbox = QtWidgets.QCheckBox("Write Credentials to File")
            self.writeCredsToFileCheckbox.setChecked(False)
            if not self.subscription_update:
                self.layoutCheckboxes = QtWidgets.QHBoxLayout()
                self.layoutCheckboxes.addWidget(self.createPresetCheckbox)
                self.layoutCheckboxes.addWidget(self.writeCredsToFileCheckbox)
                self.layout.addLayout(self.layoutCheckboxes)
            self.layout.addWidget(self.buttonBox)
            self.setLayout(self.layout)

        elif self.subscription_type == 'CloudFlexSubscription':

            self.labelFrequentTier = QtWidgets.QLabel(Dialog)
            self.labelFrequentTier.setObjectName("FrequentTier")
            self.labelFrequentTier.setText('Frequent Tier Ingest (0 - 1,000 GB/day):')
            self.lineEditFrequentTier = QtWidgets.QLineEdit(Dialog)

            self.lineEditFrequentTier.setValidator(self.intValidator)
            self.layoutFrequentTier = QtWidgets.QHBoxLayout()
            self.layoutFrequentTier.addWidget(self.labelFrequentTier)
            self.layoutFrequentTier.addWidget(self.lineEditFrequentTier)

            self.labelContinuousTier = QtWidgets.QLabel(Dialog)
            self.labelContinuousTier.setObjectName("ContinuousTier")
            self.labelContinuousTier.setText('Continuous Tier Ingest (0 - 1,000 GB/day):')
            self.lineEditContinuousTier = QtWidgets.QLineEdit(Dialog)

            self.lineEditContinuousTier.setValidator(self.intValidator)
            self.layoutContinuousTier = QtWidgets.QHBoxLayout()
            self.layoutContinuousTier.addWidget(self.labelContinuousTier)
            self.layoutContinuousTier.addWidget(self.lineEditContinuousTier)

            self.labelMetrics = QtWidgets.QLabel(Dialog)
            self.labelMetrics.setObjectName("Metrics")
            self.labelMetrics.setText('Metrics Ingest (0 - 100,000 DPM):')
            self.lineEditMetrics = QtWidgets.QLineEdit(Dialog)

            self.lineEditMetrics.setValidator(self.intValidator)
            self.layoutMetrics = QtWidgets.QHBoxLayout()
            self.layoutMetrics.addWidget(self.labelMetrics)
            self.layoutMetrics.addWidget(self.lineEditMetrics)

            self.labelTotalStorage = QtWidgets.QLabel(Dialog)
            self.labelTotalStorage.setObjectName("TotalStorage")
            self.labelTotalStorage.setText('Total Storage (30 - 100,000 GB):')
            self.lineEditTotalStorage = QtWidgets.QLineEdit(Dialog)

            self.lineEditTotalStorage.setValidator(self.intValidator)
            self.layoutTotalStorage = QtWidgets.QHBoxLayout()
            self.layoutTotalStorage.addWidget(self.labelTotalStorage)
            self.layoutTotalStorage.addWidget(self.lineEditTotalStorage)

            if self.subscription_update:

                self.lineEditFrequentTier.setText(str(self.org_details['subscription']['ingestBasic']))
                self.lineEditContinuousTier.setText(str(self.org_details['subscription']['ingestEnhanced']))
                self.lineEditMetrics.setText(str(self.org_details['subscription']['metrics']))
                self.lineEditTotalStorage.setText(str(self.org_details['subscription']['totalStorage']))

            else:
                self.lineEditFrequentTier.setText('0')
                self.lineEditContinuousTier.setText('5')
                self.lineEditMetrics.setText('50000')
                self.lineEditTotalStorage.setText('150')


            self.layout.addLayout(self.layoutFrequentTier)
            self.layout.addLayout(self.layoutContinuousTier)
            self.layout.addLayout(self.layoutMetrics)
            self.layout.addLayout(self.layoutTotalStorage)
            self.createPresetCheckbox = QtWidgets.QCheckBox("Create Credential Preset")
            self.createPresetCheckbox.setChecked(True)
            self.writeCredsToFileCheckbox = QtWidgets.QCheckBox("Write Credentials to File")
            self.writeCredsToFileCheckbox.setChecked(False)
            if not self.subscription_update:
                self.layoutCheckboxes = QtWidgets.QHBoxLayout()
                self.layoutCheckboxes.addWidget(self.createPresetCheckbox)
                self.layoutCheckboxes.addWidget(self.writeCredsToFileCheckbox)
                self.layout.addLayout(self.layoutCheckboxes)
            self.layout.addWidget(self.buttonBox)
            self.setLayout(self.layout)

        else:
            logger.info("Unknown Subscription Type.")
            return
            
    def getresults(self):

        results = {'org_name': self.lineEditOrgName.text(),
                   'first_name': self.lineEditFirstName.text(),
                   'last_name': self.lineEditLastName.text(),
                   'email': self.lineEditEmail.text(),
                   'deployment': self.comboBoxDeployment.currentText(),
                   'product_name': self.comboBoxProductName.currentText(),
                   'start_date': str(self.DateTimeStartDate.dateTime().toString(QtCore.Qt.ISODate)),
                   'subscription_type': str(self.subscription_type)
                   }


        if self.subscription_type == 'CreditsSubscription':
            results['credit_units'] = self.lineEditCredits.text()
            if not self.subscription_update:
                results['create_preset'] = self.createPresetCheckbox.isChecked()
                results['write_creds_to_file'] = self.writeCredsToFileCheckbox.isChecked()
            return results

        elif self.subscription_type == 'CloudFlexSubscription':
            results['frequent_tier'] = self.lineEditFrequentTier.text()
            results['continuous_tier'] = self.lineEditContinuousTier.text()
            results['metrics'] = self.lineEditMetrics.text()
            results['total_storage'] = self.lineEditTotalStorage.text()
            if not self.subscription_update:
                results['create_preset'] = self.createPresetCheckbox.isChecked()
                results['write_creds_to_file'] = self.writeCredsToFileCheckbox.isChecked()
            return results


class organizations_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(organizations_tab, self).__init__()
        self.mainwindow = mainwindow

        collector_ui = os.path.join(self.mainwindow.basedir, 'data/organizations.ui')
        uic.loadUi(collector_ui, self)

        #self.font = "Waree"
        #self.font_size = 12

        # UI Buttons for Organizations API tab

        self.pushButtonGetOrgs.clicked.connect(lambda: self.update_org_list(
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
        ))

        self.pushButtonCreateCloudFlexOrg.clicked.connect(lambda: self.create_org(
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            'CloudFlexSubscription'
        ))

        self.pushButtonCreateCreditsOrg.clicked.connect(lambda: self.create_org(
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            'CreditsSubscription'
        ))

        self.pushButtonCancelSubscription.clicked.connect(lambda: self.cancel_subscription(
            self.tableWidgetOrgs.selectedItems(),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))

        self.pushButtonUpdateSubscription.clicked.connect(lambda: self.update_subscription(
            self.tableWidgetOrgs.selectedItems(),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text())
        ))


        self.tableWidgetOrgs.itemDoubleClicked.connect(self.row_doubleclicked)

    def row_doubleclicked(self, qtablewidgetitem):
        selected = self.tableWidgetOrgs.selectedItems()
        row_dict = self.create_dict_from_qtable_row(selected)
        print(row_dict)

    def create_dict_from_qtable_row(self, list_of_qtableitems):
        row_dict = {}
        for qtableitem in list_of_qtableitems:
            column_number = qtableitem.column()
            key = self.tableWidgetOrgs.horizontalHeaderItem(column_number).text()
            row_dict[key] = qtableitem.text()
        return row_dict

    def reset_stateful_objects(self, side='both'):

        self.tableWidgetOrgs.clearContents()
        if self.mainwindow.cred_db_authenticated == True:
            current_org_preset = str(self.mainwindow.comboBoxPresetLeft.currentText())
            authorized_org_preset = self.mainwindow.config['Multi Account Management']['authorized_preset']
            if current_org_preset == authorized_org_preset:
                self.mainwindow.organizations.setEnabled(True)
            else:
                self.mainwindow.organizations.setEnabled(False)
        else:
            self.mainwindow.organizations.setEnabled(True)



    def update_org_list(self, url, id, key):
        logger.info("Getting Updated Org List")
        partner_name = self.mainwindow.config['Multi Account Management']['partner_name']
        orgs = []
        if self.checkBoxShowActive.isChecked():
            status_filter="Active"
        else:
            status_filter="All"
        try:

            sumo_mam = SumoLogic_MAM(id, key)
            deployments = sumo_mam.get_deployments(partner_name)
            for deployment in deployments:
                deployment_orgs=sumo_mam.get_orgs(partner_name, deployment['deploymentName'], status_filter=status_filter)
                orgs = orgs + deployment_orgs

            if self.checkBoxOrgDetails.isChecked():
                for org_index, org in enumerate(orgs, start=0):
                    details_raw = sumo_mam.get_org_details(partner_name, org['deploymentId'], org['orgId'])
                    orgs[org_index] = {'organizationName': details_raw['organizationName'],
                                       'orgId': details_raw['orgId'],
                                       'deploymentId': details_raw['deploymentId'],
                                       'subscriptionType': details_raw['subscription']['subscriptionType'],
                                       'subscriptionStatus': details_raw['subscriptionStatus'],
                                       'productName': details_raw['subscription']['productName'],
                                       'ingestFrequent': "{:.2f}".format(abs(details_raw['subscription']['ingestBasic'])),
                                       'ingestFrequentUsed': "{:.2f}".format(abs(details_raw['usage']['ingestBasicUsed'])),
                                       'ingestContinuous': "{:.2f}".format(abs(details_raw['subscription']['ingestEnhanced'])),
                                       'ingestContinuousUsed': "{:.2f}".format(abs(details_raw['usage']['ingestEnhancedUsed'])),
                                       'metrics': "{:.2f}".format(details_raw['subscription']['metrics']),
                                       'metricsUsed': "{:.2f}".format(abs(details_raw['usage']['metricsUsed'])),
                                       'totalStorage': "{:.2f}".format(abs(details_raw['subscription']['totalStorage'])),
                                       'totalStorageUsed': "{:.2f}".format(abs(details_raw['usage']['totalStorageUsed'])),
                                       'email': details_raw['email'],
                                       'firstName': details_raw['firstName'],
                                       'lastName': details_raw['lastName'],
                                       'serviceUrl': details_raw['serviceUrl'],
                                       'apiUrl': details_raw['apiUrl'],
                                       'startDate': details_raw['subscription']['startDate']
                                       }


        except Exception as e:
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            logger.exception(e)
            return

        self.update_org_table_widget(orgs)

    def update_org_table_widget(self, orgs):
        logger.info("Updating Org Table Widget")
        self.tableWidgetOrgs.clear()

        if len(orgs) > 0:
            numrows = len(orgs)
            self.tableWidgetOrgs.setRowCount(numrows)
            numcolumns = len(orgs[0])
            self.tableWidgetOrgs.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidgetOrgs.setColumnCount(numcolumns)
            self.tableWidgetOrgs.setHorizontalHeaderLabels((list(orgs[0].keys())))

            for  row in range(numrows):
                for column in range(numcolumns):
                    item = (list(orgs[row].values())[column])
                    self.tableWidgetOrgs.setItem(row, column, QtWidgets.QTableWidgetItem(item))

        else:
            self.mainwindow.errorbox('No orgs to display.')

    def create_org(self, url, id, key, subscription_type):
        logger.info("Creating Org")
        partner_name = self.mainwindow.config['Multi Account Management']['partner_name']

        try:
            sumo_mam = SumoLogic_MAM(id, key)
            deployments = sumo_mam.get_deployments(partner_name)


        except Exception as e:
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            logger.exception(e)
            return

        dialog = CreateOrUpdateOrgDialog(deployments, subscription_type)
        dialog.exec()
        dialog.show()

        if str(dialog.result()) == '1':
            org_details = dialog.getresults()

            try:
                if subscription_type == 'CreditsSubscription':
                    response = sumo_mam.create_credits_org(partner_name,
                                        org_details['deployment'],
                                        org_details['email'],
                                        org_details['org_name'],
                                        org_details['first_name'],
                                        org_details['last_name'],
                                        org_details['product_name'],
                                        org_details['start_date'],
                                        org_details['credit_units']
                                        )
                elif subscription_type == 'CloudFlexSubscription':
                    response = sumo_mam.create_cloudflex_org(partner_name,
                                                  org_details['deployment'],
                                                  org_details['email'],
                                                  org_details['org_name'],
                                                  org_details['first_name'],
                                                  org_details['last_name'],
                                                  org_details['product_name'],
                                                  org_details['start_date'],
                                                  org_details['frequent_tier'],
                                                  org_details['continuous_tier'],
                                                  org_details['metrics'],
                                                  org_details['total_storage']
                                                  )
                else:
                    logger.exception('Unknown subscription type.')
                dialog.close()

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                dialog.close()
                return

            response_dict = response.json()
            if org_details['create_preset']:
                self.mainwindow.create_preset_non_interactive(response_dict['organizationName'],
                                                              response_dict['deploymentId'],
                                                              response_dict['accessKey']['id'],
                                                              response_dict['accessKey']['key']
                                                              )
            if org_details['write_creds_to_file']:
                savepath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save Credentials Location')
                file = pathlib.Path(savepath + r'/' + str(response_dict['organizationName'] + r'.user.json'))
                try:
                    with open(str(file), 'w') as filepointer:
                        json.dump(response_dict, filepointer)

                except Exception as e:
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                    logger.exception(e)
                #  secure the credentials file
                os.chmod(file, 600)
            self.update_org_list(url, id, key)

        else:
            return

    def cancel_subscription(self, selected_row, url, id, key):
        if len(selected_row) > 0:
            logger.info("Canceling Subscription")
            partner_name = self.mainwindow.config['Multi Account Management']['partner_name']
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_mam = SumoLogic_MAM(id, key)
                sumo_mam.cancel_subscription(partner_name, row_dict['deploymentId'],row_dict['orgId'])

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                return

            self.update_org_list(url, id, key)
            return
        else:
            self.mainwindow.errorbox('Nothing Selected')

    def update_subscription(self, selected_row, url, id, key):
        if len(selected_row) > 0:
            logger.info("Updating Subscription")
            partner_name = self.mainwindow.config['Multi Account Management']['partner_name']
            row_dict = self.create_dict_from_qtable_row(selected_row)
            try:
                sumo_mam = SumoLogic_MAM(id, key)
                org_details = sumo_mam.get_org_details(partner_name, row_dict['deploymentId'],row_dict['orgId'])

            except Exception as e:
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                logger.exception(e)
                return

            dialog = CreateOrUpdateOrgDialog([{'deploymentName': org_details['deploymentId']}],
                                             org_details['subscription']['subscriptionType'],
                                             subscription_update=True,
                                             org_details=org_details
                                             )
            dialog.exec()
            dialog.show()

            if str(dialog.result()) == '1':
                org_update_details = dialog.getresults()
                subscription_type = org_update_details['subscription_type']
                try:
                    if subscription_type == 'CreditsSubscription':
                        response = sumo_mam.create_credits_org(partner_name,
                                                               org_update_details['deployment'],
                                                               org_details['orgId'],
                                                               org_details['subscription']['subscriptionType'],
                                                               org_update_details['first_name'],
                                                               org_update_details['last_name'],
                                                               org_update_details['product_name'],
                                                               org_update_details['start_date'],
                                                               org_update_details['credit_units']
                                                               )
                    elif subscription_type == 'CloudFlexSubscription':
                        response = sumo_mam.update_cloudflex_org(partner_name,
                                            org_update_details['deployment'],
                                            org_details['orgId'],
                                            org_details['subscription']['subscriptionType'],
                                            org_update_details['product_name'],
                                            org_update_details['start_date'],
                                            org_update_details['frequent_tier'],
                                            org_update_details['continuous_tier'],
                                            org_update_details['metrics'],
                                            org_update_details['total_storage']
                                            )
                except Exception as e:
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                    logger.exception(e)
                    dialog.close()

                dialog.close()
                self.update_org_list(url, id, key)


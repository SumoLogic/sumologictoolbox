class_name = 'content_tab'

from qtpy import QtCore, QtGui, QtWidgets, uic
import os
import sys
import re
import pathlib
import json
import copy
from logzero import logger
from modules.sumologic import SumoLogic
from modules.shared import ShowTextDialog, find_replace_specific_key_and_value, content_item_to_path


class findReplaceCopyDialog(QtWidgets.QDialog):

    def __init__(self, fromcategories, tocategories, parent=None):
        super(findReplaceCopyDialog, self).__init__(parent)
        self.objectlist = []
        self.setupUi(self, fromcategories, tocategories)

    def setupUi(self, Dialog, fromcategories, tocategories):

        # setup static elements
        Dialog.setObjectName("FindReplaceCopy")
        Dialog.setMinimumWidth(700)
        Dialog.setWindowTitle('Dynamically Replace Source Category Strings')

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # set up the list of destination categories to populate into the comboboxes
        itemmodel = QtGui.QStandardItemModel()
        for tocategory in tocategories:
            text_item = QtGui.QStandardItem(str(tocategory))
            itemmodel.appendRow(text_item)
        itemmodel.sort(0)



        self.layoutSelections = QtWidgets.QGridLayout()
        self.labelReplace = QtWidgets.QLabel()
        self.labelReplace.setText("Replace")
        self.layoutSelections.addWidget(self.labelReplace, 0, 0)
        self.labelOriginal = QtWidgets.QLabel()
        self.labelOriginal.setText("Original Source Category")
        self.layoutSelections.addWidget(self.labelOriginal, 0, 1)
        self.labelReplaceWith = QtWidgets.QLabel()
        self.labelReplaceWith.setText("With:")
        self.layoutSelections.addWidget(self.labelReplaceWith, 0, 2)

        # Create 1 set of (checkbox, label, combobox per fromcategory
        for index, fromcategory in enumerate(fromcategories):

            objectdict = {'checkbox': None, 'label': None, 'combobox': None}

            objectdict['checkbox'] = QtWidgets.QCheckBox()
            objectdict['checkbox'].setObjectName("checkBox" + str(index))
            objectdict['checkbox'].setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.layoutSelections.addWidget(objectdict['checkbox'], index + 1, 0)
            objectdict['label']= QtWidgets.QLabel()
            objectdict['label'].setObjectName("comboBox" + str(index))
            objectdict['label'].setText(fromcategory)
            objectdict['label'].setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.layoutSelections.addWidget(objectdict['label'], index + 1, 1)
            objectdict['combobox'] = QtWidgets.QComboBox()
            objectdict['combobox'].setObjectName("comboBox" + str(index))
            objectdict['combobox'].setModel(itemmodel)
            objectdict['combobox'].setEditable(True)
            objectdict['combobox'].setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            self.layoutSelections.addWidget(objectdict['combobox'], index + 1, 2)
            self.objectlist.append(objectdict)

        self.groupBox = QtWidgets.QGroupBox()
        self.groupBox.setLayout(self.layoutSelections)

        # Creata a vertical scroll area with a grid layout inside with label headers

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidget(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        #self.scrollArea.setFixedHeight(400)
        self.scrollArea.setMaximumHeight(500)
        self.scrollArea.setMinimumWidth(700)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def getresults(self):
        results = []
        for object in self.objectlist:
            if str(object['checkbox'].checkState()) == '2':
                objectdata = { 'from': str(object['label'].text()), 'to': str(object['combobox'].currentText())}
                results.append(objectdata)
        return results

class content_tab(QtWidgets.QWidget):

    def __init__(self, mainwindow):

        super(content_tab, self).__init__()
        self.mainwindow = mainwindow
        self.tab_name = 'Content'
        self.cred_usage = 'both'

        content_widget_ui = os.path.join(self.mainwindow.basedir, 'data/content.ui')
        uic.loadUi(content_widget_ui, self)

        # Load icons used in the listviews
        self.load_icons()
        self.reset_stateful_objects()
        # set up some variables to identify the content list widgets. This is read by some of the content methods
        # to determine proper course of action
        self.contentListWidgetLeft.side = 'left'
        self.contentListWidgetRight.side = 'right'

        # Content Pane Signals
        # Left Side
        self.pushButtonUpdateContentLeft.clicked.connect(lambda: self.updatecontentlist(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.contentListWidgetLeft.itemDoubleClicked.connect(lambda item: self.doubleclickedcontentlist(
            item,
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonParentDirContentLeft.clicked.connect(lambda: self.parentdircontentlist(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.buttonGroupContentLeft.buttonClicked.connect(lambda: self.contentradiobuttonchanged(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft,
            self.pushButtonContentDeleteLeft
        ))

        self.pushButtonContentNewFolderLeft.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentDeleteLeft.clicked.connect(lambda: self.delete_content(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentCopyLeftToRight.clicked.connect(lambda: self.copycontent(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentFindReplaceCopyLeftToRight.clicked.connect(lambda: self.findreplacecopycontent(
            self.contentListWidgetLeft,
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        # Right Side
        self.pushButtonUpdateContentRight.clicked.connect(lambda: self.updatecontentlist(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.contentListWidgetRight.itemDoubleClicked.connect(lambda item: self.doubleclickedcontentlist(
            item,
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonParentDirContentRight.clicked.connect(lambda: self.parentdircontentlist(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.buttonGroupContentRight.buttonClicked.connect(lambda: self.contentradiobuttonchanged(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight,
            self.pushButtonContentDeleteRight
        ))

        self.pushButtonContentNewFolderRight.clicked.connect(lambda: self.create_folder(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentDeleteRight.clicked.connect(lambda: self.delete_content(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentCopyRightToLeft.clicked.connect(lambda: self.copycontent(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentRight.checkedId(),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentFindReplaceCopyRightToLeft.clicked.connect(lambda: self.findreplacecopycontent(
            self.contentListWidgetRight,
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentRight.checkedId(),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentBackupLeft.clicked.connect(lambda: self.backupcontent(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId()
        ))

        self.pushButtonContentBackupRight.clicked.connect(lambda: self.backupcontent(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId()
        ))

        self.pushButtonContentRestoreLeft.clicked.connect(lambda: self.restorecontent(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId(),
            self.contentCurrentDirLabelLeft
        ))

        self.pushButtonContentRestoreRight.clicked.connect(lambda: self.restorecontent(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId(),
            self.contentCurrentDirLabelRight
        ))

        self.pushButtonContentViewJSONLeft.clicked.connect(lambda: self.view_json(
            self.contentListWidgetLeft,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionLeft.currentText())],
            str(self.mainwindow.lineEditUserNameLeft.text()),
            str(self.mainwindow.lineEditPasswordLeft.text()),
            self.buttonGroupContentLeft.checkedId()
        ))

        self.pushButtonContentViewJSONRight.clicked.connect(lambda: self.view_json(
            self.contentListWidgetRight,
            self.mainwindow.loadedapiurls[str(self.mainwindow.comboBoxRegionRight.currentText())],
            str(self.mainwindow.lineEditUserNameRight.text()),
            str(self.mainwindow.lineEditPasswordRight.text()),
            self.buttonGroupContentRight.checkedId()
        ))

    def reset_stateful_objects(self, side='both'):

        if side == 'both':
            left = True
            right = True
        if side == 'left':
            left = True
            right = False
        if side == 'right':
            left = False
            right = True

        if left:
            self.contentListWidgetLeft.clear()
            self.contentListWidgetLeft.currentcontent = {}
            self.contentListWidgetLeft.currentdirlist = []
            self.contentListWidgetLeft.updated = False


        if right:
            self.contentListWidgetRight.clear()
            self.contentListWidgetRight.currentcontent = {}
            self.contentListWidgetRight.currentdirlist = []
            self.contentListWidgetRight.updated = False

    def load_icons(self):

        self.icons = {}
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/folder.svg'))
        self.icons['Folder'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/dashboard.svg'))
        self.icons['Dashboard'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/logsearch.svg'))
        self.icons['Search'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/scheduledsearch.svg'))
        self.icons['scheduledsearch'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/correlationrules.svg'))
        self.icons['Rule'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/informationmodel.svg'))
        self.icons['Model'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/lookuptable.svg'))
        self.icons['Lookups'] = QtGui.QIcon(iconpath)
        iconpath = str(pathlib.Path(self.mainwindow.basedir + '/data/parser.svg'))
        self.icons['Parser'] = QtGui.QIcon(iconpath)
        return

    # Thanks Stackoverflow. Yoink!
    def find_keys(self, obj, key):
        """Pull all values of specified key from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        results = extract(obj, arr, key)
        return results



    def recurse_replace_query_strings(self, query_string_replacement_list, exported_json):

        if exported_json['type'] == "SavedSearchWithScheduleSyncDefinition":
            for query_string_replacement in query_string_replacement_list:
                if query_string_replacement['from'] in exported_json['search']['queryText']:
                    exported_json['search']['queryText'] = exported_json['search']['queryText'].replace(
                        str(query_string_replacement['from']),
                        str(query_string_replacement['to']))
                    break
            return exported_json

        elif exported_json['type'] == "DashboardSyncDefinition":
            for panelnum, panel in enumerate(exported_json['panels'], start=0):

                if panel['viewerType'] == "metrics":  # there can be multiple query strings so we have an extra loop here
                    for querynum, metrics_query in enumerate(panel['metricsQueries'], start=0):
                        for query_string_replacement in query_string_replacement_list:
                            if query_string_replacement['from'] in metrics_query['query']:
                                metrics_query['query'] = metrics_query['query'].replace(
                                    str(query_string_replacement['from']),
                                    str(query_string_replacement['to']))
                                break
                        panel['metricsQueries'][querynum] = metrics_query

                else:  # if panel is a log panel
                    for query_string_replacement in query_string_replacement_list:
                        if query_string_replacement['from'] in panel['queryString']:
                            panel['queryString'] = panel['queryString'].replace(
                                str(query_string_replacement['from']),
                                str(query_string_replacement['to']))
                            break
                exported_json['panels'][panelnum] = panel
            return exported_json

        elif exported_json['type'] == "DashboardV2SyncDefinition":  # if it's a new style dashboard
            for panelnum, panel in enumerate(exported_json['panels'], start=0):
                for querynum, query in enumerate(panel['queries']):
                    for query_string_replacement in query_string_replacement_list:
                        if query_string_replacement['from'] in query['queryString']:
                            query['queryString'] = query['queryString'].replace(
                                str(query_string_replacement['from']),
                                str(query_string_replacement['to']))
                            break
                    panel['queries'][querynum] = query
                exported_json['panels'][panelnum] = panel
            return exported_json


        elif exported_json['type'] == "FolderSyncDefinition":

            children = []
            for object in exported_json['children']:
                children.append(self.recurse_replace_query_strings(query_string_replacement_list, object))
            exported_json['children'] = children
            return exported_json

    # Start methods for Content Tab

    def findreplacecopycontent(self, ContentListWidgetFrom, ContentListWidgetTo, fromurl, fromid, fromkey, tourl,
                               toid, tokey,
                               fromradioselected, toradioselected, todirectorylabel):

        logger.info("[Content] Copying Content")

        selecteditemsfrom = ContentListWidgetFrom.selectedItems()
        if toradioselected == -3 or toradioselected == -4:  # Admin or Global folders selected
            toadminmode = True
        else:
            toadminmode = False
        if fromradioselected == -3 or fromradioselected == -4:  # Admin or Global folders selected
            fromadminmode = True
        else:
            fromadminmode = False
        if len(selecteditemsfrom) > 0:  # make sure something was selected
            try:
                exportsuccessful = False
                fromsumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                tosumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)

                contents = []
                for selecteditem in selecteditemsfrom:
                            item_id = selecteditem.details['id']
                            contents.append(fromsumo.export_content_job_sync(item_id, adminmode=fromadminmode))
                            exportsuccessful = True
            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong with the Source:\n\n' + str(e))
                return
            if exportsuccessful:
                categoriesfrom = []
                for content in contents:
                    query_list = self.find_keys(content, 'queryText')
                    query_list = query_list + self.find_keys(content, 'query')
                    query_list = query_list + self.find_keys(content, 'queryString')
                    for query in query_list:
                        categoriesfrom = categoriesfrom + re.findall(r'_sourceCategory\s*=\s*\\?\"?([^\s^"^)]*)\"?',
                                                                      query)
                #    contentstring = json.dumps(content)
                #    categoriesfrom = categoriesfrom + re.findall(r'\"_sourceCategory\s*=\s*\\?\"?([^\s\\|]*)',
                #                                                 contentstring)
                uniquecategoriesfrom = list(set(categoriesfrom))  # dedupe the list
                try:
                    fromtime = str(QtCore.QDateTime.currentDateTime().addSecs(-3600).toString(QtCore.Qt.ISODate))
                    totime = str(QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))

                    # We query the destination org to get a sample of active source categories
                    query = r'* | count by _sourceCategory | fields _sourceCategory'
                    searchresults = tosumo.search_job_records_sync(query, fromTime=fromtime, toTime=totime,
                                                                   timeZone='UTC', byReceiptTime='false')
                    categoriesto = []
                    for record in searchresults:
                        categoriesto.append(record['map']['_sourcecategory'])
                    uniquecategoriesto = list(set(categoriesto))

                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong with the Destination:\n\n' + str(e))
                    return
                dialog = findReplaceCopyDialog(uniquecategoriesfrom, uniquecategoriesto)
                dialog.exec()
                dialog.show()
                if str(dialog.result()) == '1':
                    replacelist = dialog.getresults()
                    logger.info(replacelist)
                    dialog.close()
                    if len(replacelist) > 0:
                        newcontents = []
                        for content in contents:
                            newcontents.append(self.recurse_replace_query_strings(replacelist, content))
                            # for entry in replacelist:
                            #     contentstring = json.dumps(content)
                            #     contentstring = contentstring.replace(str(entry['from']), str(entry['to']))
                            #     logger.info(contentstring)
                            #     newcontents.append(json.loads(contentstring))
                    else:
                        newcontents = contents

                    try:
                        tofolderid = ContentListWidgetTo.currentcontent['id']
                        for newcontent in newcontents:
                            status = tosumo.import_content_job_sync(tofolderid, newcontent, adminmode=toadminmode)

                        self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected,
                                               todirectorylabel)
                        return
                    except Exception as e:

                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong with the Destination:\n\n' + str(e))
                        return
                else:
                    dialog.close()
                    return



        else:
            self.mainwindow.errorbox('You have not made any selections.')
            return
        return

    def copycontent(self, ContentListWidgetFrom, ContentListWidgetTo, fromurl, fromid, fromkey, tourl, toid, tokey,
                    fromradioselected, toradioselected, todirectorylabel):
        logger.info("[Content] Copying Content")
        if toradioselected == -3 or toradioselected == -4:  # Admin or Global folders selected
            toadminmode = True
        else:
            toadminmode = False
        if fromradioselected == -3 or fromradioselected == -4:  # Admin or Global folders selected
            fromadminmode = True
        else:
            fromadminmode = False

        try:
            selecteditems = ContentListWidgetFrom.selectedItems()
            if len(selecteditems) > 0:  # make sure something was selected
                from_sumo = SumoLogic(fromid, fromkey, endpoint=fromurl, log_level=self.mainwindow.log_level)
                to_sumo = SumoLogic(toid, tokey, endpoint=tourl, log_level=self.mainwindow.log_level)
                current_source_dir = ContentListWidgetFrom.currentdirlist[-1]
                from_folder_id = ContentListWidgetFrom.currentcontent['id']

                current_dest_dir = ContentListWidgetTo.currentdirlist[-1]
                to_folder_id = ContentListWidgetTo.currentcontent['id']
                
                fromPaths = []

                for selecteditem in selecteditems:
                    item_id = selecteditem.details['id']
                    item_type = selecteditem.details['itemType']

                    if item_type == 'Folder':
                        from_content_item = from_sumo.get_folder(item_id, adminmode=fromadminmode)
                    else:
                        from_content_item = selecteditem.details

                    fromPaths.append(content_item_to_path(from_sumo, from_content_item, adminmode=fromadminmode))
                    print(fromPaths)

                    content = from_sumo.export_content_job_sync(item_id, adminmode=fromadminmode)
                    content = self.update_content_webhookid(from_sumo, to_sumo, content)
                    status = to_sumo.import_content_job_sync(to_folder_id, content, adminmode=toadminmode)

                toFolder = to_sumo.get_folder(to_folder_id, adminmode=toadminmode)
                toPaths = content_item_to_path(to_sumo, toFolder, adminmode=toadminmode)
                print(toPaths)
                #self.sync_copied_contents_permissions(from_sumo, to_sumo, from_folder_id, to_folder_id, fromPaths, toPaths, fromAdminMode=fromadminmode, toAdminMode=toadminmode)
                #self.updatecontentlist(ContentListWidgetTo, tourl, toid, tokey, toradioselected, todirectorylabel)
                return

            else:
                self.mainwindow.errorbox('You have not made any selections.')
                return

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
        return

    def get_source_to_dest_meta_ids(self, fromsumo, tosumo):
        logger.info('[Content] Getting Source To Destination Meta IDs')
        source_to_dest_ids = {}

        fromUsers = fromsumo.get_users_sync()
        toUsers = tosumo.get_users_sync()
        fromRoles = fromsumo.get_roles_sync()
        toRoles = tosumo.get_roles_sync()
        source_org_id = fromsumo.get_org_id()
        dest_org_id = tosumo.get_org_id()
        source_user_id_to_email = {user['id']: user['email'] for user in fromUsers}
        des_user_email_to_id = {user['email']: user['id'] for user in toUsers}

        source_user_id_to_dest_user_id = {}
        for userId, email in source_user_id_to_email.items():
            if email in des_user_email_to_id.keys():
                source_user_id_to_dest_user_id[userId] = des_user_email_to_id[email]
            else:
                #destUserId = CopyUsersAndAssignedRoles(userId, fromsumo, tosumo)['id']
                #source_user_id_to_dest_user_id[userId] = destUserId
                logger.info("Failed to find user with e-mail: {} on the destination and it was copied over along with any assigned roles".format(email))

        source_role_id_to_name = {role['id']:role['name'] for role in fromRoles}
        des_role_name_to_id = {role['name']:role['id'] for role in toRoles}

        source_role_id_to_dest_role_id = {}
        for roleId, roleName in source_role_id_to_name.items():
            if roleName in des_role_name_to_id.keys():
                source_role_id_to_dest_role_id[roleId] = des_role_name_to_id[roleName]
            else:
                missingRole = fromsumo.get_role(roleId)
                destUsersAssignedTorle = [source_user_id_to_dest_user_id[sourceUserId] for sourceUserId in missingRole['users'] if sourceUserId in source_user_id_to_dest_user_id.keys()]
                missingRole['users'] = destUsersAssignedTorle
                tosumo.create_role(missingRole)
                logger.info("Failed to find role with name: {} on the destination and it was copied over and assigned existing destination users to it".format(roleName))
        
        source_to_dest_ids = {'org': {source_org_id:dest_org_id}, 'user': source_user_id_to_dest_user_id, 'role': source_role_id_to_dest_role_id}
        return source_to_dest_ids

    def sync_copied_contents_permissions(self, fromsumo, tosumo, fromFolderId, toFolderId, fromPaths, toPaths, fromAdminMode=False, toAdminMode=False):
        logger.info('Syncing Copied Contents Permissions')

        fromBasePath = fromsumo.get_item_path(fromFolderId, adminmode=fromAdminMode)['path']
        toBasePath = tosumo.get_item_path(toFolderId, adminmode=toAdminMode)['path']
        source_to_dest_ids = self.get_source_to_dest_meta_ids(fromsumo, tosumo)

        source_ids_to_paths = {}
        for fromPerm in fromPaths:
            fromId= fromPerm['id']
            fromPath = fromPerm['path'] if fromPerm['path'] != '' else fromPerm['name']
            fromPath = str(fromPath).replace(fromBasePath, '')
            source_ids_to_paths[fromId] = fromPath

        dest_paths_to_ids = {}
        for destPerm in toPaths:
            toPath = destPerm['path'] if destPerm['path'] else destPerm['name']
            toPath = str(toPath).replace(toBasePath, '')
            dest_paths_to_ids[toPath] = destPerm['id']

        destPermissions = {}
        requestResults = {}
        for sourceContentId, sourceContentPath in source_ids_to_paths.items():
            if sourceContentPath in dest_paths_to_ids.keys():
                destContentId = dest_paths_to_ids[sourceContentPath]
                sourcePermissions = fromsumo.get_permissions(sourceContentId, explicit_only=True,adminmode=fromAdminMode)['explicitPermissions']

                currentDestPermissions = []
                for permission in sourcePermissions:
                    currentDestPermission = copy.deepcopy(permission)
                    currentSourceType = permission['sourceType']
                    currentSourceId = permission['sourceId']
                    currentDestPermission['sourceId'] = source_to_dest_ids[currentSourceType][currentSourceId]
                    currentDestPermission['contentId'] = destContentId
                    currentDestPermissions.append(currentDestPermission)

                permissionsBody = {'contentPermissionAssignments':[], 'notifyRecipients':False, 'notificationMessage':''}
                permissionsBody['contentPermissionAssignments'] = currentDestPermissions
                requestResult = tosumo.add_permissions(destContentId, permissionsBody, adminmode=toAdminMode)
                requestResults[sourceContentPath] = requestResult
            else:
                logger.warn("Failed to import content {} from {} to {}, Source content id:{}".format(sourceContentPath,fromBasePath, toBasePath, sourceContentId))
        
        return requestResults

    def update_content_webhookid(self, fromsumo, tosumo, content):
        source_connections = fromsumo.get_connections_sync()
        dest_connections = tosumo.get_connections_sync()

        source_connections_dict = {connection['id']: connection['name'] for connection in source_connections}
        print(source_connections)
        dest_connections_dict = {connection['name']: connection['id'] for connection in dest_connections}
        source_to_dest_dict = {id: dest_connections_dict[name] for id, name in source_connections_dict.items() if name in dest_connections_dict}

        for source_connection_id in source_connections_dict.keys():
            if source_connection_id not in source_to_dest_dict:
                source_connection = fromsumo.get_connection(source_connection_id, 'WebhookConnection')
                source_connection['type'] = str(source_connection['type']).replace('Connection', 'Definition')
                dest_connection = tosumo.create_connection(source_connection)
                dest_webhookId = dest_connection['id']
                source_to_dest_dict[source_connection_id] = dest_webhookId
        
        for source_connection_id, dest_connection_id in source_to_dest_dict.items():
            content = find_replace_specific_key_and_value(content,'webhookId',source_connection_id, dest_connection_id)
        return content        

    def create_folder(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        if ContentListWidget.updated == True:
            if radioselected == -3 or radioselected == -4:  # Admin or Global folders selected
                adminmode = True
            else:
                adminmode = False

            message = '''
        Please enter the name of the folder you wish to create:

                        '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Create Folder...', message)
            if result:
                for item in ContentListWidget.currentcontent['children']:
                    if item['name'] == str(text):
                        self.mainwindow.errorbox('That Directory Name Already Exists!')
                        return
                try:

                    logger.info("Creating New Folder in Personal Folder Tree")
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    error = sumo.create_folder(str(text), str(ContentListWidget.currentcontent['id']),
                                               adminmode=adminmode)

                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                    return

                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox("Please update the directory list before trying to create a new folder.")
        return

    def delete_content(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("Deleting Content")
        if radioselected == -3 or radioselected == -4:  # Admin or Global folders selected
            adminmode = True
        else:
            adminmode = False

        selecteditems = ContentListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            message = "You are about to delete the following item(s):\n\n"
            for selecteditem in selecteditems:
                message = message + str(selecteditem.text()) + "\n"
            message = message + '''
This is exceedingly DANGEROUS!!!! 
Please be VERY, VERY, VERY sure you want to do this!
You could lose quite a bit of work if you delete the wrong thing(s).

If you are absolutely sure, type "DELETE" in the box below.

                    '''
            text, result = QtWidgets.QInputDialog.getText(self, 'Warning!!', message)
            if (result and (str(text) == 'DELETE')):
                try:
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for selecteditem in selecteditems:
                        item_id = selecteditem.details['id']
                        result = sumo.delete_content_job_sync(item_id, adminmode=adminmode)
                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                    return


                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

        else:
            self.mainwindow.errorbox('You need to select something before you can delete it.')
        return

    def contentradiobuttonchanged(self, ContentListWidget, url, id, key, radioselected, directorylabel,
                                  pushButtonContentDelete):
        ContentListWidget.currentdirlist = []
        self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
        return

    def togglecontentbuttons(self, side, state):
        if side == 'left':
            self.pushButtonContentCopyRightToLeft.setEnabled(state)
            self.pushButtonContentFindReplaceCopyRightToLeft.setEnabled(state)
            self.pushButtonContentNewFolderLeft.setEnabled(state)
            self.pushButtonContentDeleteLeft.setEnabled(state)
            self.pushButtonContentBackupLeft.setEnabled(state)
            self.pushButtonContentRestoreLeft.setEnabled(state)
        elif side == 'right':
            self.pushButtonContentCopyLeftToRight.setEnabled(state)
            self.pushButtonContentFindReplaceCopyLeftToRight.setEnabled(state)
            self.pushButtonContentNewFolderRight.setEnabled(state)
            self.pushButtonContentDeleteRight.setEnabled(state)
            self.pushButtonContentBackupRight.setEnabled(state)
            self.pushButtonContentRestoreRight.setEnabled(state)

    def updatecontentlist(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        if ContentListWidget.currentdirlist:
            currentdir = ContentListWidget.currentdirlist[-1]
        else:
            currentdir = {'name': None, 'id': 'TOP'}

        try:
            if (not ContentListWidget.currentcontent) or (currentdir['id'] == 'TOP'):
                if radioselected == -2:  # if "Personal Folder" radio button is selected
                    logger.info("[Content] Updating Personal Folder List")
                    ContentListWidget.currentcontent = sumo.get_personal_folder()

                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Personal Folder', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentcontent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)

                    else:
                        self.mainwindow.errorbox('Incorrect Credentials or Wrong Endpoint.')

                elif radioselected == -3:  # if "Global Folders" radio button is selected
                    logger.info("[Content] Updating Global Folder List")
                    ContentListWidget.currentcontent = sumo.get_global_folder_sync(adminmode=True)

                    # Rename dict key from "data" to "children" for consistency
                    ContentListWidget.currentcontent['children'] = ContentListWidget.currentcontent.pop('data')
                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Global Folders', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentcontent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)

                    else:
                        self.mainwindow.errorbox('Incorrect Credentials or Wrong Endpoint.')

                else:  # "Admin Folders" must be selected
                    logger.info("[Content] Updating Admin Folder List")
                    ContentListWidget.currentcontent = sumo.get_admin_folder_sync(adminmode=True)

                    ContentListWidget.currentdirlist = []
                    dir = {'name': 'Admin Recommended', 'id': 'TOP'}
                    ContentListWidget.currentdirlist.append(dir)
                    if 'children' in ContentListWidget.currentcontent:
                        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)

                    else:
                        self.mainwindow.errorbox('Incorrect Credentials or Wrong Endpoint.')



            else:
                if radioselected == -3 or radioselected == -4:
                    adminmode = True
                else:
                    adminmode = False
                ContentListWidget.currentcontent = sumo.get_folder(currentdir['id'], adminmode=adminmode)
                self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)



        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
            return

        return

    def doubleclickedcontentlist(self, item, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("[Content] Going Down One Content Folder")
        sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
        if radioselected == -3 or radioselected == -4:
            adminmode = True
        else:
            adminmode = False
        try:
            if item.details['itemType'] == 'Folder':
                ContentListWidget.currentcontent = sumo.get_folder(item.details['id'], adminmode=adminmode)
                dir = {'name': item.text(), 'id': item.details['id']}
                ContentListWidget.currentdirlist.append(dir)

        except Exception as e:
            logger.exception(e)
            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
        self.updatecontentlistwidget(ContentListWidget, url, id, key, radioselected, directorylabel)

    def parentdircontentlist(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        if ContentListWidget.updated:
            logger.info("[Content] Going Up One Content Folder")
            sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
            currentdir = ContentListWidget.currentdirlist[-1]
            if currentdir['id'] != 'TOP':
                parentdir = ContentListWidget.currentdirlist[-2]
            else:
                return
            try:

                if parentdir['id'] == 'TOP':
                    ContentListWidget.currentdirlist = []
                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                    return

                else:
                    ContentListWidget.currentdirlist.pop()
                    if radioselected == -3 or radioselected == -4:
                        adminmode = True
                    else:
                        adminmode = False
                    ContentListWidget.currentcontent = sumo.get_folder(parentdir['id'], adminmode=adminmode)

                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)
                    return
            except Exception as e:
                logger.exception(e)
                self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))

            return

    def updatecontentlistwidget(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        try:
            ContentListWidget.clear()
            for object in ContentListWidget.currentcontent['children']:
                item_name = ''
                # if radioselected == -3:
                #     logger.info("Getting User info for Global Folder")
                #     user_info = sumo.get_user(object['createdBy'])
                #     item_name = '[' + user_info['firstName'] + ' ' + user_info['lastName'] + ']'
                item_name = item_name + object['name']
                if object['itemType'] == 'Folder':
                    item = QtWidgets.QListWidgetItem(self.icons['Folder'], item_name)
                elif object['itemType'] == 'Search':
                    item = QtWidgets.QListWidgetItem(self.icons['Search'], item_name)
                elif object['itemType'] == 'Dashboard' or object['itemType'] == 'Report':
                    item = QtWidgets.QListWidgetItem(self.icons['Dashboard'], item_name)
                elif object['itemType'] == 'Lookups':
                    item = QtWidgets.QListWidgetItem(self.icons['Lookups'], item_name)
                else:
                    item = QtWidgets.QListWidgetItem(item_name)
                #attach the details about the object to the entry in listwidget, this makes like much easier
                item.details = object
                ContentListWidget.addItem(item)  # populate the list widget in the GUI with no icon (fallthrough)

            dirname = ''
            for dir in ContentListWidget.currentdirlist:
                dirname = dirname + '/' + dir['name']
            directorylabel.setText(dirname)
            ContentListWidget.updated = True
            # if we are in the root (Top) of the global folders then we can't manipulate stuff as the entries are actually users, not content
            # so turn off the buttons until we change folder type or move down a level
            currentdir = ContentListWidget.currentdirlist[-1]
            if currentdir['id'] == 'TOP' and radioselected == -3:
                self.togglecontentbuttons(ContentListWidget.side, False)
            else:
                self.togglecontentbuttons(ContentListWidget.side, True)

        except Exception as e:
            ContentListWidget.clear()
            ContentListWidget.updated = False
            logger.exception(e)
        return

    def backupcontent(self, ContentListWidget, url, id, key, radioselected):
        logger.info("[Content] Backing Up Content")
        if radioselected == -3 or radioselected == -4:  # Admin or Global folders selected
            adminmode = True
        else:
            adminmode = False
        selecteditems = ContentListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            savepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Directory"))
            if os.access(savepath, os.W_OK):
                message = ''
                sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                for selecteditem in selecteditems:
                    item_id = selecteditem.details['id']
                    try:
                        content = sumo.export_content_job_sync(item_id, adminmode=adminmode)
                        savefilepath = pathlib.Path(savepath + r'/' + str(selecteditem.text()) + r'.sumocontent.json')
                        if savefilepath:
                            with savefilepath.open(mode='w') as filepointer:
                                json.dump(content, filepointer)
                            message = message + str(selecteditem.text()) + r'.sumocontent.json' + '\n'
                    except Exception as e:
                        logger.exception(e)
                        self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                        return
                self.mainwindow.infobox('Wrote files: \n\n' + message)
            else:
                self.mainwindow.errorbox("You don't have permissions to write to that directory")

        else:
            self.mainwindow.errorbox('No content selected.')
        return

    def restorecontent(self, ContentListWidget, url, id, key, radioselected, directorylabel):
        logger.info("[Content] Restoring Content")
        if ContentListWidget.updated == True:
            if 'id' in ContentListWidget.currentcontent:  # make sure the current folder has a folder id
                filter = "JSON (*.json)"
                filelist, status = QtWidgets.QFileDialog.getOpenFileNames(self, "Open file(s)...", os.getcwd(),
                                                                          filter)
                if len(filelist) > 0:
                    sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
                    for file in filelist:
                        try:
                            with open(file) as filepointer:
                                content = json.load(filepointer)


                        except Exception as e:
                            logger.exception(e)
                            self.mainwindow.errorbox(
                                "Something went wrong reading the file. Do you have the right file permissions? Does it contain valid JSON?")
                            return
                        try:
                            folder_id = ContentListWidget.currentcontent['id']
                            if radioselected == -4 or radioselected == -3:  # Admin Recommended Folders or Global folders Selected
                                adminmode = True
                            else:
                                adminmode = False
                            sumo.import_content_job_sync(folder_id, content, adminmode=adminmode)
                        except Exception as e:
                            logger.exception(e)
                            self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                            return
                    self.updatecontentlist(ContentListWidget, url, id, key, radioselected, directorylabel)


            else:
                self.mainwindow.errorbox("You can't restore content to this folder. Does it belong to another user?")
                return
        else:
            self.mainwindow.errorbox("Please update the directory list before restoring content")
        return

    def view_json(self, ContentListWidget, url, id, key, radioselected):
        logger.info("[Content] Viewing JSON")
        if radioselected == -3 or radioselected == -4:  # Admin or Global folders selected
            adminmode = True
        else:
            adminmode = False
        selecteditems = ContentListWidget.selectedItems()
        if len(selecteditems) > 0:  # make sure something was selected
            json_text = ''
            sumo = SumoLogic(id, key, endpoint=url, log_level=self.mainwindow.log_level)
            for selecteditem in selecteditems:
                item_id = selecteditem.details['id']
                try:
                    content = sumo.export_content_job_sync(item_id, adminmode=adminmode)
                    json_text = json_text + json.dumps(content, indent=4, sort_keys=True) + '\n\n'
                except Exception as e:
                    logger.exception(e)
                    self.mainwindow.errorbox('Something went wrong:\n\n' + str(e))
                    return
            self.json_window = ShowTextDialog('JSON', json_text, self.mainwindow.basedir)
            self.json_window.show()

        else:
            self.mainwindow.errorbox('No content selected.')
        return
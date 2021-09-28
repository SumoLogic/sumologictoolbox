from logzero import logger


class SumoPackage:

    def __init__(self, package_data=None):
        self.package_items = []
        self.package_version = 1.0
        self.item_types = ['sumocontent']
        if package_data:
            logger.debug('Loading data into package object.')
            self.package_import(package_data)

    def add_items(self, items: list):
        for item in items:
            self.add_item(item)

    def add_item(self, item: dict):
        """
        Takes a dict and creates a package item from it. Dict must contain:
        item_name: str      <- duh
        item_data: dict     <- Sumo JSON export
        item_type: str      <- See below for supported types

        The dict can also contain:
        item_options: dict  <- Deployment options. These will exist if loading from a package, otherwise they
        will get created (if there are options available for that item type)
        """
        item_name = item['item_name']
        item_data = item['item_data']
        item_type = item['item_type']
        if 'item_options' in item:
            item_options = item['item_options']
        else:
            item_options = None
        # Check to make sure the item doesn't already exist (compares data, no name, since names could be the same
        # for users)
        if not item_data in [x.item_data for x in self.package_items]:
            if item_type == 'sumocontent':
                self.package_items.append(SumoContentEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumouser':
                self.package_items.append(SumoUserEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumorole':
                self.package_items.append(SumoRoleEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumopartition':
                self.package_items.append(SumoPartitionEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumofer':
                self.package_items.append(SumoFEREntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumoscheduledview':
                self.package_items.append(SumoSVEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumosamlconfig':
                self.package_items.append(SumoSAMLEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumomonitor':
                self.package_items.append(SumoMonitorEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumoconnection':
                self.package_items.append(SumoConnectionEntry(item_name, item_data, item_options=item_options))
            elif item_type == 'sumopackage':
                pass
            else:
                logger.info(f"Couldn't add item {item_name} to package. Unknown type {item_type}")

    def package_export(self):
        package_contents = []
        for package_item in self.package_items:
            package_contents.append(package_item.item_export())
        package = {'sumoPackageVersion': self.package_version,
                   'package_contents': package_contents}
        return package

    def package_import(self, data):
        if 'sumoPackageVersion' in data and data['sumoPackageVersion'] <= self.package_version:
            for item in data['package_contents']:
                self.add_item(item)
            logger.debug(f'Imported package data: {self.package_items}')

    def deploy(self, sumo):
        for item_type in self.item_types:
            for content in self.package_items:
                if content['item_type'] == item_type:
                    content.deploy(sumo)


class SumoPackageEntry:

    def __init__(self, item_name, item_data, item_options=None):

        self.item_name = item_name
        self.item_type = None
        self.item_data = item_data
        self.item_option_template = []
        if item_options:
            self.item_options = item_options
        else:
            self.item_options = []

    def item_export(self):
        return {'item_name': self.item_name,
                'item_type': self.item_type,
                'item_data': self.item_data,
                'item_options': self.item_options}

    def _create_option(self, option):
        return {'option_name': str(option['option_name']),
                'option_display_name': str(option['option_display_name']),
                'value': option['value']}

    def _create_options(self):
        for option in self.item_option_template:
            if option['option_name'] not in [x['option_name'] for x in self.item_options]:
                self.item_options.append(self._create_option(option))

    def set_option_value(self, index, value):
        self.item_options[index]['value'] = value


class SumoContentEntry(SumoPackageEntry):

    from modules.shared import import_content

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumocontent'
        self.item_option_template = [{'option_name': 'ro_share_global', 'option_display_name': 'Global RO Share', 'value': True},
                                    {'option_name': 'rw_share_admin', 'option_display_name': 'Admin RW Share', 'value': True},
                                    {'option_name': 'include_connections', 'option_display_name': 'Include Connections', 'value': True}
                                     ]
        self._create_options()

    def deploy(self, sumo):
        admin_folder = sumo.get_admin_folder_sync()
        admin_folder_id = admin_folder['id']
        adminmode = True
        for item_option in self.item_options:
            if item_option['option_name'] == 'ro_share_global':
                ro_share_global = item_option['value']
            elif item_option['option_name'] == 'rw_share_admin':
                rw_share_admin = item_option['value']
            elif item_option['option_name'] == 'include_connections':
                include_connections = item_option['value']
        self.import_content(self.item_data, admin_folder_id, adminmode, include_connections=include_connections)


class SumoUserEntry(SumoPackageEntry):

    from modules.shared import import_user

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumouser'
        self.item_option_template = [
            {'option_name': 'include_roles', 'option_display_name': 'Include Roles', 'value': False}
            ]
        self._create_options()

    def deploy(self, sumo):
        for item_option in self.item_options:
            if item_option['option_name'] == 'include_roles':
                include_roles = item_option['value']
        self.import_user(self.item_data, sumo, include_roles=include_roles)


class SumoRoleEntry(SumoPackageEntry):

    from modules.shared import import_role

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumorole'

    def deploy(self, sumo):
        self.import_role(self.item_data, sumo)


class SumoPartitionEntry(SumoPackageEntry):

    from modules.shared import import_partition

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumopartition'

    def deploy(self, sumo):
        self.import_partition(self.item_data, sumo)


class SumoFEREntry(SumoPackageEntry):

    from modules.shared import import_fer

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumofer'

    def deploy(self, sumo):
        self.import_fer(self.item_data, sumo)


class SumoSVEntry(SumoPackageEntry):

    from modules.shared import import_scheduled_view

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumoscheduledview'

    def deploy(self, sumo):
        self.import_scheduled_view(self.item_data, sumo, use_current_date=True)


class SumoSAMLEntry(SumoPackageEntry):

    from modules.shared import import_saml_config

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumosamlconfig'

    def deploy(self, sumo):
        self.import_saml_config(self.item_data, sumo)


class SumoConnectionEntry(SumoPackageEntry):

    from modules.shared import import_connection

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumoconnection'

    def deploy(self, sumo):
        self.import_connection(self.item_data, sumo)


class SumoMonitorEntry(SumoPackageEntry):

    from modules.shared import import_monitor

    def __init__(self, item_name, item_data, item_options=None):
        super().__init__(item_name, item_data, item_options=item_options)
        self.item_type = 'sumomonitor'
        self.item_option_template = [
            {'option_name': 'include_connection', 'option_display_name': 'Include Connection', 'value': True}
            ]
        self._create_options()

    def deploy(self, sumo):
        include_connection = False
        for item_option in self.item_options:
            if item_option['option_name'] == 'include_connection':
                include_connection = item_option['value']
        monitor_root_folder_id = sumo.get_monitor_folder_root()['id']
        self.import_monitor(monitor_root_folder_id, self.item_data, sumo, include_connection=include_connection)

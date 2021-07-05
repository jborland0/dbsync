from dbsync.exceptions import DatabaseStructureException
import copy


def prepare_map_keys(columns, prefix, key):
    for col in columns:
        col['Field'] = prefix + col['Field']
        col['Key'] = key


class Table:
    name = ''

    def __init__(self, name):
        self.name = name

    def verify_structure(self, db0, db1):
        # make sure tables match
        table_desc_0 = db0.describe_table(self.name)
        table_desc_1 = db1.describe_table(self.name)
        if table_desc_0 != table_desc_1:
            raise DatabaseStructureException("table " + self.name + " does not match")

        # verify map and sync table structure
        self.verify_map_table(db0)
        self.verify_sync_table(db0)
        self.verify_map_table(db1)
        self.verify_sync_table(db1)

    def verify_map_table(self, db):
        # create map table name
        map_table_name = 'map_' + self.name

        # create lists of local and remote keys
        local_primary_keys = db.get_primary_keys(self.name)
        remote_primary_keys = copy.deepcopy(local_primary_keys)
        prepare_map_keys(local_primary_keys, "pkl_", "PRI")
        prepare_map_keys(remote_primary_keys, "pkr_", "")

        # create list of map table columns
        map_table_desc = [{'Field': 'rhostid', 'Type': 'int', 'Null': 'NO', 'Key': 'PRI', 'Default': None}] \
            + local_primary_keys + remote_primary_keys

        # if map table exists
        if db.table_exists(map_table_name):
            # get description of table
            existing_map_table = db.describe_table(map_table_name)
            # if the table doesn't look like we expect
            if map_table_desc != existing_map_table:
                raise DatabaseStructureException("table " + map_table_name + " does not match")
        else:
            db.create_table(map_table_name, map_table_desc)

    def verify_sync_table(self, db):
        # create sync table name
        sync_table_name = 'sync_' + self.name

        # create list of primary keys
        primary_keys = db.get_primary_keys(self.name)
        prepare_map_keys(primary_keys, "pkl_", "PRI")

        # create list of map table columns
        sync_table_desc = primary_keys + [
            {'Field': 'created', 'Type': 'timestamp', 'Null': 'NO', 'Key': '', 'Default': None},
            {'Field': 'modified', 'Type': 'timestamp', 'Null': 'NO', 'Key': '', 'Default': None},
            {'Field': 'deleted', 'Type': 'tinyint(1)', 'Null': 'NO', 'Key': '', 'Default': None}
        ]

        # if map table exists
        if db.table_exists(sync_table_name):
            # get description of table
            existing_sync_table = db.describe_table(sync_table_name)
            # if the table doesn't look like we expect
            if sync_table_desc != existing_sync_table:
                raise DatabaseStructureException("table " + sync_table_name + " does not match")
        else:
            db.create_table(sync_table_name, sync_table_desc)

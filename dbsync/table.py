from dbsync.exceptions import DatabaseStructureException
import copy
from mysql.connector import DatabaseError


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

        # verify triggers
        self.verify_triggers(db0)
        self.verify_triggers(db1)

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
        sync_table_name = "sync_" + self.name

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

    def verify_triggers(self, db):
        delete_trigger_sql = self.generate_delete_trigger(db)
        try:
            db.execute_sql(delete_trigger_sql)
        except DatabaseError as dberr:
            if str(dberr) == "1359 (HY000): Trigger already exists":
                pass  # TODO: make sure trigger looks like what we tried to create?
            else:
                raise dberr
        insert_trigger_sql = self.generate_insert_trigger(db)
        try:
            db.execute_sql(insert_trigger_sql)
        except DatabaseError as dberr:
            if str(dberr) == "1359 (HY000): Trigger already exists":
                pass  # TODO: make sure trigger looks like what we tried to create?
            else:
                raise dberr
        update_trigger_sql = self.generate_update_trigger(db)
        try:
            db.execute_sql(update_trigger_sql)
        except DatabaseError as dberr:
            if str(dberr) == "1359 (HY000): Trigger already exists":
                pass  # TODO: make sure trigger looks like what we tried to create?
            else:
                raise dberr

    def generate_delete_trigger(self, db):
        sql = "CREATE TRIGGER trigger_delete_" + self.name + " AFTER DELETE ON " + self.name +\
            " FOR EACH ROW BEGIN " + self.generate_delete_sync_sql(db) + " END;"
        return sql

    def generate_delete_sync_sql(self, db):
        # get table description
        sync_table_name = "sync_" + self.name
        sync_table_desc = db.describe_table(sync_table_name)

        # generate where clause
        where_clause = ""
        for field in sync_table_desc:
            if field['Key'] == "PRI":
                where_clause += field['Field'] + " = OLD." + field['Field'][4:] + " AND "

        # compose update statement
        sql = "UPDATE " + sync_table_name + " SET modified = localtimestamp, deleted = 1 WHERE " +\
              where_clause[:-5] + ";"

        # TODO: check to make sure 1 row was affected
        return sql

    def generate_insert_trigger(self, db):
        sql = "CREATE TRIGGER trigger_insert_" + self.name + " AFTER INSERT ON " + self.name +\
            " FOR EACH ROW BEGIN " + self.generate_insert_sync_sql(db) + " END;"
        return sql

    def generate_insert_sync_sql(self, db):
        # get table description
        sync_table_name = "sync_" + self.name
        sync_table_desc = db.describe_table(sync_table_name)

        # generate lists of names, values
        names = ""
        values = ""
        for field in sync_table_desc:
            names += field['Field'] + ","
            if field['Field'] == "created" or field['Field'] == "modified":
                values += "localtimestamp,"
            elif field['Field'] == "deleted":
                values += "0,"
            else:
                values += "NEW." + field['Field'][4:] + ","

        # compose insert statement
        sql = "INSERT INTO " + sync_table_name + " (" +\
            names[:-1] + ") VALUES (" + values[:-1] + ");"

        # TODO: check to make sure 1 row was affected
        return sql

    def generate_update_trigger(self, db):
        sql = "CREATE TRIGGER trigger_update_" + self.name + " AFTER UPDATE ON " + self.name +\
            " FOR EACH ROW BEGIN " + self.generate_update_sync_sql(db) + " END;"
        return sql

    def generate_update_sync_sql(self, db):
        # get table description
        sync_table_name = "sync_" + self.name
        sync_table_desc = db.describe_table(sync_table_name)

        # generate where clause
        where_clause = ""
        for field in sync_table_desc:
            if field['Key'] == "PRI":
                where_clause += field['Field'] + " = NEW." + field['Field'][4:] + " AND "

        # compose update statement
        sql = "UPDATE " + sync_table_name + " SET modified = localtimestamp WHERE " + where_clause[:-5] + ";"

        # TODO: check to make sure 1 row was affected
        return sql

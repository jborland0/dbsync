from dbsync.config import Config
from dbsync.config import unformat
from dbsync.exceptions import DatabaseStructureException
import copy
from mysql.connector import DatabaseError


def prepare_map_keys(columns, fmt, key):
    prepared_columns = copy.deepcopy(columns)
    for col in prepared_columns:
        col['Field'] = fmt.format(col['Field'])
        col['Key'] = key
    return prepared_columns


class Table:
    name = ''

    def __init__(self, name):
        self.name = name

    def generate_delete_trigger(self, db):
        sql = "CREATE TRIGGER " + Config.strings["delete_trigger_name"].format(self.name) + " AFTER DELETE ON " + \
              self.name + " FOR EACH ROW BEGIN " + self.generate_delete_sync_sql(db) + " END;"
        return sql

    def generate_delete_sync_sql(self, db):
        # get table description
        sync_table_name = Config.strings["sync_table_name"].format(self.name)
        sync_table_desc = db.describe_table(sync_table_name)

        # generate where clause
        where_clause = ""
        for field in sync_table_desc:
            if field['Key'] == "PRI":
                where_clause += field['Field'] + " = OLD." + \
                                unformat(field['Field'], Config.strings["local_primary_key"]) + " AND "

        # compose update statement
        sql = "UPDATE " + sync_table_name + " SET " + Config.strings["modified_column_name"] +\
              " = localtimestamp, " + Config.strings["deleted_column_name"] + " = 1 WHERE " + where_clause[:-5] + ";"

        # TODO: check to make sure 1 row was affected
        return sql

    def generate_insert_trigger(self, db):
        sql = "CREATE TRIGGER " + Config.strings["insert_trigger_name"].format(self.name) + " AFTER INSERT ON " +\
              self.name + " FOR EACH ROW BEGIN " + self.generate_insert_sync_sql(db) + " END;"
        return sql

    def generate_insert_sync_sql(self, db):
        # get table description
        sync_table_name = Config.strings["sync_table_name"].format(self.name)
        sync_table_desc = db.describe_table(sync_table_name)

        # generate lists of names, values
        names = ""
        values = ""
        for field in sync_table_desc:
            names += field['Field'] + ","
            if field['Field'] == Config.strings["created_column_name"] or \
                    field['Field'] == Config.strings["modified_column_name"]:
                values += "localtimestamp,"
            elif field['Field'] == Config.strings["deleted_column_name"]:
                values += "0,"
            else:
                values += "NEW." + unformat(field['Field'], Config.strings["local_primary_key"]) + ","

        # compose insert statement
        sql = "INSERT INTO " + sync_table_name + " (" + \
              names[:-1] + ") VALUES (" + values[:-1] + ");"

        # TODO: check to make sure 1 row was affected
        return sql

    def generate_update_trigger(self, db):
        sql = "CREATE TRIGGER " + Config.strings["update_trigger_name"].format(self.name) + " AFTER UPDATE ON " + \
              self.name + " FOR EACH ROW BEGIN " + self.generate_update_sync_sql(db) + " END;"
        return sql

    def generate_update_sync_sql(self, db):
        # get table description
        sync_table_name = Config.strings["sync_table_name"].format(self.name)
        sync_table_desc = db.describe_table(sync_table_name)

        # generate where clause
        where_clause = ""
        for field in sync_table_desc:
            if field['Key'] == "PRI":
                where_clause += field['Field'] + " = NEW." + \
                                unformat(field['Field'], Config.strings["local_primary_key"]) + " AND "

        # compose update statement
        sql = "UPDATE " + sync_table_name + " SET " + Config.strings["modified_column_name"] + \
              " = localtimestamp WHERE " + where_clause[:-5] + ";"

        # TODO: check to make sure 1 row was affected
        return sql

    def verify_map_table(self, db):
        # create map table name
        map_table_name = Config.strings["map_table_name"].format(self.name)

        # create lists of local and remote keys
        primary_keys = db.get_primary_keys(self.name)
        local_primary_keys = prepare_map_keys(primary_keys, Config.strings["local_primary_key"], "PRI")
        remote_primary_keys = prepare_map_keys(primary_keys, Config.strings["remote_primary_key"], "")

        # create list of map table columns
        map_table_desc = [{'Field': Config.strings["remote_host_id"], 'Type': 'int', 'Null': 'NO', 'Key': 'PRI',
                           'Default': None}] + local_primary_keys + remote_primary_keys

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
        sync_table_name = Config.strings["sync_table_name"].format(self.name)

        # create list of primary keys
        local_primary_keys = prepare_map_keys(db.get_primary_keys(self.name),
                                              Config.strings["local_primary_key"], "PRI")

        # create list of map table columns
        sync_table_desc = local_primary_keys + [
            {'Field': Config.strings["created_column_name"],
             'Type': 'timestamp', 'Null': 'NO', 'Key': '', 'Default': None},
            {'Field': Config.strings["modified_column_name"],
             'Type': 'timestamp', 'Null': 'NO', 'Key': '', 'Default': None},
            {'Field': Config.strings["deleted_column_name"],
             'Type': 'tinyint(1)', 'Null': 'NO', 'Key': '', 'Default': None}
        ]

        # if sync table exists
        if db.table_exists(sync_table_name):
            # get description of table
            existing_sync_table = db.describe_table(sync_table_name)
            # if the table doesn't look like we expect
            if sync_table_desc != existing_sync_table:
                raise DatabaseStructureException("table " + sync_table_name + " does not match")
        else:
            db.create_table(sync_table_name, sync_table_desc)

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

        # verify sync data
        self.verify_sync_data(db0)
        self.verify_sync_data(db1)

    def verify_sync_data(self, db):
        # prepare names and lists
        sync_table_name = Config.strings["sync_table_name"].format(self.name)
        primary_keys = db.get_primary_keys(self.name)
        primary_key_names = [key['Field'] for key in db.get_primary_keys(self.name)]
        local_primary_keys = prepare_map_keys(primary_keys, Config.strings["local_primary_key"], "PRI")
        local_primary_key_names = [key['Field'] for key in local_primary_keys]
        primary_key_list = ",".join(primary_key_names)
        sync_key_list = ",".join(local_primary_key_names)

        # find any rows that are unaccounted for and add them as new rows to the sync table
        sql = "INSERT INTO " + sync_table_name + " (" + sync_key_list + "," +\
              Config.strings["created_column_name"] + "," + Config.strings["modified_column_name"] + "," +\
              Config.strings["deleted_column_name"] + ") SELECT " + primary_key_list +\
              ",localtimestamp,localtimestamp,0 FROM " + self.name + " WHERE " + primary_key_list +\
              " NOT IN (SELECT " + sync_key_list + " FROM " + sync_table_name + ");"
        db.execute_sql(sql)

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

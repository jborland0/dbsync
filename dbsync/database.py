from mysql import connector
import json
import importlib.resources
from dbsync.exceptions import DatabaseStructureException


class Database:
    id = 0
    name = ''
    host = ''
    port = 0
    database = ''
    user = ''
    password = ''
    conn = None

    def __init__(self, config):
        self.id = config['id']
        self.name = config['name']
        self.host = config['host']
        self.port = config['port']
        self.database = config['database']
        self.user = config['user']
        self.password = config['password']

    def __enter__(self):
        self.conn = connector.connect(user=self.user, password=self.password,
                                      host=self.host, port=self.port, database=self.database,
                                      auth_plugin='mysql_native_password')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def create_table(self, table_name, table_desc):
        # compose sql statement
        sql = "create table " + table_name + "(\r\n"
        for col in table_desc:
            sql += col['Field'] + " " + col['Type'] + \
                   (" not null" if col['Null'] == "NO" else "") + ",\r\n"
        sql = sql + "primary key ("
        for col in table_desc:
            if col['Key'] == "PRI":
                sql += col['Field'] + ","
        sql = sql[:-1] + ")\r\n)\r\n"

        # execute sql statement
        with self.conn.cursor() as cursor:
            cursor.execute(sql)

    def describe_table(self, table_name):
        with self.conn.cursor() as cursor:
            cursor.execute("describe " + table_name)
            col_headers = [x[0] for x in cursor.description]
            row_dicts = []
            rv = cursor.fetchall()
            for result_b in rv:
                result = (result_b[0], result_b[1].decode(), result_b[2], result_b[3], result_b[4])
                row_dicts.append(dict(zip(col_headers, result)))
            return row_dicts

    def execute_sql_file(self, file_path):
        with self.conn.cursor() as cursor:
            with open(file_path, 'r') as f:
                for result in cursor.execute(f.read(), multi=True):
                    result.fetchall()

    def get_primary_keys(self, table_name):
        with self.conn.cursor() as cursor:
            cursor.execute("describe " + table_name)
            col_headers = [x[0] for x in cursor.description]
            row_dicts = []
            rv = cursor.fetchall()
            for result_b in rv:
                if result_b[3] == "PRI":
                    result = (result_b[0], result_b[1].decode(), result_b[2], result_b[3], result_b[4])
                    row_dicts.append(dict(zip(col_headers, result)))
            return row_dicts

    def query(self, sql):
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            col_headers = [x[0] for x in cursor.description]
            row_dicts = []
            rv = cursor.fetchall()
            for result in rv:
                row_dicts.append(dict(zip(col_headers, result)))
            return row_dicts

    def table_exists(self, table_name):
        with self.conn.cursor() as cursor:
            cursor.execute("select count(*) from information_schema.tables where table_schema = %s and table_name = %s",
                           (self.database, table_name))
            return cursor.fetchone()[0] == 1

    def verify_host_tables(self):
        # if sync_hosts table doesn't exist, create it
        if not self.table_exists("sync_hosts"):
            with self.conn.cursor() as cursor:
                cursor.execute(importlib.resources.read_text("dbsync", "sync_hosts.sql"))

        # verify that sync_hosts table looks like we are expecting
        sync_hosts_actual = self.describe_table("sync_hosts")
        sync_hosts_template = json.loads(importlib.resources.read_text("dbsync", "sync_hosts.json"))
        if sync_hosts_actual != sync_hosts_template:
            raise DatabaseStructureException("sync_hosts table does not match template")

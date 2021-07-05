import json
from dbsync.database import Database
from dbsync.table import Table
import sys


def sync(config):
    # create database
    with Database(config['hosts'][0]) as db0, Database(config['hosts'][1]) as db1:
        sync_db(db0, db1, config['tables'])
    return dict(result=0, message='success')


def sync_db(db0, db1, tables):
    # verify local and remote host tables
    db0.verify_host_tables()
    db1.verify_host_tables()

    # for each table we want to sync
    for table_name in tables:
        table = Table(table_name)
        table.verify_structure(db0, db1)


if __name__ == '__main__':
    # if argument was provided
    if len(sys.argv) > 1:
        # load config file and synchronize databases
        with open(sys.argv[1], 'r') as config_file:
            result = sync(json.loads(config_file.read()))
    else:
        result = dict(result=1, message="argument 1 must be path to config file")

    # print exit message and send return code
    print(result["message"])
    sys.exit(result["result"])

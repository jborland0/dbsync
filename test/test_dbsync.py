import subprocess
import sys
import unittest
from unittest import TestCase
import os
import json
from dbsync import dbsync
from dbsync.dbsync import Database
import re


def list_test_dirs():
    # get current directory
    test_home = os.path.dirname(os.path.abspath(__file__))

    # get sorted list of files in this directory
    test_files = sorted(os.listdir(test_home))
    test_dirs = []

    # for each file
    for file_name in test_files:
        test_dir = os.path.join(test_home, file_name)
        # if this is a directory and is prefixed with a 3 digit number
        if os.path.isdir(test_dir) and re.match('[0-9]{3}_', file_name):
            test_dirs.append(test_dir)

    return test_dirs


def mysqldump(test_dir, config):
    # compose mysqldump command
    cmd = "mysqldump" + \
          " -h " + config['host'] + \
          " -P " + str(config['port']) + \
          " -u " + config['user'] + \
          " -p" + config['password'] + \
          " " + config['database']

    # read mysqldump results into a string and adjust formatting
    sql_dump = subprocess.check_output(cmd).decode("utf-8").replace("\r\n", "\n")
    sql_dump = re.sub(r"-- Dump completed on \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "", sql_dump)
    return sql_dump


class Test(TestCase):
    def test_sync_db(self, db_config_file_path=None):
        # load db configuration
        if db_config_file_path is None:
            db_config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(db_config_file_path, 'r') as db_config_file:
            db_config = json.loads(db_config_file.read())

        # for each test directory
        test_dirs = list_test_dirs()
        for test_dir in test_dirs:
            success = True

            # load test configuration
            with open(os.path.join(test_dir, "config.json"), 'r') as test_config_file:
                test_config = json.loads(test_config_file.read())

            # combine db config, test config into single config object
            config = {**db_config, **test_config}

            # open databases
            with Database(config['hosts'][0]) as db0, Database(config['hosts'][1]) as db1:

                # set up test data
                db0.execute_sql_file(os.path.join(test_dir, "setup_db0.sql"))
                db1.execute_sql_file(os.path.join(test_dir, "setup_db1.sql"))

                # synchronize test databases
                dbsync.sync_db(db0, db1, config['tables'])

                # for each host
                for i, config_host in enumerate(config['hosts']):

                    # dump database to string
                    sql_dump = mysqldump(test_dir, config_host)

                    # compose sql file name
                    sql_file = os.path.join(test_dir, "verify_db" + str(i) + ".sql")

                    # if we are creating the verification file
                    if 'generate_mysql_dump' in config and config['generate_mysql_dump']:

                        # save mysqldump results to file
                        with open(sql_file, 'w+') as file:
                            file.write(sql_dump)
                    else:

                        # compare sql dump to verification file
                        with open(sql_file) as file:
                            sql_verify = file.read()
                            if sql_dump != sql_verify:
                                success = False

                # clean up
                db0.execute_sql_file(os.path.join(test_dir, "teardown_db0.sql"))
                db1.execute_sql_file(os.path.join(test_dir, "teardown_db1.sql"))

                # fail if not successful
                if not success:
                    self.fail("sql dump verification failed.")

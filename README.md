# dbsync

Synchronizes two databases according to a configuration file.

to test:

python -m unittest test.test_dbsync

to run from command line:

python -m dbsync.dbsync &lt;path to config file&gt;

where the config file looks something like the following:

	{
		"hosts": [
			{
				"id": 0,
				"name": "db0",
				"host": "127.0.0.1",
				"port": 3306,
				"database": "db0",
				"user": "db0_user",
				"password": "db0_password"
			},
			{
				"id": 1,
				"name": "db1",
				"host": "127.0.0.1",
				"port": 3307,
				"database": "db1",
				"user": "db1_user",
				"password": "db1_password"
			}
		],
		"tables": [
			"customer"
			"product",
			"sales_order",
			"etc..."
		]
	}

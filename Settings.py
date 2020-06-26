# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 12:53'

# map HDFS SCHEMA to NAMENODE HOST
NAMENODE_MAP = {
    "EXAMPLE_SCHEMA_ONE": ["NAMENODE_HOST_ONE", "NAMENODE_HOST_TWO"],
    "EXAMPLE_SCHEMA_TWO": ["NAMENODE_HOST_ONE", "NAMENODE_HOST_TWO"]
}

# HDFS HTTP PORT by default
HTTP_PORT = 50070

# SUPERUSER in HDFS
SUPER_USER = "hdfs"

# Interval for auto cleaner to delete outdated snapshots
AUTO_CLEAN_INTERVAL = 3600

# Saving snapshot/directory/auditlog info into MYSQL
MYSQL_CONFIGURES = {
    "HOST": "localhost",
    "PORT": "3306",
    "USER": "USERNAME",
    "PSW": "PASSWORD",
    "DB": "DATABASE_NAME"
}

LOG_FORMAT = '[%(asctime)s] [%(filename)s] [%(processName)s] [%(funcName)s] [line-%(lineno)s] [%(levelname)s] %(message)s'

# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 13:02'

import subprocess
from time import sleep

import requests
from Settings import NAMENODE_MAP, AUTO_CLEAN_INTERVAL, HTTP_PORT, SUPER_USER
import logging


class Automator:
    def __init__(self):
        pass

    def auto_cleaner(self):
        for schema in NAMENODE_MAP.keys():
            lssnapshottabledir_cmd = "hdfs lsSnapshottableDir -Dfs.defaultFS=hdfs://{schema}".format(
                schema=schema
            ).split()
            logging.info("Checking Cluster: {}".format(schema))
            try:
                snapshottabledir_ls = subprocess.check_output(lssnapshottabledir_cmd).decode().split("\n")[:-1]
                for snapshottabledir in snapshottabledir_ls:
                    logging.info("Checking SnapshotDir: {}".format(snapshottabledir.split()[-1]))
                    snapshots = self.ls_snapshot(schema, snapshottabledir)
                    if len(snapshots) > 7:
                        logging.info("Snapshots beyond limits, ready to clean up...")
                        try:
                            for snapshot_name in snapshots[1:-7]:
                                self.auto_delete(schema, snapshottabledir.split()[-1],
                                                 snapshot_name.split()[-1].split('/')[-1])
                        except Exception as e:
                            logging.error(e)
                    else:
                        print("Everything's fine")
            except Exception as e:
                logging.error(e)

    @staticmethod
    def ls_snapshot(schema, snapshottabledir):
        """
        List all snapshot under current snapshottable directory.
        :param schema: nameservice for HDFS HA
        :param snapshottabledir: directory which has been snapshottable
        :return: list of existed snapshots
        """
        ls_cmd = "hdfs dfs -ls -r -t hdfs://{schema}{snapshottabledir}/.snapshot".format(
            schema=schema,
            snapshottabledir=snapshottabledir.split()[-1]
        ).split()
        snapshots = subprocess.check_output(ls_cmd).decode().split("\n")[:-1]
        return snapshots

    @staticmethod
    def auto_delete(schema, snapshottabledir, snapshot_name):
        """
        Delete snapshot according to given snapshot_name.
        :param schema: nameservice for HDFS HA
        :param snapshottabledir: directory which has been snapshottable
        :param snapshot_name: name of the snapshot
        """
        for host in NAMENODE_MAP[schema]:
            url = "http://{host}:{port}/webhdfs/v1/{path}?user.name={super_user}" \
                  "&op=DELETESNAPSHOT&snapshotname={snapshot_name}".format(
                        host=host,
                        port=HTTP_PORT,
                        path=snapshottabledir,
                        super_user=SUPER_USER,
                        snapshot_name=snapshot_name
                    )
            try:
                requests.delete(url)
                logging.info("Successfully deleted snapshot: {}".format(snapshot_name))
                return
            except Exception as e:
                logging.error(e)
                continue


if __name__ == '__main__':
    # This script should be run as an isolated process in order to check and delete snapshot beyond threshold.
    while True:
        Automator().auto_cleaner()
        sleep(AUTO_CLEAN_INTERVAL)

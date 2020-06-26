# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 14:38'

import subprocess
from flask import current_app


class Recover:
    def __init__(self, path):
        self.__path = path

    def show_all(self):
        """
        List all snapshot under current directory.
        :return: snapshot list under current directory
        """
        show_cmd = "hdfs dfs -ls -r -t {path}/.snapshot".format(
            path=self.__path
        ).split()
        return subprocess.check_output(show_cmd).decode().split("\n")[:-1]

    def restore(self, filename=None, snapshot_name=None):
        """
        Copy file from snapshot to its source path, which called restore specific file from snapshot.
        :param filename: The file needs to be restored
        :param snapshot_name: The snapshot used to restore the file, latest snapshot would be chosen if not provided
        """
        # if snapshot_name is not provided, the name of latest_snapshot would be chosen for recovering.
        if snapshot_name is None:
            latest_snapshot = self.show_all()[-1].split()
            snapshot_name = latest_snapshot[-1].split('/')[-1]
        # if filename is not provided, all the file under the snapshot directory would be copied to target path.
        if filename in (None, ""):
            filename = "*"
        restore_cmd = "hdfs dfs -cp -ptopax {path}/.snapshot/{snapshot_name}/{filename} " \
                      "{path}".format(
                            path=self.__path,
                            snapshot_name=snapshot_name,
                            filename=filename
                        )
        current_app.logger.info(restore_cmd)
        try:
            code, result = subprocess.getstatusoutput(restore_cmd)
            if code == 0:
                current_app.logger.info("File restored successfully.")
                return True
            else:
                current_app.logger.error("File restored failed!")
                return False
        except Exception as e:
            current_app.logger.error("File Recovery Failed!", e)

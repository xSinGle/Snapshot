# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 14:25'

import subprocess
import time
from subprocess import CalledProcessError
import re

import requests
from requests import ConnectionError
from flask import current_app

from Settings import NAMENODE_MAP, SUPER_USER, HTTP_PORT
from app.lib.Pipeline import Pipeline


class Snapshot:
    def __init__(self, user, schema, path, snapshot_name=None):
        self.__user = user
        self.__schema = schema
        self.__hosts = NAMENODE_MAP[self.__schema]
        self.__port = HTTP_PORT
        self.__path = path
        self.__s_path = '/' + re.findall('hdfs://.*?/(.*)', self.__path)[0]
        self.__super_user = SUPER_USER
        self.__pipe = Pipeline()
        self.__snapshot_name = snapshot_name

    @staticmethod
    def requests_api(url, action):
        current_app.logger.info("Invoking API {url}".format(url=url))
        try:
            if action in ("create", "rename"):
                res = requests.put(url)
            elif action == "delete":
                res = requests.delete(url)
            else:
                raise Exception("Unrecognized request method: [{method}], "
                                "Supporting methods are: [create, rename, delete, differ, list]".format(method=action))
            if res.status_code == 200:
                current_app.logger.info("[{status_code}] Snapshot Action Succeeded!".format(status_code=res.status_code))
                if len(res.text) != 0:
                    current_app.logger.info(res.text)
                    return res.text
                else:
                    return True
            else:
                current_app.logger.error("[{status_code}] Snapshot Action Failed: ".format(
                    status_code=res.status_code), res.json())
                return
        except ConnectionError as e:
            current_app.logger.info("Requests Failed, URL: [{url}], Error: [{e}]".format(url=url, e=e))

    def allow(self):
        """
        hdfs dfsadmin [-allowSnapshot <snapshotDir>]
        :param path: hdfs directory path which needs to be snapshottable
        """
        allow_cmd = "hdfs dfsadmin -Dfs.defaultFS=hdfs://{schema} -allowSnapshot {path}".format(
            schema=self.__schema,
            path=self.__path
        ).split()

        current_app.logger.info("Executing command {cmd}".format(cmd=allow_cmd))
        try:
            subprocess.check_output(allow_cmd)
        except CalledProcessError as e:
            current_app.logger.error("Allow Snapshot Failed! HDFS Path might not existed,please check it out. {}".format(e))

    def disallow(self):
        """
        hdfs dfsadmin [-disallowSnapshot <snapshotDir>]
        :param path: hdfs directory path which needs to be unsnapshottable
        """

        disallow_cmd = "hdfs dfsadmin -Dfs.defaultFS=hdfs://{schema} -disallowSnapshot {path}".format(
            schema=self.__schema,
            path=self.__path
        )
        current_app.logger.info("Executing command {cmd}".format(cmd=disallow_cmd))
        code, result = subprocess.getstatusoutput(disallow_cmd)
        if code != 0:
            current_app.logger.error("[FAIL] disallow path {path} failed!".format(path=self.__path))

    def create(self):
        """
        SHELL: hdfs dfs [-createSnapshot <snapshotDir> [<snapshotName>]]
        HTTP: curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=CREATESNAPSHOT[&snapshotname=<SNAPSHOTNAME>]"
        NAMENODE host and port has been specified so that absolute path would be unnecessary.
        :param schema: HDSF namenode schema, used for mapping the host of NN
        :param path: hdfs directory path
        :param snapshot_name(optional): name of the snapshot
        """

        if self.__snapshot_name is not None and self.__snapshot_name != "":
            self.__snapshot_name = self.__user + "-" + self.__snapshot_name + "-" \
                                   + time.strftime("%Y%m%d-%H%M%S") + "-" + str(time.time())[-3:]
        else:
            self.__snapshot_name = self.__user + "-" + "default_snapshot_name" + "-" + time.strftime("%Y%m%d-%H%M%S") + "-" + str(time.time())[-3:]

        # Store snapshot and path info into server DB for further usage.(Creation won't happen once exceeds 7.)
        current_app.logger.info("Saving Path&Snapshot Info into Server DB...")
        create_success = self.__pipe.create_snapshot(path=self.__path, snapshot_name=self.__snapshot_name, user=self.__user)

        # which means snapshot count is over 7.
        if not create_success:
            return

        for host in self.__hosts:
            current_app.logger.info("Creating snapshot for {path}".format(path=self.__path))
            try:
                url = "http://{host}:{port}/webhdfs/v1/{path}?user.name={super_user}" \
                      "&op=CREATESNAPSHOT&snapshotname={snapshot_name}".format(
                            host=host,
                            port=self.__port,
                            path=self.__s_path,
                            super_user=self.__super_user,
                            snapshot_name=self.__snapshot_name
                        )
                if self.requests_api(url, "create"): break
            except ConnectionError as e:
                current_app.logger.error("A Connection Error Occurred while connecting to "
                                         "NameNode {host}, {e}".format(host=host, e=e))
        current_app.logger.info("Successfully created snapshot for {path}".format(path=self.__path))
        return True

    def delete(self):
        """
        SHELL:hdfs dfs [-deleteSnapshot <snapshotDir> <snapshotName>]
        HTTP: curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=DELETESNAPSHOT&snapshotname=<SNAPSHOTNAME>"
        :param path: hdfs directory path to be deleted
        :param snapshot_name: snapshot to be deleted
        """

        self.__snapshot_name = self.__snapshot_name \
            if self.__snapshot_name \
            else self.__pipe.snapshot_name_init(self.__path, self.__snapshot_name)

        for host in self.__hosts:
            try:
                current_app.logger.info("Deleting snapshot for {path}".format(path=self.__path))
                url = "http://{host}:{port}/webhdfs/v1/{path}?user.name={super_user}" \
                      "&op=DELETESNAPSHOT&snapshotname={snapshot_name}".format(
                            host=host,
                            port=self.__port,
                            path=self.__s_path,
                            super_user=self.__super_user,
                            snapshot_name=self.__snapshot_name
                        )
                delete_success = self.requests_api(url, "delete")
                if delete_success:
                    break
            except ConnectionError as e:
                current_app.logger.error("A Connection Error Occurred while connecting to "
                                         "NameNode {host}, {e}".format(host=host, e=e))
        if delete_success:
            current_app.logger.info("Successfully deleted snapshot for {path}".format(path=self.__path))

            # Delete snapshot and path info in server DB.
            current_app.logger.info("Deleting Path&Snapshot Info into Server DB...")
            disallow = self.__pipe.delete_snapshot(path=self.__path, snapshot_name=self.__snapshot_name)
            if disallow:
                current_app.logger.info('No more snapshot under path [{path}], disallowing...'.format(path=self.__path))
                self.disallow()
            return True

        # Return False if neither host finished deleted snapshot.
        current_app.logger.error("Failed to delete snapshot, snapshot might not existed.")
        return

    def differ(self, old_snapshot_name, snapshot_name):
        """
        SHELL:hdfs SnapshotDiff <snapshotDir> <from> <to>
        HTTP: curl -i GET "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=GETSNAPSHOTDIFF
                   &oldsnapshotname=<SNAPSHOTNAME>&snapshotname=<SNAPSHOTNAME>"
        Get the difference between two snapshots,
        or between a snapshot and the current tree of a directory.
        For <from>/<to>, users can use "." to present the current status,
        and use ".snapshot/snapshot_name" to present a snapshot,
        where ".snapshot/" can be omitted
        :param old_snapshot_name: previous snapshotname
        :param snapshot_name: current snapshotname
        """
        differ_cmd = "hdfs snapshotDiff -Dfs.defaultFS=hdfs://{schema} {snapshotDir} {old_snapshot_name} {snapshot_name}".format(
            schema=self.__schema,
            snapshotDir=self.__path,
            old_snapshot_name=old_snapshot_name,
            snapshot_name=snapshot_name
        ).split()

        doc = {
            "M": "该文件/目录已被修改",
            "R": "该文件/目录已被重命名",
            "+": "该文件/目录被新创建",
            "-": "该文件/目录已被删除"
        }

        try:
            diff_result = subprocess.check_output(differ_cmd).decode().split('\n')[1:-2]
            difference = '\n'.join([': '.join([doc[line.split('\t')[0]], line.split('\t')[1]]) for line in diff_result])
            return difference
        except CalledProcessError as e:
            current_app.logger.error('Show SnapshotDiff Failed! {}'.format(e))

    def rename(self, old_snapshot_name, new_snapshot_name):
        """
        SHELL: hdfs dfs [-renameSnapshot <snapshotDir> <oldName> <newName>]
        HTTP: curl -i -X PUT "http://<HOST>:<PORT>/webhdfs/v1/<PATH>?op=RENAMESNAPSHOT
                   &oldsnapshotname=<SNAPSHOTNAME>&snapshotname=<SNAPSHOTNAME>"
        :param old_snapshot_name: old snapshot name
        :param new_snapshot_name: new snap shot name
        """
        for host in self.__hosts:
            try:
                current_app.logger.info("Renaming snapshot for {path}".format(path=self.__path))
                url = "http://{host}:{port}/webhdfs/v1/{path}?user.name={super_user}" \
                      "&op=RENAMESNAPSHOT&oldsnapshotname={old_snapshot_name}&snapshotname={snapshot_name}".format(
                        host=host,
                        port=self.__port,
                        path=self.__s_path,
                        super_user=self.__super_user,
                        old_snapshot_name=old_snapshot_name,
                        snapshot_name=self.__user + "-" + new_snapshot_name + "-"
                                      + time.strftime("%Y%m%d-%H%M%S") + "-" + str(time.time())[-3:]
                    )
                rename_success = self.requests_api(url, "rename")
                if rename_success: break
            except ConnectionError as e:
                current_app.logger.error("A Connection Error Occurred while connecting to "
                                         "NameNode {host}, {e}".format(host=host, e=e))
        if rename_success:
            current_app.logger.info("Successfully renamed snapshot for {path}".format(path=self.__path))

            # Rename snapshot and path info in server DB.
            current_app.logger.info("Renaming Path&Snapshot Info into Server DB...")
            self.__pipe.rename_snapshot(path=self.__path, old_snapshot_name=old_snapshot_name,
                                        new_snapshot_name=new_snapshot_name)
            return True

        current_app.logger.error("Failed to rename snapshot for {path}".format(path=self.__path))
        return

    def ls_snapshottable_dir(self):
        """
        hdfs LsSnapshottableDir
        Get the list of snapshottable directories that are owned by the current user.
        Return all the snapshottable directories if the current user is a super user.
        """
        ls_cmd = "hdfs lsSnapshottableDir -Dfs.defaultFS=hdfs://{schema}".format(
            schema=self.__schema
        ).split()
        try:
            return subprocess.check_output(ls_cmd).decode()
        except CalledProcessError as e:
            current_app.logger.error("List Snapshottable Directory Failed! {}".format(e))

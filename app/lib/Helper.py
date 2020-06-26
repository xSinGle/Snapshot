# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 14:39'

import re

from flask import current_app

from app.lib.Snapshot import Snapshot


def param_handler(params, action):
    if "SNAPSHOTNAME" not in params.keys() or re.search("[\\\\,./\\x20]", params["SNAPSHOTNAME"]):
        snapshot_name = None
    else:
        snapshot_name = params["SNAPSHOTNAME"]

    try:
        schema = re.findall('hdfs://(.*?)/', params["PATH"])[0]
    except IndexError as e:
        current_app.logger.error("IndexError: Failed to get schema from hdfs path! {}".format(e))

    param_doc = {
        "user": params["USER"],
        "schema": schema,
        "path": params["PATH"],
        "snapshot_name": snapshot_name
    }
    if action in ("DIFFER", "RENAME"):
        try:
            param_doc["old_snapshot_name"] = params["OLDSNAPSHOTNAME"]
        except Exception as e:
            current_app.logger.info("OLDSNAPSHOTNAME was not provided!", e)
    if action == "RECOVER":
        try:
            param_doc["filename"] = params["FILENAME"]
        except Exception as e:
            current_app.logger.info("filename was not provided!", e)
    return param_doc


def snapshot_initializer(param_doc):
    snapshot = Snapshot(
        user=param_doc["user"],
        schema=param_doc["schema"],
        path=param_doc["path"],
        snapshot_name=param_doc["snapshot_name"]
    )
    return snapshot

# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 14:40'

import json
import time

from flask import request, jsonify, current_app

from app.lib.Helper import param_handler, snapshot_initializer
from app.lib.Pipeline import Pipeline
from app.lib.Recover import Recover
from app.view import view


@view.route("/snapshot/action/create", methods=["POST"])
def create_snapshot():
    current_app.logger.info("Create Snapshot Requests Received.")
    param_doc = param_handler(request.form, action='CREATE')

    if param_doc['snapshot_name'] is not None and param_doc['snapshot_name'] != "":
        audit_snapshot_name = param_doc['user'] + "-" + param_doc['snapshot_name'] + "-" \
                               + time.strftime("%Y%m%d-%H%M%S") + "-" + str(time.time())[-3:]
    else:
        audit_snapshot_name = param_doc['user'] + "-" + "default_snapshot_name" + "-" + time.strftime(
            "%Y%m%d-%H%M%S") + "-" + str(time.time())[-3:]

    pipe = Pipeline()
    pipe.audit_log(user=param_doc['user'], action='CREATE', path=param_doc['path'],
                   snapshot_name=audit_snapshot_name)

    snapshot = snapshot_initializer(param_doc)
    snapshot.allow()
    create_success = snapshot.create()
    if create_success:
        return jsonify(msg='Create Snapshot Successfully.', code=200, user=param_doc['user'], path=param_doc['path'],
                       snapshot_name=param_doc['snapshot_name'], action='CREATE')
    else:
        return jsonify(msg='Failed to create snapshot, total snapshot count might be over 7.', code=403,
                       user=param_doc['user'], path=param_doc['path'],
                       snapshot_name=param_doc['snapshot_name'], action='CREATE')


@view.route("/snapshot/action/delete", methods=["POST"])
def delete_snapshot():
    current_app.logger.info("Delete Snapshot Requests Received.")
    param_doc = param_handler(request.form, action='DELETE')

    pipe = Pipeline()
    pipe.audit_log(user=param_doc['user'], action='DELETE', path=param_doc['path'],
                   snapshot_name=param_doc['snapshot_name'])

    snapshot = snapshot_initializer(param_doc)
    delete_success = snapshot.delete()

    if delete_success:
        return jsonify(msg='Delete Snapshot Successfully.', code=200, user=param_doc['user'], path=param_doc['path'],
                       snapshot_name=param_doc['snapshot_name'], action='DELETE')
    else:
        return jsonify(msg='Failed to delete snapshot, snapshot might not existed.', code=403, user=param_doc['user'],
                       path=param_doc['path'], snapshot_name=param_doc['snapshot_name'], action='DELETE')


@view.route("/snapshot/action/differ", methods=["POST"])
def differ_snapshot():
    current_app.logger.info("Show Difference Requests Received.")
    param_doc = param_handler(request.form, action='DIFFER')

    pipe = Pipeline()
    pipe.audit_log(user=param_doc['user'], action='DIFFER', path=param_doc['path'],
                   snapshot_name=json.dumps({'old_snapshot_name': param_doc["old_snapshot_name"],
                                            'snapshot_name': param_doc["snapshot_name"]}))

    snapshot = snapshot_initializer(param_doc)
    difference = snapshot.differ(
        old_snapshot_name=param_doc["old_snapshot_name"],
        snapshot_name=param_doc["snapshot_name"]
    )

    return jsonify(msg='Show Difference between Snapshot Successfully.', code=200, user=param_doc['user'],
                   path=param_doc['path'], difference=difference,
                   snapshot_name=json.dumps({'old_snapshot_name': param_doc["old_snapshot_name"],
                                            'snapshot_name': param_doc["snapshot_name"]}), action='DIFFER')


@view.route("/snapshot/action/rename", methods=["POST"])
def rename_snapshot():
    current_app.logger.info("Rename Requests Received.")
    param_doc = param_handler(request.form, action='RENAME')

    pipe = Pipeline()
    pipe.audit_log(user=param_doc['user'], action='RENAME', path=param_doc['path'],
                   snapshot_name=json.dumps({'old_snapshot_name': param_doc["old_snapshot_name"],
                                             'snapshot_name': param_doc["snapshot_name"]}))

    snapshot = snapshot_initializer(param_doc)
    rename_success = snapshot.rename(
        old_snapshot_name=param_doc["old_snapshot_name"],
        new_snapshot_name=param_doc["snapshot_name"]
    )
    if rename_success:
        return jsonify(msg='Rename Snapshot Successfully.', code=200, user=param_doc['user'], path=param_doc['path'],
                       old_snapshot_name=param_doc["old_snapshot_name"], snapshot_name=param_doc["snapshot_name"],
                       action='RENAME')
    else:
        return jsonify(msg='Failed to rename snapshot.', code=403, user=param_doc['user'], path=param_doc['path'],
                       old_snapshot_name=param_doc["old_snapshot_name"], snapshot_name=param_doc["snapshot_name"],
                       action='RENAME')


@view.route("/snapshot/action/recover", methods=["POST"])
def recover_snapshot():
    current_app.logger.info("Restoring snapshot [{snapshot}] to path [{path}]".format(
        snapshot=request.form['SNAPSHOTNAME'], path=request.form['PATH']))

    pipe = Pipeline()
    pipe.audit_log(user=request.form['USER'], action='RECOVER', path=request.form['PATH'],
                   filename=request.form['FILENAME'], snapshot_name=request.form["SNAPSHOTNAME"])

    restore_success = Recover(request.form["PATH"]).restore(
        filename=request.form["FILENAME"], snapshot_name=request.form["SNAPSHOTNAME"])

    if restore_success:
        return jsonify(msg='Recover Snapshot Successfully.', code=200, user=request.form['USER'],
                       path=request.form['PATH'], snapshot_name=request.form['SNAPSHOTNAME'],
                       filename=request.form["FILENAME"], action='RECOVER')
    else:
        return jsonify(msg='Failed to restore snapshot!', code=403, user=request.form['USER'],
                       path=request.form['PATH'], snapshot_name=request.form['SNAPSHOTNAME'],
                       filename=request.form["FILENAME"], action='RECOVER')

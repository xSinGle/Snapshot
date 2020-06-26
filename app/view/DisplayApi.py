# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 14:42'

from flask import request, jsonify, current_app
from app.lib.Pipeline import Pipeline
from app.view import view


# 此接口暂时废弃 统一使用all接口
@view.route('/snapshot/display/path', methods=['POST'])
def display_path():
    current_app.logger.info('Display Path Requests Received.')
    pipe = Pipeline()
    path_info_count, path_info_ls = pipe.display_path(user=request.form['user'],
                                                      page_index=request.form['page_index'],
                                                      page_size=request.form['page_size'])
    return jsonify(msg='Display Path Info Successfully.', code=200, total=path_info_count, result=path_info_ls)


# 此接口暂时废弃 统一使用all接口
@view.route('/snapshot/display/snapshot', methods=['POST'])
def display_snapshot():
    current_app.logger.info('Display Snapshot Requests Received.')
    pipe = Pipeline()
    snapshot_count, snapshot_info_ls = pipe.display_snapshot(path=request.form['path'],
                                                             page_index=request.form['page_index'],
                                                             page_size=request.form['page_size'])
    return jsonify(msg='Display Snapshot Info Successfully.', code=200, total=snapshot_count, result=snapshot_info_ls)


@view.route('/snapshot/display/all', methods=['POST'])
def display_all():
    current_app.logger.info('Display All Info Requests Received.')
    pipe = Pipeline()

    pipe.audit_log(user=request.form['USER'], action='DISPLAY')

    all_info_count, all_info_ls = pipe.display_all(user=request.form['USER'],
                                                   page_index=request.form['page_index'],
                                                   page_size=request.form['page_size'])
    return jsonify(msg='Dispaly Snapshot of user [{user}] Successfully'.format(user=request.form['USER']),
                   total=all_info_count, result=all_info_ls)

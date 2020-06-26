# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 14:05'

"""
Main SQL process procedure would all be placed here.
"""


from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app

from Settings import MYSQL_CONFIGURES
from app.lib.Tables import SnapshotInfo, PathInfo, AuditLog


class Pipeline:
    def __init__(self):
        self.__engine = create_engine('mysql+pymysql://{user}:{psw}@{host}:{port}/{db}'.format(
            user=MYSQL_CONFIGURES['USER'], psw=MYSQL_CONFIGURES['PSW'], host=MYSQL_CONFIGURES['HOST'],
            port=MYSQL_CONFIGURES['PORT'], db=MYSQL_CONFIGURES['DB']))
        self.__db_session = sessionmaker(bind=self.__engine)
        self.__session = self.__db_session()

    # CREATE
    def create_snapshot(self, path, snapshot_name, user):
        new_snapshot = SnapshotInfo(path=path, name=snapshot_name)

        # Detect current quantity of path.
        path_check = self.__session.query(PathInfo).filter(PathInfo.path == path).first()
        if path_check:
            current_app.logger.info("Snapshot Count: [{}]".format(path_check.snapshot_count))
            path_snapshot_count = path_check.snapshot_count
        else:
            path_snapshot_count = 0
            current_app.logger.info("Snapshot Count: [0]")

        # 1. Current path contains no snapshots.
        if path_snapshot_count == 0:
            new_path = PathInfo(path=path, user=user)
            self.__session.add(new_path)
            # Never forget to add count for snapshot_count once the path has been added.
            self.__session.query(PathInfo) \
                .filter(PathInfo.path == path) \
                .update({'snapshot_count': PathInfo.snapshot_count + 1})
            self.__session.add(new_snapshot)
            self.__session.commit()
            self.__session.close()
            return True
        # 2. Snapshots have been already exists and addition is still available.
        elif 0 < path_snapshot_count < 7:
            self.__session.query(PathInfo) \
                .filter(PathInfo.path == path) \
                .update({'snapshot_count': PathInfo.snapshot_count + 1})
            self.__session.add(new_snapshot)
            self.__session.commit()
            self.__session.close()
            return True
        # 3. Snapshot limitation would be 7.
        elif path_snapshot_count >= 7:
            self.__session.close()
            current_app.logger.error("Snapshot of path [{path}] reaching the limit [7]!")
            return

    # DELETE
    def delete_snapshot(self, path, snapshot_name):

        try:
            # delete snapshot with given snapshot name
            current_app.logger.info('[DELETE] SNAPSHOT NAME: [{snapshot_name}]'.format(snapshot_name=snapshot_name))
            self.__session.query(SnapshotInfo).filter(SnapshotInfo.name == snapshot_name).delete()
            self.__session.commit()
            current_app.logger.info(
                'Successfully deleted snapshot: [{snapshot_name}]'.format(snapshot_name=snapshot_name))
        except Exception as e:
            current_app.logger.error(e)

        try:
            path_check = self.__session.query(PathInfo).filter(PathInfo.path == path).first()
            before_path_snapshot_count = path_check.snapshot_count
            current_app.logger.info("Before Snapshot Count: [{}]".format(before_path_snapshot_count))
            after_path_snapshot_count = path_check.snapshot_count - 1
            current_app.logger.info("After Snapshot Count: [{}]".format(after_path_snapshot_count))

            # delete path in path_info once there's no more snapshots for this path
            if after_path_snapshot_count == 0:
                current_app.logger.info("[DELETE] PATH NAME: [{path}]".format(path=path))
                self.__session.query(PathInfo).filter(PathInfo.path == path).delete()
                self.__session.commit()
                current_app.logger.info("Successfully deleted path [{path}]".format(path=path))
                return True

            # snapshot count - 1
            else:
                current_app.logger.info("[UPDATE] PATH NAME: [{path}], snapshot count - 1".format(path=path))
                self.__session.query(PathInfo).filter(PathInfo.path == path).update(
                    {'snapshot_count': PathInfo.snapshot_count - 1})
                self.__session.commit()
                current_app.logger.info("Successfully updated snapshot count for path [{path}]".format(path=path))
                return False

        except Exception as e:
            current_app.logger.error(e)

    # RENAME
    def rename_snapshot(self, path, old_snapshot_name, new_snapshot_name):
        filters = and_(SnapshotInfo.path == path, SnapshotInfo.name == old_snapshot_name)
        try:
            # check whether snapshot exists before update
            self.__session.query(SnapshotInfo).filter(filters).one()

            # update snapshot name
            self.__session.query(SnapshotInfo).filter(filters).update({'name': new_snapshot_name})
            self.__session.commit()
        except NoResultFound as e:
            current_app.logger.error('No Result Found for path: {path}, snapshot_name: {snapshot_name}, {e}'.format(
                path=path, snapshot_name=old_snapshot_name, e=e))
            return

    # GET SNAPSHOT NAME
    def snapshot_name_init(self, path, snapshot_name):
        snapshot_name = snapshot_name if snapshot_name else self.__session.query(SnapshotInfo). \
            filter(SnapshotInfo.path == path). \
            order_by(SnapshotInfo.create_date).first().name
        return snapshot_name

    # 此方法暂时废弃，统一展示到一个页面
    def display_path(self, user, page_index=1, page_size=25):
        path_info_count = self.__session.query(PathInfo).filter(PathInfo.user == user).count()
        path_info_ls = self.__session.query(PathInfo).filter(PathInfo.user == user).slice((page_index - 1) * page_size,
                                                                                          page_index * page_size)
        return path_info_count, [{'path': path_info.path,
                                  'user': path_info.user,
                                  'snapshot_count': path_info.snapshot_count,
                                  'create_date': path_info.create_date,
                                  'modification_date': path_info.modification_date} for path_info in path_info_ls]

    # 此方法暂时废弃，统一展示到一个页面
    def display_snapshot(self, path, page_index=1, page_size=25):
        snapshot_info_count = self.__session.query(SnapshotInfo).filter(SnapshotInfo.path == path).count()
        snapshot_info_ls = self.__session.query(SnapshotInfo).filter(SnapshotInfo.path == path). \
            slice((page_index - 1) * page_size, page_index * page_size)
        return snapshot_info_count, [{'path': snapshot_info.path,
                                      'name': snapshot_info.name,
                                      'create_date': snapshot_info.create_date,
                                      'modification_date': snapshot_info.modification_date}
                                     for snapshot_info in snapshot_info_ls]

    def display_all(self, user, page_index=1, page_size=25):
        all_info_count = self.__session.query(PathInfo.user, PathInfo.snapshot_count, SnapshotInfo.path,
                                              SnapshotInfo.name, SnapshotInfo.create_date,
                                              SnapshotInfo.modification_date).join(PathInfo) \
            .filter(PathInfo.user == user).count()
        all_info_ls = self.__session.query(PathInfo.user, PathInfo.snapshot_count, SnapshotInfo.path,
                                           SnapshotInfo.name, SnapshotInfo.create_date,
                                           SnapshotInfo.modification_date).join(PathInfo).filter(PathInfo.user == user) \
            .slice((int(page_index) - 1) * int(page_size), int(page_index) * int(page_size))
        return all_info_count, [{'user': info[0],
                                 'snapshot_count': info[1],
                                 'path': info[2],
                                 'snapshot_name': info[3],
                                 'create_date': info[4],
                                 'modification_date': info[5]} for info in all_info_ls]

    def audit_log(self, user, action, path=None, snapshot_name=None, filename=None):
        current_app.logger.info('Adding audit log into server DB...')
        new_audit_log = AuditLog(user=user, action=action, path=path, snapshot_name=snapshot_name, filename=filename)
        self.__session.add(new_audit_log)
        self.__session.commit()
        current_app.logger.info('audit log added Successfully.')


if __name__ == '__main__':
    """
    Local test example.
    
    engine = create_engine('mysql+pymysql://{user}:{psw}@{host}:{port}/{db}'.format(
        user=MYSQL_CONFIGURES['USER'], psw=MYSQL_CONFIGURES['PSW'], host=MYSQL_CONFIGURES['HOST'],
        port=MYSQL_CONFIGURES['PORT'], db=MYSQL_CONFIGURES['DB']))
    db_session = sessionmaker(bind=engine)
    session = db_session()
    """
    pass

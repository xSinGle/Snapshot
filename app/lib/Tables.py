# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 13:26'

from sqlalchemy import Column, VARCHAR, INT, DATETIME, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base class for object
Base = declarative_base()


class PathInfo(Base):

    __tablename__ = 'path_info'

    '''
    CREATE TABLE path_info(
        id INT PRIMARY KEY auto_increment,
        path VARCHAR(255) UNIQUE NOT NULL,
        user VARCHAR(255) NOT NULL,
        snapshot_count INT NOT NULL default 0,
        create_date DATETIME NOT NULL DEFAULT current_timestamp,
        modification_date DATETIME ON UPDATE current_timestamp
    ) default charset='utf8mb4';
    '''
    id = Column(INT(), primary_key=True, autoincrement=True)
    path = Column(VARCHAR(255), nullable=False)
    user = Column(VARCHAR(255), nullable=False)
    snapshot_count = Column(INT(), nullable=False, server_default="1")
    create_date = Column(DATETIME(), server_default=func.now())
    modification_date = Column(DATETIME(), server_onupdate=func.now())


class SnapshotInfo(Base):

    __tablename__ = 'snapshot_info'

    '''
    CREATE TABLE snapshot_info (
        id INT primary key auto_increment,
        path VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        create_date DATETIME NOT NULL DEFAULT current_timestamp,
        modification_date DATETIME ON UPDATE current_timestamp,
        FOREIGN key(path) references path_info(path)
    ) DEFAULT charset='utf8mb4';
    '''
    id = Column(INT(), primary_key=True, autoincrement=True)
    path = Column(VARCHAR(255), ForeignKey("path_info.path"), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    create_date = Column(DATETIME(), nullable=False, server_default=func.now())
    modification_date = Column(DATETIME(), server_onupdate=func.now())

    path_info = relationship('PathInfo', backref='my_snapshot')


class AuditLog(Base):

    __tablename__ = 'audit_log'

    '''
    CREATE TABLE audit_log (
      id INT primary key auto_increment,
      user VARCHAR(255) not null,
      action VARCHAR(255) not null,
      path VARCHAR(1024),
      snapshot_name VARCHAR(1024),
      filename VARCHAR(255),
      action_date datetime NOT NULL default current_timestamp
    ) DEFAULT charset='utf8mb4';
    '''

    id = Column(INT(), primary_key=True, autoincrement=True)
    user = Column(VARCHAR(255), nullable=False)
    action = Column(VARCHAR(255), nullable=False)
    path = Column(VARCHAR(1024), nullable=True)
    snapshot_name = Column(VARCHAR(1024))
    filename = Column(VARCHAR(255), nullable=True)
    action_date = Column(DATETIME(), nullable=False, server_default=func.now())

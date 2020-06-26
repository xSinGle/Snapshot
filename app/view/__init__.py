# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 13:01'

from flask import Blueprint

view = Blueprint('view', __file__)

from . import DisplayApi
from . import SnapshotApi

import datetime
import json
import math
import time
from datetime import timedelta
from decimal import Decimal
from operator import attrgetter, itemgetter
import os
from flask import json, jsonify, request
from sqlalchemy import and_, between, exists, func, or_
from . import api
from .. import db
from ..models import *


def log_info(gatewayuid, action, content, insert_data, execute_state, role):
    insert_log = Log(
        id,
        gatewayuid,
        action,
        content,
        insert_data,
        execute_state,
        datetime.datetime.now(),
        role
    )
    db.session.add(insert_log)
    db.session.commit()

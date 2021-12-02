# -*- coding: utf-8 -*-

# Copyright (c) 2015 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of CKAN Data Requests Extension.

# CKAN Data Requests Extension is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CKAN Data Requests Extension is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with CKAN Data Requests Extension. If not, see <http://www.gnu.org/licenses/>.

import ckan.model as model
import ckan.plugins.toolkit as tk
from . import db
import humanize
import pytz
from dateutil.tz import tzlocal
from datetime import datetime, timedelta

from ckan.plugins.toolkit import c, config
from ckan import logic

def get_comments_number(datarequest_id):
    # DB should be intialized
    db.init_db(model)
    return db.Comment.get_comment_datarequests_number(datarequest_id=datarequest_id)

def get_comments_badge(datarequest_id):
    return tk.render_snippet('datarequests/snippets/badge.html',
                             {'comments_count': get_comments_number(datarequest_id)})

def get_open_datarequests_number():
    # DB should be initialized
    db.init_db(model)
    return db.DataRequest.get_open_datarequests_number()

def is_following_datarequest(datarequest_id):
    # DB should be intialized
    db.init_db(model)
    return len(db.DataRequestFollower.get(datarequest_id=datarequest_id, user_id=c.userobj.id)) > 0

def get_open_datarequests_badge(show_badge):
    '''The snippet is only returned when show_badge == True'''
    if show_badge:
        return tk.render_snippet('datarequests/snippets/badge.html',
                                 {'comments_count': get_open_datarequests_number()})
    else:
        return ''


def get_datarequest_statuses():
    default_statuses = [tk._('Open'),
                        tk._('In progress'),
                        tk._('Data holder contacted'),
                        tk._('Scheduled for release'),
                        tk._('Cannot be released'),
                        tk._('Not held by public sector')]
    statuses = config.get('ckanext.datarequest.statuses', False)
    if not statuses:
        statuses = default_statuses
    else:
        statuses_labels = statuses.split(',')
        statuses = []
        for status in statuses_labels:
            statuses.append(tk._(status))

    return [{'name': status, 'value': status} for status in statuses]
def check_access(action, data_dict=None):
    context = {'model': model,
               'user': c.user or c.author,
               'ignore_auth': config.get('ckan.datarequests.ignore_auth', False) }
    if not data_dict:
        data_dict = {}
    try:
        logic.check_access(action, context, data_dict)
        authorized = True
    except logic.NotAuthorized:
        authorized = False
 
    return authorized

def calculate_time_passed_comment(str):

    now = datetime.now()
    new_date = str.split('T')
    new_date = ' '.join(new_date)

    date_time_obj = datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S.%f')
    when_commented_aware = pytz.utc.localize(date_time_obj)

    now_aware = pytz.utc.localize(now)
    diff = humanize.naturaltime(now_aware - when_commented_aware)

    return diff

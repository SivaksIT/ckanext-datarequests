# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016 CoNWeT Lab., Universidad Politécnica de Madrid

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

import ckan.lib.helpers as h
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckanext.datarequests.auth as auth
import ckanext.datarequests.actions as actions
import ckanext.datarequests.constants as constants
import ckanext.datarequests.helpers as helpers
from ckanext.datarequests import cli
import os
import sys


from functools import partial
from ckan.common import config
from flask import session, redirect
from ckanext.datarequests.views.datarequests import datarequests

def get_config_bool_value(config_name, default_value=False):
    value = config.get(config_name, default_value)
    value = value if type(value) == bool else value != 'False'
    return value

def is_fontawesome_4():
    if hasattr(h, 'ckan_version'):
        ckan_version = float(h.ckan_version()[0:3])
        return ckan_version >= 2.7
    else:
        return False

def get_plus_icon():
    return 'plus-square' if is_fontawesome_4() else 'plus-sign-alt'

def get_question_icon():
    return 'question-circle' if is_fontawesome_4() else 'question-sign'


class DataRequestsPlugin(p.SingletonPlugin):

    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # ITranslation only available in 2.5+
    try:
        p.implements(p.ITranslation)
    except AttributeError:
        pass

    def __init__(self, name=None):
        self.comments_enabled = get_config_bool_value('ckan.datarequests.comments', True)
        self._show_datarequests_badge = get_config_bool_value('ckan.datarequests.show_datarequests_badge')
        self.name = 'datarequests'

    ######################################################################
    ############################## IACTIONS ##############################
    ######################################################################

    def get_actions(self):
        additional_actions = {
            constants.CREATE_DATAREQUEST: actions.create_datarequest,
            constants.SHOW_DATAREQUEST: actions.show_datarequest,
            constants.UPDATE_DATAREQUEST: actions.update_datarequest,
            constants.LIST_DATAREQUESTS: actions.list_datarequests,
            constants.DELETE_DATAREQUEST: actions.delete_datarequest,
            constants.CLOSE_DATAREQUEST: actions.close_datarequest,
            constants.FOLLOW_DATAREQUEST: actions.follow_datarequest,
            constants.UNFOLLOW_DATAREQUEST: actions.unfollow_datarequest,
        }

        if self.comments_enabled:
            additional_actions[constants.COMMENT_DATAREQUEST] = actions.comment_datarequest
            additional_actions[constants.LIST_DATAREQUEST_COMMENTS] = actions.list_datarequest_comments
            additional_actions[constants.SHOW_DATAREQUEST_COMMENT] = actions.show_datarequest_comment
            additional_actions[constants.UPDATE_DATAREQUEST_COMMENT] = actions.update_datarequest_comment
            additional_actions[constants.DELETE_DATAREQUEST_COMMENT] = actions.delete_datarequest_comment

        return additional_actions

    ######################################################################
    ########################### AUTH FUNCTIONS ###########################
    ######################################################################

    def get_auth_functions(self):
        auth_functions = {
            constants.CREATE_DATAREQUEST: auth.create_datarequest,
            constants.SHOW_DATAREQUEST: auth.show_datarequest,
            constants.UPDATE_DATAREQUEST: auth.update_datarequest,
            constants.LIST_DATAREQUESTS: auth.list_datarequests,
            constants.DELETE_DATAREQUEST: auth.delete_datarequest,
            constants.CLOSE_DATAREQUEST: auth.close_datarequest,
            constants.FOLLOW_DATAREQUEST: auth.follow_datarequest,
            constants.UNFOLLOW_DATAREQUEST: auth.unfollow_datarequest,
        }

        if self.comments_enabled:
            auth_functions[constants.COMMENT_DATAREQUEST] = auth.comment_datarequest
            auth_functions[constants.LIST_DATAREQUEST_COMMENTS] = auth.list_datarequest_comments
            auth_functions[constants.SHOW_DATAREQUEST_COMMENT] = auth.show_datarequest_comment
            auth_functions[constants.UPDATE_DATAREQUEST_COMMENT] = auth.update_datarequest_comment
            auth_functions[constants.DELETE_DATAREQUEST_COMMENT] = auth.delete_datarequest_comment

        return auth_functions

    ######################################################################
    ############################ ICONFIGURER #############################
    ######################################################################

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

        # Register this plugin's fanstatic directory with CKAN.
        tk.add_public_directory(config, 'public')

        # Register this plugin's fanstatic directory with CKAN.
        tk.add_resource('assets', 'datarequest')

    ######################################################################
    ######################### ITEMPLATESHELPER ###########################
    ######################################################################

    def get_helpers(self):
        return {
            'show_comments_tab': lambda: self.comments_enabled,
            'get_comments_number': helpers.get_comments_number,
            'get_comments_badge': helpers.get_comments_badge,
            'get_open_datarequests_number': helpers.get_open_datarequests_number,
            'get_open_datarequests_badge': partial(helpers.get_open_datarequests_badge, self._show_datarequests_badge),
            'get_plus_icon': get_plus_icon,
            'is_following_datarequest': helpers.is_following_datarequest,
            'calculate_time_passed_comment': helpers.calculate_time_passed_comment

        }

    ######################################################################
    ########################### ITRANSLATION #############################
    ######################################################################

    # The following methods are copied from ckan.lib.plugins.DefaultTranslation
    # and have been modified to fix a bug in CKAN 2.5.1 that prevents CKAN from
    # starting. In addition by copying these methods, it is ensured that Data
    # Requests can be used even if Itranslation isn't available (less than 2.5)

    def i18n_directory(self):
        '''Change the directory of the *.mo translation files
        The default implementation assumes the plugin is
        ckanext/myplugin/plugin.py and the translations are stored in
        i18n/
        '''
        # assume plugin is called ckanext.<myplugin>.<...>.PluginClass
        extension_module_name = '.'.join(self.__module__.split('.')[:3])
        module = sys.modules[extension_module_name]
        return os.path.join(os.path.dirname(module.__file__), 'i18n')

    def i18n_locales(self):
        '''Change the list of locales that this plugin handles
        By default the will assume any directory in subdirectory in the
        directory defined by self.directory() is a locale handled by this
        plugin
        '''
        directory = self.i18n_directory()
        return [ d for
                 d in os.listdir(directory)
                 if os.path.isdir(os.path.join(directory, d))
        ]

    def i18n_domain(self):
        '''Change the gettext domain handled by this plugin
        This implementation assumes the gettext domain is
        ckanext-{extension name}, hence your pot, po and mo files should be
        named ckanext-{extension name}.mo'''
        return 'ckanext-{name}'.format(name=self.name)

    ######################################################################
    ############################## IBLUEPRINT ############################
    ######################################################################
    def get_blueprint(self):
        return datarequests

    ######################################################################
    ################################ ICLICK ##############################
    ######################################################################

    def get_commands(self):      
        return cli.get_commands()

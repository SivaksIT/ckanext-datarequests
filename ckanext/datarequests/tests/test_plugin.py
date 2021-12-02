# -*- coding: utf-8 -*-

import ckanext.datarequests.plugin as plugin
import ckanext.datarequests.constants as constants
import unittest

from mock import MagicMock, patch
from parameterized import parameterized
import pytest

TOTAL_ACTIONS = 13
COMMENTS_ACTIONS = 5
ACTIONS_NO_COMMENTS = TOTAL_ACTIONS - COMMENTS_ACTIONS


class DataRequestPluginTest(unittest.TestCase):

    def setUp(self):
        self.actions_patch = patch('ckanext.datarequests.plugin.actions')
        self.actions_mock = self.actions_patch.start()

        self.auth_patch = patch('ckanext.datarequests.plugin.auth')
        self.auth_mock = self.auth_patch.start()

        self.tk_patch = patch('ckanext.datarequests.plugin.tk')
        self.tk_mock = self.tk_patch.start()

        self.config_patch = patch('ckanext.datarequests.plugin.config')
        self.config_mock = self.config_patch.start()

        self.helpers_patch = patch('ckanext.datarequests.plugin.helpers')
        self.helpers_mock = self.helpers_patch.start()

        self.partial_patch = patch('ckanext.datarequests.plugin.partial')
        self.partial_mock = self.partial_patch.start()

        self.h_patch = patch('ckanext.datarequests.plugin.h')
        self.h_mock = self.h_patch.start()

        self.create_datarequest = constants.CREATE_DATAREQUEST
        self.show_datarequest = constants.SHOW_DATAREQUEST
        self.update_datarequest = constants.UPDATE_DATAREQUEST
        self.list_datarequests = constants.LIST_DATAREQUESTS
        self.delete_datarequest = constants.DELETE_DATAREQUEST
        self.comment_datarequest = constants.COMMENT_DATAREQUEST
        self.list_datarequest_comments = constants.LIST_DATAREQUEST_COMMENTS
        self.show_datarequest_comment = constants.SHOW_DATAREQUEST_COMMENT
        self.update_datarequest_comment = constants.UPDATE_DATAREQUEST_COMMENT
        self.delete_datarequest_comment = constants.DELETE_DATAREQUEST_COMMENT
        self.follow_datarequest = constants.FOLLOW_DATAREQUEST
        self.unfollow_datarequest = constants.UNFOLLOW_DATAREQUEST

    def tearDown(self):
        self.actions_patch.stop()
        self.auth_patch.stop()
        self.tk_patch.stop()
        self.config_patch.stop()
        self.helpers_patch.stop()
        self.partial_patch.stop()
        self.h_patch.stop()

    def test_is_fontawesome_4_false_ckan_version_does_not_exist(self):
        delattr(self.h_mock, 'ckan_version')
        assert not plugin.is_fontawesome_4()

    def test_is_fontawesome_4_false_old_ckan_version(self):
        self.h_mock.ckan_version.return_value = '2.6.0'
        assert not plugin.is_fontawesome_4()

    def test_is_fontawesome_4_true_new_ckan_version(self):
        self.h_mock.ckan_version.return_value = '2.7.0'
        assert plugin.is_fontawesome_4()

    def test_get_plus_icon_new(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=True)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        assert 'plus-square' == plugin.get_plus_icon()

    def test_get_plus_icon_old(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=False)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        assert 'plus-sign-alt' == plugin.get_plus_icon()

    def test_get_question_icon_new(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=True)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        assert 'question-circle' == plugin.get_question_icon()

    def test_get_question_icon_old(self):

        is_fontawesome_4_patch = patch('ckanext.datarequests.plugin.is_fontawesome_4', return_value=False)
        is_fontawesome_4_patch.start()
        self.addCleanup(is_fontawesome_4_patch.stop)

        assert 'question-sign' == plugin.get_question_icon()

    @parameterized.expand([
        ('True',),
        ('False',)
    ])
    def test_get_actions(self, comments_enabled):

        actions_len = TOTAL_ACTIONS if comments_enabled == 'True' else ACTIONS_NO_COMMENTS

        # Configure config and create instance
        plugin.config.get.return_value = comments_enabled
        self.plg_instance = plugin.DataRequestsPlugin()
        
        # Get actions
        actions = self.plg_instance.get_actions()

        assert actions_len == len(actions)
        assert plugin.actions.create_datarequest == actions[self.create_datarequest]
        assert plugin.actions.show_datarequest == actions[self.show_datarequest]
        assert plugin.actions.update_datarequest == actions[self.update_datarequest]
        assert plugin.actions.list_datarequests == actions[self.list_datarequests]
        assert plugin.actions.delete_datarequest == actions[self.delete_datarequest]
        assert plugin.actions.follow_datarequest == actions[self.follow_datarequest]
        assert plugin.actions.unfollow_datarequest == actions[self.unfollow_datarequest]

        if comments_enabled == 'True':
            assert plugin.actions.comment_datarequest == actions[self.comment_datarequest]
            assert plugin.actions.list_datarequest_comments == actions[self.list_datarequest_comments]
            assert plugin.actions.show_datarequest_comment == actions[self.show_datarequest_comment]
            assert plugin.actions.update_datarequest_comment == actions[self.update_datarequest_comment]
            assert plugin.actions.delete_datarequest_comment == actions[self.delete_datarequest_comment]

    @parameterized.expand([
        ('True',),
        ('False',)
    ])
    def test_get_auth_functions(self, comments_enabled):

        auth_functions_len = TOTAL_ACTIONS if comments_enabled == 'True' else ACTIONS_NO_COMMENTS

        # Configure config and create instance
        plugin.config.get.return_value = comments_enabled
        self.plg_instance = plugin.DataRequestsPlugin()

        # Get auth functions
        auth_functions = self.plg_instance.get_auth_functions()

        assert auth_functions_len == len(auth_functions)
        assert plugin.auth.create_datarequest == auth_functions[self.create_datarequest]
        assert plugin.auth.show_datarequest == auth_functions[self.show_datarequest]
        assert plugin.auth.update_datarequest == auth_functions[self.update_datarequest]
        assert plugin.auth.list_datarequests == auth_functions[self.list_datarequests]
        assert plugin.auth.delete_datarequest == auth_functions[self.delete_datarequest]
        assert plugin.auth.follow_datarequest == auth_functions[self.follow_datarequest]
        assert plugin.auth.unfollow_datarequest == auth_functions[self.unfollow_datarequest]

        if comments_enabled == 'True':
            assert plugin.auth.comment_datarequest == auth_functions[self.comment_datarequest]
            assert plugin.auth.list_datarequest_comments == auth_functions[self.list_datarequest_comments]
            assert plugin.auth.show_datarequest_comment == auth_functions[self.show_datarequest_comment]
            assert plugin.auth.update_datarequest_comment == auth_functions[self.update_datarequest_comment]
            assert plugin.auth.delete_datarequest_comment == auth_functions[self.delete_datarequest_comment]

    def test_update_config(self):
        # Create instance
        self.plg_instance = plugin.DataRequestsPlugin()

        # Test
        config = MagicMock()
        self.plg_instance.update_config(config)
        plugin.tk.add_template_directory.assert_called_once_with(config, 'templates')

    @parameterized.expand([
        ('True',  'True'),
        ('True',  'False'),
        ('False', 'True'),
        ('False', 'False')
    ])
    def test_helpers(self, comments_enabled, show_datarequests_badge):
        # Configure config and get instance
        plugin.config = {
            'ckan.datarequests.comments': comments_enabled,
            'ckan.datarequests.show_datarequests_badge': show_datarequests_badge
        }
        self.plg_instance = plugin.DataRequestsPlugin()

        # Check result
        show_comments_expected = True if comments_enabled == 'True' else False
        helpers = self.plg_instance.get_helpers()
        assert helpers['show_comments_tab']() ==  show_comments_expected
        assert helpers['get_comments_number'] == plugin.helpers.get_comments_number
        assert helpers['get_comments_badge'] == plugin.helpers.get_comments_badge
        assert helpers['get_open_datarequests_number'] == plugin.helpers.get_open_datarequests_number
        assert helpers['get_open_datarequests_badge'] == plugin.partial.return_value

        # Check that partial has been called
        show_datarequests_expected = True if show_datarequests_badge == 'True' else False
        plugin.partial.assert_called_once_with(plugin.helpers.get_open_datarequests_badge, show_datarequests_expected)

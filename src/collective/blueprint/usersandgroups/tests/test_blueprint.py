# -*- coding: utf-8 -*-
"""Setup tests blueprint."""
from collective.blueprint.usersandgroups.blueprint import CreateGroup
from collective.blueprint.usersandgroups.blueprint import CreateUser
from collective.blueprint.usersandgroups.blueprint import UpdateUserProperties
from collective.blueprint.usersandgroups.testing import \
    COLLECTIVE_BLUEPRINT_USERSANDGROUPS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class Transmogrifier:

    def __init__(self, context):
        self.context = context


class TestCreateUser(unittest.TestCase):
    """Test CreateUser."""

    layer = COLLECTIVE_BLUEPRINT_USERSANDGROUPS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

    def test_create_user(self):
        """Test if user is created."""
        transmogrifier = Transmogrifier(self.portal)
        previous = [
            {
                '_password': 'password',
                '_username': 'username',
            },
        ]
        create_user = CreateUser(transmogrifier, 'create.user', None, previous)
        iterrator = iter(create_user)
        iterrator.next()
        user = api.user.get('username')
        self.assertTrue(user)


class TestCreateGroup(unittest.TestCase):
    """Test CreateGroup."""

    layer = COLLECTIVE_BLUEPRINT_USERSANDGROUPS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']

    def test_create_group(self):
        """Test if group is created."""
        transmogrifier = Transmogrifier(self.portal)
        previous = [
            {
                '_groupname': 'groupname',
            },
        ]
        create_group = CreateGroup(
            transmogrifier,
            'create.group',
            None,
            previous
        )
        iterrator = iter(create_group)
        iterrator.next()
        group = api.group.get('groupname')
        self.assertTrue(group)


class TestUpdateUserProperties(unittest.TestCase):
    """Test UpdateUserProperties."""

    layer = COLLECTIVE_BLUEPRINT_USERSANDGROUPS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.user.create(email='test@test.com', username='username')

    def test_update_user_properties(self):
        """Test if properties is set."""
        transmogrifier = Transmogrifier(self.portal)
        previous = [
            {
                '_username': 'username',
                '_user_groups': ['Site Administrators'],
                '_root_roles': ['Reviwer'],
                '_properties': {'fullname': 'João da Silva'},
            },
        ]
        update_user_properties = UpdateUserProperties(
            transmogrifier,
            'update.user.properties',
            None,
            previous,
        )
        iterrator = iter(update_user_properties)
        iterrator.next()
        user = api.user.get('username')
        self.assertTrue(user)
        fullname = user.getOrderedPropertySheets()[0].getProperty('fullname')
        self.assertEqual(fullname, 'João da Silva')
        roles = api.user.get_roles('username')
        self.assertEqual(
            roles,
            ['Site Administrator', 'Reviwer', 'Authenticated'],
        )
        groups = api.group.get_groups('username')
        groups_ids = [group.id for group in groups]
        self.assertEqual(
            groups_ids,
            ['AuthenticatedUsers', 'Site Administrators'],
        )

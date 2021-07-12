# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer

import collective.blueprint.usersandgroups


class CollectiveBlueprintUsersandgroupsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # @UnusedVariable
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.blueprint.usersandgroups)


COLLECTIVE_BLUEPRINT_USERSANDGROUPS_FIXTURE = CollectiveBlueprintUsersandgroupsLayer()


COLLECTIVE_BLUEPRINT_USERSANDGROUPS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_BLUEPRINT_USERSANDGROUPS_FIXTURE,),
    name='CollectiveBlueprintUsersandgroupsLayer:IntegrationTesting',
)


COLLECTIVE_BLUEPRINT_USERSANDGROUPS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_BLUEPRINT_USERSANDGROUPS_FIXTURE,),
    name='CollectiveBlueprintUsersandgroupsLayer:FunctionalTesting',
)

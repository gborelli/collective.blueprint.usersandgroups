from zope.interface import implements, classProvides
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite


class CreateUser(object):
    """ """

    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.regtool = getToolByName(self.context, 'portal_registration')

    def __iter__(self):
        for item in self.previous:

            if '_user__password' not in item.keys() or \
               '_user_username' not in item.keys():
                continue

            if self.regtool.isMemberIdAllowed(item['_user_username']):
                self.regtool.addMember(item['_user_username'],
                                item['_user__password'].encode('utf-8'))
            yield item


class UpdateUserProperties(object):
    """ """

    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.memtool = getToolByName(self.context, 'portal_membership')
        self.gtool = getToolByName(self.context, 'portal_groups')
        self.portal = getSite()

    def __iter__(self):
        for item in self.previous:

            if '_user_username' in item.keys():
                member = self.memtool.getMemberById(item['_user_username'])
                props = {}
                for key in item:
                    if key.startswith('_user_') and \
                            not key.startswith('_user__'):
                        props[key[6:]] = item[key]
                member.setMemberProperties(props)

                # add member to group
                if item.get('groups'):
                    for groupid in item['groups']:
                        group = self.gtool.getGroupById(groupid)
                        if group:
                            group.addMember(item['_user_username'])

                # setting global roles
                if item.get('roles'):
                    self.portal.acl_users.userFolderEditUser(
                                item['_user_username'],
                                None,
                                item['roles'])

            yield item


class CreateGroup(object):
    """ """

    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.gtool = getToolByName(self.context, 'portal_groups')

    def __iter__(self):
        for item in self.previous:
            if item.get('_group_id'):
                self.gtool.addGroup(item['_group_id'])
            yield item


class UpdateGroupProperties(object):
    """ """

    implements(ISection)
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.gtool = getToolByName(self.context, 'portal_groups')

    def __iter__(self):
        for item in self.previous:
            if not item.get('_group_id'):
                yield item; continue

            group = self.gtool.getGroupById(item['_group_id'])

            if item.get('_group_roles'):
                self.gtool.editGroup(item['_group_id'],
                                    roles=item['_group_roles'])

            props = {}
            for key in item:
                if key.startswith('_group_') and \
                   key != '_group_id' and \
                   key != '_group_roles':
                    props[key[7:]] = item[key]
            group.setProperties(props)
            yield item


from zope.interface import implements, classProvides
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from Products.CMFCore.utils import getToolByName


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

            self.regtool.addMember(item['_user_username'], item['_user__password'].encode('utf-8'))
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

    def __iter__(self):
        for item in self.previous:

            if '_user_username' in item.keys():
                member = self.memtool.getMemberById(item['_user_username'])
                props = {}
                for key in item:
                    if key.startswith('_user_') and not key.startswith('_user__'):
                        props[key[6:]] = item[key]
                member.setMemberProperties(props)

            yield item
             

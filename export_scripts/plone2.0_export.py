
import os
import simplejson

COUNTER = 1
GCOUNTER = 1
TEMP = '/opt/plone/unex_exported_users'
GTEMP = '/opt/plone/unex_exported_groups'
USERS = {}
GROUPS = []

def export(self):
    global COUNTER
    COUNTER = 1
    store_users([self])
    store_users(walk_all(self))

def export_groups(self):
    global GCOUNTER
    GCOUNTER = 1
    store_groups([self])
    store_groups(walk_all(self))


def walk_all(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]
        yield item
        if getattr(item, 'objectIds', None) and \
           item.objectIds():
            for subitem in walk_all(item):
                yield subitem

def store_users(items):
    global COUNTER
    global USERS
    for item in items:
        if item.__class__.__name__ == 'PloneSite':
            charset = item.portal_properties.site_properties.default_charset
            if not getattr(item, 'portal_membership', False):
                continue
            properties = []
            if  getattr(item, 'portal_memberdata', False):
                mdtool = item.portal_memberdata
                for pid in mdtool.propertyIds():
                    typ = mdtool.getPropertyType(pid)
                    properties.append((pid, typ))
            for member in item.portal_membership.listMembers():
                if member.getUserName() not in USERS.keys():
                    USERS[member.getUserName()] = str(member.getUser()._getPassword())
                user_data = {}
                user_data['_user_username'] = str(member.getUserName())
                user_data['_user__password'] = str(member.getUser()._getPassword())
                user_data['_user_roles'] = member.getRoles()
                user_data['_user_groups'] = []
                user_data['_plone_site'] = item.absolute_url()
                if getattr(member, 'getGroups', False):
                    user_data['_user_groups'] = member.getGroups()
                user_data['_properties'] = {}
                for pid, typ in properties:
                    val = member.getProperty(pid)
                    if typ in ('string', 'text'):
                        if getattr(val, 'decode', False):
                            try:
                                val = val.decode(charset, 'ignore')
                            except UnicodeEncodeError:
                                val = unicode(val)
                        else:
                            val = unicode(val)
                    user_data['_properties'][pid] = val
                write(user_data, TEMP, COUNTER)
                print '   |--> '+str(COUNTER)+' - '+str(member.getUserName())+'::'+str(member.getUser()._getPassword())
                COUNTER += 1
            print '--------------------------------------------------------------------------'
            return 'OK'



def store_groups(items):
    global GCOUNTER
    global GROUPS
    for item in items:
        if item.__class__.__name__ == 'PloneSite':
            charset = item.portal_properties.site_properties.default_charset
            properties = []
            if not getattr(item, 'portal_groups', False):
                continue
            gtool = item.portal_groups
            if getattr(item, 'portal_groupdata', False):
                gdtool = item.portal_groupdata
                for pid in gdtool.propertyIds():
                    typ = gdtool.getPropertyType(pid)
                    properties.append((pid, typ))
            for group in item.portal_groups.listGroups():
                if group.getUserName() not in GROUPS:
                    GROUPS.append(group.getUserName())
                group_data = {}
                group_data['_group_username'] = str(group.getUserName())
                group_data['_group_roles'] = group.getRoles()
                group_data['_plone_site'] = item.absolute_url()
                group_data['_properties'] = {}
                for pid, typ in properties:
                    val = group.getProperty(pid)
                    if typ in ('string', 'text'):
                        if getattr(val, 'decode', False):
                            try:
                                val = val.decode(charset, 'ignore')
                            except UnicodeEncodeError:
                                val = unicode(val)
                        else:
                            val = unicode(val)
                    group_data['_properties'][pid] = val
                write(group_data, GTEMP, GCOUNTER)
                print '   |--> '+str(GCOUNTER)+' - '+str(group.getUserName())+' IN: '+item.absolute_url()
                GCOUNTER += 1
            print '--------------------------------------------------------------------------'
            return 'OK'



def write(item, temp, counter):
    SUBTEMP = str(counter/1000) # 1000 files per folder
    if not os.path.isdir(os.path.join(temp, SUBTEMP)):
        os.mkdir(os.path.join(temp, SUBTEMP))

    f = open(os.path.join(temp, SUBTEMP, str(counter)+'.json'), 'wb')
    try:
        simplejson.dump(item, f, indent=4)
    except Exception, e:
        import pdb; pdb.set_trace()
    f.close()

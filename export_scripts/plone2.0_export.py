
import os
import simplejson

COUNTER = 1
TEMP = '/opt/plone/unex_exported_users_and_groups'
GROUPS = {}
USERS = {}

def export(self):
    global COUNTER
    COUNTER = 1
    get_users_and_groups([self], 1)
    get_users_and_groups(walk_all(self), 0)
    store_users_and_groups()

def walk_all(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]
        yield item
        if getattr(item, 'objectIds', None) and \
           item.objectIds():
            for subitem in walk_all(item):
                yield subitem

def get_users_and_groups(items, root):
    global GROUPS
    global GROUP_NAMES
    global USERS
    for item in items:
        if item.__class__.__name__ == 'PloneSite':
            charset = item.portal_properties.site_properties.default_charset
            properties = []
            if getattr(item, 'portal_groups', False):
                gtool = item.portal_groups
                if getattr(item, 'portal_groupdata', False):
                    gdtool = item.portal_groupdata
                    for pid in gdtool.propertyIds():
                        typ = gdtool.getPropertyType(pid)
                        properties.append((pid, typ))
                for group in item.portal_groups.listGroups():
                    group_name = str(group.getUserName())
                    if group.getUserName() not in GROUPS.keys():
                        GROUP_NAMES[group_name] = ''
                    else:
                        GROUP_NAMES[group_name] = item.getId()
                    group_data = {}
                    group_data['_name'] = group_name
                    group_data['_roles'] = group.getRoles()
                    group_data['_plone_site'] = '/'.join(item.getPhysicalPath())
                    group_data['_properties'] = {}
                    group_data['_root_group'] = root
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
                    GROUPS[group_name] = group_data
            if not getattr(item, 'portal_membership', False):
                continue
            properties = []
            if  getattr(item, 'portal_memberdata', False):
                mdtool = item.portal_memberdata
                for pid in mdtool.propertyIds():
                    typ = mdtool.getPropertyType(pid)
                    properties.append((pid, typ))
            for member in item.portal_membership.listMembers():
                user_data = {}
                username = str(member.getUserName())
                user_data['_username'] = user_name
                user_data['_password'] = str(member.getUser()._getPassword())
                user_data['_root_user'] = root
                user_data['_root_roles'] = []
                user_data['_local_roles'] = []
                if root:
                    user_data['_root_roles'] = member.getRoles()
                else:
                    user_data['_local_roles'] = member.getRoles()
                user_data['_groups'] = []
                user_data['_plone_site'] = '/'.join(item.getPhysicalPath())
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
                USERS[user_name] = user_data

def store_users_and_groups():
    global GROUPS
    global USERS
    global COUNTER
    for group_name, group_data in GROUPS.items():
        if GROUPS_NAMES[group_name]:
            group_data['_name'] += '_'+GROUP_NAMES[group_name]
        write(group_data)
        print '   |--> '+str(COUNTER)+' - '+str(group_data['_name'])+' IN: '+group_data['_plone_site']
        COUNTER += 1
    for user_name, user_data in USERS.items():
        groups = []
        for group in user_data['_groups']:
            groups.append(GROUP_NAMES[group])
        user_data['_groups'] = groups
        write(user_data)
        COUNTER += 1
        print '   |--> '+str(COUNTER)+' - '+str(user_data['_username'])+' IN: '+user_data['_plone_site']
    print '----------------------------  --------------------------------------'



def write(item):
    SUBTEMP = str(COUNTER/1000) # 1000 files per folder
    if not os.path.isdir(os.path.join(TEMP, SUBTEMP)):
        os.mkdir(os.path.join(TEMP, SUBTEMP))

    f = open(os.path.join(TEMP, SUBTEMP, str(TEMP)+'.json'), 'wb')
    simplejson.dump(item, f, indent=4)
    f.close()

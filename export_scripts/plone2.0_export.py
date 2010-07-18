
import os
import simplejson

COUNTER = 1
UTEMP = '/opt/plone/unex_exported_users'
GTEMP = '/opt/plone/unex_exported_groups'
GROUPS = {}
GROUP_NAMES = {}
USERS = {}

def export(self):
    get_users_and_groups([self], 1)
    get_users_and_groups(walk_all(self), 0)
    store_users_and_groups()
    return 'OK'

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
        if item.__class__.__name__ == 'PloneSite' and \
                        not item.getId().startswith('copy_of'):
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
                    group_name = str(group.getUserName()).replace(' ', '_').replace('-', '_')
                    if group.getUserName() in GROUPS.keys():
                        GROUP_NAMES[group_name] = 1
                        group_name = group_name+'_'+item.getId()
                        GROUP_NAMES[group_name] = 0
                    else:
                        GROUP_NAMES[group_name] = 0
                    group_data = {}
                    group_data['_groupname'] = group_name
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
                    if getattr(group, 'getGroups', False):
                        groups = group.getGroup().getGroups()
                        group_data['_group_groups'] = groups
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
                user_name = str(member.getUserName())
                user_data['_username'] = user_name
                user_data['_password'] = str(member.getUser()._getPassword())
                user_data['_root_user'] = root
                user_data['_root_roles'] = []
                user_data['_local_roles'] = []
                if root:
                    user_data['_root_roles'] = member.getRoles()
                else:
                    user_data['_local_roles'] = member.getRoles()
                user_data['_user_groups'] = []
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
                    if typ == 'date':
                        val = str(val)
                    user_data['_properties'][pid] = val
                USERS[user_name] = user_data

def store_users_and_groups():
    global GROUPS
    global USERS
    global COUNTER
    for group_name, group_data in GROUPS.items():
        if GROUP_NAMES[group_name]:
            group_data['_groupname'] += '_'+group_data['_plone_site'].strip('/').split('/')[-1]
        groups = fix_group_names(group_data['_group_groups'], group_data)
        group_data['_group_groups'] = groups
        write(group_data, GTEMP)
        print '   |--> '+str(COUNTER)+' - '+str(group_data['_groupname'])+' IN: '+group_data['_plone_site']
        COUNTER += 1
    for user_name, user_data in USERS.items():
        groups = fix_group_names(user_data['_groups'], user_data)
        user_data['_groups'] = groups
        write(user_data, UTEMP)
        COUNTER += 1
        print '   |--> '+str(COUNTER)+' - '+str(user_data['_username'])+' IN: '+user_data['_plone_site']
    print '----------------------------  --------------------------------------'

def fix_group_names(groupnames, data):
    groups = []
    for group in groupnames:
        if GROUP_NAMES[group]:
            group.replace(' ', '_').replace('-', '_')
            groups.append(group+'_'+data['_plone_site'].strip('/').split('/')[-1])
        else:
            groups.append(group)
    return groups


def write(item, temp):
    SUBTEMP = str(COUNTER/1000) # 1000 files per folder
    if not os.path.isdir(os.path.join(temp, SUBTEMP)):
        os.mkdir(os.path.join(temp, SUBTEMP))

    f = open(os.path.join(temp, SUBTEMP, str(COUNTER % 1000)+'.json'), 'wb')
    simplejson.dump(item, f, indent=4)
    f.close()

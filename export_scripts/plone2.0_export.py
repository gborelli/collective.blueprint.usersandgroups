
import os

COUNTER = 1
TEMP = DATA_DIR = '/Users/rok/Projects/yaco/unex-pcaro/unex/export_'
USERS = {}
DOUBLED = {}

def export(self):
    global COUNTER
    COUNTER = 1
    store_users([self])
    store_users(walk_all(self))
    return str(DOUBLED)

#from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces.base import IBaseObject
from Products.CMFCore.interfaces.DublinCore import DublinCore
def walk_all(folder):
    for item_id in folder.objectIds():
        item = folder[item_id]
        yield item
        if getattr(item, 'objectIds', None) and \
           item.objectIds():
            for subitem in walk_all(item):
                yield subitem
        
def walk(folder):
    global _types
    for item_id in folder.objectIds():
        item = folder[item_id]
       
        if item_id.startswith('portal_') or \
           item_id in ['plone_utils', 'MailHost', 'cookie_authentication', 'content_type_registry', 'acl_users',
                       'HTTPCache', 'RAMCache', 'caching_policy_manager', 'error_log', 'sin_tool', 'archetype_tool',
                       'PloneArticleThumbRAMCache', 'Members']:
            continue

        if item.__class__.__name__ not in [
                'LargePloneFolder', 'PloneFolder', 'I18NFolder', 'Document', 'Event', 'Image',
                'PloneSite', 'Topic', 'FriendlyDateCriterion', 'ListCriterion', 'SortCriterion',
                'NewsItem', 'File', 'Link', 'Folder', 'SimpleStringCriterion', 'PloneArticle',
                'ZPhotoSlides', 'ZPhoto', 'Favorite', 'PloneLocalFolderNG']:
            continue

        yield item

        if getattr(item, 'objectIds', None) and \
           item.objectIds():
            for subitem in walk(item):
                yield subitem

def store_users(items):
    global COUNTER
    global DOUBLED
    global USERS
    for item in items:
        if item.__class__.__name__ == 'PloneSite':
            print '--------------------------------------------------------------------------'
            print '>>> ['+item.__class__.__name__+'] '+item.absolute_url()
            for member in item.portal_membership.listMembers():
                if member.getUserName() not in USERS.keys():
                    USERS[member.getUserName()] = str(member.getUser()._getPassword())
                elif USERS[member.getUserName()] == str(member.getUser()._getPassword()):
                    continue
                elif USERS[member.getUserName()] != str(member.getUser()._getPassword()):
                    DOUBLED.setdefault(member.getUserName(), [USERS[member.getUserName()]])
                    DOUBLED[member.getUserName()].append(str(member.getUser()._getPassword()))
                    continue
                write({'_user_username': str(member.getUserName()),
                       '_user__password': str(member.getUser()._getPassword()),
                       '_user_email':    member.getProperty('email'),
                       '_user_fullname': member.getProperty('fullname').decode(item.portal_properties.site_properties.default_charset, 'ignore'),
                      })
                print '   |--> '+str(COUNTER)+' - '+str(member.getUserName())+'::'+str(member.getUser()._getPassword())
                COUNTER += 1
            print '--------------------------------------------------------------------------'
            
            #import pdb; pdb.set_trace()

def store(items):
    global COUNTER
    for item in items:
        print '>>> '+str(COUNTER)+' :: ['+item.__class__.__name__+'] '+item.absolute_url()
        if item.__class__.__name__ in ['LargePloneFolder', 'Folder', 'I18NFolder', 'PloneSite', 'PloneFolder', 'Topic']:
            write(BaseWrapper(item))
        elif item.__class__.__name__ in ['ListCriterion']:
            write(ListCriteriaWrapper(item))
        elif item.__class__.__name__ in ['SimpleStringCriterion']:
            write(StringCriteriaWrapper(item))
        elif item.__class__.__name__ in ['SortCriterion']:
            write(SortCriteriaWrapper(item))
        elif item.__class__.__name__ in ['FriendlyDateCriterion']:
            write(DateCriteriaWrapper(item))
        elif item.__class__.__name__ in ['Document']:
            write(DocumentWrapper(item))
        elif item.__class__.__name__ in ['Image', 'File']:
            write(FileWrapper(item))
        elif item.__class__.__name__ in ['Link', 'Favorite']:
            write(LinkWrapper(item))
        elif item.__class__.__name__ in ['Event']:
            write(EventWrapper(item))
        elif item.__class__.__name__ in ['NewsItem']:
            write(NewsItemWrapper(item))
        elif item.__class__.__name__ in ['PloneArticle']:
            write(ArticleWrapper(item))
        elif item.__class__.__name__ in ['ZPhotoSlides']:
            write(ZPhotoSlidesWrapper(item))
        elif item.__class__.__name__ in ['ZPhoto']:
            write(ZPhotoWrapper(item))
        elif item.__class__.__name__ in ['PloneLocalFolderNG']:
            write(ArchetypesWrapper(item))
        else:
            import pdb; pdb.set_trace()
        COUNTER += 1

import os
import simplejson

def write(item):
    global COUNTER
    SUBTEMP = str(COUNTER/1000) # 1000 files per folder
    if not os.path.isdir(os.path.join(TEMP, SUBTEMP)):
        os.mkdir(os.path.join(TEMP, SUBTEMP))

    j = 1
    if '__datafields__' in item.keys():
        for datafield in item['__datafields__']:
            datafield_path = os.path.join(TEMP, SUBTEMP, str(COUNTER)+'.json-file-'+str(j))
            f = open(datafield_path, 'wb')
            try:
                f.write(item[datafield]['data'])
            except:
                import pdb; pdb.set_trace()
            item[datafield]['data'] = datafield_path
            f.close()
            
            # check filesize if dont match look into why
            if item[datafield]['size'] != os.path.getsize(datafield_path):
                import pdb; pdb.set_trace()

            j += 1
        _empty = item.pop(u'__datafields__')

    f = open(os.path.join(TEMP, SUBTEMP, str(COUNTER)+'.json'), 'wb')
    try:
        simplejson.dump(item, f, indent=4)
    except:
        import pdb; pdb.set_trace()
    f.close()

    if getattr(item, '_files', None):
        i = 1
        for item in  item._files:
            raise Exception, 'NOT IMPLEMENTED'
            f = open(os.path.join(TEMP, SUBTEMP, COUNTER+'-file-'+str(i)+'.json'), 'wb')
            f.close()
            i += 1

from Products.CMFCore.utils import getToolByName
from AccessControl.Permission import Permission
from Acquisition import aq_base

def getPermissionMapping(acperm):
    result = {}
    for entry in acperm:
        result[entry[0]] = entry[1]
    return result


class BaseWrapper(dict):
    """Wraps the dublin core metadata and pass it as tranmogrifier friendly style
    """
    
    def __init__(self, obj):
        self.obj = obj
        
        self.portal = getToolByName(obj, 'portal_url').getPortalObject()
        self.portal_utils = getToolByName(obj, 'plone_utils')
        self.charset = self.portal.portal_properties.site_properties.default_charset

        if not self.charset: # newer seen it missing ... but users can change it
            self.charset = 'utf-8'

        self['__datafields__'] = []
        self['_path']      = self.obj.absolute_url()

        self['_type'] = self.obj.__class__.__name__
        
        self['id'] = obj.getId()
        self['title'] = obj.title.decode(self.charset, 'ignore')
        self['description'] = obj.description.decode(self.charset, 'ignore')

        # workflow history
        if hasattr(obj, 'workflow_history'):
            workflow_history = obj.workflow_history.data
            for w in workflow_history:
                for i, w2 in enumerate(workflow_history[w]):
                    workflow_history[w][i]['time'] = str(workflow_history[w][i]['time'])
                    workflow_history[w][i]['comments'] = workflow_history[w][i]['comments'].decode(self.charset, 'ignore')
            self['_workflow_history'] = workflow_history

        # default view
        _browser = '/'.join(self.portal_utils.browserDefault(obj)[1])
        if _browser not in ['folder_listing']:
            self['_layout'] = ''
            self['_defaultpage'] = _browser
        else:
            self['_layout'] = _browser
            self['_defaultpage'] = ''

        # format
        self['_content_type'] = obj.Format()
        
        # properties        
        self['_properties'] = []
        if getattr(aq_base(obj), 'propertyIds', False):
            for pid in obj.propertyIds():
                val = obj.getProperty(pid)
                typ = obj.getPropertyType(pid)
                if typ == 'string':
                    if getattr(val, 'decode', False):
                        try:
                            val = val.decode(self.charset, 'ignore')
                        except UnicodeEncodeError:
                            val = unicode(val)
                    else:
                        val = unicode(val)
                self['_properties'].append((pid, val,
                                       obj.getPropertyType(pid)))

        # local roles
        self['_ac_local_roles'] = {}
        if getattr(obj, '__ac_local_roles__', False):
            for key, val in obj.__ac_local_roles__.items():
                if key is not None:
                    self['_ac_local_roles'][key] = val

        self['_userdefined_roles'] = ()
        if getattr(aq_base(obj), 'userdefined_roles', False):
            self['_userdefined_roles'] = obj.userdefined_roles()

        self['_ac_inherited_permissions'] = {}
        if getattr(aq_base(obj), 'ac_inherited_permissions', False):
            oldmap = getPermissionMapping(obj.ac_inherited_permissions(1))
            for key, values in oldmap.items():
                old_p = Permission(key, values, obj)
                self['_ac_inherited_permissions'][key] = old_p.getRoles()


        if getattr(aq_base(obj), 'getWrappedOwner', False):
            self['_owner'] = (1, obj.getWrappedOwner().getId())
        else:
            # fallback
            # not very nice but at least it works
            # trying to get/set the owner via getOwner(), changeOwnership(...)
            # did not work, at least not with plone 1.x, at 1.0.1, zope 2.6.2
            self['_owner'] = (0, obj.getOwner(info = 1).getId())

class DocumentWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DocumentWrapper, self).__init__(obj)
        self['text'] = obj.text.decode(self.charset, 'ignore')

class ZPhotoWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ZPhotoWrapper, self).__init__(obj)
        self['show_exif'] = obj.show_exif
        self['exif'] = obj.exif
        self['iptc'] = obj.iptc
        self['path'] = obj.path
        self['dir'] = obj.dir
        self['filename'] = obj.filename
        #self['_thumbs'] = obj._thumbs
        self['dict_info'] = obj.dict_info
        self['format'] = obj.format
        self['tmpdir'] = obj.tmpdir
        self['backup'] = obj.backup
        
        abspath = os.path.abspath(obj.path)
        if os.path.exists(abspath):
            f = open(abspath)
            self['__datafields__'].append('_data')
            self['_data'] = {'data': str(f.read()), 'size': f.len}
            f.close()

class ZPhotoSlidesWrapper(BaseWrapper):

    def __init__(self, obj):
      super(ZPhotoSlidesWrapper, self).__init__(obj)
      try:
        self['update_date'] = str(obj.update_date)
        self['show_postcard'] = obj.show_postcard
        self['show_ARpostcard'] = obj.show_ARpostcard
        self['show_rating'] = obj.show_rating
        self['size'] = obj.size
        self['max_size'] = obj.max_size
        self['sort_field'] = obj.sort_field
        self['allow_export'] = obj.allow_export
        self['show_export'] = obj.show_export
        #self['visits_log'] = obj.visits_log
        self['non_hidden_pic'] = obj.non_hidden_pic
        self['list_non_hidden_pic'] = obj.list_non_hidden_pic
        self['rows'] = obj.rows
        self['column'] = obj.column
        self['zphoto_header'] = obj.zphoto_header
        self['list_photo'] = obj.list_photo
        self['zphoto_footer'] = obj.zphoto_footer
        self['symbolic_photo'] = obj.symbolic_photo
        self['keywords'] = obj.keywords
        self['first_big'] = obj.first_big
        self['show_automatic_slide_show'] = obj.show_automatic_slide_show
        self['show_viewed'] = obj.show_viewed
        self['show_exif'] = obj.show_exif
        self['photo_space'] = obj.photo_space
        self['last_modif'] = str(obj.last_modif)
        self['show_iptc'] = obj.show_iptc
        self['formats_available'] = obj.formats_available
        self['default_photo_size'] = obj.default_photo_size
        self['formats'] = obj.formats
        self['actual_css'] = obj.actual_css
        self['thumb_width'] = obj.thumb_width
        self['thumb_height'] = obj.thumb_height
        #self['list_rating'] = obj.list_rating
        self['photo_folder'] = obj.photo_folder
        self['tmpdir'] = obj.tmpdir
        self['lib'] = obj.lib
        self['convert'] = obj.convert
        self['use_http_cache'] = obj.use_http_cache
      except Exception, e:
        import pdb; pdb.set_trace()

class LinkWrapper(BaseWrapper):

    def __init__(self, obj):
        super(LinkWrapper, self).__init__(obj)
        self['remote_url'] = obj.remote_url

class NewsItemWrapper(DocumentWrapper):

    def __init__(self, obj):
        super(NewsItemWrapper, self).__init__(obj)
        self['text_format'] = obj.text_format

class ArticleWrapper(NewsItemWrapper):

    def __init__(self, obj):
        super(ArticleWrapper, self).__init__(obj)
        try:
            self['cooked_text'] = obj.cooked_text.decode(self.charset)
        except:
            self['cooked_text'] = obj.cooked_text.decode('latin-1')
    
        self['attachments_ids'] = obj.attachments_ids
        self['images_ids'] = obj.images_ids

class ListCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ListCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operator'] = obj.operator

class StringCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(StringCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value

class SortCriteriaWrapper(BaseWrapper):
    
    def __init__(self, obj):
        super(SortCriteriaWrapper, self).__init__(obj)
        self['index'] = obj.index
        self['reversed'] = obj.reversed

class DateCriteriaWrapper(BaseWrapper):

    def __init__(self, obj):
        super(DateCriteriaWrapper, self).__init__(obj)
        self['field'] = obj.field
        self['value'] = obj.value
        self['operation'] = obj.operation
        self['daterange'] = obj.daterange

class FileWrapper(BaseWrapper):

    def __init__(self, obj):
        super(FileWrapper, self).__init__(obj)
        self['__datafields__'].append('_data')
        self['_data'] = {'data': str(obj.data), 'size': obj.getSize()}
    
class EventWrapper(BaseWrapper):
    
    def __init__(self, obj):
        super(EventWrapper, self).__init__(obj)
        self['effective_date'] = str(obj.effective_date)
        self['expiration_date'] = str(obj.expiration_date)
        self['start_date'] = str(obj.start_date)
        self['end_date'] = str(obj.end_date)
        self['location'] = obj.location.decode(self.charset, 'ignore')
        self['contact_name'] = obj.contact_name.decode(self.charset, 'ignore')
        self['contact_email'] = obj.contact_email
        self['contact_phone'] = obj.contact_phone
        self['event_url'] = obj.event_url

class ArchetypesWrapper(BaseWrapper):

    def __init__(self, obj):
        super(ArchetypesWrapper, self).__init__(obj)

        fields = obj.schema.fields()
        for field in fields:
            type_ = field.__class__.__name__
            if type_ in ['StringField', 'BooleanField', 'LinesField', 'IntegerField', 'TextField',
                         'SimpleDataGridField', 'FloatField', 'FixedPointField']:
                try:
                    value = field.get(obj)
                except:
                    try:
                        value = field.getRaw(obj)
                    except:
                        if field.getStorage().__class__.__name__ == 'PostgreSQLStorage':
                            continue
                        else:
                            import pdb; pdb.set_trace()
                if callable(value) is True:
                    value = value()
                if value:
                    self[unicode(field.__name__)] = value
            elif type_ in ['TALESString', 'ZPTField']:
                value = field.getRaw(obj)
                if value:
                    self[unicode(field.__name__)] = value
            elif type_ in ['DateTimeField']:
                value = str(field.get(obj))
                if value:
                    self[unicode(field.__name__)] = value
            elif type_ in ['ReferenceField']:
                value = field.get(obj)
                if value:
                    if field.multiValued:
                        self[unicode(field.__name__)] = ['/'+i.absolute_url() for i in value]
                    else:
                        self[unicode(field.__name__)] = value.absolute_url()
            elif type_ in ['ImageField', 'FileField']:
                fieldname = unicode('_data_'+field.__name__)
                value = field.get(obj)
                value2 = value
                if type(value) is not str:
                    value = str(value.data)
                if value:
                    size = value2.getSize()
                    self['__datafields__'].append(fieldname)
                    self[fieldname] = {
                        'data': value,
                        'size': size,}
            elif type_ in ['ComputedField']:
                pass
            else:
                import pdb; pdb.set_trace()

    def _guessFilename(self, data, fname='', mimetype='', default=''):
        """
         Use the mimetype to guess the extension of the file/datafield if none exists.
         This is not a 100% correct, but does not really matter.
         In most cases it is nice that a word document has the doc extension, or that a picture has jpeg or bmp.
         It is a bit more human readable. When the extension is wrong it can just be ignored by the import anyway.
         """
        if not fname:
            return fname
        obj = self.obj
        mimetool = getToolByName(obj, 'mimetypes_registry')
        imimetype = mimetool.lookupExtension(fname)
        if mimetype and (imimetype is None): # no valid extension on fname
            # find extensions for mimetype
            classification = mimetool.classify(data, mimetype=mimetype)
            extensions = getattr(classification, 'extensions', default)
            extension = extensions[0] # just take the first one ... :-s
            fname = '%s.%s' % (fname, extension)
        return fname


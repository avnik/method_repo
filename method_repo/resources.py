import time
import binascii
import os
import datetime
import StringIO

import pytz
import colander
import deform.schema

from pyramid.security import (
    Allow,
    Everyone,
    )

from persistent import Persistent
from ZODB.blob import Blob

from substanced.content import content
from substanced.schema import Schema
from substanced.folder import Folder
from substanced.form import FileUploadTempStore
from substanced.property import PropertySheet
from substanced.site import (
    Site,
    SitePropertySheet,
    )

from .interfaces import (
    IMethodRepo,
    IMethodEntry,
    IComment,
    IFile,
    )

def make_name_validator(content_type):
    @colander.deferred
    def name_validator(node, kw):
        request = kw['request']
        context = request.context
        def exists(node, value):
            if request.registry.content.istype(context, content_type):
                if value != context.__name__:
                    try:
                        context.__parent__.check_name(value)
                    except Exception as e:
                        raise colander.Invalid(node, e.args[0], value)
            else:
                try:
                    context.check_name(value)
                except Exception as e:
                    raise colander.Invalid(node, e.args[0], value)

        return exists
    return name_validator

@colander.deferred
def now_default(node, kw):
    return datetime.date.today()

@colander.deferred
def upload_widget(node, kw):
    request = kw['request']
    tmpstore = FileUploadTempStore(request)
    return deform.widget.FileUploadWidget(tmpstore)

eastern = pytz.timezone('US/Eastern')

class FileUploadSchema(Schema):
    file = colander.SchemaNode(
        deform.schema.FileData(),
        widget = upload_widget,
        )

class FileUploadPropertySheet(PropertySheet):
    schema = FileUploadSchema()
    
    def get(self):
        context = self.context
        filedata = dict(
            fp=None,
            uid=str(context.__objectid__),
            filename='',
            )
        return dict(file=filedata)
    
    def set(self, struct):
        context = self.context
        file = struct['file']
        if file.get('fp'):
            fp = file['fp']
            fp.seek(0)
            context.upload(fp)
        

class MethodEntrySchema(Schema):
    name = colander.SchemaNode(
        colander.String(),
        validator = make_name_validator(IMethodEntry),
        )
    title = colander.SchemaNode(
        colander.String(),
        )
    pubdate = colander.SchemaNode(
       colander.DateTime(default_tzinfo=eastern),
       default = now_default,
       )

class MethodUploadSchema(Schema):
    name = colander.SchemaNode(
        colander.String(),
        validator = make_name_validator(IMethodEntry),
        )
    body = colander.SchemaNode(
        deform.schema.FileData(),
        widget = upload_widget,
        )

class MethodEntryPropertySheet(PropertySheet):
    schema = MethodEntrySchema()
    def get(self):
        context = self.context
        return dict(title=context.title,
                    pubdate=context.pubdate,
                    name=context.__name__)

    def set(self, struct):
        context = self.context
        if struct['name'] != context.__name__:
            context.__parent__.rename(context.__name__, struct['name'])
        context.title = struct['title']
        context.pubdate = struct['pubdate']

@content(
    IMethodEntry,
    name='Method Entry',
    icon='icon-book',
    add_view='add_entry',
    propertysheets=(
        ('Basic', MethodEntryPropertySheet),
        ),
    catalog=True,
    tab_order=('properties', 'contents', 'acl_edit'),
    )
class MethodEntry(Folder):
    def __init__(self, body):
        Folder.__init__(self)
        self.modified = datetime.datetime.now()
        self.pubdate = datetime.datetime.now()
        self.title = u""
        self['attachments'] = Folder()
        self['comments'] = Folder()
        if body.get('fp'):
            fp = body['fp']
            fp.seek(0)
            self.body = File(fp)
        else:
            raise RuntimeError("upload failed")

    def add_comment(self, comment):
        while 1:
            name = str(time.time())
            if not name in self:
                self['comments'][name] = comment
                break

_marker = object()


class FilePropertiesSchema(Schema):
    name = colander.SchemaNode(
        colander.String(),
        validator = make_name_validator(IFile),
        )
    mimetype = colander.SchemaNode(
        colander.String(),
        missing = 'application/octet-stream',
        )

class FilePropertySheet(PropertySheet):
    schema = FilePropertiesSchema()

    def get(self):
        context = self.context
        return dict(
            name=context.__name__,
            mimetype=context.mimetype
            )

    def set(self, struct):
        context = self.context
        newname = struct['name']
        mimetype = struct['mimetype']
        context.mimetype = mimetype
        oldname = context.__name__
        if newname and newname != oldname:
            context.__parent__.rename(oldname, newname)

@content(
    IFile,
    icon='icon-file',
    add_view='add_file',
    # prevent view tab from sorting first (it would display the file when
    # manage_main clicked)
    tab_order = ('properties', 'acl_edit', 'view'),
    propertysheets = (
        ('Basic', FilePropertySheet),
        ('Upload', FileUploadPropertySheet),
        ),
    catalog = True,
    )
class File(Persistent):
    def __init__(self, stream, mimetype='application/octet-stream'):
        self.mimetype = mimetype
        self.blob = Blob()
        self.upload(stream)
           
    def upload(self, stream):
        if not stream:
            stream = StringIO.StringIO()
        fp = self.blob.open('w')
        size = 0
        for chunk in chunks(stream):
            size += len(chunk)        
            fp.write(chunk)
        fp.close()
        self.size = size
        
def chunks(stream, chunk_size=10000):
    while True:
        chunk = stream.read(chunk_size)
        if not chunk: break
        yield chunk

class CommentSchema(Schema):
    commenter = colander.SchemaNode(
       colander.String(),
       )
    text = colander.SchemaNode(
       colander.String(),
       )
    pubdate = colander.SchemaNode(
       colander.DateTime(),
       default = now_default,
       )

class CommentPropertySheet(PropertySheet):
    schema = CommentSchema()

@content(
    IComment,
    name='Comment',
    icon='icon-comment',
    add_view='add_comment',
    propertysheets = (
        ('Basic', CommentPropertySheet),
        ),
    catalog = True,
    )
class Comment(Persistent):
    def __init__(self, commenter_name, text, pubdate):
        self.commenter_name = commenter_name
        self.text = text
        self.pubdate = pubdate

@content(
    IMethodRepo,
    name='Method Repo',
    icon='icon-home',
    propertysheets = (
        ('Basic', SitePropertySheet),
        ),
    )
class MethodRepo(Site):
    def __init__(self, initial_login, initial_email, initial_password):
        Site.__init__(self, initial_login, initial_email, initial_password)
        acl = list(getattr(self, '__acl__', []))
        acl.append((Allow, Everyone, 'view'))
        self.__acl__ = acl
        

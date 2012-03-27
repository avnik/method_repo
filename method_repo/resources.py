import datetime
from pyramid.decorator import reify
from composite.alchemist import get_session
from .document import ParsedDocument
from .backend.archive import Document
from .interfaces import IBackend

class ArchivableItem(object):
    klass = None
    user = "admin"
    path = ""
    description = ""
    comment = ""

    def __init__(self, doc, fileobj):
        self.document = doc
        self.docid = doc.docid
        self.attrs = {}
        self.blobs = { "..": fileobj }
        self.created = self.modified = datetime.datetime.now()
        parsed = ParsedDocument(fileobj)
        self.attrs["encoding"] = parsed["config"]["encoding"]

        #move it to event handler
        self.document.producer = parsed["header"]["producer"]
        self.title = self.document.name = parsed["header"]["name"]

class MethodFolder(object):
    __name__ = "methods"
    __title__ = "Methods"  # for breadcrumbs
    def __init__(self, request):
        self.request = request
        self.backend = self.request.registry.getUtility(IBackend)

    def __getitem__(self, key):
        context = get_session().query(Document).load(key)
        return self.backend.current(context.docid)

    def upload(self, fileobj):
        """Upload a new document"""
        document = Document()
        get_session().add(document)
        get_session().flush()  # not transaction safe
        item = ArchivableItem(document, fileobj)
        self.backend.archive(item)

class Root(object):
    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        """Stub"""
        if key == MethodFolder.__name__:
            return MethodFolder(self.request)
        raise KeyError

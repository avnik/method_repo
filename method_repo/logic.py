from persistent import Persistent
from zope.interface import implementer, Interface, Attribute
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import IObject, IContainer
from substanced.interfaces import IFolder
from substanced.content import content
from .interfaces import IMethodEntry, IVirtualSection, IVirtualList
from .schema import IMethodConfigurationSchema
from .parser import ParsedDocument

def compound_field(field):
    return IContainer.providedBy(field) or IObject.providedBy(field)

class CommonBullshit(object):
    def get(self, name, default=None):
        name = unicode(name)
        try:
            return self[name]
        except KeyError:
            return default

    def values(self):
        for each in self.keys():
            yield self[each]

    def exists(self, key):
        """For both VirtualSection and VirtualList, but not for root"""
        return key in self.context[self.__name__]

@content(IVirtualList)
@implementer(IFolder)
class VirtualList(CommonBullshit):
    __addable__ = ()
    def __init__(self, parent, name, context, schema):
        self.__name__ = name
        self.__parent__ = parent
        self.context = context
        self.schema = schema
        items = context[parent.__name__][name]
        self._items = map(lambda x: x.strip(), items.split(', '))

    def __getitem__(self, key):
        if key in self._items:
            return VirtualSection(self, key, self.context, self.schema.schema)
        raise KeyError(key)

    def keys(self):
        return iter(self._items)

    def items(self):
        for each in self.keys():
            yield each, self[each]

@content(IVirtualSection)
@implementer(IFolder)
class VirtualSection(CommonBullshit):
    __addable__ = ()
    def __init__(self, parent, name, context, schema):
        self.__name__ = name
        self.__parent__ = parent
        self.context = context
        if IObject.providedBy(schema):
            schema = schema.schema
        self.schema = schema

    def keys(self):
        for each in getFieldNamesInOrder(self.schema):
            field = self.schema[each]
            if compound_field(field):
                if self.exists(each):
                    yield each

    def items(self):
        for each in self.keys():
            yield each, self[each]
    
    def __getitem__(self, key):
        field = self.schema[key]
        if IContainer.providedBy(field):
            return VirtualList(self, key, self.context, field.value_type)
        elif IObject.providedBy(field):
            return VirtualSection(self, key, self.context, field.schema)
        raise KeyError(key)
        

@content(IFolder)
@implementer(IFolder)
class MethodEditor(VirtualSection, Persistent):
    __addable__ = ()
    _v_context = None

    @property
    def schema(self):
        return IMethodConfigurationSchema

    def exists(self, key):
        return key in self.context

    @property
    def context(self):
        if not self._v_context:
            self._v_context = ParsedDocument(self.__parent__.body.blob.open('r'))
        return self._v_context

    def __init__(self):
        pass


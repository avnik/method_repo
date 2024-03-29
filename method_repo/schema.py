from zope.interface import Interface
from zope.schema import Object
from zope.schema import BytesLine
from zope.schema import TextLine
from zope.schema import Text
from zope.schema import Id
from zope.schema import List

class IMethodConfigurationMagic(Interface):
    version = Id(title=u"Version")
    encoding = BytesLine(title=u".ini encoding")

class IMethodConfigurationHeader(Interface):
    lot = Text(title=u"lot description")
    producer = TextLine(title=u"Lot producer")
    name = TextLine(title=u"name") 

class ITechprocessStep(Interface):
    title = TextLine(title=u"Title")  
    text = Text(title=u"Description")
    duration = BytesLine(title=u"Duration")

class ITechprocess(Interface):
    steps = List(title=u"Techprocesses steps",
        value_type=Object(title=u"Techproces", schema=ITechprocessStep))

class IMethodConfigurationSchema(Interface):
    config = Object(title=u"Magic header", schema=IMethodConfigurationMagic)
    header = Object(title=u"Header for humans",
        schema=IMethodConfigurationHeader)
    techprocess = Object(title=u"Techprocesses list",
        schema=ITechprocess)

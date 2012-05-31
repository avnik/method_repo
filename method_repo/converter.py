#!/usr/bin/python
# -*- coding: utf-8 -*-
from translationstring import TranslationString
from zope.component import getUtility
from zope.schema import _bootstrapfields as zfields2
from zope.schema import _field as zfields
from zope.schema.interfaces import IVocabulary
from zope.schema.interfaces import IVocabularyFactory
from pyramid.threadlocal import get_current_registry
import colander
import deform

def getUtility(*a):
    get_current_registry().getUtility(*a)

class SequenceAsTuple(colander.Sequence):

    def serialize(
        self,
        node,
        appstruct,
        accept_scalar=None,
        ):
        return tuple(super(SequenceAsTuple, self).serialize(node,
                     appstruct, accept_scalar))

    def deserialize(
        self,
        node,
        cstruct,
        accept_scalar=None,
        ):
        return tuple(super(SequenceAsTuple, self).deserialize(node,
                     cstruct, accept_scalar))


class ZDateTime(colander.DateTime):

    def serialize(self, node, appstruct):
        if appstruct != colander.null:
            if hasattr(appstruct, 'asdatetime'):
                appstruct = appstruct.asdatetime()
        return super(ZDateTime, self).serialize(node, appstruct)


#    def deserialize(self, node, cstruct):
#        ob = datetime.strptime(cstruct, "%Y-%m-%dT%H:%M:%S")
#        return super(ZDateTime, self).deserialize(node, ob)


@colander.deferred
def deferredVocabularyValidator(node, kw):

    def validate(value):
        if node.field.vocabulary:
            factory = node.field.vocabulary
        else:
            factory = getUtility(IVocabularyFactory,
                                 name=node.field.vocabularyName)
        if IVocabulary.providedBy(factory):
            vocabulary = factory
        else:
            vocabulary = factory(kw['context'])
        try:
            vocabulary.getTerm(value)
            return True
        except LookupError:
            raise colander.Invalid(node, 'Illegal value selected',
                                   value)

    return colander.Function(validate)


@colander.deferred
def deferredVocularyWidget(node, kw):
    if node.field.vocabulary:
        factory = node.field.vocabulary
    else:
        factory = getUtility(IVocabularyFactory,
                             name=node.field.vocabularyName)
    if IVocabulary.providedBy(factory):
        vocabulary = factory
    else:
        vocabulary = factory(kw['context'])
    choices = [('', '- Select -')]
    for term in vocabulary.by_token.values():
        choices.append((term.value, term.title))
    return deform.widget.SelectWidget(values=choices)


def mapZopeFieldsToColanderFields(fields):

    def convertI18n(obj):
            return obj

    retval = {}
    adder = lambda typ, name, field, widget=None, validator=None: \
        retval.update({field: colander.SchemaNode(
            typ(),
            name=convertI18n(name),
            title=convertI18n(field.title),
            description=convertI18n(field.description),
            widget=widget,
            validator=validator,
            default=field.default or colander.null,
            )})
    for field in fields:
        field_cls = field.__class__
        name = field.__name__
        if field_cls in [
            zfields.URI,
            zfields.ASCIILine,
            zfields.ASCII,
            zfields2.Password,
            zfields2.TextLine,
            zfields2.Text,
            zfields.Bytes,
            zfields.BytesLine,
            zfields.Choice,
            ]:
            widget = None
            validator = None
            if field_cls in [zfields2.Text]:
                widget = deform.widget.TextAreaWidget(rows=10, cols=60)
            if field_cls in [zfields.Choice]:
                widget = deferredVocularyWidget
                validator = deferredVocabularyValidator
            adder(colander.String, name, field, widget, validator)
            retval[field].field = field
        elif field_cls in [zfields2.Bool]:
            adder(colander.Boolean, name, field)
        elif field_cls in [zfields.Float]:
            adder(colander.Float, name, field)
        elif field_cls in [zfields.Date]:
            adder(colander.Date, name, field)
        elif field_cls in [zfields.Datetime]:
            adder(ZDateTime, name, field)
        elif field_cls in [zfields2.Int]:
            adder(colander.Integer, name, field)
        elif field_cls == zfields.Tuple and field.value_type.__class__ \
            in [zfields2.TextLine]:

            if field.value_type.__class__ == zfields2.TextLine:
                default = field.default
                if default == None:
                    default = tuple()
                list_field = colander.SchemaNode(
                    SequenceAsTuple(),
                    colander.SchemaNode(colander.String(), name=name
                            + '_item', title=''),
                    name=convertI18n(name),
                    title=convertI18n(field.title),
                    description=convertI18n(field.description),
                    default=default,
                    )
                retval[field] = list_field
        elif field_cls == zfields.List and field.value_type.__class__ \
            in [zfields.Choice]:
            if field.value_type.__class__ == zfields.Choice:
                default = field.default
                if default == None:
                    default = []
                list_field = colander.SchemaNode(
                    colander.Sequence(),
                    colander.SchemaNode(
                        colander.String(),
                        widget=deferredVocularyWidget,
                        validator=deferredVocabularyValidator,
                        name=name + '_item',
                        title='',
                        field=field.value_type,
                        ),
                    name=convertI18n(name),
                    title=convertI18n(field.title),
                    description=convertI18n(field.description),
                    default=default,
                    )
                retval[field] = list_field
        else:
            retval[field] = None
        if not field.required:
            retval[field].missing = field.missing_value
    return retval


def convertToColander(fields):
    retval = colander.SchemaNode(colander.Mapping())
    mapping = mapZopeFieldsToColanderFields(fields)
    for field in fields:
        if not mapping[field]:
            raise TypeError('Oh, the mapping for %s has not been defined yet'
                             % field.__class__)
        retval.add(mapping[field])
    return retval

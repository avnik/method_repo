from webob.exc import HTTPFound
from substanced.sdi import mgmt_view
from substanced.form import FormView
from substanced.interfaces import ISite

from ..resources import (
    IMethodEntry,
    MethodEntrySchema,
    )

@mgmt_view(
    context=ISite,
    name='add_blog_entry',
    permission='sdi.add-content', 
    renderer='substanced.sdi:templates/form.pt',
    tab_condition=False,
    )
class AddMethodEntryView(FormView):
    title = 'Add Method Entry'
    schema = MethodEntrySchema()
    buttons = ('add',)

    def add_success(self, appstruct):
        name = appstruct.pop('name')
        request = self.request
        blogentry = request.registry.content.create(IMethodEntry, **appstruct)
        self.context[name] = blogentry
        loc = request.mgmt_path(self.context, name, '@@properties')
        return HTTPFound(location=loc)


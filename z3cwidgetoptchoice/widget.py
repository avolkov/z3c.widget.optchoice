import os.path
import zope.interface
import zope.schema
import zope.component
import zope.interface

from zope.component import provideAdapter
from zope.traversing.interfaces import ITraversable
from zope.traversing.adapters import DefaultTraversable
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form.widget import Widget, FieldWidget
from z3c.form import interfaces

class OptChoiceWidget(Widget):
    zope.interface.implements(interfaces.ISequenceWidget)
    value = ()
    terms = None
    klass = u'optchoice-widget'
    hw = "Hello, world!"
    noValueToken ='--NOVALUE--'

    def __init__(self, request):
        dirname = os.path.dirname(os.path.abspath(__file__))
        outp = os.path.join(dirname, 'templates', 'optchoice.pt')
        self.template = ViewPageTemplateFile(outp)
        super(self.__class__, self).__init__(request)

    def render(self):
        template = self.template
        return template(self)

    def updateTerms(self):
        if self.terms is None:
            self.terms = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.ITerms)
        return self.terms
    def update(self):
        """This is where all the interesting stuff happens"""
        self.updateTerms()
        super(self.__class__, self).update()
    def extract(self, default=interfaces.NO_VALUE):
        #Get value from the request
        #TODO: check that value exists
        value = self.request.get(self.name, default)
        #TODO: add more or fewer checks compared to SequenceWidget
        return value

@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
def OptChoiceWidgetFactory(field, request):
    """IFieldWidget factory for OptChoiceWidget"""
    return FieldWidget(field, OptChoiceWidget(request))
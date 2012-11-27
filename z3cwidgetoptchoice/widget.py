import os.path
import zope.interface
import zope.schema

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from z3c.form.widget import Widget, FieldWidget
from z3c.form import interfaces

class OptChoiceWidget(Widget):
    zope.interface.implements(interfaces.IWidget)
    klass = u'optchoice-widget'

    def __init__(self, request):
        dirname = os.path.dirname(os.path.abspath(__file__))
        outp = os.path.join(dirname, 'templates', 'optchoice.pt')
        self.template = ViewPageTemplateFile(outp)
        super(self.__class__, self).__init__(request)

    @property
    def items(self):
        if self.terms is None:
            return ()

    def render(self):
        template = self.template
        return template(self)

    def update(self):
        """This is where all the interesting stuff happens"""

@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
def OptChoiceWidgetFactory(field, request):
    """IFieldWidget factory for OptChoiceWidget"""
    return FieldWidget(field, OptChoiceWidget(request))
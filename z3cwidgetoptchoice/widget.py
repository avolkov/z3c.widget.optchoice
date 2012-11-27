from z3c.form.widget import Widget, WidgetTemplateFactory
import os.path
import inspect
class OptChoice(Widget):
    def __init__(self, request):
        dirname = os.path.dirname(os.path.abspath(__file__))
        outp = os.path.join(dirname, 'templates', 'optchoice.pt')
        self.template = WidgetTemplateFactory(outp)
        super(self.__class__, self).__init__(request)
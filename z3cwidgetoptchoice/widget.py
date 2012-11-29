import os.path
from functools import partial

import zope.interface
import zope.schema
import zope.component
import zope.interface

from zope.i18n import translate
from zope.component import provideAdapter
from zope.traversing.interfaces import ITraversable
from zope.traversing.adapters import DefaultTraversable
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement

from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser.widget import HTMLSelectWidget
from z3c.form import interfaces

class OptChoiceWidget(HTMLSelectWidget, Widget):
    zope.interface.implements(interfaces.ISequenceWidget)
    value = ()
    terms = None
    klass = u'optchoice-widget'
    noValueToken ='--NOVALUE--'
    other_token = None

    def __init__(self, request, other_token=None):
        dirname = os.path.dirname(os.path.abspath(__file__))
        outp = os.path.join(dirname, 'templates', 'optchoice.pt')
        self.template = ViewPageTemplateFile(outp)
        if other_token:
            self.other_token = other_token

        super(self.__class__, self).__init__(request)

    def render(self):
        template = self.template
        return template(self)

    def updateTerms(self):
        if self.terms is None:
            self.terms = zope.component.getMultiAdapter(
                (self.context, self.request, self.form, self.field, self),
                interfaces.ITerms
                                                        )
        if not self.other_token:
            return self.terms
        if self.other_token in self.terms:
            return self.terms
        #Add 'other' token to the end of options list
        try:
            verifyObject(interfaces.ITerms, self.other_token)
        except DoesNotImplement:
            #Prep the token that is presumably a tuple
            if len(self.other_token) == 2:
                list(self.other_token).append(self.other_token[-1])
            all_tokens = [ x for x in self.terms ]
            self.other_token = self.terms.createTerm(*self.other_token)
            all_tokens.append(self.other_token)
            self.terms = self.terms.__class__(all_tokens)
        return self.terms
    def update(self):
        """This is where all the interesting stuff happens"""
        self.updateTerms()
        super(self.__class__, self).update()
    def extract(self, default=interfaces.NO_VALUE):
        #Get value from the request
        #TODO: check that value exists
        value = self.request.get(self.name, default)
        if not isinstance(value, list):
            value = [value]
        if self.other_token and self.other_token.value in value:
            value = [self.request.get("%s-input" % self.name, default)]
        #TODO: add more or fewer checks compared to SequenceWidget
        return value
    def isSelected(self, term):
        return term.token in self.value
    @property
    def items(self):
        """
        Using z3c.form.browser.select -- SelectWidget.items
        """
        if self.terms is None:
            return ()
        items = []
        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = "%s-%i" % (self.id, count)
            content = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                content = translate(term.title, context=self.request,
                                    default=term.title)
            items.append({
                          'id':id,
                          'value':term.token,
                          'content':content,
                          'selected':selected,
                          })
        return items

@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
def OptChoiceWidgetFactory(field, request):
    """IFieldWidget factory for OptChoiceWidget"""
    return FieldWidget(field, OptChoiceWidget(request))

@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
def OptchoiceWidgetCustomTokenFactory(field, request, other_token=None):
    """
    IField widget factory that specifies other token for optional input field
    """
    return FieldWidget(field, OptChoiceWidget(request, other_token=other_token))

#Sorry for javascript names, I blame zope.
def OptChoiceWidgetCustomTokenFactoryFactory(token):
    """
    A factory that creates custom token with token set -- a case of currying
    """
    return partial(OptchoiceWidgetCustomTokenFactory, other_token=token)

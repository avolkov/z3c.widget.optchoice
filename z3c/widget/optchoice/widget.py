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
from zope.component.interfaces import ComponentLookupError

from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser.widget import HTMLSelectWidget
from z3c.form import interfaces
from z3c.form.error import ValueErrorViewSnippet

def convert_to_term(terms, to_convert):
    """
    Convert tuple into term of a vocabulary that implements
     interfaces.ITerms
    """
    try:
        verifyObject(zope.schema.interfaces.ITokenizedTerm, to_convert)
        return to_convert
    except DoesNotImplement:
        if len(to_convert) == 2:
                list(to_convert).append(to_convert[-1])
        return (x for x in terms).next().__class__(*to_convert)

def append_to_terms(terms, input_field_token):
    try:
        verifyObject(zope.schema.interfaces.ITokenizedTerm, input_field_token)
        all_terms = [ x for x in terms]
        if input_field_token.value in [ x.value for x in all_terms]:
            return (terms, terms.by_value[input_field_token.value], )
        all_terms.append(input_field_token)
        return (terms.__class__(all_terms), input_field_token)
    except ValueError:
        import traceback
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info() 
        e_stack = traceback.extract_tb(exc_traceback)
        import pdb; pdb.set_trace()

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
                    interfaces.ITerms)
        if not self.other_token:
            return self.terms
        self.other_token = convert_to_term(self.terms, self.other_token)
        if self.other_token in self.terms:
            return self.terms
        try:
            #Assume terms are SimpleVocabulary-ish
            verifyObject(zope.schema.interfaces.IVocabularyTokenized,
                         self.terms)
            self.terms, self.other_token = append_to_terms(self.terms,
                                                           self.other_token)
            return self.terms
        except DoesNotImplement:
            pass

        #Assume self.terms.terms is SimpleVocabulary-ish
        verifyObject(interfaces.ITerms, self.terms)
        verifyObject(zope.schema.interfaces.IVocabularyTokenized,
                      self.terms.terms)
        self.terms.terms, self.other_token = \
            append_to_terms(self.terms.terms, self.other_token)
        return self.terms
    def update(self):
        """This is where all the interesting stuff happens"""
        self.updateTerms()
        super(self.__class__, self).update()
    def extract(self, default=interfaces.NO_VALUE):
        """Extract values from the request"""
        value = self.request.get(self.name, default)
        if not isinstance(value, list):
            value = [value]
        if self.other_token and self.other_token.value in value:
            value = [self.request.get("%s-input" % self.name, default)]
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

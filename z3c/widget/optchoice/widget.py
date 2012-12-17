import os.path
from datetime import datetime
from functools import partial

import zope.interface
import zope.schema
import zope.component
from zope.schema.interfaces import RequiredMissing

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

def wrapGW(func):
    """Wrap GetValue function, but this could be used in other cases"""
    def wrappedGW(token):
        """Return value token even if it is not in list"""
        try:
            return func(token)
        except LookupError:
            return token
    return wrappedGW

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
    verifyObject(zope.schema.interfaces.ITokenizedTerm, input_field_token)
    all_terms = [ x for x in terms]
    if input_field_token.value in [ x.value for x in all_terms]:
        return (terms, terms.by_value[input_field_token.value], )
    all_terms.append(input_field_token)
    return (terms.__class__(all_terms), input_field_token)

class OptChoiceWidget(HTMLSelectWidget, Widget):
    zope.interface.implements(interfaces.ISequenceWidget)
    value = ()
    klass = u'optchoice-widget'
    noValueToken ='--NOVALUE--'
    other_token = None
    other_selected = False
    onchange = open(os.path.join(os.path.dirname(__file__),
                                 'js/show_input_field.js')).read()
    _terms = None
    value = None
    @property
    def terms(self):
        return self._terms
    @terms.setter
    def terms(self, value):
        self._terms = value
        self._terms.getValue = wrapGW(self.terms.getValue)
    @terms.deleter
    def terms(self):
        del self._terms

    def __init__(self, request, other_token=None):
        dirname = os.path.dirname(os.path.abspath(__file__))
        outp = os.path.join(dirname, 'templates', 'optchoice.pt')
        self.template = ViewPageTemplateFile(outp)
        
        if other_token:
            self.other_token = other_token
        super(self.__class__, self).__init__(request)

    def render(self):
        self.onchange = self.onchange.replace(
                                "NAME_PLACEHOLDER", "%s:textarea" % self.name)
        self.onchange = self.onchange.replace(
                                "VALUE_PLACEHOLDER", self.other_token.token)
        return self.template(self)

    def updateTerms(self):
        if self.value:
            self._validate(self.value)
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

        #Assume self.terms.terms are SimpleVocabulary-ish
        verifyObject(interfaces.ITerms, self.terms)
        verifyObject(zope.schema.interfaces.IVocabularyTokenized,
                      self.terms.terms)
        self.terms.terms, self.other_token = \
            append_to_terms(self.terms.terms, self.other_token)
        return self.terms
    def _validate(self, value):
        if len(value) == 1 and not value[0]:
            raise RequiredMissing
    def update(self):
        """This is where all the interesting stuff happens"""
        self.updateTerms()
        super(self.__class__, self).update()
    def extract(self, default=interfaces.NO_VALUE):
        """Extract values from the request"""
        value = self.request.get(self.name, default)
        if not isinstance(value, list):
            value = [value]
        if unicode(value[0]) == unicode(self.other_token.token):
            value = value[1:]
        self.value = value
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
    if other_token:
        other_token = tuple([ unicode(x) for x in other_token ])
    return FieldWidget(field, OptChoiceWidget(request, other_token=other_token))

#Sorry for javascript names, I blame zope.
def OptChoiceWidgetCustomTokenFactoryFactory(token):
    """
    A factory that creates custom token with token set -- a case of currying
    """
    return partial(OptchoiceWidgetCustomTokenFactory, other_token=token)

import unittest2 as unittest

import zope.interface
import zope.schema
from zope import component
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.namespace import view
from zope.component.interfaces import ComponentLookupError

from z3c.form.term import ChoiceTermsVocabulary
from z3c.form.testing import TestRequest
from z3c.schema.optchoice import OptionalChoice
from z3c.form import form, field, interfaces, testing, action
from z3c.schema.optchoice.interfaces import IOptionalChoice

from zope.configuration import xmlconfig
from widget import OptChoiceWidget, OptChoiceWidgetCustomTokenFactoryFactory


class Terms(SimpleVocabulary):
    zope.interface.implements(interfaces.ITerms)
    def getValue(self, token):
        return self.getTermByToken(token).value

sample_terms = Terms([
        SimpleTerm(value="first", title="First"),
        SimpleTerm(value="second", title="Second")
                    ])
longer_sample_terms = Terms([
        SimpleTerm(value="f1", title="One"),
        SimpleTerm(value="f2", title="Two"),
        SimpleTerm(value="f3", title="Three"),
        SimpleTerm(value="f4", title="Four"),
        SimpleTerm(value="f5", title="Five"),
        SimpleTerm(value="f6", title="Six"),
        SimpleTerm(value="f7", title="Seven"),
        SimpleTerm(value="f8", title="Eight"),
                            ])
ot = ('other', "Other")

comparison_terms = ["first", "second"]

class ISchema(zope.interface.Interface):
    test_name = OptionalChoice(
            title= u"This is a title",
            values=sample_terms,
            value_type=zope.schema.TextLine(),
                          )
class SampleForm(form.AddForm):
    fields = field.Fields(ISchema)
    fields['test_name'].widgetFactory = \
        OptChoiceWidgetCustomTokenFactoryFactory(('other', "Other"))

class TestActions(action.Actions):
    def append(self, name, action):
        """See z3c.form.interfaces.IActions"""
        if not name in self:
            self._data_keys.append(name)
        self._data_values.append(action)
        self._data[name] = action

class TestContent(object):
    zope.interface.implements(interfaces.IForm)

class TestBasicOptChoice(unittest.TestCase):
    def setUp(self):
        self.request = TestRequest()
        #http://www.llakomy.com/articles/testing-templates-with-zope-2.10
        #plone.z3cform/tests.py
        component.provideAdapter(DefaultTraversable, [None])

    def test_import(self):
        self.assertEqual(OptChoiceWidget.__name__, 'OptChoiceWidget')

    def test_custom_template_noterms(self):
        """Sequence widget with no terms raises ComponentLookupError"""
        oc = OptChoiceWidget(self.request)
        with self.assertRaises(ComponentLookupError):
            oc.update()
            data = oc.render()

    def test_custom_template_terms(self):
        oc = OptChoiceWidget(self.request)
        oc.terms = sample_terms
        oc.name = 'opt-widget'
        oc.ignoreContext = True
        oc.update()
        data = oc.render()
        self.assertGreaterEqual(len(data), 28)

    def test_custom_template_terms2(self):
        """A call to update doesn't change the terms"""
        oc = OptChoiceWidget(self.request)
        oc.name = 'opt-widget'
        oc.terms = sample_terms
        oc.update()
        self.assertListEqual([x.value for x in oc.terms], comparison_terms )

    def test_init_widget(self):
        opt_widget = OptChoiceWidget(self.request)
        opt_widget.name = 'opt-choice'
        self.assertIsNone(opt_widget.terms)

    def test_render_sequence(self):
        opt_widget = OptChoiceWidget(self.request)
        opt_widget.name = 'opt-choice'
        opt_widget.id = 'oc1'
        opt_widget.terms = longer_sample_terms
        opt_widget.update()
        rendered_data = opt_widget.render()
        self.assertIn('id="oc1"', rendered_data)
        self.assertIn('id="oc1-0"', rendered_data)
        self.assertIn('id="oc1-7"', rendered_data)
        self.assertEqual(8, rendered_data.count('value="f'))

    def test_optional_input_token_present(self):
        """Make sure that the optional input token is appended to the list"""
        token_widget = OptChoiceWidget(self.request,other_token=ot)
        token_widget.name = 'opt-choice-in'
        token_widget.id = 'tw'
        token_widget.terms = longer_sample_terms
        token_widget.update()
        items = token_widget.items
        self.assertEqual(len(items), len(longer_sample_terms)+1)
        self.assertEqual(items[-1]['content'], 'Other')

    def test_select_input_extract(self):
        """Base case for extract method -- select one of the values"""
        oc = OptChoiceWidget(self.request)
        oc.name = oc.id = 'oc'
        oc.terms = sample_terms
        oc.request = TestRequest(form={'oc':['first']})
        values = oc.extract()
        self.assertListEqual(values, ['first'])

    def test_select_custom_input(self):
        """Extract data from input field"""
        """Base case for extract method -- select one of the values"""
        oc = OptChoiceWidget(self.request, other_token=ot)
        oc.name = oc.id = 'oc'
        oc.terms = sample_terms
        oc.update()
        oc.request = TestRequest(form={'oc':['other'], 'oc-input':'testval1'})
        values = oc.extract()
        self.assertListEqual(['testval1'], values)

    def test_custom_token_factory(self):
        factory = OptChoiceWidgetCustomTokenFactoryFactory(ot)
        self.assertDictEqual(factory.keywords,
                              {'other_token':('other', 'Other')})

    def test_select_in_wrapper(self):
        """
        Test when SimpleVocabulary is wrapped with
        z3c.form.term.ChoiceTermsVocabulary
        """
        ct = ChoiceTermsVocabulary(*[None]*6)
        ct.terms = sample_terms
        oc = OptChoiceWidget(self.request, other_token=ot)
        oc.name = oc.id = 'optional_widget'
        oc.terms = ct
        oc.update()
        self.assertEquals(len(oc.terms.terms), len(sample_terms)+1)

    def test_select_in_wrapper_SimpleTerm(self):
        """
        Test when SimpleVocabulary is wrapped with
        z3c.form.term.ChoiceTermsVocabulary, passing SimpleTerm instead of a
         tuple
        """
        ct = ChoiceTermsVocabulary(*[None]*6)
        ct.terms = sample_terms
        oc = OptChoiceWidget(self.request,
                             other_token=SimpleTerm('other', "Other", "Other")
                            )
        oc.name = oc.id = 'optional_widget'
        oc.terms = ct
        oc.update()
        self.assertEquals(len(oc.terms.terms), len(sample_terms)+1)

def setupWidget(field):
    request = TestRequest()
    widget = zope.component.getMultiAdapter((field, request), 
                                            interfaces.IFieldWidget)
    widget.id = 'foo'
    widget.name = 'bar'
    return widget


class TestFunctionalForm(unittest.TestCase):
    def setUp(self):
        testing.setUp(self)
        component.provideAdapter(field.FieldWidgets)
        component.provideAdapter(DefaultTraversable, [None])
        self.context = self.globs['root']
    def tearDown(self):
        testing.tearDown(self)
    def test_add_form(self):
        sample_form = SampleForm(self.context, TestRequest())
        data = sample_form.updateWidgets()
    def test_update_form(self):
        content = TestContent()
        request = TestRequest()
        component.provideAdapter(self.context.__class__ , interfaces.IAction)
        form = SampleForm(self.context, request)
        manager = TestActions(form, request, content)
        form.update()

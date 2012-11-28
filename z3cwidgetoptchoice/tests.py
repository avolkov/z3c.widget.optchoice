import unittest2 as unittest

from zope import component
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.namespace import view
from z3c.form.testing import TestRequest
from widget import OptChoiceWidget
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.component.interfaces import ComponentLookupError

sample_terms = SimpleVocabulary([
                        SimpleTerm(value="first", title="First"),
                        SimpleTerm(value="second", title="Second")
                                ])
comparison_terms = ["first", "second"]

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

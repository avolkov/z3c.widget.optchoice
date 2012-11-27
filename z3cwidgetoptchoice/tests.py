import unittest2 as unittest
from z3c.form.testing import TestRequest
from widget import OptChoiceWidget
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.component.interfaces import ComponentLookupError

class TestBasicOptChoice(unittest.TestCase):
    def setUp(self):
        self.request = TestRequest()
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
        oc.terms = SimpleVocabulary([
                        SimpleTerm(value="first", title="First"),
                        SimpleTerm(value="second", title="Second")
                                    ])
        oc.update()
        data = oc.render()
        import pdb; pdb.set_trace()
        self.assertGreaterEqual(len(data), 28)
    def test_init_widget(self):
        opt_widget = OptChoiceWidget(self.request)
        opt_widget.name = 'opt-choice'
        self.assertIsNone(opt_widget.terms)

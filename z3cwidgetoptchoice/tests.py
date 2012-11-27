import unittest2 as unittest
from z3c.form.testing import TestRequest

class TestBasicOptChoice(unittest.TestCase):
    def setUp(self):
        self.request = TestRequest()
    def test_init(self):
        from widget import OptChoice
        self.assertEqual(OptChoice.__name__, 'OptChoice')
    def test_custom_template(self):
        from widget import OptChoice
        oc = OptChoice(self.request)
        self.assertEquals(oc.template.template(oc), u'<h1>Hello, world!</h1>\n')
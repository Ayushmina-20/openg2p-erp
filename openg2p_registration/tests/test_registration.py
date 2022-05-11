from odoo.exceptions import Warning
from odoo.tests import common, tagged
from .testingdata1 import testing_data1
from .testingdata2 import testing_data2
from .testingdata3 import testing_data3
from .testingdata4 import testing_data4
import unittest

@tagged('standard','at-install','registration')
class RegistrationTestModule(unittest.TestCase):
    def setUp(self):
        print('this is setUP')
        super(RegistrationTestModule, self).setUp()
        # add test setup code here

    def test_data(self):
        print('hello entering to test')
        test_case1 = self.env['openg2p.registration'].create_registration_from_odk(testing_data1)
        self.assertIsNone(test_case1.id, msg="ID is empty")
        print("Test is successful")
        # testcase2
        test_case2 = self.env['openg2p.registration'].create_registration_from_odk(testing_data2)
        self.assertIsNone(test_case2.id, msg="ID is empty")
        print("Test is successful")
        # testcase3
        test_case3 = self.env['openg2p.registration'].create_registration_from_odk(testing_data3)
        self.assertIsNone(test_case3.id, msg="ID is empty")
        print("Test is successful")
        # testcase4
        test_case4 = self.env['openg2p.registration'].create_registration_from_odk(testing_data4)
        self.assertIsNotNone(test_case4.id, msg="ID is empty")
        print("Test is successful")

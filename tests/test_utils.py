from unittest import TestCase
from pbvoting.utils import *

class TestUtils(TestCase):
    def test_gini(self):
        test_1 = [0,0,0,0,100]
        assert(gini_coefficient(test_1) == 0.8)
        test_2 = [0,0,0,0,0]
        assert(gini_coefficient(test_2) == 0) 
        # test_3 = [-10,0,10]
        # TestCase.assertRaises(BaseException, lambda: gini_coefficient(test_3))
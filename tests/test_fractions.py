from unittest import TestCase
from pbvoting.fractions import *

import pbvoting.fractions


class TestFractions(TestCase):

    def test_fraction_toggle(self):
        assert isinstance(frac(3, 2), mpq)
        pbvoting.fractions.FRACTION = "float"
        assert not isinstance(frac(3, 2), mpq)
        assert isinstance(frac(3, 2), float)

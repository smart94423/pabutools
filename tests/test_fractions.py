"""
Module testing the custom fractions.
"""
from unittest import TestCase
from pabutools.fractions import *

import pabutools.fractions


class TestFractions(TestCase):
    def test_fraction_toggle(self):
        pabutools.fractions.FRACTION = "gmpy2"
        assert isinstance(frac(3, 2), mpq)
        assert isinstance(str_as_frac("4"), mpq)
        pabutools.fractions.FRACTION = "float"
        assert not isinstance(frac(3, 2), mpq)
        assert isinstance(frac(3, 2), float)
        assert isinstance(str_as_frac("4"), float)

    def test_frac_one_arg(self):
        pabutools.fractions.FRACTION = "gmpy2"
        assert frac(2) == mpq(2)
        pabutools.fractions.FRACTION = "float"
        assert frac(2) == 2.0

    def test_frac_two_arg(self):
        pabutools.fractions.FRACTION = "gmpy2"
        assert frac(2, 54) == mpq(2, 54)
        pabutools.fractions.FRACTION = "float"
        assert frac(2, 10) == 0.2

    def test_frac_exception(self):
        with self.assertRaises(ValueError):
            pabutools.fractions.FRACTION = "lalalalalalaksdjbqksbdsd"
            frac(0)
        with self.assertRaises(ValueError):
            pabutools.fractions.FRACTION = "lalalalalalaksdjbqksbdsd"
            frac(0, 4)
        with self.assertRaises(ValueError):
            frac(3, 4, 5)

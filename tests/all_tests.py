#!/usr/bin/env python

"""Tests for `pbvoting` package."""

import pytest

from .test_instance import *
from .test_pabulib import *
from .test_profile import *
from .test_rule import *
from .test_properties import *
from .test_utils import *


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""

    test_instance_as_set()
    test_instance()
    test_projects()

    test_approval()
    test_cumulative()

    test_approval_profile()
    test_approval_ballot()

    test_greedy_welfare_approval()
    test_mes_approval()

    test_satisfaction_properties()

    test_gini()

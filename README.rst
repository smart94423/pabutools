========
pbvoting
========


Overview
========

Pbvoting is a python package providing many tools to work with
participatory budgeting instances.

Participatory budgeting (PB) is a democratic tool used to allocate
a given amount of money to a collection of projects based on a
group of individuals' preferences over the projects. It has been invented
in Brazil in the late 80's and is now a widely implemented. See the
`Wikipedia page <https://en.wikipedia.org/wiki/Participatory_budgeting>`
for more details.

In this library we provide the tools to handle PB instances of different
kinds, together with voting rules to determine the outcome of the elections
and some analytic tools. In particular, we provide full support for the
instances taken from `pabulib <http://pabulib.org/>`, the reference library
when it comes to PB data.

Installation
============

Ultimately, the goal is to host this library on pip. For now, use the
source code provided here.

Usage
=====

PB Instances and Profiles
-------------------------

The basic components are the instances and the profiles. An instance
includes the projects that are being voted on, together with the budget
limit. A profile is a collection of votes, one per voter.

Let's start with the instances. The main class here is
:code:`PBInstance`. This class inherits from the Python class :code:`set`
and behaves as a set of projects, with additional information. Projects
are instantiations of the class :code:`Project` that stores a project' name
and cost (and potential additional information). Let's see an example.

.. code-block:: python

    instance = PBInstance()
    p1 = Project("p1", 1)
    instance.add(p1)
    p2 = Project("p2", 1)
    instance.add(p2)
    p3 = Project("p3", 3)
    instance.add(p3)

An instance also stores additional information such as the budget limit
of the election, and additional metadata.

.. code-block:: python

    instance.budget_limit = 3 # The budget limit
    instance.meta   # dict storing metadata on the instance
    instance.project_meta  # dict of (project, dict) storing metadata on the projects

Several methods can be called on an instance to run through all the
budget allocations, test the feasiblity of a set of projects etc...

.. code-block:: python

    for b in instance.budget_allocations:
        print(str(b) + " is a feasible budget allocation")
    instance.is_feasible([p1, p2, p3])  # Returns False
    instance.is_exhaustive([p1, p2])  # Returns True


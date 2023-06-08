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

Instances
---------

A PB instance describes all the elements that define the elections.
It includes the projects that are being voted on, together with the
budget limit.

The main class here is :code:`PBInstance`. This class inherits
from the Python class :code:`set` and behaves as a set of projects,
with additional information. Projects are instantiations of the
class :code:`Project` that stores a project' name and cost
(and potential additional information). Let's see an example.

.. code-block:: python

    instance = PBInstance()   # There are many optional parameters
    p1 = Project("p1", 1)   # The constructor takes name and cost of the project
    instance.add(p1)   # Use the set methods to add/delete projects to an instance
    p2 = Project("p2", 1)
    instance.add(p2)
    p3 = Project("p3", 3)
    instance.add(p3)

Importantly, any Python comparison between two projects (equality etc...) is
done on the name of the projects. Since an instance is a set, adding a
project :code:`Project("p", 1)` and another project :code:`Project("p", 3)`
will only lead to an instance with one element.

An instance also stores additional information such as the budget limit
of the election, and additional metadata.

.. code-block:: python

    instance.budget_limit = 3   # The budget limit
    instance.meta   # dict storing metadata on the instance
    instance.project_meta   # dict of (project, dict) storing metadata on the projects

Several methods can be called on an instance to run through all the
budget allocations, test the feasiblity of a set of projects etc...

.. code-block:: python

    for b in instance.budget_allocations:
        print(str(b) + " is a feasible budget allocation")
    instance.is_feasible([p1, p2, p3])   # Returns False
    instance.is_exhaustive([p1, p2])   # Returns True


Profiles
--------

A profile is the second basic component of a PB election, it stores
the ballots of the voters.

We provide one general class :code:`Profile` that inherits from the Python
:code:`list` and that is inherited from by all specific profile types. It
is really meant to be an abstract class and should not really be used for
any other purpose than inheritance. Similarly, we provide a class
:code:`Ballot` that will be inherited by specific ballot formats.

A profile is linked to an instance, which is given as a parameter, and then
stored in an attribute. It also implements a validation of the ballots to
ensure consistency of the ballots in a profile.

.. code-block:: python

    instance = PBInstance()
    profile = Profile(instance=instance)
    profile.ballot_validation = True   # Boolean (de)activating the validation of the ballot type
    profile.ballot_type = Ballot   # The type used for the ballot validation
    b = {1, 2, 3}
    profile.validate_ballot(b)   # The validator, would raise a TypeError here


Approval Profiles
~~~~~~~~~~~~~~~~~

When submitting approval ballots, voters submit a set of projects they
approve of. Approval ballots are represented through the class
:code:`ApprovalBallot` that inherits both from :code:`set` and from
:code:`Ballot`.
========
PBvoting
========


Overview
========

PBvoting is a python package providing many tools to work with
participatory budgeting instances.

Participatory budgeting (PB) is a democratic tool used to allocate
a given amount of money to a collection of projects based on a
group of individuals' preferences over the projects. It has been invented
in Brazil in the late 80's and is now a widely implemented. See the
`Wikipedia page <https://en.wikipedia.org/wiki/Participatory_budgeting>`_
for more details.

In this library we provide the tools to handle PB instances of different
kinds, together with voting rules to determine the outcome of the elections
and some analytic tools. In particular, we provide full support for the
instances taken from `pabulib <http://pabulib.org/>`_, the reference library
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

    from pbvoting.instance import PBInstance, Project

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

    from pbvoting.instance import PBInstance, Profile, Ballot

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

A profile of approval ballots, i.e., an approval profile, is instantiated
from the class :code:`ApprovalProfile`. It inherits from :code:`Profile`.
The type for the ballot validator is by default set to :code:`ApprovalBallot`.

.. code-block:: python

    from pbvoting.instance import Project, ApprovalBallot, ApprovalProfile

    projects = [Project("p{}".format(i), 1) for i in range(10)]
    b1 = ApprovalBallot(projects[:3])   # Approval ballot containing the first 3 projects
    b1.add(projects[4])   # Add project to approval ballot
    b2 = ApprovalBallot(projects[1:5])
    profile = ApprovalProfile([b1, b2])
    b3 = ApprovalBallot({projects[0], projects[8]})
    profile.append(b3)
    b1 in profile   # Tests membership, returns True here

Several additional methods are provided in the :code:`ApprovalProfile` class.

.. code-block:: python

    profile.approval_score(p1)   # The approval score of a project, i.e., the number of approvers
    profile.is_party_list()   # Boolean indicating if the profile is party_list


Cardinal Profiles
~~~~~~~~~~~~~~~~~

When asked for cardinal ballots, voters are asked to associate each project
with a score. Cardinal ballots are represented using the class
:code:`CardinalBallot`. It inherits directly from the Python
:code:`dict` class and our :code:`Ballot` class.

A profile of cardinal ballots, i.e., a cardinal profile, is instantiated
through the :code:`CardinalProfile` class. It inherits from the
:code:`Profile` class and validates ballot types using
:code:`CardinalBallot`.

.. code-block:: python

    from pbvoting.instance import Project, CardinalBallot, CardinalProfile

    projects = [Project("p{}".format(i), 1) for i in range(10)]
    b1 = CardinalBallot({projects[1]: 5, projects[2]: 0)   # Cardinal ballot scoring 5 for p1 and 0 for p2
    b2 = CardinalBallot()
    b2[projects[0]] = 9   # Assign score to p0
    profile = CardinalProfile([b1, b2])

Cumulative Profiles
~~~~~~~~~~~~~~~~~~~

Cumulative ballots correspond to a specific type of cardinal ballots where
the voters are allocated a specific number of points that they can
distribute among the projects. The class :code:`CumulativeBallot`
is used to deal with cumulative ballots. It inherits from
:code:`CardinalBallot` and thus also from the Python class
:code:`dict`.

As before, a profile of cumulative ballots is defined in the class
:code:`CumulativeProfile` that inherits from the :code:`Profile` class
(and act thus as a list).

Ordinal Profiles
~~~~~~~~~~~~~~~~

When ordinal ballots are used, voters are asked to order the projects
based on their preferences. The class :code:`OrdinalBallot` represents
such ballots. It inherits from the Python class :code:`list` and our
class :code:`Ballot`.

Ordinal profiles are handled by the class :code:`OrdinalProfile`.

.. code-block:: python

    from pbvoting.instance import Project, OrdinalBallot, OrdinalProfile

    projects = [Project("p{}".format(i), 1) for i in range(10)]
    b1 = OrdinalBallot((projects[0], projects[4], projects[2]))   # Ordinal ballot ranking p0 > p4 > p2
    b1.append(projects[1])   # The ballot becomes p0 > p4 > p2 > p1
    profile = CardinalProfile()
    profile.append(b1)

Pabulib
-------

We provide the function :code:`pbvoting.instance.parse_pabulib`.


Satisfaction
------------

See the module :code:`pbvoting.instance.satisfaction`. Note that there are
many pre-defined satisfaction functions.

Rules
-----

See the module :code:`pbvoting.rules`.


Approximation of Social Welfare Optimum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the module :code:`pbvoting.rules.greedywelfare`.

Method of equal shares
~~~~~~~~~~~~~~~~~~~~~~

See the module :code:`pbvoting.rules.mes`.

Tie-Breaking
~~~~~~~~~~~~

See the module :code:`pbvoting.tiebreaking`.

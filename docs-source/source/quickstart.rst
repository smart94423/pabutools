Quick Start
===========

Now that the pabutools are installed (if not, see :ref:`installation`), you can start
using them!

On this page, you will be guided through a simple example.

Describing an Election
----------------------

We start by describing an election. We need to encode at least the projects, the budget
limit and the ballots of the voters.

Projects and Instances
^^^^^^^^^^^^^^^^^^^^^^

The most basic element is the projects, i.e., the
entities that are voted upon. We start by defining them through the class
:py:class:`~pabutools.election.instance.Project`.

.. code-block:: python

    from pabutools.election import Project

    p1 = Project("p1", 1)   # The constructor takes name and cost of the project
    p2 = Project("p2", 1)
    p3 = Project("p3", 3)

Then, we define what we call an instance, that is, a collection of projects together with
some additional information about the election. It stores all the information regarding
the election, except for what concerns the voters.

An instance is an instantiation of the :py:class:`~pabutools.election.instance.Instance`
class. This class derives from the Python `set` class and can be used as one.

.. code-block:: python

    from pabutools.election import Instance

    instance = Instance()   # There are many optional parameters
    instance.add(p1)   # Use set methods to populate
    instance.update([p2, p3])

    instance.budget_limit = 3   # The instance stores the budget limit

Importantly, any Python comparison between two projects (equality etc...) is done on
the name of the projects. Since an instance is a set, adding a project
`Project("p", 1)` and another project `Project("p", 3)` will lead to an
instance with a single project.

Ballots and Profiles
^^^^^^^^^^^^^^^^^^^^

The next basic component of a participatory budgeting election is the ballot. A ballot
stores all the information provided by a voter. All the ballots are gathered into a
profile.

For this example, we assume that voters submitted approval ballots. They are instantiated
through the class :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot`
as follows:

.. code-block:: python

    from pabutools.election import ApprovalBallot

    b1 = ApprovalBallot([p1, p2])   # Initialise an approval ballot with two projects
    b1.add(p2)   # Add project to approval ballot using set methods
    b2 = ApprovalBallot({p1, p2, p3})
    b3 = ApprovalBallot({p3})

The :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot` class inherits
from the Python `set` and can be used as one.

We can now define the approval profile:

.. code-block:: python

    from pabutools.election import ApprovalProfile

    profile = ApprovalProfile([b1, b2])   # Initialise the profile with two ballots
    profile.append(b3)   # Use list methods to handle the profile

The approval profile is instantiated using the class
:py:class:`~pabutools.election.profile.approvalprofile.ApprovalProfile` that inherits from
the Python class `list`.

Computing the Outcome of an Election
------------------------------------

The election is ready, we can now work with it. The most natural next step is then to
compute the winning projects. For that, we turn to the module :py:mod:`~pabutools.rules`.

Assuming we want to do like 99% all the cities in the world, we will compute the outcome
of the election using the standard greedy method. That works as follows:

.. code-block:: python

    from pabutools.election import Cost_Sat
    from pabutools.rules import greedy_utilitarian_welfare

    outcome = greedy_utilitarian_welfare(instnace, profile, sat_class=Cost_Sat)

This computes the outcome of the greedy approximation of the utilitarian welfare using
the satisfaction measure
:py:class:`~pabutools.election.satisfaction.additivesatisfaction.Cost_Sat`.
Satisfaction measures have not be discussed yet. Keep in mind that they describe the way
voters are assumed to assess the quality of a set of project. For instance,
:py:class:`~pabutools.election.satisfaction.additivesatisfaction.Cost_Sat` measures the
satisfaction of a voter as the total cost of the projects that have been selected and
that appear in the voter's ballot. For more information, check out
:py:mod:`~pabutools.election.satisfaction`.

Other methods can be used such as Phragmén's sequential rule or the method of equal shares.

.. code-block:: python

    from pabutools.election import Cost_Sat
    from pabutools.rules import sequential_phragmen, method_of_equal_shares

    outcome1 = sequential_phragmen(instnace, profile)
    outcome2 = method_of_equal_shares(instnace, profile, sat_class=Cost_Sat)

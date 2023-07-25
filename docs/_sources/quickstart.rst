.. _quickstart:

Quick Start
===========

Now that you have installed pabutools (if not, see :ref:`installation`), you can start
using the package!

On this page, we will guide you through a simple example.

Describing an Election
----------------------

Let's begin by describing an election. We need to encode at least the projects, the budget
limit, and the ballots of the voters.

Projects and Instances
^^^^^^^^^^^^^^^^^^^^^^

The fundamental elements are the projects, i.e., the
entities that will be voted upon. We define them using the class
:py:class:`~pabutools.election.instance.Project`.

.. code-block:: python

    from pabutools.election import Project

    p1 = Project("p1", 1)   # The constructor takes the name and cost of the project
    p2 = Project("p2", 1)
    p3 = Project("p3", 3)

Next, we define an instance, which is a collection of projects along with
additional information about the election. It stores all the information regarding
the election, except for what concerns the voters.

An instance is an instantiation of the :py:class:`~pabutools.election.instance.Instance`
class. This class derives from the Python `set` class and can be used as one.

.. code-block:: python

    from pabutools.election import Instance

    instance = Instance()   # There are many optional parameters
    instance.add(p1)   # Use set methods to populate
    instance.update([p2, p3])

    instance.budget_limit = 3   # The instance stores the budget limit for the projects

Importantly, any Python comparison between two projects (e.g., equality) is based on
the name of the projects. Since an instance is a set, adding a project
`Project("p", 1)` and another project `Project("p", 3)` will result in an
instance with a single project.

Ballots and Profiles
^^^^^^^^^^^^^^^^^^^^

The next essential components of a participatory budgeting election are the ballots. A ballot
stores all the information provided by a voter. All the ballots are gathered into a
profile.

For this example, we assume that voters submitted approval ballots. They are instantiated
using the class :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot`
as follows:

.. code-block:: python

    from pabutools.election import ApprovalBallot

    b1 = ApprovalBallot([p1, p2])   # Initialize an approval ballot with two projects
    b1.add(p2)   # Add projects to the approval ballot using set methods
    b2 = ApprovalBallot({p1, p2, p3})
    b3 = ApprovalBallot({p3})

The :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot` class inherits
from the Python `set` and can be used as one.

We can now define the approval profile:

.. code-block:: python

    from pabutools.election import ApprovalProfile

    profile = ApprovalProfile([b1, b2])   # Initialize the profile with two ballots
    profile.append(b3)   # Use list methods to handle the profile

The approval profile is instantiated using the class
:py:class:`~pabutools.election.profile.approvalprofile.ApprovalProfile`, which inherits from
the Python class `list`.

Computing the Outcome of an Election
------------------------------------

The election is ready; now, let's compute the winning projects. For this purpose, we will
use the module :py:mod:`~pabutools.rules`.

Assuming we want to use the standard greedy method, which is commonly used in many cities
around the world, we can compute the outcome of the election as follows:

.. code-block:: python

    from pabutools.election import Cost_Sat
    from pabutools.rules import greedy_utilitarian_welfare

    outcome = greedy_utilitarian_welfare(instance, profile, sat_class=Cost_Sat)

This computes the outcome of the greedy approximation of the utilitarian welfare using
the satisfaction measure
:py:class:`~pabutools.election.satisfaction.additivesatisfaction.Cost_Sat`.
Satisfaction measures have not been discussed yet. Keep in mind that they describe the way
voters are assumed to assess the quality of a set of projects. For instance,
:py:class:`~pabutools.election.satisfaction.additivesatisfaction.Cost_Sat` measures the
satisfaction of a voter as the total cost of the projects that have been selected and
that appear in the voter's ballot. For more information, check out
:py:mod:`~pabutools.election.satisfaction`.

Other methods can be used, such as Phragmén's sequential rule or the method of equal shares.

.. code-block:: python

    from pabutools.election import Cost_Sat
    from pabutools.rules import sequential_phragmen, method_of_equal_shares

    outcome1 = sequential_phragmen(instance, profile)
    outcome2 = method_of_equal_shares(instance, profile, sat_class=Cost_Sat)

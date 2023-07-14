# pabutools

[![Build badge](https://github.com/pbvoting/pabutools/workflows/build/badge.svg?branch=main)](https://github.com/pbvoting/pabutoolsactions?query=workflow%3Abuild)
[![codecov](https://codecov.io/gh/pbvoting/pabutools/branch/main/graphs/badge.svg)](https://codecov.io/gh/pbvoting/pabutools/tree/main)

## Overview

The pabutools are a complete set of tools work with
participatory budgeting instances.

Participatory budgeting (PB) is a democratic tool used to allocate
a given amount of money to a collection of projects based on a
group of individuals' preferences over the projects. It has been invented
in Brazil in the late 80's and is now a widely implemented. See the
[Wikipedia page](https://en.wikipedia.org/wiki/Participatory_budgeting)
for more details.

In this library we provide the tools to handle PB instances of different
kinds, together with voting rules to determine the outcome of the elections
and some analytic tools. In particular, we provide full support for the
instances taken from [pabulib](http://pabulib.org), the reference library
when it comes to PB data.

## Installation

Ultimately, the goal is to host this library on pip. For now, use the
source code provided here.

## Documentation

The complete documentation is available [here](https://pbvoting.github.io/pabutools/).

## Usage

### Instances

A PB instance describes all the elements that define the elections.
It includes the projects that are being voted on, together with the
budget limit.

The main class here is `Instance`. This class inherits
from the Python class `set` and behaves as a set of projects,
with additional information. Projects are instantiations of the
class `Project` that stores a project' name and cost
(and potential additional information). Let's see an example.

```python
from pabutools.election import Instance, Project

instance = Instance()   # There are many optional parameters
p1 = Project("p1", 1)   # The constructor takes name and cost of the project
instance.add(p1)   # Use the set methods to add/delete projects to an instance
p2 = Project("p2", 1)
instance.add(p2)
p3 = Project("p3", 3)
instance.add(p3)
```

Importantly, any Python comparison between two projects (equality etc...) is
done on the name of the projects. Since an instance is a set, adding a
project `Project("p", 1)` and another project `Project("p", 3)`
will only lead to an instance with one element.

An instance also stores additional information such as the budget limit
of the election, and additional metadata.

```python
instance.budget_limit = 3   # The budget limit
instance.meta   # dict storing metadata on the instance
instance.project_meta   # dict of (project, dict) storing metadata on the projects
```

Several methods can be called on an instance to run through all the
budget allocations, test the feasiblity of a set of projects etc...

```python
for b in instance.budget_allocations():
    print(str(b) + " is a feasible budget allocation")
instance.is_feasible([p1, p2, p3])   # Returns False
instance.is_exhaustive([p1, p2])   # Returns True
```

### Profiles

A profile is the second basic component of a PB election, it stores
the ballots of the voters.

We provide one general class `Profile` that inherits from the Python
`list` and that is inherited from by all specific profile types. It
is really meant to be an abstract class and should not really be used for
any other purpose than inheritance. Similarly, we provide a class
`Ballot` that will be inherited by specific ballot formats.

A profile is linked to an instance, which is given as a parameter, and then
stored in an attribute. It also implements a validation of the ballots to
ensure consistency of the ballots in a profile.

```python
from pabutools.election import Instance, Profile, Ballot

instance = Instance()
profile = Profile(instance=instance)
profile.ballot_validation = True   # Boolean (de)activating the validation of the ballot type
profile.ballot_type = Ballot   # The type used for the ballot validation
b = {1, 2, 3}
profile.validate_ballot(b)   # The validator, would raise a TypeError here
```

#### Approval Profiles

When submitting approval ballots, voters submit a set of projects they
approve of. Approval ballots are represented through the class
`ApprovalBallot` that inherits both from `set` and from
`Ballot`.

A profile of approval ballots, i.e., an approval profile, is instantiated
from the class `ApprovalProfile`. It inherits from `Profile`.
The type for the ballot validator is by default set to `ApprovalBallot`.

```python
from pabutools.election import Project, ApprovalBallot, ApprovalProfile

projects = [Project("p{}".format(i), 1) for i in range(10)]
b1 = ApprovalBallot(projects[:3])   # Approval ballot containing the first 3 projects
b1.add(projects[4])   # Add project to approval ballot
b2 = ApprovalBallot(projects[1:5])
profile = ApprovalProfile([b1, b2])
b3 = ApprovalBallot({projects[0], projects[8]})
profile.append(b3)
b1 in profile   # Tests membership, returns True here
```

Several additional methods are provided in the `ApprovalProfile` class.

```python
profile.approval_score(p1)   # The approval score of a project, i.e., the number of approvers
profile.is_party_list()   # Boolean indicating if the profile is party_list
```


#### Cardinal Profiles

When asked for cardinal ballots, voters are asked to associate each project
with a score. Cardinal ballots are represented using the class
`CardinalBallot`. It inherits directly from the Python
`dict` class and our `Ballot` class.

A profile of cardinal ballots, i.e., a cardinal profile, is instantiated
through the `CardinalProfile` class. It inherits from the
`Profile` class and validates ballot types using
`CardinalBallot`.

```python
from pabutools.election import Project, CardinalBallot, CardinalProfile

projects = [Project("p{}".format(i), 1) for i in range(10)]
b1 = CardinalBallot({projects[1]: 5, projects[2]: 0})   # Cardinal ballot scoring 5 for p1 and 0 for p2
b2 = CardinalBallot()
b2[projects[0]] = 9   # Assign score to p0
profile = CardinalProfile([b1, b2])
```

#### Cumulative Profiles

Cumulative ballots correspond to a specific type of cardinal ballots where
the voters are allocated a specific number of points that they can
distribute among the projects. The class `CumulativeBallot`
is used to deal with cumulative ballots. It inherits from
`CardinalBallot` and thus also from the Python class
`dict`.

As before, a profile of cumulative ballots is defined in the class
`CumulativeProfile` that inherits from the `Profile` class
(and act thus as a list).

#### Ordinal Profiles

When ordinal ballots are used, voters are asked to order the projects
based on their preferences. The class `OrdinalBallot` represents
such ballots. It inherits from the Python class `list` and our
class `Ballot`.

Ordinal profiles are handled by the class `OrdinalProfile`.

```python
from pabutools.election import Project, OrdinalBallot, OrdinalProfile

projects = [Project("p{}".format(i), 1) for i in range(10)]
b1 = OrdinalBallot((projects[0], projects[4], projects[2]))   # Ordinal ballot ranking p0 > p4 > p2
b1.append(projects[1])   # The ballot becomes p0 > p4 > p2 > p1
profile = OrdinalProfile()
profile.append(b1)
```

#### Pabulib

We provide full support of the PB data hosted on the
[pabulib](http://pabulib.org) website. The function
`pabutools.election.parse_pabulib` can be used to parse a file
formatted according to the pabulib format. It returns the instance
and the profile, using the suitable profile class given the ballot
format in the data.

```python
from pabutools.election import parse_pabulib

instance, profile = parse_pabulib("path_to_the_file")
```

Pabulib files provide a whole range of metadata, not all of which are
relevant to everyone. These metadata are stored in the `meta`
members of the instance and profile classes.

```python
from pabutools.election import parse_pabulib

instance, profile = parse_pabulib("path_to_the_file")
instance.meta   # The meta dict is populated with all the metadata described in the file
instance.project_meta    # The project_meta dict is populated with the metadata related to the projects
for ballot in profile:
    ballot.meta    # The meta dict populated with the metadata corresponding to the ballot
```

There are several metadata that are stored as members of the relevant
classes. These for instance include all the constraints (when known)
the voters faced when submitting their ballots. It includes the minimum
length of a ballot, or the number of points that have to be distributed
for instance.

```python
### For ApprovalProfile, CardinalProfile, CumulativeProfile and OrdinalProfile
profile.legal_min_length   # Imposed minimum length of the ballots in the profile
profile.legal_max_length   # Imposed maximum length of the ballots in the profile

### For ApprovalProfile only
profile.legal_min_cost   # Imposed minimum total cost of the ballots in the profile
profile.legal_max_cost   # Imposed maximum total cost of the ballots in the profile

### For CardinalProfile and CumulativeProfile
profile.legal_min_score   # Imposed minimum score assigned to a project for the ballots in the profile
profile.legal_max_score   # Imposed maximum score assigned to a project for the ballots in the profile

### For CumulativeProfile only
profile.legal_min_total_score   # Imposed minimum total scores for the ballots in the profile
profile.legal_max_total_score   # Imposed maximum total scores for the ballots in the profile
```

### Satisfaction

Many concepts, including celebrated PB rules, are not using the ballots
directly but rather proxies for the satisfaction of the voters that are
deduced from the ballots.

We provide many satifaction functions, and flexible ways to create new ones.
A satisfaction function is a class that inherits from `Satisfaction`,
i.e., a class initialised for a given instance, profile, and ballot and
that implements a `sat` method that is used to compute the
satisfaction. Since a satisfaction function corresponds to a single ballot,
we also provide a `SatisfactionProfile` class. This class inherits
from the Python class `list` and implements a satisfaction profile.

The typical workflow is thus to gather the ballots in a profile, then
convert it into a collection of satisfaction functions, that are finally
provided as input of a rule.

```python
from pabutools.election import SatisfactionProfile, SatisfactionMeasure
from pabutools.election import parse_pabulib

instance, profile = parse_pabulib("path_to_the_file")
sat_profile = SatisfactionProfile(instance=instance)
# We define a satisfaction function:
class MySatisfaction(SatisfactionMeasure):
    def sat(self, projects):
        return 100 if "p1" in projects else len(projects)
# We populate the satisfaction profile
for ballot in profile:
    sat_profile.append(MySatisfaction(instance, profile, ballot))
# The satisfaction profile is ready for use
outcome = rule(sat_profile)
```

Because the above can be tedious, we provide simpler ways to define the
satisfaction profile. Several widely used satisfaction functions are also
directly provided.

```python
from pabutools.election import SatisfactionProfile, Cardinality_Sat
from pabutools.election import parse_pabulib

instance, profile = parse_pabulib("path_to_the_file")
# If a profile and a sat_class are given to the constructor, the satisfaction profile
# is directly initialised with one instance of the sat_class per ballot in the profile.
sat_profile = SatisfactionProfile(instance=instance, profile=profile, sat_class=Cardinality_Sat)
# The satisfaction profile is ready for use
outcome = rule(sat_profile)
```

We now present useful tools we provide to define satisfaction functions.

#### Functional Satisfaction Functions

We also provide more specific ways of defining satisfaction function.
The class `FunctionalSatisfaction` corresponds to satisfaction
function that are defined by a function taking as argument an instance,
a profile, a ballot and a set of projects. We illustrate its use by
defining the Chamberlin-Courant satisfaction function with approval
(equals to 1 if at least one approved project is selected and
0 otherwise).

```python
from pabutools.election import FunctionalSatisfaction

def cc_sat_func(instance, profile, ballot, projects):
    return int(any(p in ballot for p in projects))

class CC_Sat(FunctionalSatisfaction):
        def __init__(self, instance, profile, ballot):
            super(CC_Sat, self).__init__(instance, profile, ballot, cc_sat_func)
```


#### Additive Satisfaction Functions

Another important set of satisfaction functions are the additive ones,
i.e., the ones for which the satisfaction for a set of projects is
equal to the satisfaction of each individual project. The class
`AdditiveSatisfaction` implements them. It inherits from the
`Satisfaction` class and its constructor takes as a parameter
a function mapping instance, profile, ballot and project to a score.
We illustrate its use by presenting how to define the cardinality
satisfaction function.

```python
from pabutools.election import AdditiveSatisfaction

def cardinality_sat_func(instance, profile, ballot, project):
    return int(project in ballot)

class Cardinality_Sat(AdditiveSatisfaction):
    def __init__(self, instance, profile, ballot):
        super(Cardinality_Sat, self).__init__(instance, profile, ballot, cardinality_sat_func)
```


#### Positional Satisfaction Functions

Positional satisfaction functions are to be used with ordinal ballots.
When using them, the satisfaction of a voter is a function of the
position of the projects in the ballot of the voter. The class
`PositionalSatisfaction` implements them. The constructor takes
as parameters two functions: one mapping ballots and projects to a score,
and a second one aggregating the individual scores for sets of projects.
We illustrate its usage by defining the additive Borda satisfaction
function.

```python
from pabutools.election import PositionalSatisfaction

def borda_sat_func(ballot, project):
    if project not in ballot:
        return 0
    return len(ballot) - ballot.index(project)

class Additive_Borda_Sat(PositionalSatisfaction):
    def __init__(self, instance, profile, ballot):
        super(Additive_Borda_Sat, self).__init__(instance, profile, ballot, borda_sat_func, sum)
```

#### Satisfaction Functions Already Defined

As we have seen above, several satisfaction functions are already defined
in the library and can be imported from `pabutools.election`. We list
them below.

- `CC_Sat` implements the Chamberlin-Courant satisfaction function for approval ballots.
- `Cost_Sqrt_Sat` defines the satisfaction as the square root of the total cost of the selected and approed projects.
- `Cost_Log_Sat` defines the satisfaction as the log of the total cost of the approved and selected projects.
- `Cardinality_Sat` defines the satisfaction as the number of approved and selected projects.
- `Cost_Sat` defines the satisfaction as the total cost of the approved and selected projects.
- `Effort_Sat` defines the satisfaction as the total share of a voter
- `Additive_Cardinal_Sat` defines the satisfaction as the sum of the scores of the selected projects, where the scores are taken from the cardinal ballot of the voter.
- `Additive_Borda_Sat` defines the satisfaction as the sum of the Borda scores of the selected projects.

### Rules

See the module `pabutools.rules`.

#### Approximation of Social Welfare Optimum

See the module `pabutools.rules.greedywelfare`.

#### Method of equal shares

See the module `pabutools.rules.mes`.

#### Tie-Breaking

See the module `pabutools.tiebreaking`.

## Development

We are more than happy to receive help with the development of the package.
If you want to contribute, here are some elements to take into account.

First, install the development dependencies by running the following command:
```shell
pip install -e ".[dev]"
```

You can run the unit tests with the following:
```shell
python -m unittest
```

The doc is generated using sphinx. We use the [numpy style guide](https://numpydoc.readthedocs.io/en/latest/format.html).
The [napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) extension for Sphinx is used
and the HTML style is defined by the [Book Sphinx Theme](https://sphinx-book-theme.readthedocs.io/en/stable/).

To generate the doc, first move inside the `docs-source` folder and run the following:
```shell
make clean 
make html
```

This will generate the documentation locally (in the folder `docs-source/build`. If you want to push the new documentation, run:
```shell
make github
```

After having pushed, the documentation will automatically be updated.

Note that a large part of the documentation is done by hand (to ensure proper display and correct ordering). 
This means that if you create new class of functions that should appear in the documentation, you may have
to add they yourself using to autodoc directives (take inspiration from the files in `docs-source/source`). 

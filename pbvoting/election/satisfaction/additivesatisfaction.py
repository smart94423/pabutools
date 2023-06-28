from collections.abc import Callable, Iterable
from numbers import Number

from pbvoting.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pbvoting.election.ballot import ApprovalBallot, CardinalBallot
from pbvoting.election.instance import Instance, Project, total_cost
from pbvoting.election.profile import Profile
from pbvoting.fractions import frac


class AdditiveSatisfaction(SatisfactionMeasure):
    """
        Class representing additive satisfaction functions, that is, satisfaction functions for which the total
        satisfaction is exactly the sum of the satisfaction of the individual projects. To speed up computations,
        scores are only computed once and for all.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.Ballot
                The approval ballot.
            func : Callable[[PBInstance, Profile, Ballot, Project], Number]
                A function taking as input an instance, a profile, a ballot and a project, and returning
                the score as a fraction.
        Attributes
        ----------
            func : function
                A function taking as input an instance, a profile, a ballot and a project, and returning the score of
                the project as a fraction.
    """

    def __init__(self,
                 instance: Instance,
                 profile: Profile,
                 ballot: ApprovalBallot,
                 func: Callable[[Instance, Profile, ApprovalBallot, Project], Number]
                 ) -> None:
        super(AdditiveSatisfaction, self).__init__(instance, profile, ballot)
        self.func = func
        self.scores = dict()

    def get_score(self,
                  project: Project
                  ) -> Number:
        if project in self.scores:
            return self.scores[project]
        score = self.func(self.instance, self.profile, self.ballot, project)
        self.scores[project] = score
        return score

    def sat(self,
            projects: Iterable[Project]
            ) -> Number:
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects. The
            satisfaction is additive, it is thus defines as the sum of the score of the projects under consideration.
            Parameters
            ----------
                projects : set of pbvoting.instance.pbinstance.Project
                    The set of projects.
            Returns
            -------
                float
        """
        return sum(self.get_score(project) for project in projects)


def cardinality_sat_func(instance: Instance,
                         profile: Profile,
                         ballot: ApprovalBallot,
                         project: Project
                         ) -> int:
    return int(project in ballot)


class Cardinality_Sat(AdditiveSatisfaction):

    def __init__(self, instance: Instance, profile: Profile, ballot: ApprovalBallot):
        super(Cardinality_Sat, self).__init__(instance, profile, ballot, cardinality_sat_func)


def cost_sat_func(instance: Instance,
                  profile: Profile,
                  ballot: ApprovalBallot,
                  project: Project
                  ) -> Number:
    return int(project in ballot) * project.cost


class Cost_Sat(AdditiveSatisfaction):

    def __init__(self, instance: Instance, profile: Profile, ballot: ApprovalBallot):
        super(Cost_Sat, self).__init__(instance, profile, ballot, cost_sat_func)


def relative_cardinality_sat_func(instance: Instance,
                                  profile: Profile,
                                  ballot: ApprovalBallot,
                                  project: Project,
                                  max_budget_allocation_card: int
                                  ) -> int:
    if max_budget_allocation_card == 0:
        return 0
    return frac(int(project in ballot), max_budget_allocation_card)


class Relative_Cardinality_Sat(AdditiveSatisfaction):

    def __init__(self, instance: Instance, profile: Profile, ballot: ApprovalBallot):
        super(Relative_Cardinality_Sat, self).__init__(instance, profile, ballot, relative_cardinality_sat_func)
        
        self.max_budget_allocation_card = self.compute_max_budget_allocation_card(ballot, instance.budget_limit)

    def compute_max_budget_allocation_card(self, ballot, budget_limit):
        ballot_sorted = sorted(ballot, key=lambda p: (p.cost))
        i, c = 0, 0
        while i < len(ballot) and c + ballot_sorted[i].cost <= budget_limit:
            c += ballot_sorted[i].cost
            i += 1
        return i

    def get_score(self,
                  project: Project
                  ) -> Number:
        if project in self.scores:
            return self.scores[project]
        score = self.func(self.instance, self.profile, self.ballot, project, self.max_budget_allocation_card)
        self.scores[project] = score
        return score


def relative_cost_sat_func(instance: Instance,
                           profile: Profile,
                           ballot: ApprovalBallot,
                           project: Project,
                           max_budget_allocation_cost: int
                           ) -> int:
    if max_budget_allocation_cost == 0:
        return 0
    return frac(int(project in ballot), max_budget_allocation_cost)


class Relative_Cost_Sat(AdditiveSatisfaction):

    def __init__(self, instance: Instance, profile: Profile, ballot: ApprovalBallot):
        super(Relative_Cost_Sat, self).__init__(instance, profile, ballot, relative_cost_sat_func)
        
        self.max_budget_allocation_cost = self.compute_max_budget_allocation_cost(ballot, instance.budget_limit)

    def compute_max_budget_allocation_cost(self, ballot, budget_limit):
        # TODO
        return 1

    def get_score(self,
                  project: Project
                  ) -> Number:
        if project in self.scores:
            return self.scores[project]
        score = self.func(self.instance, self.profile, self.ballot, project, self.max_budget_allocation_cost)
        self.scores[project] = score
        return score


def relative_cost_unbounded_sat_func(instance: Instance,
                  profile: Profile,
                  ballot: ApprovalBallot,
                  project: Project
                  ) -> Number:
    return frac(int(project in ballot) * project.cost, total_cost([p for p in ballot if p in ballot]))


class Relative_Cost_Unbounded_Sat(AdditiveSatisfaction):

    def __init__(self, instance: Instance, profile: Profile, ballot: ApprovalBallot):
        super(Relative_Cost_Unbounded_Sat, self).__init__(instance, profile, ballot, relative_cost_unbounded_sat_func)


def effort_sat_func(instance: Instance,
                    profile: Profile,
                    ballot: ApprovalBallot,
                    project: Project
                    ) -> Number:
    projects = [project for b in profile if project in b]
    if projects:
        return int(project in ballot) * frac(project.cost, len(projects))
    return 0


class Effort_Sat(AdditiveSatisfaction):

    def __init__(self,
                 instance: Instance,
                 profile: Profile,
                 ballot: ApprovalBallot):
        super(Effort_Sat, self).__init__(instance, profile, ballot, effort_sat_func)


def additive_card_sat_func(instance: Instance,
                           profile: Profile,
                           ballot: CardinalBallot,
                           project: Project
                           ) -> Number:
    return ballot.get(project, 0)


class Additive_Cardinal_Sat(AdditiveSatisfaction):

    def __init__(self,
                 instance: Instance,
                 profile: Profile,
                 ballot: CardinalBallot
                 ) -> None:
        super(Additive_Cardinal_Sat, self).__init__(instance, profile, ballot, additive_card_sat_func)


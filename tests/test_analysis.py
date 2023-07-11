from unittest import TestCase

from pbvoting.analysis.instanceproperties import *
from pbvoting.analysis.profileproperties import *
from pbvoting.analysis.votersatisfaction import *
from pbvoting.analysis.category import *

from pbvoting.election.satisfaction import Cost_Sat, Additive_Borda_Sat, Cardinality_Sat
from pbvoting.election.ballot import ApprovalBallot, OrdinalBallot, CardinalBallot
from pbvoting.election.profile import OrdinalProfile
from pbvoting.election.satisfaction.additivesatisfaction import Relative_Cardinality_Sat
from pbvoting.fractions import frac


class TestAnalysis(TestCase):
    def test_satisfaction_properties(self):
        projects = [Project(str(i), 10 + i) for i in range(10)]
        instance = Instance(projects, budget_limit=90)
        app_ball_1 = ApprovalBallot([projects[0], projects[1], projects[2], projects[3]])
        app_ball_2 = ApprovalBallot([projects[0]])
        app_ball_3 = ApprovalBallot([projects[5], projects[6]])
        app_ball_4 = ApprovalBallot([projects[8], projects[9]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2, app_ball_3, app_ball_4])

        budget_allocation = [projects[0], projects[1], projects[8], projects[9]]

        assert (
            avg_satisfaction(instance, app_profile, budget_allocation, Cost_Sat) == 17
        )
        assert percent_non_empty_handed(
            instance, app_profile, budget_allocation
        ) == frac(3, 4)
        assert gini_coefficient_of_satisfaction(
            instance, app_profile, budget_allocation, Cardinality_Sat
        ) == frac(7, 20)
        assert gini_coefficient_of_satisfaction(
            instance, app_profile, budget_allocation, Cardinality_Sat, invert=True
        ) == 1 - frac(7, 20)

        budget_allocation = [projects[0], projects[1], projects[8], projects[9]]

        assert (
            avg_satisfaction(instance, app_profile, budget_allocation, Cost_Sat) == 17
        )
        assert percent_non_empty_handed(
            instance, app_profile, budget_allocation
        ) == frac(3, 4)
        assert gini_coefficient_of_satisfaction(
            instance, app_profile, budget_allocation, Cardinality_Sat
        ) == frac(7, 20)

        ord_ball_1 = OrdinalBallot([projects[0], projects[1], projects[2], projects[3]])
        ord_ball_2 = OrdinalBallot([projects[0]])
        ord_ball_3 = OrdinalBallot([projects[5], projects[6]])
        ord_ball_4 = OrdinalBallot([projects[8], projects[9]])
        ord_profile = OrdinalProfile([ord_ball_1, ord_ball_2, ord_ball_3, ord_ball_4])

        assert (
            avg_satisfaction(
                instance, ord_profile, budget_allocation, Additive_Borda_Sat
            )
            == 1.5
        )

        budget_allocation = []
        sat_hist = satisfaction_histogram(instance, app_profile, budget_allocation, Relative_Cardinality_Sat, max_satisfaction=1, num_bins=10)
        
        assert(sat_hist == [1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        
        budget_allocation = [projects[0], projects[1], projects[2], projects[5]]
        sat_hist = satisfaction_histogram(instance, app_profile, budget_allocation, Relative_Cardinality_Sat, max_satisfaction=1, num_bins=10)

        assert(sat_hist == [.25, 0, 0, 0, 0, 0.25, 0, .25, 0, .25])


    def test_proportionality_properties(self):
        projects = [
            Project("p1", cost=1, categories={"c1", "c2"}),
            Project("p2", cost=2, categories={"c1", "c2"}),
        ]
        instance = Instance(projects, budget_limit=90, categories={"c1", "c2", "c3"})
        app_ball_1 = ApprovalBallot([projects[0], projects[1]])
        app_ball_2 = ApprovalBallot([projects[0], projects[1]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2])
        budget_allocation = [projects[0], projects[1]]

        assert category_proportionality(instance, app_profile, budget_allocation) == 1

        projects = [
            Project("p1", cost=1, categories={"c1", "c2"}),
            Project("p2", cost=2, categories={"c2", "c3"}),
            Project("p3", cost=2, categories=set()),
        ]
        instance = Instance(
            projects, budget_limit=90, categories={"c1", "c2", "c3", "c4"}
        )
        app_ball_1 = ApprovalBallot([projects[0], projects[1]])
        app_ball_2 = ApprovalBallot([projects[0]])
        app_ball_3 = ApprovalBallot([projects[1]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2, app_ball_3])
        budget_allocation = [projects[0], projects[2]]

        assert category_proportionality(
            instance, app_profile, budget_allocation
        ) == np.exp(-31.0 / 162)

        projects = [
            Project("p1", cost=1),
            Project("p2", cost=2),
        ]
        instance = Instance(projects, budget_limit=90)
        app_ball_1 = ApprovalBallot([projects[0], projects[1]])
        app_ball_2 = ApprovalBallot([projects[0], projects[1]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2])
        budget_allocation = [projects[0], projects[1]]

        with self.assertRaises(ValueError):
            category_proportionality(instance, app_profile, budget_allocation)

    def test_instance_properties(self):
        projects = [
            Project("p1", cost=1),
            Project("p2", cost=2),
            Project("p3", cost=6),
        ]
        instance = Instance(projects, budget_limit=6)

        assert sum_project_cost(instance) == 9
        assert avg_project_cost(instance) == 3
        assert median_project_cost(instance) == 2
        assert funding_scarcity(instance) == frac(3, 2)
        assert std_dev_project_cost(instance) == np.sqrt(14.0 / 3)

        instance = Instance(projects)
        with self.assertRaises(ValueError):
            funding_scarcity(instance)

    def test_profile_properties(self):
        projects = [
            Project("p1", cost=1),
            Project("p2", cost=2),
            Project("p3", cost=3),
        ]
        instance = Instance(projects, budget_limit=3)
        app_ball_1 = ApprovalBallot([projects[0], projects[1]])
        app_ball_2 = ApprovalBallot([projects[0], projects[2]])
        app_ball_3 = ApprovalBallot([projects[1]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2, app_ball_3])

        assert avg_ballot_length(instance, app_profile) == frac(5, 3)
        assert median_ballot_length(instance, app_profile) == 2
        assert avg_ballot_cost(instance, app_profile) == 3
        assert median_ballot_cost(instance, app_profile) == 3
        assert avg_approval_score(instance, app_profile) == frac(5, 3)
        assert median_approval_score(instance, app_profile) == 2

        card_ball_1 = CardinalBallot({projects[0]: 2, projects[1]: 5})
        card_ball_2 = CardinalBallot({projects[0]: 1, projects[2]: 1})
        card_ball_3 = CardinalBallot({projects[1]: 3})
        card_profile = CardinalProfile([card_ball_1, card_ball_2, card_ball_3])

        assert avg_total_score(instance, card_profile) == 4
        assert median_total_score(instance, card_profile) == 3

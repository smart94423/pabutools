from unittest import TestCase
from pbvoting.fractions import frac
from pbvoting.instance.pbinstance import PBInstance, Project
from pbvoting.instance.profile import ApprovalBallot, ApprovalProfile, OrdinalBallot, OrdinalProfile
from pbvoting.instance.satisfaction import Cost_Sat, Additive_Borda_Sat, Cardinality_Sat
from pbvoting.analysis.votersatisfaction import *
from pbvoting.analysis.categoryanalysis import *

class TestProperties(TestCase):
    def test_satisfaction_properties(self):
        projects = [Project(str(i), 10+i) for i in range(10)]
        instance = PBInstance(projects, budget_limit=90)
        app_ball_1 = ApprovalBallot([projects[0], projects[1], projects[2], projects[3]])
        app_ball_2 = ApprovalBallot([projects[0]])
        app_ball_3 = ApprovalBallot([projects[5], projects[6]])
        app_ball_4 = ApprovalBallot([projects[8], projects[9]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2, app_ball_3, app_ball_4])
        
        budget_allocation = [projects[0], projects[1],projects[8],projects[9]]
        
        assert(avg_satisfaction(instance, app_profile, budget_allocation, Cost_Sat) == 17)
        assert(percent_non_empty_handed(instance, app_profile, budget_allocation) == frac(3,4))
        assert(gini_coefficient_of_satisfaction(instance, app_profile, budget_allocation, Cardinality_Sat) == frac(7,20))


        ord_ball_1 = OrdinalBallot([projects[0], projects[1], projects[2], projects[3]])
        ord_ball_2 = OrdinalBallot([projects[0]])
        ord_ball_3 = OrdinalBallot([projects[5], projects[6]])
        ord_ball_4 = OrdinalBallot([projects[8], projects[9]])
        ord_profile = OrdinalProfile([ord_ball_1, ord_ball_2, ord_ball_3, ord_ball_4])

        assert(avg_satisfaction(instance, ord_profile, budget_allocation, Additive_Borda_Sat) == 2.75)


    def test_proportionality_properties(self):
        projects = [
            Project("p1", cost=1, categories={"c1", "c2"}),
            Project("p2", cost=2, categories={"c1", "c2"}),
        ]
        instance = PBInstance(projects, budget_limit=90, categories={"c1", "c2", "c3"})
        app_ball_1 = ApprovalBallot([projects[0], projects[1]])
        app_ball_2 = ApprovalBallot([projects[0], projects[1]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2])
        budget_allocation = [projects[0], projects[1]]
        
        assert category_proportionality(instance, app_profile, budget_allocation) == 1
        
        
        projects = [
            Project("p1", cost=1, categories={"c1", "c2"}),
            Project("p2", cost=2, categories={"c2", "c3"}),
            Project("p3", cost=2, categories=set())
        ]
        instance = PBInstance(projects, budget_limit=90, categories={"c1", "c2", "c3", "c4"})
        app_ball_1 = ApprovalBallot([projects[0], projects[1]])
        app_ball_2 = ApprovalBallot([projects[0]])
        app_ball_3 = ApprovalBallot([projects[1]])
        app_profile = ApprovalProfile([app_ball_1, app_ball_2, app_ball_3])
        budget_allocation = [projects[0], projects[2]]

        assert category_proportionality(instance, app_profile, budget_allocation) == np.exp(-31./162)


        
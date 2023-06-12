from pbvoting.instance.pbinstance import PBInstance, Project
from pbvoting.instance.profile import ApprovalBallot, ApprovalProfile, OrdinalBallot, OrdinalProfile
from pbvoting.instance.satisfaction import Cost_Sat, Additive_Borda_Sat, Cardinality_Sat
from pbvoting.properties.satisfactionproperties import *


def test_satisfaction_properties():
    projects = [Project(str(i), 10+i) for i in range(10)]
    instance = PBInstance(projects, budget_limit=90)
    app_ball_1 = ApprovalBallot([projects[0], projects[1], projects[2], projects[3]])
    app_ball_2 = ApprovalBallot([projects[0]])
    app_ball_3 = ApprovalBallot([projects[5], projects[6]])
    app_ball_4 = ApprovalBallot([projects[8], projects[9]])
    app_profile = ApprovalProfile([app_ball_1, app_ball_2, app_ball_3, app_ball_4])
    
    budget_allocation = [projects[0], projects[1],projects[8],projects[9]]
    
    assert(avg_satisfaction(instance, app_profile, budget_allocation, Cost_Sat) == 17)
    assert(percent_non_empty_handed(instance, app_profile, budget_allocation) == 0.75)
    assert(gini_coefficient_of_satisfaction(instance, app_profile, budget_allocation, Cardinality_Sat) == 0.35)


    ord_ball_1 = OrdinalBallot([projects[0], projects[1], projects[2], projects[3]])
    ord_ball_2 = OrdinalBallot([projects[0]])
    ord_ball_3 = OrdinalBallot([projects[5], projects[6]])
    ord_ball_4 = OrdinalBallot([projects[8], projects[9]])
    ord_profile = OrdinalProfile([ord_ball_1, ord_ball_2, ord_ball_3, ord_ball_4])

    assert(avg_satisfaction(instance, ord_profile, budget_allocation, Additive_Borda_Sat) == 2.75)


from pbvoting.instance.pbinstance import Project, PBInstance
from pbvoting.instance.profile import ApprovalBallot, ApprovalProfile, CardinalBallot


def test_approval_profile():
    projects = [Project("p" + str(i), cost=2) for i in range(10)]
    instance = PBInstance(projects, budget_limit=1)
    b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
    b2 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
    b3 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
    profile = ApprovalProfile((b1, b2, b3), instance=instance)
    assert profile.is_party_list() is True
    b4 = ApprovalBallot((projects[4], projects[5]))
    b5 = ApprovalBallot((projects[4], projects[5]))
    profile += [b4, b5]
    assert len(profile) == 5
    assert profile.is_party_list() is True
    b6 = ApprovalBallot([projects[0], projects[4]])
    profile.append(b6)
    assert profile.is_party_list() is False
    assert len(profile.approved_projects()) == 6
    assert profile.is_trivial() is True
    instance.budget_limit = 3
    assert profile.is_trivial() is False

    card_ballot = CardinalBallot({projects[1]: 5, projects[2]: 2})
    try:
        profile.append(card_ballot)
    except TypeError:
        pass

    profile.ballot_validation = False
    profile.append(card_ballot)




def test_approval_ballot():
    p1 = Project("p1", 1)
    p2 = Project("p2", 2)
    p3 = Project("p3", 5)
    p4 = Project("p4", 3)
    p5 = Project("p5", 2)
    p6 = Project("p6", 2)
    ballot = ApprovalBallot([p1, p2, p3, p4])
    assert p1 in ballot
    assert p2 in ballot
    assert p3 in ballot
    assert p4 in ballot
    assert p5 not in ballot
    assert p6 not in ballot


# from mip import *
#
# from copy import deepcopy
#
# from fairshare import *
# from instance import *
#
#
# ###############
# # Useless stuff
# ###############
#
# def avgFairShareRatio(instance, profile, budgetAllocation):
#     v = vectorFairShareRatio(instance, profile, budgetAllocation)
#     return sum(v) / len(v)
#
#
# def maxFairShareRatio(instance, profile, budgetAllocation):
#     return max(vectorFairShareRatio(instance, profile, budgetAllocation))
#
#
# def minFairShareRatio(instance, profile, budgetAllocation):
#     return min(vectorFairShareRatio(instance, profile, budgetAllocation))
#
#
# ###############
# # Preprocessing
# ###############
#
# def preprocessThreshold(instance, profile, threshold=0.05):
#     projectsToDelete = []
#     for p in instance.projects:
#         if sum(p in ballot for ballot in profile) < threshold * len(profile):
#             projectsToDelete.append(p)
#     newInstance = Instance()
#     newInstance.add_projects([(p, instance.costs[p]) for p in instance.projects if p not in projectsToDelete])
#     newInstance.budget_limit = instance.budget_limit
#     newInstance.file_path = instance.file_path
#     newInstance.file_name = instance.file_name
#     newInstance.meta = deepcopy(instance.meta)
#     newProfile = []
#     for ballot in profile:
#         newBallot = tuple(p for p in ballot if p not in projectsToDelete)
#         if len(newBallot) > 0:
#             newProfile.append(newBallot)
#     return (newInstance, newProfile)
#
#
# def preprocessCohesiveness(instance, profile):
#     projectsToDelete = []
#     for p in instance.projects:
#         if sum(p in ballot for ballot in profile) * instance.budget_limit / len(profile) < instance.costs[p]:
#             projectsToDelete.append(p)
#     newInstance = Instance()
#     newInstance.add_projects([(p, instance.costs[p]) for p in instance.projects if p not in projectsToDelete])
#     newInstance.budget_limit = instance.budget_limit
#     newInstance.file_path = instance.file_path
#     newInstance.file_name = instance.file_name
#     newInstance.meta = deepcopy(instance.meta)
#     newProfile = []
#     for ballot in profile:
#         newBallot = tuple(p for p in ballot if p not in projectsToDelete)
#         if len(newBallot) > 0:
#             newProfile.append(newBallot)
#     return (newInstance, newProfile)
#
#
# ###################
# # ILPs to approx FS
# ###################
#
# def avgFairShareRatioILP(instance, profile, approxRatio=1, verbose=True):
#     m = Model(solver_name=GRB)
#
#     multiplicity = {}
#     for ballot in profile:
#         if ballot in multiplicity:
#             multiplicity[ballot] += 1
#         else:
#             multiplicity[ballot] = 1
#
#     projectVars = {p: m.add_var(var_type=BINARY, name="p_" + str(p)) for p in instance.projects}
#     shareVars = {ballot: m.add_var(var_type=CONTINUOUS) for ballot in multiplicity}
#     shareRatioVars = {ballot: m.add_var(var_type=CONTINUOUS, lb=0, ub=1) for ballot in multiplicity}
#
#     m.objective = mip.maximize(xsum(mul * shareRatioVars[ballot] for ballot, mul in multiplicity.items()))
#
#     m.add_constr(xsum(projectVars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit)
#
#     for ballot in multiplicity:
#         m.add_constr(
#             shareVars[ballot] == xsum(projectVars[p] * instance.ballot_share(ballot, profile, [p]) for p in ballot))
#         m.add_constr(shareRatioVars[ballot] <= shareVars[ballot] / (instance.fair_share(ballot, profile) * approxRatio))
#
#     if not verbose:
#         m.verbose = 0
#
#     m.optimize()
#
#     # print("OPTIMAL SOLUTION IS {}".format(sum(v.x for v in shareRatioVars.values()) / len(profile)))
#     # print("SHARE RATIO ARE:")
#     # for k, v in shareVars.items():
#     #     print("{} -> {}".format(k, v.x))
#
#     return ([shareRatioVars[ballot].x for ballot in profile], [p for p in instance.projects if projectVars[p].x == 1])
#
#
# def avg_fairshare_ratio_max_rule(instance, profile):
#     return avgFairShareRatioILP(instance, profile, approxRatio=1, verbose=False)[1]
#
#
# def minFairShareRatioILP(instance, profile, approxRatio=1, verbose=True):
#     m = Model(solver_name=GRB)
#
#     multiplicity = {}
#     for ballot in profile:
#         if ballot in multiplicity:
#             multiplicity[ballot] += 1
#         else:
#             multiplicity[ballot] = 1
#
#     projectVars = {p: m.add_var(var_type=BINARY, name="p_" + str(p)) for p in instance.projects}
#     shareVars = {ballot: m.add_var(var_type=CONTINUOUS) for ballot in multiplicity}
#     minVar = m.add_var(var_type=CONTINUOUS, lb=0, ub=1, name="minVar")
#
#     m.objective = minVar
#     m.sense = MAXIMIZE
#
#     m.add_constr(xsum(projectVars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit,
#                  name="budgetCstr")
#
#     ballotIndex = 0
#     for ballot in multiplicity:
#         m.add_constr(
#             shareVars[ballot] == xsum(projectVars[p] * instance.ballot_share(ballot, profile, [p]) for p in ballot),
#             name="shareVarCstr_" + str(ballotIndex))
#         m.add_constr(minVar <= shareVars[ballot] / (instance.fair_share(ballot, profile) * approxRatio),
#                      name="minVarConstr_" + str(ballotIndex))
#         ballotIndex += 1
#
#     if not verbose:
#         m.verbose = 0
#
#     status = m.optimize()
#
#     return ([min(shareVars[ballot].x / (instance.fair_share(ballot, profile) * approxRatio), 1) for ballot in profile],
#             sorted([p for p in instance.projects if projectVars[p].x == 1]))
#
#
# def min_fairshare_ratio_max_rule(instance, profile):
#     return minFairShareRatioILP(instance, profile, approxRatio=1, verbose=False)[1]
#
#
# def fairShareApproxNumAgentsILP(instance, profile, approxRatio=1, verbose=False):
#     m = Model(solver_name=GRB)
#
#     multiplicity = {}
#     for ballot in profile:
#         if ballot in multiplicity:
#             multiplicity[ballot] += 1
#         else:
#             multiplicity[ballot] = 1
#
#     projectVars = {p: m.add_var(var_type=BINARY, name="p_" + str(p)) for p in instance.projects}
#     ballotVars = {ballot: m.add_var(var_type=BINARY) for ballot in multiplicity}
#
#     m.objective = maximize(xsum(ballotVars[ballot] * mul for (ballot, mul) in multiplicity.items()))
#
#     m.add_constr(xsum(projectVars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit)
#
#     for ballot in multiplicity:
#         m.add_constr(xsum(projectVars[p] * instance.ballot_share(ballot, profile, [p]) for p in
#                           ballot) >= approxRatio * instance.fair_share(ballot, profile) * ballotVars[ballot])
#
#     if not verbose:
#         m.verbose = 0
#
#     m.optimize()
#
#     return [ballotVars[ballot].x for ballot in profile], [p for p in instance.projects if projectVars[p].x == 1]
#
#
# def agents_with_fairshare_max_rule(instance, profile):
#     return fairShareApproxNumAgentsILP(instance, profile, approxRatio=1, verbose=False)[1]
#
#
# def avg_fairshare_l1_dist_ILP(instance, profile, approxRatio=1, verbose=True):
#     m = Model(solver_name=GRB)
#
#     multiplicity = {}
#     for ballot in profile:
#         if ballot in multiplicity:
#             multiplicity[ballot] += 1
#         else:
#             multiplicity[ballot] = 1
#
#     project_vars = {p: m.add_var(var_type=BINARY, name="p_" + str(p)) for p in instance.projects}
#     share_vars = {ballot: m.add_var(var_type=CONTINUOUS) for ballot in multiplicity}
#     share_abs_vars = {ballot: m.add_var(var_type=CONTINUOUS) for ballot in multiplicity}
#
#     m.objective = mip.minimize(xsum(mul * share_abs_vars[ballot] for ballot, mul in multiplicity.items()))
#
#     m.add_constr(xsum(project_vars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit)
#
#     for ballot in multiplicity:
#         m.add_constr(
#             share_vars[ballot] == xsum(project_vars[p] * instance.ballot_share(ballot, profile, [p]) for p in ballot))
#         m.add_constr(share_abs_vars[ballot] >= share_vars[ballot] - instance.fair_share(ballot, profile) * approxRatio)
#         m.add_constr(share_abs_vars[ballot] >= instance.fair_share(ballot, profile) * approxRatio - share_vars[ballot])
#
#     if not verbose:
#         m.verbose = 0
#
#     m.optimize()
#
#     # print("OPTIMAL SOLUTION IS {}".format(sum(v.x for v in shareRatioVars.values()) / len(profile)))
#     # print("SHARE RATIO ARE:")
#     # for k, v in shareVars.items():
#     #     print("{} -> {}".format(k, v.x))
#
#     return [share_abs_vars[ballot].x for ballot in profile], [p for p in instance.projects if project_vars[p].x == 1]
#
#
# def avg_fairshare_l1_dist_min_rule(instance, profile):
#     return avg_fairshare_l1_dist_ILP(instance, profile, approxRatio=1, verbose=False)[1]

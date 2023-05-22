# from fractions import Fraction
# from copy import deepcopy
#
# from satisfactionfunctions import cost_sat, cardinality_sat, effort_sat
# from tiebreaking import lexicographic_tie_breaking, app_score_tie_breaking
#
#
# FLOATCORRECTOR = 1000000000000000
#
#
# def is_affordable(instance, sat_functions, project, budgets):
#     rich = set(i for i in range (len(sat_functions)) if sat_functions[i].sat([project]) > 0)
#     poor = set()
#     while len(rich) > 0:
#         poor_budget = sum(budgets[i] for i in poor)
#         affordability_numerator = Fraction(instance.costs[project] - poor_budget)
#         affordability_denominator = sum(Fraction(sat_functions[i].sat([project])) for i in rich)
#         affordability = Fraction(affordability_numerator, affordability_denominator)
#         new_poor = {i for i in rich if budgets[i] < affordability * sat_functions[i].sat([project])}
#         if len(new_poor) == 0:
#             contributions = [0] * len(sat_functions)
#             for i in poor:
#                 contributions[i] = budgets[i]
#             for i in rich:
#                 contributions[i] = affordability * sat_functions[i].sat([project])
#             return affordability, contributions
#         rich -= new_poor
#         poor.update(new_poor)
#     return None, None
#
#
# def method_equal_share(instance, profile, sat_functions, afford_func=is_affordable,
#                        tie_breaking=app_score_tie_breaking):
#     alloc = []
#     local_budgets = [Fraction(Fraction(instance.budgetLimit), len(profile)) for _ in profile]
#     affordabilities = {p: afford_func(instance, sat_functions, p, local_budgets) for p in instance.projects}
#     # print("**********************")
#     # print([v[0] for v in affordabilities.values()])
#     while not all(afford[0] is None for afford in affordabilities.values()):
#         min_affordability = min(v[0] for v in affordabilities.values() if v[0] is not None)
#         tied_projects = [project for project in affordabilities if affordabilities[project][0] == min_affordability]
#         # print("!!!!!!!!!! tied = {}".format(tied_projects))
#         # print([v[0] for v in affordabilities.values()])
#         selected_project = tie_breaking(instance, profile, tied_projects)
#         # print(selected_project)
#         alloc.append(selected_project)
#         local_budgets = [local_budgets[i] - affordabilities[selected_project][1][i] for i in range(len(profile))]
#         affordabilities = {p: afford_func(instance, sat_functions, p, local_budgets)
#                            for p in instance.projects if p not in alloc}
#     return alloc
#
#
# def method_equal_share_irresolute(instance, profile, sat_functions, afford_func=is_affordable):
#
#     def aux(instance, profile, sat_functions, alloc, allocs, local_budgets, affordabilities):
#         # print("**********************")
#         # print([v[0] for v in affordabilities.values()])
#         if all(afford[0] is None for afford in affordabilities.values()):
#             allocs.add(tuple(sorted(alloc)))
#             # print("Finished, added " + str(alloc))
#         else:
#             min_affordability = min(v[0] for v in affordabilities.values() if v[0] is not None)
#             tied_projects = [project for project in affordabilities if affordabilities[project][0] == min_affordability]
#             # print("!!!!!!!!!! tied = {}".format(tied_projects))
#             # print([(k, v[0]) for k, v in affordabilities.items()])
#             for selected_project in tied_projects:
#                 # print(selected_project)
#                 new_alloc = deepcopy(alloc) + [selected_project]
#                 # print(local_budgets)
#                 # print([v[0] for v in affordabilities.values()])
#                 new_local_budgets = tuple(local_budgets[i] - affordabilities[selected_project][1][i]
#                     for i in range(len(profile)))
#                 new_affordabilities = {p: afford_func(instance, sat_functions, p, new_local_budgets)
#                     for p in instance.projects if p not in new_alloc}
#                 # print(new_alloc)
#                 # print(new_local_budgets)
#                 # print([v[0] for v in new_affordabilities.values()])
#                 aux(instance, profile, sat_functions, new_alloc, allocs, new_local_budgets, new_affordabilities)
#
#     allocs = set()
#     initial_local_budgets = tuple(Fraction(Fraction(instance.budgetLimit), len(profile)) for _ in profile)
#     initial_affordabilities = {p: afford_func(instance, sat_functions, p, initial_local_budgets)
#         for p in instance.projects}
#     aux(instance, profile, sat_functions, [], allocs, initial_local_budgets, initial_affordabilities)
#
#     return list(allocs)
#
#
# #### COST SHORTCUTS
#
# def method_equal_share_cost(instance, profile, afford_func=is_affordable):
#     return method_equal_share(instance, profile, [cost_sat(instance, ballot) for ballot in profile],
#                               afford_func=afford_func)
#
# def method_equal_share_cost_irresolute(instance, profile, afford_func=is_affordable):
#     return method_equal_share_irresolute(instance, profile, [cost_sat(instance, ballot) for ballot in profile],
#                                          afford_func=afford_func)
#
# #### CARDINALITY SHORTCUTS
#
# def method_equal_share_cardinality(instance, profile, afford_func=is_affordable):
#     return method_equal_share(instance, profile, [cardinality_sat(instance, ballot) for ballot in profile],
#                               afford_func=afford_func)
#
# def method_equal_share_cardinality_irresolute(instance, profile, afford_func=is_affordable):
#     return method_equal_share_irresolute(instance, profile, [cardinality_sat(instance, ballot) for ballot in profile],
#                                          afford_func=afford_func)

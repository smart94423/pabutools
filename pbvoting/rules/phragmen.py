# from fractions import Fraction
# from copy import deepcopy
#
# from tiebreaking import app_score_tie_breaking, priority_tie_breaking
#
#
# def seq_phragmen_exhaustive(instance, profile, initial_load=None, partial_alloc=None,
#                             tie_breaking=app_score_tie_breaking):
#     load = initial_load
#     if load is None:
#         load = [0 for _ in range(len(profile))]
#     alloc = partial_alloc
#     if alloc is None:
#         alloc = []
#     current_cost = instance.cost(alloc)
#
#     available_projects = set(project for project in instance.projects if project not in alloc and instance.costs[project] <= instance.budgetLimit)
#     approval_score = {project: sum(1 for ballot in profile if project in ballot) for project in instance.projects}
#     for project in instance.projects:
#         if approval_score[project] == 0 and project in available_projects:
#             available_projects.remove(project)
#     to_remove = []
#     for project in available_projects:
#         if instance.costs[project] + current_cost > instance.budgetLimit:
#             to_remove.append(project)
#     for project in to_remove:
#         available_projects.remove(project)
#
#     while len(available_projects) > 0:
#         approvers_load = {project: sum(Fraction(load[i]) for i in range(len(profile)) if project in profile[i])
#                           for project in available_projects}
#         new_maxload = {project: Fraction(approvers_load[project] + Fraction(instance.costs[project]), approval_score[project])
#                        for project in available_projects}
#         min_new_maxload = min(new_maxload.values())
#         tied_projects = [project for project in available_projects if new_maxload[project] == min_new_maxload]
#         selected_project = tie_breaking(instance, profile, tied_projects)
#
#         for i in range(len(profile)):
#             if selected_project in profile[i]:
#                 load[i] = new_maxload[selected_project]
#         alloc.append(selected_project)
#         current_cost += instance.costs[selected_project]
#         available_projects.remove(selected_project)
#
#         to_remove = []
#         for project in available_projects:
#             if instance.costs[project] + current_cost > instance.budgetLimit:
#                 to_remove.append(project)
#         for project in to_remove:
#             available_projects.remove(project)
#
#     return alloc
#
#
# def seq_phragmen(instance, profile, initial_load=None, partial_alloc=None, tie_breaking=app_score_tie_breaking):
#     load = initial_load
#     if load is None:
#         load = [0 for _ in range(len(profile))]
#     alloc = partial_alloc
#     if alloc is None:
#         alloc = []
#     current_cost = instance.cost(alloc)
#
#     available_projects = set(project for project in instance.projects if project not in alloc and instance.costs[project] <= instance.budgetLimit)
#     approval_score = {project: sum(1 for ballot in profile if project in ballot) for project in instance.projects}
#     for project in instance.projects:
#         if approval_score[project] == 0 and project in available_projects:
#             available_projects.remove(project)
#
#     while len(available_projects) > 0:
#         approvers_load = {project: sum(Fraction(load[i]) for i in range(len(profile)) if project in profile[i])
#                           for project in available_projects}
#         new_maxload = {project: Fraction(approvers_load[project] + Fraction(instance.costs[project]), approval_score[project])
#                        for project in available_projects}
#         min_new_maxload = min(new_maxload.values())
#
#         tied_projects = [project for project in available_projects if new_maxload[project] == min_new_maxload]
#
#         new_cost = [current_cost + instance.costs[project] for project in tied_projects]
#         if any(c > instance.budgetLimit for c in new_cost):
#             break
#
#         selected_project = tie_breaking(instance, profile, tied_projects)
#
#         for i in range(len(profile)):
#             if selected_project in profile[i]:
#                 load[i] = new_maxload[selected_project]
#         alloc.append(selected_project)
#         current_cost += instance.costs[selected_project]
#         available_projects.remove(selected_project)
#
#     return alloc
#
# def seq_phragmen_irresolute(instance, profile, initial_load=None, partial_alloc=None):
#
#     def aux(instance, profile, available_projects, load, alloc, current_cost, allocs):
#         if len(available_projects) == 0:
#             allocs.add(tuple(sorted(alloc)))
#         else:
#             approvers_load = {project: sum(Fraction(load[i]) for i in range(len(profile)) if project in profile[i])
#                               for project in available_projects}
#             new_maxload = {project: Fraction(approvers_load[project] + Fraction(instance.costs[project]), approval_score[project])
#                            for project in available_projects}
#             min_new_maxload = min(new_maxload.values())
#
#             tied_projects = [project for project in available_projects if new_maxload[project] == min_new_maxload]
#             new_cost = [current_cost + instance.costs[project] for project in tied_projects]
#             if any(c > instance.budgetLimit for c in new_cost):
#                 allocs.add(tuple(sorted(alloc)))
#             else:
#
#                 for selected_project in tied_projects:
#                     new_load = deepcopy(load)
#                     for i in range(len(profile)):
#                         if selected_project in profile[i]:
#                             new_load[i] = new_maxload[selected_project]
#                     new_alloc = deepcopy(alloc) + [selected_project]
#                     new_current_cost = current_cost + instance.costs[selected_project]
#                     new_available_projects = deepcopy(available_projects)
#                     new_available_projects.remove(selected_project)
#                     aux(instance, profile, new_available_projects, new_load, new_alloc, new_current_cost, allocs)
#
#     load = initial_load
#     if load is None:
#         load = [0 for _ in range(len(profile))]
#     alloc = partial_alloc
#     if alloc is None:
#         alloc = []
#     current_cost = instance.cost(alloc)
#
#     available_projects = set(project for project in instance.projects if project not in alloc and instance.costs[project] <= instance.budgetLimit)
#     approval_score = {project: sum(1 for ballot in profile if project in ballot) for project in instance.projects}
#     for project in instance.projects:
#         if approval_score[project] == 0 and project in available_projects:
#             available_projects.remove(project)
#
#     allocs = set()
#     aux(instance, profile, available_projects, load, [], current_cost, allocs)
#
#     return list(allocs)

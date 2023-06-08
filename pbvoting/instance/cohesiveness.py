# from pbvoting.utils import powerset, fixed_size_subsets
#
#
# def is_cohesive(instance, profile, P, N):
#     if instance.total_cost(P) > len(N) * instance.budget_limit / len(profile):
#         return False
#     if len(N) == 0 or len(P) == 0:
#         return False
#     for i in N:
#         if not set(P) <= set(profile[i]):
#             return False
#     return True
#
#
# def cohesive_groups(instance, profile, projects=None):
#     if projects is None:
#         projects = instance.projects
#     res = set()
#     for N in powerset(range(len(profile))):
#         for P in powerset(projects):
#             if is_cohesive(instance, profile, P, N):
#                 res.add((N, P))
#     return res
#
#
# def maximal_P_cohesive(instance, profile, P):
#     res = set()
#     for i in range(len(profile)):
#         if set(P) <= set(profile[i]):
#             res.add(i)
#     if len(res) > 0 and instance.total_cost(P) <= len(res) * instance.budget_limit / len(profile):
#         return tuple(res)
#     else:
#         return None
#
#
# def maximal_cohesive_groups(instance, profile, projects=None):
#     if projects is None:
#         projects = instance.projects
#     res = set()
#     for P in powerset(projects):
#         N = maximal_P_cohesive(instance, profile, P)
#         if N:
#             res.add((N, P))
#     return res
#
#
# def exists_k_cohesive(instance, profile, k):
#     for projects in fixed_size_subsets(instance.projects, k):
#         if maximal_P_cohesive(instance, profile, projects) is not None:
#             return True
#     return False

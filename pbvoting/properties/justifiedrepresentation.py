# from cohesiveness import *
#
#
# def isEJR(instance, profile, alloc):
#     for (N, P) in cohesive_groups(instance, profile):
#         one_is_sat = False
#         for i in N:
#             size_intersection = len([p for p in alloc if p in profile[i]])
#             if size_intersection >= len(P):
#                 one_is_sat = True
#                 break
#         if not one_is_sat:
#             return False, (N, P)
#     return True, None

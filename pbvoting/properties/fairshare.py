# from mip import *
#
#
# def project_share(self, profile, project):
#     return Fraction(Fraction(Decimal(self.costs[project])), self.project_support(profile, project))
#
#
# def ballot_share(self, ballot, profile, projSet):
#     res = Fraction(0, 1)
#     for p in projSet:
#         if p in ballot:
#             c = self.project_support(profile, p)
#             res += Fraction(Fraction(Decimal(self.costs[p])), c)
#     return res
#
#
# def share_vector(self, profile, projSet):
#     return tuple(self.ballot_share(ballot, profile, projSet) for ballot in profile)
#
#
# def fair_share(self, ballot, profile):
#     return min(self.ballot_share(ballot, profile, ballot),
#                Fraction(Fraction(Decimal(self.budget_limit)), len(profile)))
#
#
# def fair_share_vector(self, profile):
#     return tuple(self.fair_share(ballot, profile) for ballot in profile)
#
#
# def findFSAlloc(instance, profile):
#     m = Model()
#
#     projectVars = {p: m.add_var(var_type=BINARY, name="p_" + str(p)) for p in instance.projects}
#     minVar = m.add_var(name="minvar")
#
#     m.objective = maximize(minVar)
#
#     m.add_constr(xsum(projectVars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit)
#
#     for ballot in set(profile):
#         m.add_constr(xsum(projectVars[p] * instance.ballot_share(ballot, profile, [p]) for p in ballot) >= minVar)
#
#     # m.write("model.lp")
#
#     m.optimize()
#
#     return [p for p in instance.projects if projectVars[p].x == 1]
#
#
# def findMaxFSAlloc(instance, profile):
#     m = Model()
#
#     uniqBallots = dict()
#     for b in profile:
#         if b in uniqBallots:
#             uniqBallots[b] += 1
#         else:
#             uniqBallots[b] = 1
#
#     projectVars = {p: m.add_var(var_type=BINARY, name="p_" + str(p)) for p in instance.projects}
#     ballotVars = {b: m.add_var(var_type=BINARY) for b in uniqBallots}
#
#     m.objective = maximize(xsum(ballotVars[b] * num for (b, num) in uniqBallots.items()))
#
#     m.add_constr(xsum(projectVars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit)
#
#     for ballot in uniqBallots:
#         m.add_constr(
#             xsum(projectVars[p] * instance.ballot_share(ballot, profile, [p]) for p in ballot) >= instance.fair_share(
#                 ballot, profile) * ballotVars[ballot])
#
#     # m.write("model.lp")
#
#     m.optimize()
#
#     return [p for p in instance.projects if projectVars[p].x == 1]
#
#
# def isFairShare(instance, profile, budgetAllocation, approxRatio=1):
#     for b in profile:
#         fairShare = instance.fair_share(b, profile)
#         currentShare = instance.ballot_share(b, profile, budgetAllocation)
#         if currentShare < fairShare * approxRatio:
#             return (False, (b, currentShare, fairShare))
#     return (True, None)
#
#
# def isAllNonZeroShare(instance, profile, budgetAllocation):
#     for b in profile:
#         if instance.ballot_share(b, profile, budgetAllocation) == 0:
#             return (False, b)
#     return (True, None)
#
#
# def agentFairShareRatio(instance, ballot, profile, budgetAllocation):
#     share = instance.ballot_share(ballot, profile, budgetAllocation)
#     fairShare = instance.fair_share(ballot, profile)
#     if share >= fairShare:
#         return 1
#     else:
#         return share / fairShare
#
#
# def vectorFairShareRatio(instance, profile, budgetAllocation):
#     return tuple(agentFairShareRatio(instance, ballot, profile, budgetAllocation) for ballot in profile)
#
#
# def isApproxFSNumAgents(instance, profile, budgetAllocation, approxRatio=1):
#     fail = []
#     success = []
#     for b in profile:
#         fairShare = min(instance.ballot_share(b, profile, b), instance.budget_limit / len(profile))
#         currentShare = instance.ballot_share(b, profile, budgetAllocation)
#         if currentShare < fairShare:
#             fail.append(b)
#         else:
#             success.append(b)
#     if len(success) / len(profile) < approxRatio:
#         return False, fail
#     return True, success
#
#
# def isFairShareUpToOneProject(instance, profile, budgetAllocation):
#     for b in profile:
#         fairShare = instance.fair_share(b, profile)
#         currentShare = instance.ballot_share(b, profile, budgetAllocation)
#         if currentShare < fairShare:
#             pExists = False
#             for p in instance.projects:
#                 if p not in budgetAllocation:
#                     if currentShare + instance.ballot_share(b, profile, [p]) >= fairShare:
#                         pExists = True
#                         break
#             if not pExists:
#                 return False, b
#     return True, None
#
#
# def isLocalFairShare(instance, profile, budgetAllocation):
#     for p in instance.projects:
#         if p not in budgetAllocation:
#             bExists = False
#             pApproved = False
#             for b in profile:
#                 if p in b:
#                     bApproved = True
#                     fairShare = min(instance.ballot_share(b, profile, b), instance.budget_limit / len(profile))
#                     currentShare = instance.ballot_share(b, profile, budgetAllocation)
#                     if currentShare + instance.ballot_share(b, profile, [p]) >= fairShare:
#                         bExists = True
#                         break
#             if pApproved and not bExists:
#                 return (False, p)
#     return (True, None)
#
#
# def isLexDominated(vector1, vector2):
#     for i in range(len(vector1)):
#         if vector2[i] > vector1[i]:
#             return True
#         if vector1[i] > vector2[i]:
#             return False
#     return None
#
#
# def getLexShareVector(instance, profile, budgetAllocation):
#     res = []
#     for ballot in profile:
#         share = instance.ballot_share(ballot, profile, budgetAllocation)
#         if share > instance.fair_share(ballot, profile):
#             res.append(float('inf'))
#         else:
#             res.append(share)
#     return sorted(res)
#
#
# def maxLexShare(instance, profile):
#     argBest = None
#     lexVectBest = None
#     for budgetAllocation in instance.budget_allocations():
#         lexVect = getLexShareVector(instance, profile, budgetAllocation)
#         if lexVectBest == None or isLexDominated(lexVectBest, lexVect):
#             argBest = [budgetAllocation]
#             lexVectBest = lexVect
#         elif isLexDominated(lexVectBest, lexVect) == None:
#             argBest.append(budgetAllocation)
#     return argBest
#
#
# def isParetoDominated(vector1, vector2):
#     oneStrict = False
#     for i in range(len(vector1)):
#         if vector1[i] > vector2[i]:
#             return False
#         if vector2[i] > vector1[i]:
#             oneStrict = True
#     return oneStrict
#
#
# def ParetoShareDominantAllocs(instance, profile):
#     res = []
#     for budgetAllocation in instance.budget_allocations():
#         shareVector = [instance.ballot_share(ballot, profile, budgetAllocation) for ballot in profile]
#         newNotDominated = True
#         newRes = []
#         #		print("Trying {} with share vector {}".format(budgetAllocation, shareVector))
#         for oldBudgetAllocation in res:
#             oldShareVector = [instance.ballot_share(ballot, profile, oldBudgetAllocation) for ballot in profile]
#             #			print("\tAgainst {} with vector {}, oldDominated = {}, newDominated = {}".format(oldBudgetAllocation, oldShareVector, isParetoDominated(oldShareVector, shareVector), isParetoDominated(shareVector, oldShareVector)))
#             if not isParetoDominated(oldShareVector, shareVector):
#                 newRes.append(oldBudgetAllocation)
#             if isParetoDominated(shareVector, oldShareVector):
#                 newNotDominated = False
#         if newNotDominated:
#             newRes.append(budgetAllocation)
#         res = newRes
#     #		print("res = {}".format(res))
#     return res
#
#
# def isFSDominant(instance, profile, budgetAllocation):
#     dominants = ParetoShareDominantAllocs(instance, profile)
#     if budgetAllocation in dominants:
#         return (True, None)
#     else:
#         return (False, dominants)

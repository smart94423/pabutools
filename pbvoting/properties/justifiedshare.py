# from utils import *
#
# from fractions import Fraction
# from copy import deepcopy
#
# from cohesiveness import *
#
# def isStrongEJS(instance, profile, budgetAllocation):
# 	for (N, P) in cohesive_groups(instance, profile):
# 		allAreSat = True
# 		for i in N:
# 			if instance.ballot_share(profile[i], profile, budgetAllocation) < instance.ballot_share(profile[i], profile, P):
# 				allAreSat = False
# 				break
# 		if not allAreSat:
# 			return (False, (N, P))
# 	return (True, None)
#
# def isEJS(instance, profile, budgetAllocation):
# 	for (N, P) in cohesive_groups(instance, profile):
# 		oneIsSat = False
# 		for i in N:
# 			if instance.ballot_share(profile[i], profile, budgetAllocation) >= instance.ballot_share(profile[i], profile, P):
# 				oneIsSat = True
# 				break
# 		if not oneIsSat:
# 			return (False, (N, P))
# 	return (True, None)
#
# def isPJS(instance, profile, budgetAllocation):
# 	for (N, P) in cohesive_groups(instance, profile):
# 		averageShare = 0
# 		for i in N:
# 			averageShare += instance.ballot_share(profile[i], profile, budgetAllocation)
# 		averageShare = Fraction(averageShare, len(N))
# 		if averageShare < instance.ballot_share(profile[N[0]], profile, P):
# 			return (False, (N, P))
# 	return (True, None)
#
# def isEJSUpToOneProject(instance, profile, budgetAllocation):
# 	for (N, P) in cohesive_groups(instance, profile):
# 		oneIsSat = False
# 		for i in N:
# 			agentShare = instance.ballot_share(profile[i], profile, budgetAllocation)
# 			shareBound = instance.ballot_share(profile[i], profile, P)
# 			if agentShare >= shareBound:
# 				oneIsSat = True
# 				break
# 			else:
# 				pExists = False
# 				for p in instance.projects:
# 					if p not in budgetAllocation:
# 						if agentShare + instance.ballot_share(profile[i], profile, [p]) >= shareBound:
# 							pExists = True
# 							break
# 				if pExists:
# 					oneIsSat = True
# 					break
# 		if not oneIsSat:
# 			return (False, (N, P))
# 	return (True, None)
#
# def isLocalEJS(instance, profile, budgetAllocation):
# 	for (N, P) in cohesive_groups(instance, profile):
# 		for p in P:
# 			if p not in budgetAllocation:
# 				iExists = False
# 				for i in N:
# 					agentShare = instance.ballot_share(profile[i], profile, budgetAllocation)
# 					shareBound = instance.ballot_share(profile[i], profile, P)
# 					if agentShare + instance.ballot_share(profile[i], profile, [p]) >= shareBound:
# 						iExists = True
# 						break
# 				if not iExists:
# 					return (False, (N, P, p))
# 	return (True, None)
#
# def greedyEJS(instance, profile):
# 	# print("\nSTART NEW\n " + str(profile))
#
# 	res = set()
# 	satAgents = set()
# 	projects = deepcopy(instance.projects)
# 	profile = [list(b) for b in profile]
# 	while len(profile) > 0:
# 		# print("Profile = {} and Projects = {}".format(profile, projects))
# 		best = None
# 		argBest = None
# 		for (N, P) in maximal_cohesive_groups(instance, profile, projects):
# 			# print((N, P))
# 			maxShare = 0
# 			for i in N:
# 				maxShare = max(maxShare, instance.ballot_share(profile[i], profile, P))
# 			if best == None or maxShare > best:
# 				best = maxShare
# 				argBest = [(N, P)]
# 			elif maxShare == best:
# 				argBest.append((N, P))
# 		# print("best = {} argBest = {}".format(best, argBest))
#
# 		if best == None:
# 			break
# 		for p in argBest[0][1]:
# 			res.add(p)
# 			projects.remove(p)
# 		for i in sorted(argBest[0][0], reverse = True):
# 			# print(i)
# 			# print(profile)
# 			del profile[i]
# 	return res
#
# def isGreedyEJS(instance, profile, budgetAllocation):
# 	greedyEJSAlloc = greedyEJS(instance, profile)
# 	if budgetAllocation == greedyEJSAlloc:
# 		return (True, None)
# 	else:
# 		return (False, greedyEJSAlloc)
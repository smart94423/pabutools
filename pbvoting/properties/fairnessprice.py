# from fractions import Fraction
#
# from mip import *
#
# def cardinalWelfare(instance, profile, budgetAllocation):
# 	res = 0
# 	for ballot in profile:
# 		for p in ballot:
# 			if p in budgetAllocation:
# 				res += 1
# 	return res
#
# def maxCardinalWelfare(instance, profile):
# 	m = Model()
#
# 	projectVars = {p: m.add_var(var_type = BINARY, name = "p_" + str(p)) for p in instance.projects}
#
# 	m.add_constr(xsum(projectVars[p] * instance.costs[p] for p in instance.projects) <= instance.budget_limit)
#
# 	m.objective = maximize(sum(projectVars[p] for ballot in profile for p in ballot))
#
# 	m.verbose = 0
# 	m.optimize()
#
# 	return [p for p in instance.projects if projectVars[p].x == 1]
#
# def priceOfFairness(instance, profile, budgetAllocation):
# 	argOpt = maxCardinalWelfare(instance, profile)
# 	opt = cardinalWelfare(instance, profile, argOpt)
# 	return Fraction(cardinalWelfare(instance, profile, budgetAllocation), opt)
#
# def priceOfFairnessCriteria(instance, profile, posCriteria = [], negCriteria = []):
# 	argOpt = maxCardinalWelfare(instance, profile)
# 	opt = cardinalWelfare(instance, profile, argOpt)
#
# 	best = None
# 	for budgetAllocation in instance.budget_allocations():
# 		allSat = True
# 		for c in posCriteria:
# 			if not c(instance, profile, budgetAllocation)[0]:
# 				allSat = False
# 				break
# 		if allSat:
# 			for c in negCriteria:
# 				if c(instance, profile, budgetAllocation)[0]:
# 					allSat = False
# 					break
# 			if allSat:
# 				welfare = cardinalWelfare(instance, profile, budgetAllocation)
# 				if best == None or welfare > best:
# 					best = welfare
#
# 	return Fraction(best, opt)
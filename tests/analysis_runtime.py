import time
import os

from pbvoting.election import SatisfactionProfile, SatisfactionMultiProfile, Cost_Sat, parse_pabulib
from pbvoting.rules import greedy_welfare


def greedy_runtime():
    print("============== Run Time Analysis - Greedy Rule ==============")
    for file in os.listdir(os.path.join("test_elections")):
        if file.endswith(".pb"):
            print("------ {} ------".format(file))
            t = time.time()
            instance, profile = parse_pabulib(os.path.join("test_elections", file))
            print("Parsed in {} seconds".format(time.time() - t))
            print("Instance with {} projects -- Profile with {} voters".format(len(instance), len(profile)))
            t = time.time()
            sat_multiprofile = SatisfactionMultiProfile(profile=profile, sat_class=Cost_Sat)
            print("Sat-Multi-Profile created in {} seconds".format(time.time() - t))
            print("Satisfaction Multi-Profile of length {} (saved {})".format(len(sat_multiprofile),
                                                                              len(profile) - len(sat_multiprofile)))
            outcome2 = greedy_welfare(instance, profile, sat_profile=sat_multiprofile, is_sat_additive=True,
                                      resoluteness=True)
            print("{} - Time greedy on {} for sat multi-profile".format(time.time() - t, file))
            t = time.time()
            sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Sat)
            print("Sat-Profile created in {} seconds".format(time.time() - t))
            outcome1 = greedy_welfare(instance, profile, sat_profile=sat_profile,  is_sat_additive=True,
                                      resoluteness=True)
            print("{} - Time greedy on {} for sat profile".format(time.time() - t, file))


if __name__ == "__main__":
    greedy_runtime()

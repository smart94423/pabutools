import os
import time

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from pbvoting.election import parse_pabulib, SatisfactionMultiProfile, Cost_Sat, SatisfactionProfile
from pbvoting.rules import greedy_welfare
from pbvoting.rules.maxwelfare import max_welfare


def multiproifle_gain(folder_path, csv_file="multiprofile_gain.csv", recompute=False):
    print("============== Multiprofile Gain Analysis ==============")

    if not recompute and os.path.isfile(os.path.join("csv", csv_file)):
        data = pd.read_csv(os.path.join("csv", csv_file), sep=";", encoding='utf-8')
    else:
        data = {"file": [], "gains": [], "gains_percent": [], "num_voters": [], "num_sat": [], "avg_vote_length": [],
                "avg_vote_length_cat": []}
        for file in os.listdir(os.path.join(folder_path)):
            if file.endswith(".pb"):
                print("File: {}".format(file))
                instance, profile = parse_pabulib(os.path.join(folder_path, file))
                sat_multiprofile = SatisfactionMultiProfile(profile=profile, sat_class=Cost_Sat)
                data["file"].append(file)
                data["gains"].append(len(profile) - len(sat_multiprofile))
                data["gains_percent"].append(1 - len(sat_multiprofile) / len(profile))
                data["num_voters"].append(len(profile))
                data["num_sat"].append(len(sat_multiprofile))
                data["avg_vote_length"].append(sum(len(b) for b in profile) / len(profile))
                data["avg_vote_length_cat"].append(round(sum(len(b) for b in profile) / len(profile)))
        data = pd.DataFrame(data)
        data.to_csv(os.path.join("csv", csv_file), sep=";", encoding='utf-8')

    plt.close('all')

    sns.set_theme()

    g = sns.histplot(
        data=data,
        x="gains_percent",
        multiple="stack",
        binwidth=None
    )

    plt.show()

    plt.close('all')

    g = sns.boxplot(
        data=data,
        x="avg_vote_length_cat",
        y="gains_percent",
    )
    g.set_yticks(np.linspace(0, 1, 11))

    plt.show()


def multiprofile_runtime(folder_path, rules, rule_params, csv_file="multiprofile_runtime.csv", recompute=False):
    print("============== Multiprofile Runtime Analysis ==============")

    if not recompute and os.path.isfile(os.path.join("csv", csv_file)):
        data = pd.read_csv(os.path.join("csv", csv_file), sep=";", encoding='utf-8')
    else:
        data = {"file": [], "rule": [], "runtime_profile": [], "runtime_multiprofile": [], "time_gains": [],
                "time_gains_percent": [], "length_gains": [], "length_gains_percent": [],
                "num_voters": [], "num_sat": [], "avg_vote_length": [], "avg_vote_length_cat": []}
        for file in os.listdir(os.path.join(folder_path)):
            if file.endswith(".pb"):
                print("File: {}".format(file))
                instance, profile = parse_pabulib(os.path.join(folder_path, file))

                sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Sat)
                sat_multiprofile = SatisfactionMultiProfile(profile=profile, sat_class=Cost_Sat)

                for index, rule in enumerate(rules):
                    profile_time = time.time()
                    rule(instance, profile, sat_profile=sat_profile, resoluteness=True, **rule_params[index])
                    profile_time = time.time() - profile_time
                    multiprofile_time = time.time()
                    rule(instance, profile, sat_profile=sat_multiprofile, resoluteness=True, **rule_params[index])
                    multiprofile_time = time.time() - multiprofile_time

                    data["file"].append(file)
                    data["rule"].append(rule.__name__)
                    data["runtime_profile"].append(profile_time)
                    data["runtime_multiprofile"].append(multiprofile_time)
                    data["time_gains"].append(profile_time - multiprofile_time)
                    data["time_gains_percent"].append(1 - multiprofile_time/profile_time)
                    data["length_gains"].append(len(profile) - len(sat_multiprofile))
                    data["length_gains_percent"].append(1 - len(sat_multiprofile) / len(profile))
                    data["num_voters"].append(len(profile))
                    data["num_sat"].append(len(sat_multiprofile))
                    data["avg_vote_length"].append(sum(len(b) for b in profile) / len(profile))
                    data["avg_vote_length_cat"].append(round(sum(len(b) for b in profile) / len(profile)))
        data = pd.DataFrame(data)
        data.to_csv(os.path.join("csv", csv_file), sep=";", encoding='utf-8')

    plt.close('all')

    sns.set_theme()

    for rule in rules:

        g = sns.boxplot(
            data=data[data["rule"] == rule.__name__],
            x="avg_vote_length_cat",
            y="time_gains_percent",
        )
        g.set_yticks(np.linspace(-1, 1, 21))
        g.set_title(rule.__name__)

        plt.show()

        g = sns.boxplot(
            data=data[data["rule"] == rule.__name__],
            x="avg_vote_length_cat",
            y="time_gains",
        )
        g.set_title(rule.__name__)

        plt.show()


if __name__ == "__main__":
    recompute = False
    # recompute = True

    multiproifle_gain("all_app_pabulib", recompute=recompute)

    multiprofile_runtime("all_app_pabulib",
                         [greedy_welfare, max_welfare],
                         [{"is_sat_additive": True}, {}],
                         recompute=recompute)

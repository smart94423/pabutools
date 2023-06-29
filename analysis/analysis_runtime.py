import os
import time

from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from pbvoting.election import parse_pabulib, Cost_Sat, Cardinality_Sat
from pbvoting.rules import greedy_welfare, sequential_phragmen, method_of_equal_shares
from pbvoting.rules.maxwelfare import max_welfare


def runtime_analysis_pool(file_rule_set):
    file, rule = file_rule_set
    print("File {} for rule {}".format(file, rule.__name__))
    instance, prof = parse_pabulib(file)

    res = []
    for profile in [prof, prof.as_multiprofile()]:
        data = {}
        init_time = time.time()
        rule(instance, profile)
        total_time = time.time() - init_time
        data["file"] = instance.file_name
        data["rule"] = rule.__name__
        data["profile_type"] = profile.__class__.__name__
        data["runtime"] = total_time
        data["num_projects"] = len(instance)
        data["num_projects_cat"] = round(len(instance) / 10) * 10
        data["num_voters"] = len(profile)
        data["num_voters_cat"] = round(len(profile) / 1000) * 1000
        data["avg_vote_length"] = sum(len(b) for b in profile) / len(profile)
        data["avg_vote_length_cat"] = round(sum(len(b) for b in profile) / len(profile))
        res.append(data)
    return res


def runtime_analysis_write_data(folder_path, rules, csv_file="runtime.csv"):
    file_rule_set = []
    for file in os.listdir(os.path.join(folder_path)):
        if file.endswith(".pb"):
            for rule in rules:
                file_rule_set.append((os.path.join(folder_path, file), rule))

    print("A total of {} element will be computed".format(len(file_rule_set)))

    with open(os.path.join("csv", csv_file), "w"):
        pass

    pool = Pool()
    csv_keys = None
    for res in pool.imap_unordered(runtime_analysis_pool, file_rule_set):
    # for instance_profile_rule in file_rule_set:
    #     res = runtime_analysis_pool(instance_profile_rule)

        for line in res:
            with open(os.path.join("csv", csv_file), "a") as f:
                if csv_keys is None:
                    csv_keys = tuple(line.keys())
                    f.write(";".join((str(key) for key in csv_keys)) + "\n")
                f.write(";".join((str(line[key]) for key in csv_keys)) + "\n")


def runtime_analysis_plot(csv_file="runtime.csv"):
    print("============== Rule Runtime Analysis ==============")
    plt.close('all')

    data = pd.read_csv(os.path.join("csv", csv_file), sep=";", encoding='utf-8')

    sns.set_theme()

    for rule in data["rule"].unique():
        plt.close('all')
        g = sns.pointplot(
            data=data[data["rule"] == rule],
            x="num_projects_cat",
            y="runtime",
            hue="profile_type"
        )
        g.set_title(rule)

        plt.show()

    for profile_type in data["profile_type"].unique():
        plt.close('all')

        g = sns.pointplot(
            data=data[data["profile_type"] == profile_type],
            x="num_projects_cat",
            y="runtime",
            hue="rule"
        )
        g.set_title(profile_type)

        plt.show()


def greed_cost_res(instance, profile):
    return greedy_welfare(instance, profile, sat_class=Cost_Sat, resoluteness=True)


def maxwelfare_cost_res(instance, profile):
    return max_welfare(instance, profile, sat_class=Cost_Sat, resoluteness=True)


def greed_card_res(instance, profile):
    return greedy_welfare(instance, profile, sat_class=Cardinality_Sat, resoluteness=True)


def seqphragmen_res(instance, profile):
    return sequential_phragmen(instance, profile, resoluteness=True)


def mes_cost_res(instance, profile):
    return method_of_equal_shares(instance, profile, sat_class=Cost_Sat, resoluteness=True)


if __name__ == "__main__":

    runtime_analysis_write_data(os.path.join("Pabulib", "all_app_75"),
                                [greed_cost_res, maxwelfare_cost_res, seqphragmen_res, mes_cost_res])

    runtime_analysis_plot()

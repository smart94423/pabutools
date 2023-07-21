import os
import time
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

from pabutools.election import (
    parse_pabulib,
    SatisfactionMultiProfile,
    Cost_Sat,
    SatisfactionProfile,
)
from pabutools.rules import greedy_utilitarian_welfare
from pabutools.rules.maxwelfare import max_additive_utilitarian_welfare


def multiprofile_analysis_pool(file):
    print("File {}".format(file))
    instance, profile = parse_pabulib(file)
    multiprofile = profile.as_multiprofile()
    data = {}
    data["file"] = instance.file_name
    data["gains"] = len(profile) - len(multiprofile)
    data["gains_percent"] = 1 - len(multiprofile) / len(profile)
    data["num_projects"] = len(instance)
    data["num_projects_cat"] = round(len(instance) / 10) * 10
    data["num_voters"] = len(profile)
    data["num_voters_cat"] = round(len(profile) / 1000) * 1000
    data["avg_vote_length"] = sum(len(b) for b in profile) / len(profile)
    data["avg_vote_length_cat"] = round(sum(len(b) for b in profile) / len(profile))
    return data


def multiprofile_analysis_write_data(folder_path, csv_file="multiprofile_gain.csv"):
    print("============== Multiprofile Gain Analysis ==============")

    files = []
    for file in os.listdir(os.path.join(folder_path)):
        if file.endswith(".pb"):
            files.append(os.path.join("Pabulib", "all_app", file))

    print("A total of {} element will be computed".format(len(files)))

    with open(os.path.join("csv", csv_file), "w"):
        pass

    pool = Pool()
    csv_keys = None
    for line in pool.imap_unordered(multiprofile_analysis_pool, files):
        with open(os.path.join("csv", csv_file), "a") as f:
            if csv_keys is None:
                csv_keys = tuple(line.keys())
                f.write(";".join((str(key) for key in csv_keys)) + "\n")
            f.write(";".join((str(line[key]) for key in csv_keys)) + "\n")


def multiprofile_analysis_write_plot(csv_file="multiprofile_gain.csv"):
    plt.close("all")

    data = pd.read_csv(os.path.join("csv", csv_file), sep=";", encoding="utf-8")

    sns.set_theme()

    g = sns.histplot(data=data, x="gains_percent", multiple="stack", binwidth=None)

    plt.show()

    plt.close("all")

    g = sns.boxplot(
        data=data,
        x="avg_vote_length_cat",
        y="gains_percent",
    )
    g.set_yticks(np.linspace(0, 1, 11))

    plt.show()


if __name__ == "__main__":
    # multiprofile_analysis_write_data(os.path.join("Pabulib", "all_app"))
    multiprofile_analysis_write_plot()

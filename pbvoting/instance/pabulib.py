"""
Tools to work with PaBuLib instances.
"""
from copy import deepcopy
from fractions import Fraction

from pbvoting.fractions import as_frac
from pbvoting.instance.pbinstance import PBInstance, Project
from pbvoting.instance.profile import Profile, ApprovalProfile, ApprovalBallot, CardinalProfile, CumulativeProfile, \
    OrdinalProfile, CardinalBallot, OrdinalBallot

import csv
import os


def parse_pabulib(file_path):
    """
        Parses a PaBuLib files and returns the corresponding instance and profile.
        Parameters
        ----------
            file_path : str
                Path to the PaBuLib file to be parsed.
        Returns
        -------
            Tuple of pbvoting.instances.instance.PBInstance and pbvoting.instances.profile.Profile
    """
    instance = PBInstance()
    ballots = []
    instance.file_path = file_path
    instance.file_name = os.path.basename(file_path)

    with open(file_path, 'r', newline='', encoding="utf-8-sig") as csvfile:
        section = ""
        header = []
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                section = str(row[0]).strip().lower()
                header = next(reader)
            elif section == "meta":
                instance.meta[row[0]] = row[1].strip()
            elif section == "projects":
                p = Project(project_name=row[0])
                instance.project_meta[p] = dict()
                for i in range(len(row)):
                    instance.project_meta[p][header[i].strip()] = row[i].strip()
                p.cost = Fraction(instance.project_meta[p]["cost"].replace(",", "."))
                instance.add(p)
            elif section == "votes":
                ballot_meta = {}
                for i in range(len(row)):
                    ballot_meta[header[i].strip()] = row[i].strip()
                if instance.meta["vote_type"] == "approval":
                    ballot = ApprovalBallot()
                    for project_name in ballot_meta["vote"].split(","):
                        ballot.add(instance.get_project(project_name))
                elif instance.meta["vote_type"] in ("scoring", "cumulative"):
                    ballot = CardinalBallot()
                    points = ballot_meta["points"].split(',')
                    for index, project_name in enumerate(ballot_meta["vote"].split(",")):
                        ballot[instance.get_project(project_name)] = Fraction(points[index].strip())
                elif instance.meta["vote_type"] == "ordinal":
                    ballot = OrdinalBallot()
                    for project_name in ballot_meta["vote"].split(","):
                        ballot.append(instance.get_project(project_name))
                else:
                    raise NotImplementedError("The PaBuLib parser cannot parse {} profiles for now.".format(
                        instance.meta["vote_type"]))
                ballot.meta = ballot_meta
                ballots.append(ballot)

    profile = None
    if instance.meta["vote_type"] == "approval":
        profile = ApprovalProfile(deepcopy(ballots))
    elif instance.meta["vote_type"] == "scoring":
        profile = CardinalProfile(deepcopy(ballots))
    elif instance.meta["vote_type"] == "cumulative":
        profile = CumulativeProfile(deepcopy(ballots))
    elif instance.meta["vote_type"] == "ordinal":
        profile = OrdinalProfile(deepcopy(ballots))

    # We retrieve the budget limit from the meta information
    instance.budget_limit = Fraction(instance.meta["budget"].replace(",", "."))

    return instance, profile

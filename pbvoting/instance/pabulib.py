"""
Tools to work with PaBuLib instances.
"""

from pbvoting.instance.pbinstance import PBInstance, Project
from pbvoting.instance.profile import ApprovalProfile, ApprovalBallot

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
    profile = ApprovalProfile()
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
                for it, key in enumerate(header[1:]):
                    instance.project_meta[p][key.strip()] = row[it + 1].strip()
                p.cost = float(instance.project_meta[p]["cost"].replace(",", "."))
                instance.add(p)
            elif section == "votes":
                if instance.meta["vote_type"] != "approval":
                    raise NotImplementedError("The PaBuLib parser cannot parse non-approval profiles for now.")
                ballot = ApprovalBallot()
                for it, key in enumerate(header[1:]):
                    ballot.meta[key.strip()] = row[it + 1].strip()
                for project_name in row[it + 1].split(","):
                    ballot.add(instance.get_project(project_name))
                profile.append(ballot)

    # We retrieve the budget limit from the meta information
    instance.budget_limit = float(instance.meta["budget"].replace(",", "."))

    return instance, profile

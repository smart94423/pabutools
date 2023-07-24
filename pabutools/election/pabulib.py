"""
Tools to work with PaBuLib.
"""
from copy import deepcopy

from pabutools.fractions import str_as_frac
from pabutools.election.instance import Instance, Project
from pabutools.election.ballot import (
    ApprovalBallot,
    CardinalBallot,
    OrdinalBallot,
    CumulativeBallot,
)
from pabutools.election.profile import (
    AbstractProfile,
    ApprovalProfile,
    CardinalProfile,
    CumulativeProfile,
    OrdinalProfile,
)

import csv
import os


def parse_pabulib_from_string(file_content: str) -> tuple[Instance, AbstractProfile]:
    """
    Parses a PaBuLib file given as a string and returns the corresponding instance and profile. The returned profile will be of the
    correct type depending on the metadata in the file.

    Parameters
    ----------
        file_content : str
            String containing the contents of the PaBuLib file to be parsed.

    Returns
    -------
        tuple[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.Profile`]
            The instance and the profile corresponding to the file.
    """
    instance = Instance()
    ballots = []
    optional_sets = {"categories": set(), "targets": set()}

    lines = file_content.splitlines()
    section = ""
    header = []
    reader = csv.reader(lines, delimiter=";")
    for row in reader:
        if len(row) == 1 and len(row[0].strip()) == 0:
            continue
        if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
            section = str(row[0]).strip().lower()
            header = next(reader)
        elif section == "meta":
            instance.meta[row[0].strip()] = row[1].strip()
        elif section == "projects":
            p = Project()
            project_meta = dict()
            for i in range(len(row)):
                key = header[i].strip()
                p.name = row[0].strip()
                if row[i].strip().lower() != "none":
                    if key in ["category", "categories"]:
                        project_meta["categories"] = [
                            entry.strip() for entry in row[i].split(",")
                        ]
                        p.categories = set(project_meta["categories"])
                        optional_sets["categories"].update(project_meta["categories"])
                    elif key in ["target", "targets"]:
                        project_meta["targets"] = [
                            entry.strip() for entry in row[i].split(",")
                        ]
                        p.targets = set(project_meta["targets"])
                        optional_sets["targets"].update(project_meta["targets"])
                    else:
                        project_meta[key] = row[i].strip()
            p.cost = str_as_frac(project_meta["cost"].replace(",", "."))
            instance.add(p)
            instance.project_meta[p] = project_meta
        elif section == "votes":
            ballot_meta = dict()
            for i in range(len(row)):
                if row[i].strip().lower() != "none":
                    ballot_meta[header[i].strip()] = row[i].strip()
            if instance.meta["vote_type"] == "approval":
                ballot = ApprovalBallot()
                for project_name in ballot_meta["vote"].split(","):
                    ballot.add(instance.get_project(project_name))
                ballot_meta.pop("vote")
            elif instance.meta["vote_type"] == "scoring":
                ballot = CardinalBallot()
                points = ballot_meta["points"].split(",")
                for index, project_name in enumerate(ballot_meta["vote"].split(",")):
                    ballot[instance.get_project(project_name)] = str_as_frac(
                        points[index].strip()
                    )
                ballot_meta.pop("vote")
                ballot_meta.pop("points")
            elif instance.meta["vote_type"] == "cumulative":
                ballot = CumulativeBallot()
                points = ballot_meta["points"].split(",")
                for index, project_name in enumerate(ballot_meta["vote"].split(",")):
                    ballot[instance.get_project(project_name)] = str_as_frac(
                        points[index].strip()
                    )
                ballot_meta.pop("vote")
                ballot_meta.pop("points")
            elif instance.meta["vote_type"] == "ordinal":
                ballot = OrdinalBallot()
                for project_name in ballot_meta["vote"].split(","):
                    ballot.append(instance.get_project(project_name))
                ballot_meta.pop("vote")
            else:
                raise NotImplementedError(
                    "The PaBuLib parser cannot parse {} profiles for now.".format(
                        instance.meta["vote_type"]
                    )
                )
            ballot.meta = ballot_meta
            ballots.append(ballot)

    legal_min_length = instance.meta.get("min_length", None)
    if legal_min_length is not None:
        legal_min_length = int(legal_min_length)
        if legal_min_length == 1:
            legal_min_length = None
    legal_max_length = instance.meta.get("max_length", None)
    if legal_max_length is not None:
        legal_max_length = int(legal_max_length)
        if legal_max_length >= len(instance):
            legal_max_length = None
    legal_min_cost = instance.meta.get("min_sum_cost", None)
    if legal_min_cost is not None:
        legal_min_cost = str_as_frac(legal_min_cost)
        if legal_min_cost == 0:
            legal_min_cost = None
    legal_max_cost = instance.meta.get("max_sum_cost", None)
    if legal_max_cost is not None:
        legal_max_cost = str_as_frac(legal_max_cost)
        if legal_max_cost >= instance.budget_limit:
            legal_max_cost = None
    legal_min_total_score = instance.meta.get("min_sum_points", None)
    if legal_min_total_score is not None:
        legal_min_total_score = str_as_frac(legal_min_total_score)
        if legal_min_total_score == 0:
            legal_min_total_score = None
    legal_max_total_score = instance.meta.get("max_sum_points", None)
    if legal_max_total_score is not None:
        legal_max_total_score = str_as_frac(legal_max_total_score)
    legal_min_score = instance.meta.get("min_points", None)
    if legal_min_score is not None:
        legal_min_score = str_as_frac(legal_min_score)
        if legal_min_score == 0:
            legal_min_score = None
    legal_max_score = instance.meta.get("max_points", None)
    if legal_max_score is not None:
        legal_max_score = str_as_frac(legal_max_score)
        if legal_max_score == legal_max_total_score:
            legal_max_score = None

    profile = None
    if instance.meta["vote_type"] == "approval":
        profile = ApprovalProfile(
            deepcopy(ballots),
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_cost=legal_min_cost,
            legal_max_cost=legal_max_cost,
        )
    elif instance.meta["vote_type"] == "scoring":
        profile = CardinalProfile(
            deepcopy(ballots),
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_score=legal_min_score,
            legal_max_score=legal_max_score,
        )
    elif instance.meta["vote_type"] == "cumulative":
        profile = CumulativeProfile(
            deepcopy(ballots),
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_score=legal_min_score,
            legal_max_score=legal_max_score,
            legal_min_total_score=legal_min_total_score,
            legal_max_total_score=legal_max_total_score,
        )
    elif instance.meta["vote_type"] == "ordinal":
        profile = OrdinalProfile(
            deepcopy(ballots),
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
        )

    # We retrieve the budget limit from the meta information
    instance.budget_limit = str_as_frac(instance.meta["budget"].replace(",", "."))

    # We add the category and target information that we collected from the projects
    instance.categories = optional_sets["categories"]
    instance.targets = optional_sets["targets"]

    return instance, profile


def parse_pabulib(file_path: str) -> tuple[Instance, AbstractProfile]:
    """
    Parses a PaBuLib files and returns the corresponding instance and profile. The returned profile will be of the
    correct type depending on the metadata in the file.

    Parameters
    ----------
        file_path : str
            Path to the PaBuLib file to be parsed.

    Returns
    -------
        tuple[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.Profile`]
            The instance and the profile corresponding to the file.
    """

    with open(file_path, "r", newline="", encoding="utf-8-sig") as csvfile:
        instance, profile = parse_pabulib_from_string(csvfile.read())

    instance.file_path = file_path
    instance.file_name = os.path.basename(file_path)

    return instance, profile

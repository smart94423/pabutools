from unittest import TestCase

from pabutools.election import (
    Project,
    Instance,
    ApprovalBallot,
    ApprovalProfile,
    CardinalProfile,
    CardinalBallot,
    CumulativeBallot,
    CumulativeProfile,
    OrdinalProfile,
    OrdinalBallot,
)
from pabutools.election.preflib import (
    approval_to_preflib,
    cardinal_to_preflib,
    ordinal_to_preflib,
)

import os


def check_preflib_instance(projects, profile, preflib_instance, project_name_prefix):
    assert sum(preflib_instance.multiplicity.values()) == profile.num_ballots()
    assert preflib_instance.num_alternatives == len(projects)
    assert preflib_instance.file_path == "file_path"
    assert preflib_instance.file_name == "file_name"
    assert preflib_instance.modification_type == "modification_type"
    assert preflib_instance.relates_to == "relates_to"
    assert preflib_instance.related_files == "related_files"
    assert preflib_instance.title == "title"
    assert preflib_instance.description == "description"
    assert preflib_instance.publication_date == "publication_date"
    assert preflib_instance.modification_date == "modification_date"
    for p in projects:
        assert (
            preflib_instance.alternatives_name[p.name] == project_name_prefix + p.name
        )


class TestPreflib(TestCase):
    def test_approval(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects)
        app_prof = ApprovalProfile([ApprovalBallot(projects) for _ in range(100)])
        for profile in [app_prof, app_prof.as_multiprofile()]:
            preflib_instance = approval_to_preflib(
                instance,
                profile,
                file_path="file_path",
                file_name="file_name",
                modification_type="modification_type",
                relates_to="relates_to",
                related_files="related_files",
                title="title",
                description="description",
                publication_date="publication_date",
                modification_date="modification_date",
                alternative_names={p: "Project " + p.name for p in projects},
            )
            check_preflib_instance(projects, profile, preflib_instance, "Project ")
            assert len(preflib_instance.preferences) == 1

    def test_cardinal(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects)
        card_prof = CardinalProfile(
            [CardinalBallot({p: i for i, p in enumerate(projects)}) for _ in range(100)]
        )
        cum_prof = CumulativeProfile(
            [
                CumulativeBallot({p: i for i, p in enumerate(projects)})
                for _ in range(100)
            ]
        )
        for profile in [
            card_prof,
            card_prof.as_multiprofile(),
            cum_prof,
            cum_prof.as_multiprofile(),
        ]:
            preflib_instance = cardinal_to_preflib(
                instance,
                profile,
                file_path="file_path",
                file_name="file_name",
                modification_type="modification_type",
                relates_to="relates_to",
                related_files="related_files",
                title="title",
                description="description",
                publication_date="publication_date",
                modification_date="modification_date",
            )
            check_preflib_instance(projects, profile, preflib_instance, "")
            assert len(preflib_instance.orders) == 1
            assert preflib_instance.orders[0] == tuple(projects)

    def test_ordinal(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects)
        ord_prof = OrdinalProfile([OrdinalBallot(projects) for _ in range(100)])
        for profile in [ord_prof, ord_prof.as_multiprofile()]:
            preflib_instance = ordinal_to_preflib(
                instance,
                profile,
                file_path="file_path",
                file_name="file_name",
                modification_type="modification_type",
                relates_to="relates_to",
                related_files="related_files",
                title="title",
                description="description",
                publication_date="publication_date",
                modification_date="modification_date",
                alternative_names={p: "Project " + p.name for p in projects},
            )
            check_preflib_instance(projects, profile, preflib_instance, "Project ")
            assert len(preflib_instance.orders) == 1
            assert preflib_instance.orders[0] == tuple(projects)

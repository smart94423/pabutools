"""
Tools to work with PrefLib.
"""
import preflibtools.instances as preflib
from preflibtools.instances import PrefLibInstance

from pabutools.election import (
    Instance,
    Project,
    AbstractApprovalProfile,
    AbstractCardinalProfile,
    AbstractOrdinalProfile,
)


def init_preflib_instance(
    preflib_inst: PrefLibInstance,
    instance: Instance,
    file_path: str,
    file_name: str,
    modification_type: str,
    relates_to: str,
    related_files: str,
    title: str,
    description: str,
    publication_date: str,
    modification_date: str,
    alternative_names: dict[Project, str],
) -> None:
    """
    Initialises a PrefLib instance with all the necessary parameters.

    Parameters
    ----------
        preflib_inst : preflibtools.instances.PrefLibInstance
            The PrefLib instance to initialise.
        instance: :py:class:`~pabutools.election.instance.Instance`
            The Pabutools instance used to define the PrefLib one.
        file_path: str
            The path to the file containing the details of the instance.
        file_name: str
            The name to the file containing the details of the instance.
        modification_type: str
            The modification type as described by the PrefLib documentation.
        relates_to: str
            The files that the PrefLib instance relates to.
        related_files: str
            The related files to the PrefLib instance.
        title: str
            The title of the PrefLib instance.
        description: str
            The description of the PrefLib instance.
        publication_date: str
            The publication date of the PrefLib instance.
        modification_date: str
            The last modification date of the PrefLib instance.
        alternative_names: dict[:py:class:`~pabutools.election.instance.Project`, str]
            A mapping of projects to names of the corresponding alternatives.
    """
    preflib_inst.file_path = file_path
    preflib_inst.file_name = file_name
    preflib_inst.modification_type = modification_type
    preflib_inst.relates_to = relates_to
    preflib_inst.related_files = related_files
    preflib_inst.title = title
    preflib_inst.description = description
    preflib_inst.publication_date = publication_date
    preflib_inst.modification_date = modification_date

    preflib_inst.num_alternatives = len(instance)
    if alternative_names:
        for project in instance:
            preflib_inst.alternatives_name[project.name] = alternative_names[project]
    else:
        for project in instance:
            preflib_inst.alternatives_name[project.name] = project.name


def approval_to_preflib(
    instance: Instance,
    profile: AbstractApprovalProfile,
    file_path: str = "",
    file_name: str = "",
    modification_type: str = "original",
    relates_to: str = "",
    related_files: str = "",
    title: str = "",
    description: str = "",
    publication_date: str = "",
    modification_date: str = "",
    alternative_names: dict[Project, str] = None,
) -> preflib.CategoricalInstance:
    """
    Converts a participatory budgeting instance and profile of approval ballots into a PrefLib instance.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The Pabutools instance used to define the PrefLib one.
        profile: py:class:`~pabutools.election.profile.approvalprofile.AbstractApprovalProfile`
            The Pabutools profile of approval ballots.
        file_path: str
            The path to the file containing the details of the instance.
        file_name: str
            The name to the file containing the details of the instance.
        modification_type: str
            The modification type as described by the PrefLib documentation.
        relates_to: str
            The files that the PrefLib instance relates to.
        related_files: str
            The related files to the PrefLib instance.
        title: str
            The title of the PrefLib instance.
        description: str
            The description of the PrefLib instance.
        publication_date: str
            The publication date of the PrefLib instance.
        modification_date: str
            The last modification date of the PrefLib instance.
        alternative_names: dict[:py:class:`~pabutools.election.instance.Project`, str]
            A mapping of projects to names of the corresponding alternatives.
    """
    preflib_inst = preflib.CategoricalInstance()
    init_preflib_instance(
        preflib_inst,
        instance,
        file_path,
        file_name,
        modification_type,
        relates_to,
        related_files,
        title,
        description,
        publication_date,
        modification_date,
        alternative_names,
    )

    preflib_inst.data_type = "cat"
    preflib_inst.num_categories = 2
    preflib_inst.categories_name = {1: "Approved", 2: "Not approved"}
    for ballot in profile:
        approved = tuple(ballot)
        not_approved = tuple(p for p in instance if p not in ballot)
        pref = (approved, not_approved)
        if pref in preflib_inst.preferences:
            preflib_inst.multiplicity[pref] += profile.multiplicity(ballot)
        else:
            preflib_inst.preferences.append(pref)
            preflib_inst.multiplicity[pref] = profile.multiplicity(ballot)

    preflib_inst.recompute_cardinality_param()

    return preflib_inst


def cardinal_to_preflib(
    instance: Instance,
    profile: AbstractCardinalProfile,
    file_path: str = "",
    file_name: str = "",
    modification_type: str = "original",
    relates_to: str = None,
    related_files: str = None,
    title: str = "",
    description: str = "",
    publication_date: str = "",
    modification_date: str = "",
    alternative_names: dict[Project, str] = None,
) -> preflib.OrdinalInstance:
    """
    Converts a participatory budgeting instance and profile of cardinal ballots into a PrefLib instance.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The Pabutools instance used to define the PrefLib one.
        profile: py:class:`~pabutools.election.profile.cardinalprofile.AbstractCardinalProfile`
            The Pabutools profile of approval ballots.
        file_path: str
            The path to the file containing the details of the instance.
        file_name: str
            The name to the file containing the details of the instance.
        modification_type: str
            The modification type as described by the PrefLib documentation.
        relates_to: str
            The files that the PrefLib instance relates to.
        related_files: str
            The related files to the PrefLib instance.
        title: str
            The title of the PrefLib instance.
        description: str
            The description of the PrefLib instance.
        publication_date: str
            The publication date of the PrefLib instance.
        modification_date: str
            The last modification date of the PrefLib instance.
        alternative_names: dict[:py:class:`~pabutools.election.instance.Project`, str]
            A mapping of projects to names of the corresponding alternatives.
    """
    preflib_inst = preflib.OrdinalInstance()
    init_preflib_instance(
        preflib_inst,
        instance,
        file_path,
        file_name,
        modification_type,
        relates_to,
        related_files,
        title,
        description,
        publication_date,
        modification_date,
        alternative_names,
    )
    preflib_inst.data_type = "toi"
    for ballot in profile:
        order = tuple(sorted(ballot, key=lambda p: ballot[p]))
        if order in preflib_inst.orders:
            preflib_inst.multiplicity[order] += profile.multiplicity(ballot)
        else:
            preflib_inst.orders.append(order)
            preflib_inst.multiplicity[order] = profile.multiplicity(ballot)

    preflib_inst.recompute_cardinality_param()

    return preflib_inst


def ordinal_to_preflib(
    instance: Instance,
    profile: AbstractOrdinalProfile,
    file_path: str = "",
    file_name: str = "",
    modification_type: str = "original",
    relates_to: str = None,
    related_files: str = None,
    title: str = "",
    description: str = "",
    publication_date: str = "",
    modification_date: str = "",
    alternative_names: dict[Project, str] = None,
) -> preflib.OrdinalInstance:
    """
    Converts a participatory budgeting instance and profile of ordinal ballots into a PrefLib instance.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The Pabutools instance used to define the PrefLib one.
        profile: py:class:`~pabutools.election.profile.ordinalprofile.AbstractOrdinalProfile`
            The Pabutools profile of approval ballots.
        file_path: str
            The path to the file containing the details of the instance.
        file_name: str
            The name to the file containing the details of the instance.
        modification_type: str
            The modification type as described by the PrefLib documentation.
        relates_to: str
            The files that the PrefLib instance relates to.
        related_files: str
            The related files to the PrefLib instance.
        title: str
            The title of the PrefLib instance.
        description: str
            The description of the PrefLib instance.
        publication_date: str
            The publication date of the PrefLib instance.
        modification_date: str
            The last modification date of the PrefLib instance.
        alternative_names: dict[:py:class:`~pabutools.election.instance.Project`, str]
            A mapping of projects to names of the corresponding alternatives.
    """
    preflib_inst = preflib.OrdinalInstance()
    init_preflib_instance(
        preflib_inst,
        instance,
        file_path,
        file_name,
        modification_type,
        relates_to,
        related_files,
        title,
        description,
        publication_date,
        modification_date,
        alternative_names,
    )
    preflib_inst.data_type = "toi"
    for ballot in profile:
        order = tuple(ballot)
        if order in preflib_inst.orders:
            preflib_inst.multiplicity[order] += profile.multiplicity(ballot)
        else:
            preflib_inst.orders.append(order)
            preflib_inst.multiplicity[order] = profile.multiplicity(ballot)

    preflib_inst.recompute_cardinality_param()

    return preflib_inst

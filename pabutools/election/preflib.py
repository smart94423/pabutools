import preflibtools.instances as preflib


def init_preflib_instance(
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
):
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
    instance,
    profile,
    file_path="",
    file_name="",
    modification_type="original",
    relates_to=None,
    related_files=None,
    title="",
    description="",
    publication_date="",
    modification_date="",
    alternative_names=None,
):
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
            preflib_inst.multiplicity[pref] += 1
        else:
            preflib_inst.preferences.append(pref)
            preflib_inst.multiplicity[pref] = 1

    preflib_inst.recompute_cardinality_param()

    return preflib_inst


def cardinal_to_preflib(
    instance,
    profile,
    file_path="",
    file_name="",
    modification_type="original",
    relates_to=None,
    related_files=None,
    title="",
    description="",
    publication_date="",
    modification_date="",
    alternative_names=None,
):
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
        order = list(ballot)
        order.sort(key=lambda p: ballot[p])
        if order in preflib_inst.orders:
            preflib_inst.multiplicity[order] += 1
        else:
            preflib_inst.orders.append(order)
            preflib_inst.multiplicity[order] = 1

    preflib_inst.recompute_cardinality_param()

    return preflib_inst


def ordinal_to_preflib(
    instance,
    profile,
    file_path="",
    file_name="",
    modification_type="original",
    relates_to=None,
    related_files=None,
    title="",
    description="",
    publication_date="",
    modification_date="",
    alternative_names=None,
):
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
        order = list(ballot)
        if order in preflib_inst.orders:
            preflib_inst.multiplicity[order] += 1
        else:
            preflib_inst.orders.append(order)
            preflib_inst.multiplicity[order] = 1

    preflib_inst.recompute_cardinality_param()

    return preflib_inst

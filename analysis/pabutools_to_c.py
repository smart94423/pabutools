from pabutools.election import (
    parse_pabulib,
    Cost_Sat,
    Project,
    Instance,
    ApprovalProfile,
    ApprovalBallot,
    Cardinality_Sat,
)
from pabutools.rules import method_of_equal_shares

p = [
    Project("a", 1),
    Project("b", 1),
    Project("c", 1),
    Project("d", 1),
    Project("e", 1),
    Project("f", 1),
    Project("g", 1),
]
instance = Instance(p, budget_limit=4)
profile = ApprovalProfile(
    [
        ApprovalBallot({p[0], p[1]}),
        ApprovalBallot({p[0], p[1]}),
        ApprovalBallot({p[0], p[1]}),
        ApprovalBallot({p[0], p[2]}),
        ApprovalBallot({p[0], p[2]}),
        ApprovalBallot({p[0], p[2]}),
        ApprovalBallot({p[0], p[3]}),
        ApprovalBallot({p[0], p[3]}),
        ApprovalBallot({p[1], p[2], p[5]}),
        ApprovalBallot({p[4]}),
        ApprovalBallot({p[5]}),
        ApprovalBallot({p[6]}),
    ],
    instance=instance,
)
instance, profile = parse_pabulib("poland_wieliczka_2023.pb")
projects = sorted(instance, key=lambda p: p.name)
SAT_CLASS = Cost_Sat

file_root = "lask"
file_name = file_root + ".c"
with open(file_name, "w") as f:
    f.write(
        "int "
        + file_root
        + "NumVoters() {\n\t return "
        + f"{profile.num_ballots()};\n"
        + "}\n"
    )

    f.write(
        "int "
        + file_root
        + "NumProjects () {\n\treturn "
        + f"{len(instance)};\n"
        + "}\n"
    )

    f.write("void " + file_root + "Utilities(double* utilities) {\n")
    index = 0
    for sat in profile.as_sat_profile(SAT_CLASS):
        for proj in projects:
            f.write(f"\tutilities[{index}] = {float(sat.sat_project(proj))};\n")
            index += 1
    f.write("}\n")

    f.write("void " + file_root + "Costs(double* costs) {\n")
    for j, proj in enumerate(projects):
        f.write(f"\tcosts[{j}] = {float(proj.cost)};\n")
    f.write("}\n")

    f.write("void " + file_root + "PabulibIDs(int* pabulibIDs) {\n")
    for j, proj in enumerate(projects):
        try:
            name = int(proj.name)
        except Exception as e:
            if isinstance(proj.name, str) and len(proj.name) == 1:
                name = ord(proj.name) - 97
            else:
                name = proj.name
        f.write(f"\tpabulibIDs[{j}] = {name};\n")
    f.write("}\n")

    f.write(
        "double "
        + file_root
        + "BudgetLimit () {\n\treturn "
        + f"{float(instance.budget_limit)};\n"
        + "}\n"
    )

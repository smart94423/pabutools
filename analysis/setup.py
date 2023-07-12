import os
import shutil

from pabutools.election import parse_pabulib


if __name__ == "__main__":
    for file in os.listdir(os.path.join("Pabulib", "all_app")):
        if file.endswith(".pb"):
            instance, prof = parse_pabulib(os.path.join("Pabulib", "all_app", file))

            for num_proj_bound in [10, 20, 30, 50, 75, 100, 150, 200, 500]:
                os.makedirs(
                    os.path.join("Pabulib", "all_app_{}".format(num_proj_bound)),
                    exist_ok=True,
                )
                if len(instance) <= num_proj_bound:
                    shutil.copy(
                        os.path.join("Pabulib", "all_app", file),
                        os.path.join(
                            "Pabulib", "all_app_{}".format(num_proj_bound), file
                        ),
                    )

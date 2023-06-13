from pbvoting.instance import Project, Profile, PBInstance
from pbvoting.tiebreaking.rule import TieBreakingRule


def lexicographic_untie(instance: PBInstance, profile: Profile, project: Project):
    """
        Unties projects based on their name.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.profile.Profile
                The profile.
            project : pbvoting.instance.pbinstance.Project
                The project.

        Returns
        -------
            str
    """
    return project.name


lexico_tie_breaking = TieBreakingRule(lexicographic_untie)

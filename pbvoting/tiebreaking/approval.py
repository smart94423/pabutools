from pbvoting.tiebreaking.rule import TieBreakingRule


def approval_score_untie(instance, profile, project):
    """
        Unties projects based on their approval scores, higher approval score being better.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.profile.ApprovalProfile
                The approval profile.
            project : pbvoting.instance.pbinstance.Project
                The project.

        Returns
        -------
            int
    """
    return -profile.approval_score(project)


app_score_tie_breaking = TieBreakingRule(approval_score_untie)

"""
Module describing different profile formats. A profile simply correspond to a list of ballots
(see the :py:mod:`~pabutools.election.ballot` module), one for each voter of the election. The structure of this module
is very similar to that of the :py:mod:`~pabutools.election.ballot` module.

All profiles are derived from the :py:class:`~pabutools.election.profile.profile.AbstractProfile` class. Then, two
general categories of profiles are introduced. First, the usual profiles that contain one ballot per voter. These are
implemented by the following classes, all inheriting from the class
:py:class:`~pabutools.election.profile.profile.Profile`:

* :py:class:`~pabutools.election.profile.approvalprofile.ApprovalProfile`
* :py:class:`~pabutools.election.profile.cardinalprofile.CardinalProfile`
* :py:class:`~pabutools.election.profile.cumulativeprofile.CumulativeProfile`
* :py:class:`~pabutools.election.profile.ordinalprofile.OrdinalProfile`

The second category of profiles this module introduce are the so-called multiprofile. In those profiles, only unique
ballots are stored, together with their multiplicity. Frozen ballots are used here as the ballots need to be
non-mutable. The corresponding classes all inherit from
:py:class:`~pabutools.election.profile.profile.MultiProfile`, and are:

* :py:class:`~pabutools.election.profile.approvalprofile.ApprovalMultiProfile`
* :py:class:`~pabutools.election.profile.cardinalprofile.CardinalMultiProfile`
* :py:class:`~pabutools.election.profile.cumulativeprofile.CumulativeMultiProfile`
* :py:class:`~pabutools.election.profile.ordinalprofile.OrdinalMultiProfile`

"""


from pabutools.election.profile.profile import AbstractProfile, Profile, MultiProfile
from pabutools.election.profile.approvalprofile import (
    ApprovalProfile,
    ApprovalMultiProfile,
    get_random_approval_profile,
    get_all_approval_profiles,
)
from pabutools.election.profile.cumulativeprofile import (
    CumulativeProfile,
    CumulativeMultiProfile,
)
from pabutools.election.profile.cardinalprofile import (
    CardinalProfile,
    CardinalMultiProfile,
)
from pabutools.election.profile.ordinalprofile import (
    OrdinalProfile,
    OrdinalMultiProfile,
)

__all__ = [
    "Profile",
    "MultiProfile",
    "ApprovalProfile",
    "ApprovalMultiProfile",
    "get_random_approval_profile",
    "get_all_approval_profiles",
    "CumulativeProfile",
    "CumulativeMultiProfile",
    "CardinalProfile",
    "CardinalMultiProfile",
    "OrdinalProfile",
    "OrdinalMultiProfile",
]

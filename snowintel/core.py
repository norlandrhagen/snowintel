from dataclasses import dataclass

import pandas as pd

from .utils import get_sites


@dataclass(repr=False)
class GetSites:
    dataframe: pd.DataFrame = None  # Assigned in __post__init__

    # ToDo / Future Methods:
    # Find nearest n sites. Input site_ID & n closest sites
    # Find sites within radius of site
    # Find sites within radius of input lat/lon pair
    # Filter sites by elevation

    def __post_init__(self):
        self.dataframe = get_sites()

    def filter_by_state(self, state):
        """Returns DataFrame for selected state

        :param state: Two leter state abbv. ex: MT
        :type state: str
        :return: DataFrame filtered by State
        :rtype: pd.DataFrame
        """
        return self.dataframe[self.dataframe["state"] == state]

    def filter_by_elevation(self, minimum_elevation, maximum_elevation):
        return self.dataframe[
            self.dataframe["elevation_m"].between(
                float(minimum_elevation), float(maximum_elevation)
            )
        ]


@dataclass
class GetSitesSpatialQuery(GetSites):
    pass


# @dataclass
# class GetSnotel():
#     site_ids: str | list

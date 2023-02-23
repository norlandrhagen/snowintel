from dataclasses import dataclass

import pandas as pd

from .utils import get_sites


@dataclass(repr=False)
class GetSites:
    """_summary_

    :return: _description_
    :rtype: _type_
    """

    dataframe: pd.DataFrame = None  # Assigned in __post__init__
    state_filter: str | list | None = None
    minimum_elevation: str | int | None = None
    maximum_elevation: str | int | None = None

    def __post_init__(self):
        self.dataframe = get_sites()

        if self.state_filter:
            self.dataframe = self.filter_by_state(state_filter=self.state_filter)

        if self.minimum_elevation and self.maximum_elevation:
            self.dataframe = self.filter_by_elevation(
                minimum_elevation=self.minimum_elevation, maximum_elevation=self.maximum_elevation
            )

    def filter_by_state(self, state_filter):
        """Returns DataFrame for selected state

        :param state_filer: Two leter state abbv. ex: MT
        :type state: str
        :return: DataFrame filtered by State
        :rtype: pd.DataFrame
        """
        if isinstance(state_filter, str):
            state_filter = [state_filter]
        return self.dataframe[self.dataframe["state"].isin(state_filter)]

    def filter_by_elevation(self, minimum_elevation, maximum_elevation):
        """Returns DataFrame of sites between elevation min/max

        :param minimum_elevation: min elevation (m)
        :type minimum_elevation: str | float
        :param maximum_elevation: max elevation (m)
        :type maximum_elevation: str | float
        :return: Modified DataFrame
        :rtype: Pandas DataFrame
        """
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

from dataclasses import dataclass

from .utils import get_sites


@dataclass(repr=False)
class GetSites:
    data_dict: dict = None  # Assigned in __post__init__

    def __post_init__(self):
        self.data_dict = get_sites()

    def dataframe(self):
        from pandas import DataFrame

        return DataFrame.from_dict(self.data_dict, orient="index")

from datetime import datetime
from typing import Union

import pandas as pd
import requests


def _create_WSDL_cache(*, sqlite_cache_path: str = "/tmp/sqlite.db", timeout: int = 60):
    """_summary_

    :param sqlite_cache_path: path to sqlite db cache, defaults to '/tmp/sqlite.db'
    :type sqlite_cache_path: str, optional
    :param timeout: cache timeout, defaults to 60 seconds
    :type timeout: int, optional
    :return: zeep Transport object to pass to Client
    :rtype: zeep.transports.Transport
    """

    from zeep.cache import SqliteCache
    from zeep.transports import Transport

    SqliteCache(path=sqlite_cache_path, timeout=timeout)
    return Transport(cache=SqliteCache())


def _init_WSDL_client(*, url: str = "https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL"):
    """Initalize a zeep WSDL Client using a cache

    :param url: input url, defaults to "https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL"
    :type url: str, optional
    :return: zeep Client
    :rtype: zeep.Client
    """
    from zeep import Client

    transport = _create_WSDL_cache()
    return Client(url, transport=transport)


def _clean_last_site_df(*, df: pd.DataFrame) -> pd.DataFrame:
    """_summary_

    :param df: input DataFrame created from xml -> dict
    :type df: pd.DataFrame
    :return: cleaned DataFrame
    :rtype: pd.DataFrame
    """
    site_code = df["siteCode"].apply(pd.Series)["#text"]
    site_name = df["siteName"]
    state = site_code.str.split("_", expand=True)[1]
    latlon = (
        df["geoLocation"]
        .apply(pd.Series)["geogLocation"]
        .apply(pd.Series)[["latitude", "longitude"]]
    )
    latitude = latlon["latitude"]
    longitude = latlon["longitude"]
    elevation_m = df["elevation_m"].astype(float).round(1)
    elevation_ft = (elevation_m * 3.28084).round(1)

    # Note: 'siteProperty' parsing ignored for now and removed from cleaned df
    cdf = pd.DataFrame(
        {
            "site_code": site_code,
            "site_name": site_name,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
            "elevation_m": elevation_m,
            "elevation_ft": elevation_ft,
        }
    )
    # Drops the invalid site code
    return cdf[cdf["site_code"] != "894_TC_SNTL"]


def _parse_site_xml(*, response) -> pd.DataFrame:
    """Parse XML response from Client. Transform xml to dictionary,
    create and clean DataFrame

    :param response: Input response from Client
    :type response: str
    :return: cleaned DataFrame
    :rtype: pd.DataFrame
    """
    import xmltodict

    response_dict = xmltodict.parse(response)
    list_site_dicts = [i["siteInfo"] for i in response_dict["sitesResponse"]["site"]]
    df = pd.DataFrame(list_site_dicts)
    cdf = _clean_last_site_df(df=df)
    return cdf


def get_sites() -> pd.DataFrame:
    client = _init_WSDL_client()
    response = client.service.GetSites("")
    cdf = _parse_site_xml(response=response)
    return cdf


def _get_site_info_response(*, site_id) -> requests.models.Response:
    client = _init_WSDL_client()
    return client.service.GetSiteInfo(site=f"SNOTEL:{site_id}")


def get_site_variables(*, site_id: str) -> pd.DataFrame:
    """For site_id return DataFrame of variable information

    :param site_id: SNOTEL site_id. Ex: '301_CA_SNTL'
    :type site_id: str
    :return: DataFrame of variable information for site
    :rtype: Pandas DataFrame
    """
    import xmltodict

    response = _get_site_info_response(site_id=site_id)

    response_dict = xmltodict.parse(response)

    # computers were a mistake
    df_tuple_input = [
        (
            i["variable"]["variableCode"]["#text"],
            i["variable"]["variableCode"]["@variableID"],
            i["variable"]["variableName"],
            i["variable"]["unit"]["unitAbbreviation"],
        )
        for i in response_dict["sitesResponse"]["site"]["seriesCatalog"]["series"]
    ]

    return pd.DataFrame(
        df_tuple_input, columns=["variable_code", "variable_id", "variable_name", "unit"]
    )


def _validate_input_site_variables(*, site_id: str, input_vars: Union[str, list]) -> bool:
    """helper function to validate if input variables are available for selected snotel site"""
    if not isinstance(input_vars, list):
        input_vars = [input_vars]

    avail_var_codes = get_site_variables(site_id=site_id)["variable_code"].to_list()
    valid_bool = set(input_vars).issubset(avail_var_codes)
    return valid_bool


def _validate_input_site_id(site_id: str) -> bool:
    """helper function to validate if input site_id is a valid SNOTEL site

    :param site_ids: input str of site ID. Note: This do not have 'SNOTEL:' prefix
    :type site_ids: list[str]
    :return: validation bool
    :rtype: bool
    """
    avail_site_list = get_sites()["site_code"].to_list()
    valid_bool = {site_id}.issubset(avail_site_list)
    return valid_bool


def _convert_to_isodate(input_date: str) -> str:
    import isodate

    if not isinstance(input_date, datetime):
        input_date = datetime.strptime(input_date, "%Y-%m-%d")

    return isodate.datetime_isoformat(input_date)


def _clean_var_df(*, df: pd.DataFrame) -> pd.DataFrame:
    # remove '-9999.0' elements in value. Corresponding @qualifiers contain nans where value is invalid.
    df.dropna(inplace=True)
    df = df[
        [
            "@dateTimeUTC",
            "#text",
        ]
    ]
    return df.rename({"@dateTimeUTC": "time", "#text": "value"}, axis=1)


def _parse_var_xml(*, response) -> pd.DataFrame:
    """Parse XML response from Client. Transform xml to dictionary,
    create and clean DataFrame

    :param response: Input response from Client
    :type response: str
    :return: cleaned DataFrame
    :rtype: pd.DataFrame
    """
    import xmltodict

    response_dict = xmltodict.parse(response)
    val_dict = [i for i in response_dict["timeSeriesResponse"]["timeSeries"]["values"]["value"]]
    df = pd.DataFrame(val_dict)
    cdf = _clean_var_df(df=df)

    return cdf


def get_snotel_data_by_site_id(
    *, site_id: str, start_date: str, end_date: str, variable: str
) -> pd.DataFrame:
    # validate input site_ids
    if not _validate_input_site_id(site_id):
        raise TypeError(
            """One or more of input site_ids is not a valid SNOTEL ID code.
        Call get_sites() for available SNOTEL site ids """
        )

    if not _validate_input_site_variables(site_id=site_id, input_vars=variable):
        raise TypeError(
            f"""Input variable code of {variable} is not a valid SNOTEL variable code for the site: {site_id}
        Call get_variables_by_site() for available variables for a given SNOTEL site"""
        )

    # validate date times

    start_date_valid = _convert_to_isodate(start_date)
    end_date_valid = _convert_to_isodate(end_date)

    # add SNOTEL prefix:
    site_code = f"SNOTEL:{site_id}"
    variable_code = f"SNOTEL:{variable}"
    # initalize client
    client = _init_WSDL_client()

    # call get_values
    response = client.service.GetValues(
        site_code, variable_code, startDate=start_date_valid, endDate=end_date_valid
    )

    return _parse_var_xml(response=response)


# site_id = '301_CA_SNTL'
# site_id = '682_CO_SNTL'

# variable = 'SNWD_D'
# variable='WTEQ_D'
# start_date = '2000-01-01'
# end_date = '2000-02-02'

# cdf = get_snotel_data_by_site_id(site_id=site_id, variable=variable, start_date=start_date, end_date=end_date)

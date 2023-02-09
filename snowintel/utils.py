import pandas as pd


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
    state = site_code.str.split("_", expand=True)[1]
    latlon = (
        df["geoLocation"]
        .apply(pd.Series)["geogLocation"]
        .apply(pd.Series)[["latitude", "longitude"]]
    )
    latitude = latlon["latitude"]
    longitude = latlon["longitude"]
    elevation_m = df["elevation_m"].astype(float).round(1)

    # Note: 'siteProperty' parsing ignored for now and removed from cleaned df
    cdf = pd.DataFrame(
        {
            "site_code": site_code,
            "state": state,
            "latitude": latitude,
            "longitude": longitude,
            "elevation_m": elevation_m,
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

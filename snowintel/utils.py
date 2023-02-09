import io

from ulmo import util, waterml
from zeep import Client


def get_sites() -> dict:
    SNOTEL_WSDL_URL = "https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL"
    client = Client(SNOTEL_WSDL_URL)
    response = client.service.GetSites("")
    response_buffer = io.BytesIO(util.to_bytes(response))
    return waterml.v1_1.parse_site_infos(response_buffer)

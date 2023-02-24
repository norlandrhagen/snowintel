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
    geodataframe = None
    state_filter: str | list = None
    minimum_elevation: str | list = None
    maximum_elevation: str | list = None

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

    def geodataframe(self):
        try:
            import geopandas as gpd
        except Exception:
            raise ImportError(
                'Geopandas is not installed. Please install with conda/mamba "conda install -c conda-forge geopandas"'
            )

        gdf = gpd.GeoDataFrame(
            self.dataframe,
            geometry=gpd.points_from_xy(self.dataframe.longitude, self.dataframe.latitude),
        )
        gdf.crs = "EPSG:4326"
        self.geodataframe = gdf
        return gdf

    def create_map(self, basemap="google_terrain"):
        try:
            import folium
        except Exception:
            raise ImportError("Folium is not installed. Please install with conda/mamba/pip.")

        basemaps = {
            "google_maps": folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                attr="Google",
                name="Google Maps",
                overlay=True,
                control=True,
            ),
            "google_satellite": folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                attr="Google",
                name="Google Satellite",
                overlay=True,
                control=True,
            ),
            "google_terrain": folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
                attr="Google",
                name="Google Terrain",
                overlay=True,
                control=True,
            ),
            "google_satellite_hybrid": folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                attr="Google",
                name="Google Satellite",
                overlay=True,
                control=True,
            ),
            "esri_satellite": folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Esri Satellite",
                overlay=True,
                control=True,
            ),
        }

        m = folium.Map()

        basemaps[basemap].add_to(m)

        geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in self.geodataframe.geometry]

        for i, coords in enumerate(geo_df_list):
            m.add_child(
                folium.CircleMarker(
                    location=coords,
                    radius=10,  # in meters
                    fill_color="#f25c3c",
                    color="#f25c3c",
                    popup="site_code: "
                    + str(self.geodataframe.site_code.iloc[i])
                    + "<br>"
                    + "elevation: "
                    + str(self.geodataframe.elevation_m.iloc[i])
                    + "<br>"
                    + "Coordinates: "
                    + str(coords),
                )
            )

        # folium.GeoJson(data=self.geodataframe["geometry"]).add_to(m)

        sw = self.geodataframe[["latitude", "longitude"]].min().values.tolist()
        ne = self.geodataframe[["latitude", "longitude"]].max().values.tolist()
        m.fit_bounds([sw, ne])

        return m


@dataclass
class GetSitesSpatialQuery(GetSites):
    pass


# @dataclass
# class GetSnotel():
#     site_ids: str | list

def _return_basemaps() -> dict:
    import folium

    return {
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


def create_map(*, gdf, basemap="google_terrain"):
    try:
        import folium
    except Exception:
        raise ImportError("Folium is not installed. Please install with conda/mamba/pip.")

    m = folium.Map()
    _return_basemaps()[basemap].add_to(m)

    geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry]

    for i, coords in enumerate(geo_df_list):
        m.add_child(
            folium.CircleMarker(
                location=coords,
                z_index_offset=1000,
                radius=10,  # in meters
                fill_color="#f25c3c",
                color="#f25c3c",
                popup="site_code: "
                + str(gdf.site_code.iloc[i])
                + "<br>"
                + str(gdf.site_name.iloc[i])
                + "<br>"
                + "elevation (meters): "
                + str(gdf.elevation_m.iloc[i])
                + "<br>"
                + "elevation (FT): "
                + str(gdf.elevation_ft.iloc[i])
                + "<br>"
                + "Coordinates: "
                + str(coords),
            )
        )

    sw = gdf[["latitude", "longitude"]].min().values.tolist()
    ne = gdf[["latitude", "longitude"]].max().values.tolist()
    m.fit_bounds([sw, ne])

    return m

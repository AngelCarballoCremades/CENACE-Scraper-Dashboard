import plotly.express as px
import geopandas
import folium
import pandas as pd


# gdf = geopandas.read_file('..\\inegi\\00mun.shp')

# df = gdf[['CVEGEO','CVE_ENT','CVE_MUN','NOMGEO']]
# df['LAT'] = gdf.centroid.to_crs(epsg = 4326).y
# df['LON'] = gdf.centroid.to_crs(epsg = 4326).x


# print(df)

# # print(gdf.T.head())



# # gdf2 = gdf.centroid.to_crs(epsg = 4326)
# # fig = px.scatter_mapbox(gdf2, lat=gdf2.centroid.y, lon=gdf2.centroid.x, color_discrete_sequence=["fuchsia"], zoom=3, height=700)
# # fig.update_layout(mapbox_style="open-street-map")
# # fig.update_layout(margin={"r":1,"t":2,"l":3,"b":4})
# # fig.show()


latitud = '23.769457'
longitud = '-102.507216'
zoom = 4.3
mapbox_style = 'open-street-map'


# fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon",     color="peak_hour", size="car_hours",
#                   color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)

fig = px.scatter_mapbox(
    # df_final,
    lat=[0],
    lon=[0],
    zoom=zoom,
    height=700,
    center = dict(
        lat = float(latitud),
        lon = float(longitud))
    )

fig.update_layout(mapbox_style=mapbox_style)
fig.update_layout(coloraxis_showscale=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

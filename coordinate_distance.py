import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from functions import *
import psycopg2 as pg2
import plotly.express as px



db_name = 'cenace'

conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
cursor = conn.cursor()

cursor.execute("""SELECT * FROM nodes_info""")

colnames = [desc[0] for desc in cursor.description]
df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
# print(df)

conn.close()


# print(len(df[df.lat.apply(lambda x: x=='') | df.lon.apply(lambda x: x=='')].values))
# print(len(df.values))
# [print(row[-2],row[-1]) for row in df.values]


lats = [float(row[-2]) if row[-2] != '' else 0 for row in df.values]
lons = [float(row[-1]) if row[-1] != '' else 0 for row in df.values]


df['Points'] = [Point(lat,lon) for lat, lon in zip(lats,lons)]
# print(df)
# print(df[df.Points == Point(0,0)])

# 20.622246, -99.651244
# 29.722570, -114.963932


# latitud = '29.722570'
# longitud = '-114.963932'

latitud = '17.050212'
longitud = '-96.684237'
selected_point = Point(float(latitud), float(longitud))

max_nodes = 9

distances = []
for p in df.Points.values:
    l = p.distance(selected_point)
    distances.append(l)

df['distance'] = distances
# print(type(df))
df.sort_values(by='distance', axis = 0, ascending=True, inplace=True)


distances_ordered = sorted(list(set(distances)))

df_final = pd.DataFrame(columns = df.columns)

while df_final.shape[0] < max_nodes and df_final.shape[0] < df.shape[0]:
    df_final = pd.concat([df_final , df[df.distance == distances_ordered.pop(0)]])

print(df_final)
df_final['color'] = 1

selected_point_df = pd.DataFrame.from_dict(data = {'lat':[latitud], 'lon':[longitud], 'color': [500]}, orient = 'columns')
df_final = df_final.append(selected_point_df)
df_final['marker_size'] = 12


# gdf2 = gdf.centroid.to_crs(epsg = 4326)
fig = px.scatter_mapbox(df_final,
    lat=df_final['lat'].astype('float'),
    lon=df_final['lon'].astype('float'),
    size = 'marker_size',
    color = 'color',
    color_discrete_sequence=["identity"],
    zoom=8,
    height=700,
    center = dict(
        lat = float(latitud),
        lon = float(longitud))
    # hover_data =
    )
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(mapbox_style='stamen-terrain')

fig.update_layout(coloraxis_showscale=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
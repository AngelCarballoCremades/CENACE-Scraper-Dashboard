import plotly.express as px
import pandas as pd
import numpy as np
import psycopg2 as pg2
import os
import sys
import psycopg2 as pg2
from functions import *
import datetime
from scipy.signal import savgol_filter


db_name = 'cenace'

conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
cursor = conn.cursor()


# cursor.execute("Select * FROM generation_real LIMIT 0")
# print(cursor.description)
# colnames = [desc[0] for desc in cursor.description]
# print(colnames)

def get_zones_list(cursor, system='sin', market='mda'):

    cursor.execute("""SELECT DISTINCT(zona_de_carga) FROM {}_pnd_{};""".format(system, market))
    zone_list = cursor.fetchall()
    # print(zone_list)
    return [zone[0] for zone in zone_list]


def generation_daily(cursor):

    print('requesting daily generation...\n')
    cursor.execute("""
        SELECT * FROM generation_real
        ORDER BY
            fecha ASC,
            hora ASC
        ;""")

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float')

    # df['total_gen'] = sum([df[col] for col in df.columns if col not in ['sistema','fecha','hora']])
    df_filtered = df.groupby(['fecha']).sum()
    df_filtered.drop(columns=['hora'], inplace=True)
    df_filtered = df_filtered.stack().to_frame()
    df_filtered.reset_index(inplace=True)
    df_filtered.columns = ['fecha','gen_type','generation_mwh']
    # print(df_filtered)

    fig = px.area(
        data_frame=df_filtered,
        x="fecha",
        y="generation_mwh",
        color="gen_type",
        hover_data=['gen_type','generation_mwh'],
        category_orders=dict(
            gen_type = [
                'nucleoelectrica',
                'carboelectrica',
                'combustion_interna',
                'ciclo_combinado',
                'geotermoelectrica',
                'termica_convencional',
                'turbo_gas',
                'hidroelectrica',
                'biomasa',
                'eolica',
                'fotovoltaica'
                ]))
    fig.update_layout(clickmode='event+select')
    # fig.update_traces(legendgroup='group')
    return fig
# fig.show()



def generation_month_hourly_average(cursor):

    print('requesting hourly generation...\n')
    cursor.execute("""
        SELECT * FROM generation_real
        ORDER BY
            fecha ASC,
            hora ASC
        ;""")

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df = df[df.hora != 25]
    df['fecha'] = pd.to_datetime(df['fecha'])

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float')

    df['total_gen'] = sum([df[col] for col in df.columns if col not in ['sistema','fecha','hora']])
    df['year'] = df.fecha.apply(lambda x: x.year)
    df['month'] = df.fecha.apply(lambda x: x.month)

    df_filtered = df.groupby(['year','month','hora']).mean()
    # print(df_filtered)
    # df_filtered = df_filtered.stack().to_frame()
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered[['year','month','hora','total_gen']]
    # df_filtered.columns = ['year','month','hora','gen_type','generation_mwh']
    df_filtered['month_hour'] =  df_filtered['month'].astype('str')+' '+df_filtered['hora'].astype('str')
    df_filtered['month_hour'] = df_filtered['month_hour'].apply(lambda x: datetime.datetime.strptime(x, '%m %d'))

    # print(df_filtered)
    # print(df_filtered)

    fig = px.line(
        data_frame=df_filtered,
        x="month_hour",
        y="total_gen",
        color="year",
        hover_data=['total_gen','month','hora'],
        )
    fig.update_layout(clickmode='event+select')
    fig.update_xaxes(tickformat="%b")# %b\n%Y
    return fig
    # fig.show()




# # Year VS Year GRAPH-------------------------------------------------

# cursor.execute("""
#     SELECT * FROM generation_real
#     ORDER BY
#         fecha ASC,
#         hora ASC
#     ;""")

# colnames = [desc[0] for desc in cursor.description]
# df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
# df['fecha'] = pd.to_datetime(df['fecha'])

# print(df)

# df_total = df.groupby(['fecha']).sum()
# df_total.reset_index(inplace=True)
# print(df_total)
# df_total.drop(columns=['hora'], inplace=True)
# df_total['year'] = df_total['fecha'].apply(lambda x: x.year)
# print(df_total)
# df_total['total_gen'] = sum([df_total[col] for col in df_total.columns if col not in ['fecha', 'year']])

# # for col in df_total.columns:
# #     if col not in ['fecha','year','gen_type']:
# #         df_total[col+'_s'] = savgol_filter(df_total[col].values.tolist(), 51,5)

# print(df_total)
# df_total = df_total.stack().to_frame()
# print(df_total)
# df_total.reset_index(inplace=True)
# df_total.columns = ['fecha','gen_type','generation_mwh']
# # print(df_total.head(30))

# df_total['year'] = df_total['fecha'].apply(lambda x: str(x.year))
# df_total['fecha'] = df_total['fecha'].apply(lambda x: datetime.datetime(year=2016, month=x.month, day=x.day))
# # print(df_total)
# # df_total = df_total.pivot_table(index = ['fecha_xaxis','year','gen_type'], columns = ['generation_mwh','fecha'])
# df_total.reset_index(inplace=True)
# print(df_total)


# fig = px.line(
#     data_frame=df_total,
#     x="fecha",
#     y='generation_mwh',
#     color='gen_type',
#     line_dash='year',
#     line_dash_sequence = ['dot', 'dash','solid'],
#     # line_shape='spline',
#     # render_mode='svg',
#     hover_data=['fecha','gen_type', 'generation_mwh'],
#     category_orders=dict(
#         gen_type = [
#             'total_gen',
#             'nucleoelectrica',
#             'carboelectrica',
#             'combustion_interna',
#             'ciclo_combinado',
#             'geotermoelectrica',
#             'termica_convencional',
#             'turbo_gas',
#             'hidroelectrica',
#             'biomasa',
#             'eolica',
#             'fotovoltaica'
#             ]))
# fig.update_xaxes(
#     tickformat="%b")# %b\n%Y

# fig.show()




# # df_total.drop(columns=[col for col in df_total.columns if col != 'total_gen'], inplace=True)
# # for col in ['total_gen']:
# #     df_total[col+'_soft'] = savgol_filter(df_total[col].values.tolist(), 21,5)

# # df_total.reset_index(inplace=True)
# # df_total['year'] = df_total['fecha'].apply(lambda x: x.year)
# # print(df_total)


# # print(pd.concat([df_total_2018, df_total_2019, df_total_2020], axis=1, ignore_index = True))





# # df_weekly = df_filtered.copy()
# # df_weekly['year'] = df_weekly['fecha'].apply(lambda x: x.year)
# # df_weekly['week'] = df_weekly.fecha.apply(lambda x: x.isocalendar()[1])
# # print(df_weekly)







# # HOURLY GRAPH-----------------------------------------------------

def generation_hourly(cursor, dates = 0):

    print('requesting:')

    if not dates:
        print('max date...')
        cursor.execute("""
            SELECT * FROM generation_real
            WHERE
                fecha = (SELECT MAX(fecha) FROM generation_real)
            ORDER BY
                fecha ASC,
                hora ASC
            ;""")

    elif type(dates) == type([]):
        # print(dates)
        cursor.execute("""
            SELECT * FROM generation_real
            WHERE
                fecha BETWEEN '{}' AND '{}'
            ORDER BY
                fecha ASC,
                hora ASC
            ;""".format(dates[0],dates[1]))

    colnames = [desc[0] for desc in cursor.description]
    df_hourly = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df_hourly['fecha'] = pd.to_datetime(df_hourly['fecha'])
    df_hourly['fecha'] +=  pd.to_timedelta(df_hourly.hora, unit='h')
    df_hourly.drop(columns=['hora'], inplace=True)

    for col in df_hourly.columns:
        if col not in ['sistema','fecha','hora']:
            df_hourly[col] = df_hourly[col].astype('float')


    df_hourly = df_hourly.groupby(['fecha']).sum()
    df_hourly = df_hourly.stack().to_frame()
    df_hourly.reset_index(inplace=True)
    df_hourly.columns = ['fecha','gen_type','generation_mwh']

    # print(df_hourly)

    fig = px.area(
        data_frame=df_hourly,
        x='fecha',
        y="generation_mwh",
        color="gen_type",
        hover_data=['gen_type','generation_mwh'],
        category_orders=dict(
            gen_type = [
                'nucleoelectrica',
                'carboelectrica',
                'combustion_interna',
                'ciclo_combinado',
                'geotermoelectrica',
                'termica_convencional',
                'turbo_gas',
                'hidroelectrica',
                'biomasa',
                'eolica',
                'fotovoltaica'
                ]),
        )
    # fig.update_traces(legendgroup='group')

    return fig


# # fig.show()


# db_name = 'cenace'

# conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
# cursor = conn.cursor()


def consumption_daily(cursor, zonas_de_carga = ['OAXACA','CAMPECHE','ACAPULCO','PUEBLA']):

    total = False
    # print(zonas_de_carga)
    if zonas_de_carga == ['MEXICO (PAIS)']:
        total = True

    if total:
        print('requesting zonas...')
        cursor.execute("""
            SELECT fecha, SUM(energia) AS energia FROM consumption_real
            GROUP BY fecha
            ORDER BY
                fecha ASC
            ;""")

    else:
        zonas_string = "','".join([zona for zona in zonas_de_carga])

        print('requesting zonas...')
        cursor.execute("""
            SELECT * FROM consumption_real
            WHERE zona_de_carga in ('{}')
            ORDER BY
                fecha ASC,
                hora ASC
            ;""".format(zonas_string))

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['energia'] = df['energia'].astype('float')

    # print(df)


    if total:
        fig = px.line(
            data_frame=df,
            x="fecha",
            y="energia",
            # color="zona_de_carga",
            # hover_data=['zona_de_carga','energia']
            )

        fig.update_layout(clickmode='event+select')
        # fig.update_traces(legendgroup='group')
        return fig

    if not total:
        df_filtered = df.groupby(['fecha','zona_de_carga']).sum()
        df_filtered.drop(columns=['hora'], inplace=True)
        df_filtered.reset_index(inplace=True)
        # print(df_filtered)
        df_filtered.columns = ['fecha','zona_de_carga','energia']

        # print(df_filtered)

        fig = px.line(
            data_frame=df_filtered,
            x="fecha",
            y="energia",
            color="zona_de_carga",
            hover_data=['zona_de_carga','energia']
            )

        fig.update_layout(clickmode='event+select')
        # fig.update_traces(legendgroup='group')
        return fig





def zone_daily_prices(cursor, system='sin', market='mda', zone='OAXACA'):

    print('requesting prices...', zone)
    cursor.execute("""
        SELECT * FROM {}_pnd_{}
        WHERE zona_de_carga = '{}'
        ORDER BY
            fecha ASC,
            hora ASC
        ;""".format(system,market, zone))

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    print(df)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.drop(columns=['hora','sistema','mercado','zona_de_carga'], inplace=True)

    print(df.T)

    for col in ['c_energia','c_perdidas','c_congestion','precio_e']:
        df[col] = df[col].astype('float')


    df = df.groupby(['fecha', 'precio_e']).mean()
    df = df.stack().to_frame()
    df.reset_index(inplace=True)
    df.columns = ['fecha','precio_e','price_component','$/MWh']
    # print(df)
    df = df.groupby(['fecha','price_component']).mean()
    df.reset_index(inplace=True)
    print(df)
    print('\n\n\n\n\n\n')

    fig = px.area(
        data_frame=df,
        x='fecha',
        y="$/MWh",
        color="price_component",
        hover_data=['price_component','$/MWh','precio_e'],
        category_orders=dict(
            price_component = [
                'c_energia',
                'c_perdidas',
                'c_congestion'
                ])
        )
    # fig.show()
    fig.update_layout(title_text=f'{zone} Daily Prices', title_x=0.5)
    return fig


def zone_hourly_prices(cursor, system='sin', market='mda', zone='OAXACA', dates = 0):

    print('requesting:')

    if not dates:
        print('max date...')
        cursor.execute("""
            SELECT * FROM {}_pnd_{}
            WHERE
                zona_de_carga = '{}' AND
                fecha = (SELECT MAX(fecha) from {}_pnd_{})
            ORDER BY
                fecha ASC,
                hora ASC
            ;""".format(system,market, zone, system, market))

    elif type(dates) == type([]):
        print(dates)
        cursor.execute("""
            SELECT * FROM {}_pnd_{}
            WHERE
                zona_de_carga = '{}' AND
                fecha BETWEEN '{}' AND '{}'
            ORDER BY
                fecha ASC,
                hora ASC
            ;""".format(system,market, zone, dates[0], dates[1]))

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    print(df)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['fecha'] +=  pd.to_timedelta(df.hora, unit='h')
    df.drop(columns=['hora'], inplace=True)

    print(df)

    for col in ['c_energia','c_perdidas','c_congestion','precio_e']:
        df[col] = df[col].astype('float')



    df = df.groupby(['fecha', 'precio_e']).mean()
    df = df.stack().to_frame()
    df.reset_index(inplace=True)
    df.columns = ['fecha','precio_e','price_component','$/MWh']
    print(df)

    # df = df.groupby(['fecha']).sum()
    # df = df.stack().to_frame()
    # df.reset_index(inplace=True)
    # df.columns = ['fecha','gen_type','generation_mwh']

    fig = px.area(
        data_frame=df,
        x='fecha',
        y="$/MWh",
        color="price_component",
        hover_data=['price_component','$/MWh','precio_e'],
        category_orders=dict(
            price_component = [
                'c_energia',
                'c_perdidas',
                'c_congestion'
                ])
        )
    # fig.update_traces(legendgroup='group')

    return fig


conn.close()
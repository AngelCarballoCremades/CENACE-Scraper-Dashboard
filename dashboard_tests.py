import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import numpy as np

# np.random.seed(42)

# x1 = np.random.randint(1,101,100)
# y1 = np.random.randint(1,101,100)

# fig = px.scatter(x=x1, y=y1)
# fig.show()

# data = [go.Scatter(x=x1,
#                    y=y1,
#                    mode='markers',
#                    marker=dict(
#                         size=12,
#                         color='rgb(51,204,153)',
#                         symbol='pentagon',
#                         line={'width':2}
#                     ))]
# layout = go.Layout(title='Gráfica1',
#                    xaxis={'title':'Eje x'},
#                    yaxis=dict(title='Eje y'),
#                    hovermode = 'closest')
# fig = go.Figure(data=data, layout = layout)
# pyo.plot(fig, filename='scatter.html')




df = px.data.gapminder()
df_2007 = df.query("year==2007")

for template in ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]:
    fig = px.scatter(df_2007,
                     x="gdpPercap", y="lifeExp", size="pop", color="continent",
                     log_x=True, size_max=60,
                     template=template, title="Gapminder 2007: '%s' theme" % template)
    fig.show()

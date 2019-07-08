import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from collections import deque
import pandas as pd
from query_from_csv import OscClient


osc_client = OscClient()
interval = 1
X = deque(maxlen=800)
X.append(0)
Y = deque(maxlen=800)
Y.append(0)
Z = deque(maxlen=800)
Z.append(0)

df = pd.read_csv('logs/log_refactored_correction_factor.csv', na_values=['no info', '.'], delimiter=',')
df_indexed = df.reset_index(drop=False)

index = df_indexed['index']
delta = df_indexed['Delta']
volume = df_indexed['Blood Accumulated']

delta_min = delta.min()
delta_max = delta.max()
volume_min = volume.min()
volume_max = volume.max()

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.Div([
            html.H1(children="Sonification of Bleeding Measurements Based on Simulated Data"),
            html.Img(src="/assets/heart-blood-icon.png"),
        ], className="banner"),

        html.Div([
            html.Div([
                html.Div(children="Spontaneous Value of Bleeding per Second: 'Delta'", className="title"),
                dcc.Graph(id='live-graph-delta', animate=True),
                dcc.Interval(
                    id='graph-update-delta',
                    interval=interval*1000,  # in milliseconds
                    n_intervals=0,
                )], className="graph"),
            html.Div([
                html.Div(children="Total Amount of Bleeding from the Beginning of the Operation: 'Volume'", className="title"),
                dcc.Graph(id='live-graph-volume', animate=True),
                dcc.Interval(
                    id='graph-update-volume',
                    interval=interval*1000,  # in milliseconds
                    n_intervals=0
                )
            ], className="graph"),
        ], className="row"),

        # html.Button('stop', id='button')
    ]
)

"""
@app.callback([Output(),
               Input('button', 'n_clicks')])
def onclick():
    osc_client.stop()

"""


@app.callback(Output('live-graph-delta', 'figure'),
              [Input('graph-update-delta', 'n_intervals')])
def update_graph_scatter(n):
    X.append(index[n])
    Y.append(delta[n])
    data1 = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers',
        line=dict(color='#f44242')
    )

    return {'data': [data1], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)+1],),
                                                 yaxis=dict(range=[min(Y), max(Y)+1]),)}


@app.callback(Output('live-graph-volume', 'figure'),
              [Input('graph-update-volume', 'n_intervals')])
def update_graph_scatter(n):
    osc_client.run(n)
    X.append(index[n])
    Z.append(volume[n])
    data2 = go.Scatter(
        x=list(X),
        y=list(Z),
        name='Scatter',
        mode='lines+markers',
        line=dict(color='#425ff4')
    )
    return {'data': [data2], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)+1],),
                                                 yaxis=dict(range=[min(Z), max(Z)+1]),)}


if __name__ == '__main__':
    app.run_server(debug=True)
    osc_client.stop()

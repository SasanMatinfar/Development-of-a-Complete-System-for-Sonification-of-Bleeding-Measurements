import dash
from dash.dependencies import Output, Input, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
import pandas as pd


X = deque(maxlen=50)
X.append(0)
Y = deque(maxlen=50)
Y.append(0)


df = pd.read_csv('logs/log_refactored_correction_factor.csv', na_values=['no info', '.'], delimiter=',')
df_indexed = df.reset_index(drop=False)

index = df_indexed['index']
delta = df_indexed['Delta']
volume = df_indexed['Blood Accumulated']

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.Div(html.H1(children="Sonification of Bleeding Measurements Based on Simulated Data")),
        html.Label("Spontaneous Value of Bleeding per Second"),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000,  # in milliseconds
            n_intervals=0
        )
    ]
)


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    X.append(index[n])
    Y.append(delta[n])
    data = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers',
        line=dict(color='#f44242')
    )
    return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                                yaxis=dict(range=[min(Y), max(Y)]),)}


if __name__ == '__main__':
    app.run_server(debug=True)

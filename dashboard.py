# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

m_systems = ['m_'+str(x).zfill(4) for x in range(250)]
#t1 = pd.Timestamp.now().floor('1 min')
#t0 = t1 - pd.Timedelta('7 days')

t1 = datetime.utcnow()
t0 = t1 - timedelta(days=7)

app.layout = html.Div(children=[
    html.H1('MAPCO2 Iridium Dashboard', style={'textAlign': 'center', 'color': '#7FDFF'}),


    html.Label('MAPCO2 Systems'),

    html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in m_systems],
                value=['m_168'],
                multi=True
            ),
            dcc.DatePickerRange(
                start_date_placeholder_text=t0,
                end_date_placeholder_text=t1,
                #calendar_orientation='vertical',
            )
    ]),



    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
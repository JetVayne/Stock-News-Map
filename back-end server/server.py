import json
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Output, Input

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    },
    {
        'href':'http://allfont.net/allfont.css?fonts=open-sans-light',
        'rel': 'stylesheet',
        'type': 'text/css'
    }
]

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

df = pd.read_csv('apple_data.csv')

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([html.H2(' Apple Stock Map - 2019'),
              html.Img(src='/assets/apple-logo.png')],
             className='banner'),

    dcc.Graph(
        id='graph_open',
        figure={
            'data': [
                {
                    'x': list(df.date),
                    'y': list(df.price),
                    # 'text': list(df.news),
                    # 'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                    # 'name': 'Trace 1',
                    'mode': 'line',
                    'marker': {'size': 15}
                }
            ],
            'layout': {
                'clickmode': 'event+select'
            }
        }
    ),

    html.Div(className='news-info', children=[
        html.Div([
            dcc.Markdown(d("""
                **Most Related News:**
            """)),
            html.Div(id='click-data'),
        ], className='news-info'),
    ])
])


@app.callback(
    Output('click-data', 'children'),
    [Input('graph_open', 'clickData')])
def display_click_data(clickData):
    if clickData:
        index = clickData['points'][0]['pointNumber']
        # print(index, len(df))
        nd = df.loc[index]['news']
        news_json = json.loads(nd)
        temp = []
        for i in news_json['data']:
            temp.append(html.A(href=i['url'], target='_blank', children=html.P(i['title'])))
            temp.append(html.Hr(style={'box-sizing': 'content-box',
                                       'height': '1px',
                                       'color': '#414042',
                                       'background-color': '#333'
                                       }))

            if len(temp) == 10:
                return temp

        if len(temp) != 0:
            return temp
        else:
            return 'There is no News-data on this day.'
    else:
        return 'Click the plot to see the related news.'


if __name__ == '__main__':
    app.run_server(debug=True)

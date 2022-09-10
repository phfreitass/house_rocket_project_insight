from email.mime import application
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import dash
from re import template
from tempfile import tempdir
import plotly.graph_objects as go

df = pd.read_csv('kc_house_data.csv')
df1 = pd.read_csv('kc_house_report.csv')

mean_lat = df.lat.mean()
mean_long = df.long.mean()
#----------------------------------------------------------------------------------------------------------------------------
#Insights

# H1: Imóvies que possuem vista para água, são 30% mais caros, na media
h1 = df1[['waterfront','price']].groupby(['waterfront']).mean().reset_index()
figl = px.bar(h1, x='waterfront', y='price')
figl.update_layout(template='plotly_dark', paper_bgcolor="rgba(0, 0, 0, 0)")

# H2: Imóveis que sofreram reformas são 43.37% mais caros em media
#Coluna discriminando se o imovel foi ou nao renovado
h2 = df1[['renovated', 'price']].groupby('renovated').mean().reset_index()
figl1 = px.bar(h2, x='renovated', y='price')
figl1.update_layout(template='plotly_dark', paper_bgcolor="rgba(0, 0, 0, 0)")

# H3: No verão os imoveis vendem -2.91% em relaçao a primavera (maior estação de venda)
h3 = df1[['season', 'price']].groupby('season').count().reset_index()
figl2 = px.bar(h3, x='season', y='price')
figl2.update_layout(template='plotly_dark', paper_bgcolor="rgba(0, 0, 0, 0)")

#----------------------------------------------------------------------------------------------------------------------------
# Data do mapa
data = pd.read_csv('dataset_mapa.csv')
data.loc[data['price'] > 2000000, 'price'] = 2000000
data.loc[data['price'] < 100000, 'price'] = 100000

#-----------------------------------------------------------------------------------------------------------------------------
# Mapas interativos

#px.set_mapbox_access_token('pk.eyJ1Ijoid3JmZXJyZWlyYTEiLCJhIjoiY2w3YWR3dzVhMGY4eDN4bm92Njd1dGJlbSJ9.jGtsocq6UByGdUVJ--0jYQ')
fig = go.Figure()
fig.update_layout(template='plotly_dark', paper_bgcolor="rgba(0, 0, 0, 0)")

#--------------------------------------Layout---------------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.SLATE],
                                                meta_tags=[{'name': 'viewport',
                                                            'content':'width-device-whidth, initialscale=1.0'}])
application= app.server

app.layout = dbc.Container([

    dbc.Row([

        dbc.Col(html.H1('Dashboard House Rocket',
                   className= 'text-center text primary,display-2 shadow',),
                   width= 12 ),
    ]),
#-------------------------------------------------------------------------------------------------------------------------------    
    dbc.Row([

        dbc.Col(html.H1('Principais Insights',
                   className= 'text-left',),
                   width= 12 ),
    ]),
#--------------------------------------------------------------------------------------------------------------------------------
    dbc.Row([
        dbc.Col([
                dcc.Graph(id='bar-fig', figure=figl),
                html.P('H1: Imóveis com visão para o mar são em média 212.64% mais caros que os demais',
                className='display-20 shadow'),
                ], width = {'size':4, 'order':1}),
  

        dbc.Col([
                dcc.Graph(id='bar-fig1', figure=figl1),
                html.P('H2: Imóveis reformados são 43.37% mais caros na média',
                className='display-20 shadow'),
                ], width = {'size':4, 'order':2}),


        dbc.Col([
                dcc.Graph(id='bar-fig2', figure=figl2),
                html.P('H3: No verão os imoveis vendem -2.91% em relaçao a primavera (maior estação de venda)',
                className='display-20 shadow'),
                ], width = {'size':4, 'order':3})
]),

    dbc.Row([
        dbc.Col([
        html.H4("""Distrito""", style={"margin-top": "50px", "margin-bottom": "25px"}),
        ],sm=6, md=6),

        dbc.Col([
        html.H4("""Selecione a opção de compra""", style={"margin-top": "50px", "margin-bottom": "25px"}),
        ],sm=6, md=6),
]),

    dbc.Row([
        dbc.Col([
        dcc.Dropdown(
        id="location_dropdown",
        options=[{"label":x, "value":x} for x in data.zipcode.unique()],
        value= 0,
        placeholder= "Filtrar por Distrito"
        ),

],sm=6, md=6),


    dbc.Col([
        dcc.Dropdown(
        id="status_dropdown",
        options=[{"label":x, "value":x} for x in data.status.unique()],
        value= 0,
        placeholder= "Filtrar Imóveis aptos ou não aptos para compra"
        ),

],sm=6, md=6),

]),
    dbc.Row([
        dcc.Graph(id= 'map-graph', figure=fig)
        ], style={"height": "80vh"})

])

@app.callback(
    Output('map-graph', 'figure'),
    [Input('location_dropdown', 'value'),
    Input('status_dropdown', 'value')]
)

def update_graph(color_map, status_map):
    
    px.set_mapbox_access_token('pk.eyJ1Ijoid3JmZXJyZWlyYSIsImEiOiJjbDJxcml1YngwMGduM2NwZXkyeGx2bXR6In0.Smk9XrVHXr-I7qdmmkpFtg')
    
    if (color_map is None) & (status_map is None):
        df_aux = data.copy()

    elif (color_map == 0) & (status_map == 0):
        df_aux = data.copy()
    
    elif(color_map != 0) & ((status_map is None) or (status_map ==0) ): 
        df_aux = data[(data['zipcode'] == color_map)] 
    
    elif((color_map is None) or (color_map ==0)) & (status_map != 0 ):
        df_aux = data[(data['status'] == status_map)]

    else:
        df_aux = data[(data['zipcode'] == color_map) & (data['status'] == status_map) ]
    
    
    status_map = 'price' #Variavel de teste 
    color_rgb = px.colors.sequential.GnBu
    
    df_quantiles= data[status_map].quantile(np.linspace(0, 1, len(color_rgb))).to_frame()
    df_quantiles=(df_quantiles - df_quantiles.min()) / (df_quantiles.max() - df_quantiles.min())
    df_quantiles['colors'] = color_rgb
    
    df_quantiles.set_index(status_map, inplace=True)
    color_scale = [[i, j] for i , j in df_quantiles['colors'].iteritems()]
    
    map_fig = px.scatter_mapbox(df_aux, lat="lat", lon="long", color='price',
                size='price', size_max=15, zoom=10, opacity=0.4)
    
    map_fig.update_coloraxes(colorscale = color_scale)
    
    map_fig.update_layout(mapbox= dict(center=go.layout.mapbox.Center(lat=mean_lat, lon=mean_long)),
                                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                                margin=go.layout.Margin(l=10, r=10, t=10, b=10),)
    return map_fig


if __name__ == '__main__':
    app.run_server(debug=False, port=8080)
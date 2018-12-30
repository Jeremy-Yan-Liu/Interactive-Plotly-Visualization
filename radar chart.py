#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 14:58:02 2018

@author: ly
"""
import plotly
plotly.tools.set_credentials_file(username='LY_Air', api_key='hTbvl6jcjK4SMe6OeUZ4')
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# Get external style sheet template
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Read data
df = pd.read_csv(
        'cleaned_data.csv', sep=',',encoding='utf-8-sig',
        usecols = ['Track_name','Album_name','Movie_name',
                   'acousticness','danceability','energy',
                   'instrumentalness','liveness','speechiness'
                   ]
        )

# Get only unique track names
unique_df = df.drop_duplicates(subset = 'Track_name')

# Extract the subset of movie names and track names
names = unique_df.loc[:,['Track_name','Movie_name']]
groupedDF = names.groupby("Movie_name")
mvTrackPair = {}
for movie,group in groupedDF:        
        mvTrackPair[movie] = list(group['Track_name'])
all_options = mvTrackPair

# Change index of the data frame for easy access
unique_df = unique_df.set_index('Track_name')

# Desired attributes for the radar plot 
attributes = ['acousticness','danceability','energy',
              'instrumentalness','liveness','speechiness','acousticness']

#Capitalize for better display
cap_attributes = [attribute.capitalize() for attribute in attributes ]

# Design the layout of the output html
app.layout = html.Div([
    html.Div([
        # Add a dropdown menu for movies
        html.Div('Movie'),    
        html.Div([
            dcc.Dropdown(
                id='movie_dropdown',
                options=[{'label': i, 'value': i} for i in all_options.keys()],
            ),
        ],
        style={'width': '24%', 'display': 'inline-block'}),
        # Add html.Hr for division
        html.Hr(),
        # Add a dropdown menu for track 1
        html.Div('Track 1'),
        html.Div([
            dcc.Dropdown(
                id='track_1_dropdown',
            ),
        ],
        style={'width': '24%', 'display': 'inline-block'}),
        # Add html.Hr for division
        html.Hr(),
        # Add a dropdown menu for track 2
        html.Div('Track 2'),
        html.Div([
            dcc.Dropdown(
                id='track_2_dropdown',
            ),
        ],
        style={'width': '24%', 'display': 'inline-block'})
    ]),
        # Add html.Hr for division
        html.Hr(),
        # Add a text to display results 
        html.Div(id='display-selected-values'),
        # Add a header for the radar graph
        html.H2(
            children='Radar Graph',
            style={
                'textAlign': 'center'
            }
        ),
        # Add the radar graph
        dcc.Graph(id='radar_graph')

])

# Use multiple callbacks to acheive interaction 
# Update track 1 options based on the selected movie
@app.callback(
    dash.dependencies.Output('track_1_dropdown', 'options'),
    [dash.dependencies.Input('movie_dropdown', 'value')])
def set_track_1_options(selected_movie):
    return [{'label': i, 'value': i} for i in all_options[selected_movie]]

# Update track 1 value based on the selected track from options
@app.callback(
    dash.dependencies.Output('track_1_dropdown', 'value'),
    [dash.dependencies.Input('track_1_dropdown', 'options')])
def set_track_1_value(available_options):
    return available_options[0]['value']

# Update track 2 options based on the selected movie
@app.callback(
    dash.dependencies.Output('track_2_dropdown', 'options'),
    [dash.dependencies.Input('movie_dropdown', 'value')])
def set_track_2_options(selected_movie):
    return [{'label': i, 'value': i} for i in all_options[selected_movie]]

# Update track 1 value based on the selected track from options
@app.callback(
    dash.dependencies.Output('track_2_dropdown', 'value'),
    [dash.dependencies.Input('track_2_dropdown', 'options')])
def set_track_2_value(available_options):
    return available_options[0]['value']

# Update the output texts based on the selected movie, track1 and track2
@app.callback(
    dash.dependencies.Output('display-selected-values', 'children'),
    [dash.dependencies.Input('movie_dropdown', 'value'),
     dash.dependencies.Input('track_1_dropdown', 'value'),
     dash.dependencies.Input('track_2_dropdown', 'value')])
def set_display_children(selected_movie, selected_track_1,selected_track_2):
    return u'You\'ve selected {} and {} in {}'.format(
        selected_track_1,selected_track_2, selected_movie,
    )   
    
# Update the output radar graph based on the selected track1 and track2
@app.callback(
    dash.dependencies.Output('radar_graph', 'figure'),
    [dash.dependencies.Input('track_1_dropdown', 'value'),
     dash.dependencies.Input('track_2_dropdown', 'value')])
    
# Plot the graph
def update_graph(track_1_name, track_2_name):

    trace1 = go.Scatterpolar(
                r = list(unique_df.loc[track_1_name,attributes]),
                theta = cap_attributes,
                         fill = 'toself',
                         name = track_1_name
            )
    trace2 = go.Scatterpolar(
                r = list(unique_df.loc[track_2_name,attributes]),
                  theta = cap_attributes,
                  fill = 'toself',
                  name = track_2_name
            )


    return {           
            'data': [trace1,trace2],
            
            'layout' : go.Layout(
                            polar = dict(
                                radialaxis = dict(
                                      visible = True,
                                      range = [0, 1]
                                          )
                                    ),
                            showlegend = True
                        )

    }


if __name__ == '__main__':
    app.run_server(debug=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 22:03:24 2018

@author: ly
"""
import plotly
plotly.tools.set_credentials_file(username='LY_Air', api_key='hTbvl6jcjK4SMe6OeUZ4')

import pandas as pd
import numpy as np
import networkx as nx
import plotly.plotly as py
import plotly.graph_objs as go
import math

def processDF():
    # Read data frame 
    df = pd.read_csv('cleaned_data.csv', sep=',',encoding='utf-8-sig',
                     usecols = ['Movie_genre','Movie_name'])
    # Drop duplicated movie name   
    df = df.drop_duplicates(subset = 'Movie_name')
    # Split genre column to calculate the number of genres a movie has
    genre = df['Movie_genre']
    genre_list = [i.split(',') for i in genre.tolist()]
    # Add a new column for the nubmer of genres a movie belongs to 
    length = [len(i) for i in genre_list]
    df['length'] = length
    # Create e new data frame, repeat movie name for certain times 
    # depending on the numbe of genres
    df_temp = pd.DataFrame({'movie':np.repeat(df['Movie_name'], length)})
    
    # split genre again but into separate columns 
    genre_split = genre.str.split(',',expand = True)
    # Transpose the genre columns to add to the new data frame
    row_temp = pd.Series()
    for index, row in genre_split.iterrows():
        row_temp = pd.concat([row_temp,row], ignore_index=True)    
    row_temp = row_temp.dropna()
    # Add the new genre column for the temporary data frame 
    df_temp['genre'] = row_temp.tolist()
    
    return df_temp
    
# The code below is adapted from two example from plotly tutorials
# Reference:
# https://plot.ly/python/network-graphs/
# https://plot.ly/python/custom-buttons/
  
def plotNetwork(df):
    # Use networkx to create a graph directly from the tailored data frame
    G = nx.from_pandas_edgelist(df, source='movie', target='genre')           
      
    # Set node positions
    
    pos = nx.kamada_kawai_layout(G)
    for node in G.nodes():
        G.node[node]['pos']= pos[node]

   
    # Create node trace:   
    node_trace = go.Scatter(
                            x=[],
                            y=[],
                            name='Node Trace',
                            text=[],
                            mode='markers',
                            hoverinfo='text',
                            marker=dict(
                                showscale=True,
                                # colorscale options
                                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                                colorscale='Jet',
                                reversescale= True,
                                color=[],
                                size= [],
                                colorbar=dict(
                                    thickness=15,
                                    title='Node Connections',
                                    xanchor='left',
                                    titleside='right'
                                ),
                                line=dict(width=2)))
    
    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    
    
    
    # Create edge trace:
    edge_trace = go.Scatter(
                            x=[],
                            y=[],
                            name='Edge Trace',
                            line=dict(width=0.5,color='#888'),
                            hoverinfo='none',
                            mode='lines')
    
    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    
    # Color and resize nodes by degree
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = str(adjacencies[0]) + '<br>'+'# of connections: '+str(len(adjacencies[1]))
        node_trace['text']+=tuple([node_info])
        # Use log transformation to alleviate extremely large values
        # Multiply by 3 so that small nodes are visible 
        node_trace['marker']['size']+=tuple([math.log1p(len(adjacencies[1]))*3])
        # math.log1p(x)
        # Return the natural logarithm of 1+x (base e). 
        # The result is calculated in a way which is accurate for x near zero.
    
    # Data is ready!
    data = [edge_trace, node_trace]
    
    # Set the layout 
    layout = go.Layout(
                     title = '<br>Movies and Genres Network',
                     titlefont = dict(size = 18),
                     showlegend = True,
                     legend=dict(
                        x = 0.8,
                        y = 1.065,
                        font=dict(size=12)
                     ),
                     margin = dict(b = 20, l = 10, r = 5, t = 40),
                     xaxis = dict(showgrid = False, 
                                   zeroline = False, 
                                   showticklabels = False),
                     yaxis = dict(showgrid = False, 
                                   zeroline = False, 
                                   showticklabels = False))
    # Create update menus
    updatemenus=list([
            dict(
            # Create buttons for changing node color scale
            buttons=list([
                dict(
                    args=['marker.colorscale','Jet'],
                    label='Jet',
                    method='restyle'
                ),
                dict(
                    args=['marker.colorscale','YlOrRd'],
                    label='YlOrRd',
                    method='restyle'
                ),
                dict(
                    args=['marker.colorscale','Reds'],
                    label='Reds',
                    method='restyle'
                ),
                dict(
                    args=['marker.colorscale','Picnic'],
                    label='Picnic',
                    method='restyle'
                ),  
                dict(
                    args=['marker.colorscale','Electric'],
                    label='Electric',
                    method='restyle'
                ),
                dict(
                    args=['marker.colorscale','Viridis'],
                    label='Viridis',
                    method='restyle'
                ),                       
            ]),
            direction = 'left',
            pad = {'r': 10, 't': 10},
            showactive = True,
            type = 'buttons',
            x = 0.06,
            xanchor = 'left',
            y = 1.065,
            yanchor = 'top'            
        ),
        # Create reverse color scale buttons 
        dict(
            buttons=list([   
                dict(
                    args=['marker.reversescale', True],
                    label='Reverse',
                    method='restyle'
                ),
                dict(
                    args=['marker.reversescale', False],
                    label='Undo',
                    method='restyle'
                )                    
            ]),
            direction = 'left',
            pad = {'r': 10, 't': 10},
            showactive = True,
            type = 'buttons',
            x = 0.32,
            xanchor = 'left',
            y = 1.13,
            yanchor = 'top'            
        ),
        # Create buttons for changing edge color 
        dict(
            buttons=list([   
                dict(
                    args=['line.color', 'rgba(100,90,80,0.5)'],
                    label='Gray',
                    method='restyle'
                ),
                dict(
                    args=['line.color', 'rgba(0,176,246,0.5)'],
                    label='Blue',
                    method='restyle'
                ),         
                dict(
                    args=['line.color', 'rgba(231,107,243,0.5)'],
                    label='Pink',
                    method='restyle'
                )                    
            ]),
            direction = 'left',
            pad = {'r': 10, 't': 10},
            showactive = True,
            type = 'buttons',
            x = 0.06,
            xanchor = 'left',
            y = 1.13,
            yanchor = 'top'
        )
    ])
                
    # Add annotations           
    annotations = list([
        dict(text='Node Color<br>Scale', x=0, y=1.05,xref = 'paper', yref='paper', align='left', showarrow=False),
        dict(text='Node Reverse', x=0.24, y=1.11,xref = 'paper',  yref='paper', showarrow=False),
        dict(text='Edge Color', x=0, y= 1.11, xref = 'paper', yref='paper', showarrow=False),    
    ])
        
    layout['updatemenus'] = updatemenus
    layout['annotations'] = annotations            
    # Layout is ready! 
    
    # Figure is ready!
    fig = go.Figure(data = data,layout = layout)            
    # Plot it!
    py.iplot(fig, filename = 'networkx')        

def main():
    
    df = processDF()
    plotNetwork(df)
    
if __name__ == "__main__":
    main()





















            
            
            
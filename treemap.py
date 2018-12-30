#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 23:17:17 2018

@author: ly
"""
import plotly
plotly.tools.set_credentials_file(username='LY_Air', api_key='hTbvl6jcjK4SMe6OeUZ4')

import plotly.plotly as py
import plotly.graph_objs as go
import squarify
import pandas as pd
import numpy as np
import colorlover as cl

def dataProcess():
    # Define desired clumns
    sel_cols = ['Movie_name','Movie_yr','Movie_gross']
    # Read data frame and order the column as sel_cols
    df = pd.read_csv('cleaned_data.csv', sep=',',encoding='utf-8-sig',
                     usecols =sel_cols)[sel_cols]
    # Drop duplicated tracks
    df = df.drop_duplicates(subset = 'Movie_name')
    # Fix movie gross
    # Some movie gross is 0, which actually is less than 0.01 million dollars
    # Fill movie gross = 0 with 0.01
    gross_temp = df['Movie_gross']
    gross_temp.replace(to_replace = 0, value = 0.01,inplace = True)
    df['Movie_gross'] = gross_temp
    
    return df

# Select desired subsets
def subset(df,yr):
    
    try:
        sub1 = df[df['Movie_yr'] == yr]
        sort_sub1 = sub1.sort_values(by = 'Movie_gross').reset_index()
        q = [i/10 for i in range(1,11)]
        index = pd.Series(sort_sub1.index.tolist())
        subIndex = list(np.quantile(index,q,interpolation = 'higher', axis=0))
        sub2 = sort_sub1.iloc[subIndex,[1,2,3]]
        
    except:
        print('Less than 10 movies in the selected year.')
    
    return sub2

# Normalize data use squarify    
def square(df):
    
    x = 0
    y = 0
    width = 400
    height = 400
    
    values = list(df['Movie_gross'])    
    normed = squarify.normalize_sizes(values, width, height)
    rects = squarify.squarify(normed, x, y, width, height)
    
    return rects

def addShape(rects):
    shapes = []
    counter = 0
    ryb = cl.scales['10']['div']['RdYlBu']
    for r in rects:
        shapes.append( 
            dict(
                type = 'rect', 
                x0 = r['x'], 
                y0 = r['y'], 
                x1 = r['x']+r['dx'], 
                y1 = r['y']+r['dy'],
                fillcolor = ryb[counter],
                opacity = 0.4,
                line = {
                    'width':0
                },
            ) 
        )
        counter = counter + 1
        if counter >= len(ryb):
            counter = 0
    
    return shapes

# For hover text
def addTrace(df):
    values = list(df['Movie_gross'])
    names = list(df['Movie_name'])
    rects = square(df)
    
    trace = go.Scatter(
        x = [ r['x']+(r['dx']/2) for r in rects], 
        y = [ r['y']+(r['dy']/2) for r in rects],
        mode = 'text',
        text = [ str(v) for v in values ], 
        visible = False,
        hovertext = names,
        hoverinfo = 'text',
        hoverlabel = dict(bgcolor = 'rgba(180, 180, 180,0.5)')                            
    )        

    return trace

# Add updatemenus
def addMenus(shapelist):
    updatemenus = list([
        dict(type="buttons",
             active=-1,
             buttons=list([
                dict(label = '1987',
                     method = 'update',
                     args = [{'visible': [True, False, False, False]},
                             {'title': 'Treemap for Movie Gross in 1987',
                              'shapes': shapelist[0]}
                             ]),
                dict(label = '1997',
                     method = 'update',
                     args = [{'visible': [False, True, False,False]},
                              {'title': 'Treemap for Movie Gross in 1997',
                              'shapes': shapelist[1]}
                              ]),
                dict(label = '2007',
                     method = 'update',
                     args = [{'visible': [False, False, True, False]},
                             {'title': 'Treemap for Movie Gross in 2007',
                              'shapes': shapelist[2]}
                             ]),
                dict(label = '2017',
                     method = 'update',
                     args = [{'visible': [False, False, False,True]},
                             {'title': 'Treemap for Movie Gross in 2017',
                              'shapes': shapelist[3]}
                             ])
            ]),
        )
    ])
    
    return updatemenus
# All set！
def plotTree(tracelist,shapelist):
    
    data = tracelist
    
    layout = dict(
            height=700, 
            width=700,
            xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
            yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
            hovermode='closest',
            showlegend=False,
            updatemenus=addMenus(shapelist)
            )

    figure = dict(data=data, layout=layout)
    
    py.iplot(figure, filename='squarify-treemap-interactive')

def main():
    df = dataProcess()
    # Make tree plot for 1987, 1997, 2007, 2017
    yrs = [1987,1997,2007,2017]
    dflist = [subset(df,yr) for yr in yrs]   
    tracelist = [addTrace(df) for df in dflist]
    shapelist = [addShape(square(df)) for df in dflist]
    # Plot all     
    plotTree(tracelist,shapelist)
    
if __name__ == "__main__":
    main()

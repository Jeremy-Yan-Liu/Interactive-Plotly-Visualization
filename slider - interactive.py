#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 23:46:52 2018

@author: ly
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 23:46:52 2018

@author: ly
"""

from plotly.offline import init_notebook_mode, iplot
from IPython.display import display, HTML
import pandas as pd
import os

# Please run the code in Jupyter (not Spyder) in order for the output to display
# The code below is adapted from the official tutorial of plotly in basic animation
# https://plot.ly/python/animations/

init_notebook_mode(connected=True)


def processData():
    # Change work directory
    # Please change the work directory to where you keep the cleaned_data.csv file
    os.chdir('/Users/ly/Downloads/')

    # Select desired columns
    sel_cols = ['Movie_name','Movie_yr','Movie_genre',
                'Movie_gross','Movie_runtime','Movie_rate']

    # Read data frame and order the column as sel_cols
    dataset = pd.read_csv('cleaned_data.csv', sep=',',encoding='utf-8-sig',
                     usecols =sel_cols)[sel_cols]

    # Drop duplicated movies with the same gross due to our preprocessing of movie titles in Project 1 
    dataset = dataset.drop_duplicates(subset = ['Movie_name','Movie_gross'])

    # Fix movie gross
    # Use log scale of movie gross as the size of the movie node
    # Some movie gross is 0, which actually is less than 0.01 million dollars
    # Fill movie gross = 0 with 0.01
    gross = dataset['Movie_gross']
    gross.replace(to_replace = 0, value = 0.01,inplace = True)
    dataset['Movie_gross'] = gross
    
    return dataset

def slider(dataset):
    # Get unique movie years and genres    
    years = sorted([str(yr) for yr in dataset['Movie_yr'].unique()])
    genres = list(dataset['Movie_genre'])

    # make figure
    figure = {
        'data': [],
        'layout': {},
        'frames': []
    }


    # fill in most of layout
    figure['layout']['xaxis'] = {'range': [7, 10], 'title': 'Rating'}
    figure['layout']['yaxis'] = {'title': 'Run time', 'range':[60,280],'type': 'linear'}
    figure['layout']['hovermode'] = 'closest'
    figure['layout']['sliders'] = {
        'args': [
            'transition', {
                'duration': 400,
                'easing': 'cubic-in-out'
            }
        ],
        'initialValue': years[0],
        'plotlycommand': 'animate',
        'values': years,
        'visible': True
    }
    figure['layout']['updatemenus'] = [
        {
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 500, 'redraw': False},
                             'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                    'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    ]

    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'Year:',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': []
    }


    # make data
    year = int(years[0])
    for genre in genres:
        dataset_by_year = dataset[dataset['Movie_yr'] == int(year)]
        dataset_by_year_and_movie = dataset_by_year[dataset_by_year['Movie_genre'] == genre]

        data_dict = {
            'x': list(dataset_by_year_and_movie['Movie_rate']),
            'y': list(dataset_by_year_and_movie['Movie_runtime']),
            'mode': 'markers',
            'text': list(dataset_by_year_and_movie['Movie_name']),
            'marker': {
                'sizemode': 'area',
                'sizeref': 3*max(list(dataset['Movie_gross']))/(40**3),
                'size': list(dataset_by_year_and_movie['Movie_gross'])
            },
            'name': genre
        }
        figure['data'].append(data_dict)

    # make frames
    for year in years:
        frame = {'data': [], 'name': year}
        dataset_by_year = dataset[dataset['Movie_yr'] == int(year)]
        genres = dataset_by_year['Movie_genre']
        for genre in genres: 
            dataset_by_year_and_movie= dataset_by_year[dataset_by_year['Movie_genre'] == genre]
            data_dict = {
                'x': list(dataset_by_year_and_movie['Movie_rate']),
                'y': list(dataset_by_year_and_movie['Movie_runtime']),
                'mode': 'markers',
                'text': list(dataset_by_year_and_movie['Movie_name']),
                'marker': {
                    'sizemode': 'area',
                    'sizeref': 3*max(list(dataset['Movie_gross']))/(40**2.7),
                    'size': list(dataset_by_year_and_movie['Movie_gross'])
                },
                'name': genre
            }
            frame['data'].append(data_dict)

        figure['frames'].append(frame)
        slider_step = {'args': [
            [year],
            {'frame': {'duration': 300, 'redraw': False},
             'mode': 'immediate',
           'transition': {'duration': 300}}
         ],
         'label': year,
         'method': 'animate'}
        sliders_dict['steps'].append(slider_step)



    figure['layout']['sliders'] = [sliders_dict]

    iplot(figure, {'config':{'scrollzoom': True}})

def main():
    dataset = processData()
    slider(dataset)
    
if __name__ == "__main__":
    main()

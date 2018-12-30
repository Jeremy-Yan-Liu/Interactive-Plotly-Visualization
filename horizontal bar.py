#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 19:44:29 2018

@author: ly
"""
import plotly
plotly.tools.set_credentials_file(username='LY_Air', api_key='hTbvl6jcjK4SMe6OeUZ4')

import pandas as pd 
import plotly.plotly as py
import plotly.graph_objs as go


def processDF():
    # Read data frame 
    df = pd.read_csv('cleaned_data.csv', sep=',',encoding='utf-8-sig',
                     usecols = ['Movie_genre','Movie_name','Movie_yr'])
    # Drop duplicated movie name   
    df = df.drop_duplicates(subset = 'Movie_name')

    genre = df['Movie_genre']
    year = df['Movie_yr']

    # Split genre into separate columns 
    genre_split = genre.str.split(',',expand = True)
    genre_split['yr'] = year
    genre_yr= genre_split
    
    return genre_yr

def genreCountByYr(genre_yr,yr):
    sub = genre_yr[genre_yr['yr'] == yr]
    genres = []
    for i in [0,1,2]:
        genres.extend(sub[i].tolist())
    genres = list(filter(None, genres)) 

    genres = [i.strip(' ') for i in genres]

    # Convert to series for group by and count 
    genres = pd.Series(genres)
    
    groups = genres.groupby(genres)
    
    genre_count = pd.DataFrame({'count': groups.count()})  
    
    return genre_count

def check(common_genre, dflist):
    for n in [0,2,3]:
        for i in common_genre:
            if i in list(dflist[n].index):
                continue
            else:
                print('Wrong assumption, lazy boy...')
            break
        print('Pass, lucky guy!')
  
def countAcrossYr(common_genre, dflist):
    counts= []
    for n in range(4):
        count = []
        for genre in common_genre:       
            count.append(dflist[n].loc[genre].at['count'])    
        counts.append(count)
    return counts
    
def addTrace(common_genre, yrs, counts):
    color = ['violet','salmon','palevioletred','red']    
    tracelist = []
    
    for i in range(4):    
        trace = go.Bar(
            y= common_genre,
            x= counts[i],
            name= yrs[i],
            orientation = 'h',
            marker = dict(
                color = color[i],
                opacity = 0.4,
                line = dict(
                    color = 'white',
                    width = 2)
            )
        )
        tracelist.append(trace)
        
    return tracelist
    
def plotBar(tracelist):
    
    data = tracelist
    layout = go.Layout(
        barmode='stack',
        title='Genre Counts Across 10-year Gap',
        xaxis=dict(
        title='Number of Movies ',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='Genres',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
    )
    
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='Horizontal Group Bar')
    
def main():
    yrs = [1987,1997,2007,2017]
    genre_yr = processDF()
    dflist = [genreCountByYr(genre_yr, yr) for yr in yrs]
    
    # A quick look of the four data frame,
    # the second one (1997) has the least genres appeared. 
    # Assume all of the genres appearing in 1997 appear
    # also in the other three years for simplification
    
    common_genre = list(dflist[1].index)
    
    # A helper function - check()
    # Check if the assumpltion is right
    check(common_genre, dflist)
    
    # Prepare counts for plot
    counts = countAcrossYr(common_genre, dflist)
    # Create a trace list
    tracelist = addTrace(common_genre, yrs, counts)
    # Plot
    plotBar(tracelist)
    
if __name__ == "__main__":
    main()    
    


    
        


    
    






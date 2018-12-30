#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 15:02:53 2018

@author: ly
"""
# Explore network structure of movie genres
# What genre tend to co-exist with others and what tend to be isolate
# etc.
import plotly
plotly.tools.set_credentials_file(username='LY_Air', api_key='hTbvl6jcjK4SMe6OeUZ4')

import pandas as pd
from igraph import *
import cairocffi
import math
import plotly.plotly as py
import plotly.graph_objs as go
import networkx as nx
import matplotlib.pyplot as plt
import community.community_louvain as community

def readDF():
    # Read in data frame 
    df = pd.read_csv('cleaned_data.csv', sep=',',encoding='utf-8-sig',
                 usecols =['Movie_name','Movie_genre'])
    # Clean movie names, remove spaces
    # Drop duplicated movie names
    df = df.drop_duplicates()
    
    genre = df['Movie_genre']
    genre_split = genre.str.split(',',expand = True)
    
    return genre_split
    
def clean(genre_split):
    '''
    This function cleans the data frame and returns a sorted genre data frame.
    '''
    clean_genre = pd.DataFrame()
    # Iterate every series to clean spaces in genre names
    for i in range(3):
        # Clean the splitted genre columns
        series = genre_split.iloc[:,i]
        for index,s in series.iteritems():
            if s is not None:
                series[index] = s.strip(' ')
        clean_genre[i] = series
    # Reset index
    clean_genre = clean_genre.reset_index().loc[:,[0,1,2]]
    # Add a new column represents counts of genres
    clean_genre['count'] = clean_genre.count(axis = 1)
    # Sort by count
    sort_genre = clean_genre.sort_values(by = ['count'])
    return sort_genre


def getEdges(sort_genre):
    '''
    This function extract edges from the sorted data frame.
    '''
    # Create a data frame as edge lists
    # For rows of length 2, directly assign as source and target
    edges = sort_genre[sort_genre['count'] == 2].loc[:,[0,1]]
    edges = edges.rename({0:'source',1:'target'}, axis = 'columns')

    # For rows of length 3, iterate over every two-two combinations 
    # of the three columns, order ignored
    triple = sort_genre[sort_genre['count'] == 3]
    
    edges = edges.append(triple.loc[:,[0,1]].rename({0:'source',1:'target'}, axis = 'columns'),ignore_index=True)
    edges = edges.append(triple.loc[:,[1,2]].rename({1:'source',2:'target'}, axis = 'columns'),ignore_index=True)
    edges = edges.append(triple.loc[:,[0,2]].rename({0:'source',2:'target'}, axis = 'columns'),ignore_index=True)


    # Check if rows of length 1, i.e., genres appear as singleton, all exist in the 
    # edge list, if not, add to the edge list with targe as None
    singleton = sort_genre[sort_genre['count'] == 1].loc[:,0]
    for single in singleton.unique():
        if single in list(edges['source']):
           # print('Already in source.')
           pass
        elif single in list(edges['target']):
           # print('Already in target.')
           pass
        else:
            edges.append(pd.DataFrame(data={'source':[single],'target':['NA']}))
    return edges

def getEdgeDF(edges):
    '''
    This function extract weights from the edges and returns an edge data frame with
    weights as the last column.
    '''
    # Use the number of occurences of edges as the weight of an edge
    # For example, if (Action, Drama) appears thirty times, the 'connection' between
    # them are considered stronger than (Crime, Musical), which appears, say once.
    
    # Recombine the two ends of all edges
    edges['edge'] = edges['source'] + edges['target']
    edges['edge'] = edges.source.str.cat(edges.target, sep=',') 

    # Create an edge set containing all distinct edges. The order is ignored.      
    edgeSet = set()
    edgeList = []
    for e in edges['edge']:
        frozen = frozenset(tuple(e.split(',')))
        edgeList.append(frozen)
        if frozen not in edgeSet:
            edgeSet.add(frozen)
    # Create an edge dictionary with edges as keys and the counts/weights
    # as the values
    edgeDict = {}
    for edge in edgeSet:
        count = 0
        for i in range(len(edgeList)):
            if edgeList[i] == edge:
                count += 1
        edgeDict[edge] = count

    # Create a data frame of edges and weights
    sum(edgeDict.values())
    source = []
    target = []
    weight = []            
    for key,value in edgeDict.items():
         source.append(list(key)[0])
         target.append(list(key)[1])
         weight.append(value)
    edgeDF = pd.DataFrame({'source': source,
                           'target': target,
                           'weight': weight})
         
    return edgeDF

def basicAnlyIgraph(edgeDF):
    tuples = [tuple(x) for x in edgeDF.values]
    G = Graph.TupleList(tuples, directed = False, edge_attrs = ['weight'])

    # Tips for igraph plotting:
    # if TypeError: plotting not available:
    #   then please install cairocffi or pycairo for plotting 
    # if AttributeError: 'bytes' object has no attribute 'encode':
    #   then please follow the link below
    # 'https://github.com/igraph/python-igraph/commit/
    # 8864b46849b031a3013764d03e167222963c0f5d' 
    # to manually change the file
    # in digraph/drawing/__init__.py
    
    # The analysis below follows the framework of the network cheatsheet given
    # by Dr. Lisa Singh
    
    ####### VISUALIZE NETWORK
    # Draw the network with kk layout
    plot(G,layout = G.layout('kk'))

    ####### COMPUTE & PRINT NETWORK STATS
    # Prints summary information about the graph
    print(summary(G))
    print('')

    # Print the degree of each node
    print("Node Degree：")
    print(G.degree())
    print('')
    print("Node Degree Distribution：")
    print(G.degree_distribution())
    print('')

    # Compute and print number of nodes and edges
    print("Number of nodes:", G.vcount())
    print("Number of edges:", G.ecount())
    # Confirm the graph is weighted
    print('Weighted? ' + str(G.is_weighted()))
    print('')

    # Calculates the vertex connectivity of the graph 
    print('The minimal vertex connectivity over all vertex pairs of G is:',
          G.vertex_disjoint_paths())
    # Calculates the edge connectivity of the graph
    print('The minimal edge connectivity over all vertex pairs of G is:',
           G.edge_disjoint_paths())
    print('')

    # Compute betweeness and then store the value with each node in the networkx graph
    print("Betweeness of the first 5 edges:")
    print(G.edge_betweenness()[:5])
    # Find edges which have the highest betweenness
    ebs = G.edge_betweenness()
    max_eb = max(ebs)
    print("The edge with the highest betweenness:")
    print([G.es[idx].tuple for idx, eb in enumerate(ebs) if eb == max_eb])
    print('')

    # Calculate density and print it out
    print("Density: ")
    print(round(G.density(),3))
    print('')
    print("Diameter: ")
    print(round(G.diameter(),3))
    print('')

    # Compute the number of triangles
    # Seems no defined function for compute the triangles
    # Follow Tamas's answer on stackoverflow,
    # define a triangle function using graph.cliques()
    # https://stackoverflow.com/questions/34219481/python-igraph-finding-number-of-triangles-for-each-vertex
    # A “triangle” is a set of three vertices that are mutually adjacent in a graph.
    
    # Brutal force approach
    def triangles(g):
        # Cliques are fully connected subgraphs of a graph.
        cliques = g.cliques(min=3, max=3)
        # cliques is a list of tuples of length 3
        # Initialize a list of the number of vertices
        result = [0] * g.vcount()
        # Initialize a dictionary 
        triangle = {}
        # Iterate over all triangles
        # If a vertice is one fo the three vertices of a triangle,
        # its number of triangles increases 1
        for i, j, k in cliques:
            result[i] += 1
            result[j] += 1
            result[k] += 1
        for idx, val in enumerate(result):
            triangle[idx] = val
        return triangle
    
    print('Vertice Triangles Pairs:')
    print(triangles(G))
    print('The total number of triangles is:', len(G.cliques(min=3, max=3)))
    print('')


    # Visualize the graph again with circular layout；
    # the width of the edges represent the weights (log scale)
    visual_style = {}
    visual_style["vertex_size"] = G.degree()
    visual_style["vertex_color"] = 'green'
    visual_style["vertex_label"] = G.vs["name"]
    visual_style["vertex_label_size"] = G.degree()
    visual_style["vertex_label_color"] = 'black'
    visual_style["edge_color"] = "skyblue"
    visual_style["edge_width"] = [math.log1p(w) for w in G.es["weight"]]
    visual_style["layout"] = G.layout('circular')
    visual_style["opacity"] = 0.8
    visual_style["bbox"] = (600, 600)
    visual_style["margin"] = 40
    
    plot(G,"genre_network_igraph.png", **visual_style)
    
    return G

def clusterNx(edgeDF):

    G_nx =nx.from_pandas_edgelist(edgeDF, 
                                  source = 'source', 
                                  target = 'target',
                                  edge_attr = 'weight')
    
    # Clustering
    # Conduct modularity clustering
    partition = community.best_partition(G_nx)
    
    # Print clusters (You will get a list of each node with the cluster you are in)
    print();
    print("Clusters")
    print(partition)
    print('')
    # Determine the final modularity value of the network
    modValue = community.modularity(partition,G_nx)
    print("Modularity:", modValue)
    print('')
    # Get the values for the clusters and select the node color based on the cluster value
    values = [partition.get(node) for node in G_nx.nodes()]
    plt.figure(3,figsize=(10,10)) 
    nx.draw_circular(G_nx, 
                     cmap = plt.get_cmap('Set3'), 
                     node_color = values, 
                     node_size=[20*G_nx.degree(v) for v in G_nx], 
                     font_size = 14,
                     with_labels=True,
                     style = 'solid',
                     width = [math.log1p(d['weight']) for (u,v,d) in G_nx.edges(data= True)],
                     edge_color = 'grey',
                     alpha = 0.8)
    plt.savefig("Genre Network NX.png", format="PNG")
    plt.show()


def plotlyViz(G):
    # Reference:
    # https://plot.ly/python/3d-network-graph/
    N = G.vcount()
    # Speficy a layout
    layt=G.layout("sphere")
    
    
    Xn=[layt[k][0] for k in range(N)]# x-coordinates of nodes
    Yn=[layt[k][1] for k in range(N)]# y-coordinates
    Zn=[layt[k][2] for k in range(N)]# z-coordinates
    
    
    Xe=[]
    Ye=[]
    Ze=[]
    
    for e in G.es:
        Xe+=[layt[e.tuple[0]][0],layt[e.tuple[1]][0], None]# x-coordinates of edge ends
        Ye+=[layt[e.tuple[0]][1],layt[e.tuple[1]][1], None]# y-coordinates of edge ends
        Ze+=[layt[e.tuple[0]][2],layt[e.tuple[1]][2], None]# z-coordinates of edge ends
    
    
    # Edge trace
    edge_trace=go.Scatter3d(x=Xe,
                   y=Ye,
                   z=Ze,
                   mode='lines',
                   line=dict(
                             color= 'limegreen',
                             width=2),
                   text = G.es['weight'],
                   hoverinfo= 'text'
                   )
    
    # Node trace
    node_trace=go.Scatter3d(x=Xn,
                   y=Yn,
                   z=Zn,
                   mode='markers+text',
                   text = G.vs['name'],
                   textfont=dict(
                            family='sans serif',
                            size=[i*1.5 for i in G.degree()],
                            color='black'
                        ),
                   name='genre',
                   marker=dict( symbol='circle',
                                 size= [i*3 for i in G.degree()],
                                 color = 'green',
                                 opacity = 0.7
                                 #line=dict(color='rgba(50,50,50,0.5)', width=0.5)
                                 ),
                   hoverinfo= 'skip'
                   )
    
    axis=dict(showbackground=False,
              showline=False,
              zeroline=False,
              showgrid=False,
              showticklabels=False,
              title='',
              showspikes=False
              )
    
    layout = go.Layout(
             title="Genre Network",
             titlefont=dict(
                            family='sans serif',
                            size=36,
                            color='black'
                        ),
             width=1000,
             height=1000,
             showlegend=False,
             scene=dict(
                 xaxis=dict(axis),
                 yaxis=dict(axis),
                 zaxis=dict(axis),
                 ),
            hovermode='closest'
            )
    
    data = [node_trace, edge_trace]
    fig=go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='Genre Network')
    
def main():
    
    ## Data Cleaning
    
    # Read in data
    df = readDF()
    # Data cleaning
    sorted_genre = clean(df)
    # Extract edges
    edges = getEdges(sorted_genre)
    # Create a data frame of edges and weights
    edgeDF = getEdgeDF(edges)
    
    ## Network Analysis
    
    # Conduct basic analysis with igraph
    G = basicAnlyIgraph(edgeDF)
    # Clustering analysis with networkx
    clusterNx(edgeDF)
    # 3D-Visualize with plotly
    plotlyViz(G)

if __name__ == "__main__":
    main()      
    


  
    
    
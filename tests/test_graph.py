"""
test_graph: unit tests for Hybrid
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses

import sourdough


def test_graph():
    # Tests adjacency matrix constructor
    matrix = [[0, 0, 1], [1, 0, 0], [0, 0, 0]]
    names = ['scorpion', 'frog', 'river']
    graph = sourdough.Graph.from_matrix(
        matrix = matrix, 
        names = names)
    assert 'scorpion' in graph['frog']
    assert 'river' not in graph['frog']
    # Tests adjacency list constructor
    adjacency = {'grumpy': ['sleepy'],
                 'doc': [],
                 'sneezy': ['grumpy', 'bashful']}
    graph = sourdough.Graph.from_adjacency(adjacency = adjacency)
    assert 'sleepy' in graph['grumpy']
    assert 'bashful' in graph['sneezy']
    assert 'bashful' not in graph['doc']
    # Tests edge list constructor
    edges = [('camera', 'woman'), 
             ('camera', 'man'), 
             ('person', 'man'), 
             ('tv', 'person')]
    graph_edges = sourdough.Graph.from_edges(edges = edges)
    assert 'woman' in graph_edges['camera']
    assert 'man' in graph_edges['camera']
    assert 'tv' not in graph_edges['person']
    # Tests manual construction
    graph = sourdough.Graph()
    graph.add_node('bonnie')
    graph.add_node('clyde')
    graph.add_node('butch')
    graph.add_node('sundance')
    graph.add_node('henchman')
    graph.add_edge('bonnie', 'clyde')
    graph.add_edge('butch', 'sundance')
    graph.add_edge('bonnie', 'henchman')
    graph.add_edge('sundance', 'henchman')
    assert 'clyde' in graph['bonnie']
    assert 'henchman' in graph ['bonnie']
    assert 'henchman' not in graph['butch']
    # Tests searches and paths
    # depth_search = graph.search()
    # assert depth_search == ['bonnie', 'clyde', 'henchman']
    # breadth_search = graph.search(depth_first = False)
    # print(breadth_search)
    # assert breadth_search == ['clyde', 'bonnie', 'henchman']
    all_paths = graph.paths
    assert all_paths == [['bonnie', 'clyde'], 
                         ['bonnie', 'henchman'], 
                         ['butch', 'sundance', 'henchman']]
    graph.combine(graph = graph_edges)
    print(graph)
    print(graph.endpoints)
    print(graph.paths)
    return


if __name__ == '__main__':
    test_graph()
    
import networkx as nx

def minimum_spanning_tree(graph):
    mst = nx.minimum_spanning_tree(graph)
    return mst

def odd_degree_vertices(mst):
    odd_vertices = [v for v, degree in mst.degree() if degree % 2 != 0]
    return odd_vertices

def minimum_weight_matching(graph, odd_vertices):
    subgraph = graph.subgraph(odd_vertices)
    matching = nx.max_weight_matching(subgraph, maxcardinality=True)
    return matching

def eulerian_circuit(graph):
    eulerian_circuit = list(nx.eulerian_circuit(graph))
    return eulerian_circuit

def christofides_tsp(graph):

    mst = minimum_spanning_tree(graph)

    odd_vertices = odd_degree_vertices(mst)

    matching = minimum_weight_matching(graph, odd_vertices)

    multigraph = nx.MultiGraph()
    multigraph.add_edges_from(mst.edges())
    multigraph.add_edges_from(matching)

    eulerian_circuit_edges = eulerian_circuit(multigraph)

    tour = []
    tour_weight = 0

    for edge in eulerian_circuit_edges:
        tour.append(edge[0])
        tour_weight += graph[edge[0]][edge[1]]['weight']

    tour.append(eulerian_circuit_edges[-1][1])

    return tour, tour_weight

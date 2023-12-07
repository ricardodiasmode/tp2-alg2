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

    # Passo 1: Calcular a MST
    mst = minimum_spanning_tree(graph)

    # Passo 2: Encontrar vértices de grau ímpar na MST
    odd_vertices = odd_degree_vertices(mst)

    # Passo 2: Calcular um matching perfeito de peso mínimo
    matching = minimum_weight_matching(graph, odd_vertices)

    # Passo 3: Criar multigrafo com vértices de G e arestas de M e T
    multigraph = nx.MultiGraph()
    multigraph.add_edges_from(mst.edges())
    multigraph.add_edges_from(matching)

    # Passo 3: Calcular um circuito euleriano em G'
    eulerian_circuit_edges = eulerian_circuit(multigraph)

    # Passo 4: Eliminar vértices duplicados
    tour = []
    for edge in eulerian_circuit_edges:
        tour.append(edge[0])
    tour.append(eulerian_circuit_edges[-1][1])

    return tour

import time
import networkx as nx

max_execution_time = 30 * 60


class MaxExecTime(Exception):
    pass


def approx_tsp_tour(G, c):
    initial_exec_time = time.time()

    root = list(G.nodes())[0]
    T = nx.minimum_spanning_tree(G, algorithm='prim', weight=c)
    H, path_length = preorder_walk(T, root, initial_exec_time, G, c)

    return H, path_length


def preorder_walk(tree, root, initial_exec_time, G, c):
    def dfs(v, visited, in_initial_exec_time, path_length):
        visited.append(v)
        for neighbor in tree.neighbors(v):
            current_time = time.time() - in_initial_exec_time
            if current_time > max_execution_time:
                raise MaxExecTime("Max execution time reached")

            if neighbor not in visited:
                edge_weight = G[v][neighbor][c]
                path_length[0] += edge_weight  # Atualiza o valor da lista

                dfs(neighbor, visited, in_initial_exec_time, path_length)

        return visited

    path_length = [0]  # Use uma lista para passar por referência
    visited_nodes = dfs(root, [], initial_exec_time, path_length)

    return visited_nodes, path_length[0]  # Retorna o primeiro (e único) elemento da lista


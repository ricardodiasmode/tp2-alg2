import time
import networkx as nx

max_execution_time = 60 * 30


class MaxExecTime(Exception):
    pass


def approx_tsp_tour(G, c):
    initial_exec_time = time.time()

    # Step 1: Select a vertex r in G.V to be a "root" vertex
    root = list(G.nodes())[0]

    # Step 2: Compute a minimum spanning tree T for G from root r using MST-Prim
    T = nx.minimum_spanning_tree(G, algorithm='prim', weight=c)

    # Step 3: Let H be a list of vertices, ordered according to a preorder tree walk of T
    H = preorder_walk(T, root, initial_exec_time)

    # Step 4: Return the Hamiltonian cycle
    return H


def preorder_walk(tree, root, initial_exec_time):
    # Helper function for preorder tree walk
    def dfs(v, visited, in_initial_exec_time):
        visited.append(v)
        for neighbor in tree.neighbors(v):
            current_time = time.time() - in_initial_exec_time
            if current_time > max_execution_time:
                raise MaxExecTime("Max execution time reached")

            if neighbor not in visited:
                dfs(neighbor, visited, in_initial_exec_time)

        return visited

    # Perform preorder tree walk starting from the root
    visited_nodes = dfs(root, [], initial_exec_time)

    # Return the Hamiltonian cycle
    return visited_nodes

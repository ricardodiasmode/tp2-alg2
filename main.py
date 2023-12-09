import math
import time

import networkx as nx
import pandas as pd
import multiprocessing
import branch_and_bound
import christofides
import twice_around_the_tree
import matplotlib.pyplot as plt


def read_tp_datasets(path_file):
    with open(path_file, 'r') as file:
        lines = file.readlines()
    return lines


def read_dataset(dataset_name):

    def convert_to_int(value):
        return int(float(value))

    dataset_path = f'data/{dataset_name}.tsp'
    graph = []

    with open(dataset_path, 'r') as arquivo:
        lines = arquivo.readlines()
        coord_section = False
        coords = {}

        for every_line in lines:
            part = every_line.split()

            if len(part) > 0:
                if part[0] == 'NODE_COORD_SECTION':
                    coord_section = True
                elif part[0] == 'EOF':
                    coord_section = False
                elif coord_section:
                    node, x, y = map(convert_to_int, part)
                    coords[node] = (x, y)

    for u, pos_u in coords.items():
        node_row = []
        for v, pos_v in coords.items():
            if u != v:
                distance = ((pos_u[0] - pos_v[0]) ** 2 + (pos_u[1] - pos_v[1]) ** 2) ** 0.5
                node_row.append(distance)
            else:
                node_row.append(-1)
        graph.append(node_row)

    return graph, coords


def plot_and_save_graph(coords, graph, cycle, path_to_save):
    positions = {i: (coords[i+1][0], coords[i+1][1]-1) for i in graph.nodes}

    edges_to_plot = [(cycle[i], cycle[i+1]) for i in range(len(cycle)-1)]
    edges_to_plot.append((cycle[-1], cycle[0]))

    plt.clf()

    nx.draw(graph, pos=positions, edgelist=edges_to_plot, with_labels=True, font_weight='light',
            node_size=int(math.log(19000 - len(positions))*3), node_color='skyblue', font_size=6)

    plt.savefig(path_to_save)


def add_line_on_file(line_to_add, path):
    with open(path, 'a') as file:
        file.write(f'{line_to_add}\n')


tp_datasets = read_tp_datasets('tp2_datasets.txt')
tp_datasets.pop(0)

# Branch and bound
for line in tp_datasets:
    dataset_name = line.split('\t')[0]
    print("Lendo: " + dataset_name + " e aplicando branch and bound...")
    G, coord = read_dataset(dataset_name)

    bb_class = branch_and_bound.branch_and_bound(len(G))

    try:
        before = time.time()
        bb_class.TSP(G)
        after = time.time()
        timelapse = after - before
        print("Minimum cost :", bb_class.final_res)
        print("Path Taken : ", bb_class.final_path)
        plot_and_save_graph(coord, G, bb_class.final_path, f'plots/bb/{dataset_name}')
        add_line_on_file(dataset_name + ": " + "qualidade=" + str(bb_class.final_res) + ", tempo decorrido=" + str(timelapse),
                                f'plots/bb/Success.txt')
    except branch_and_bound.MaxExecTime as err:
        print(err)
        add_line_on_file(dataset_name, f'plots/bb/NA.txt')

# Twice-Around-The-Tree
for line in tp_datasets:
    dataset_name = line.split('\t')[0]
    print("Lendo: " + dataset_name + " e aplicando twice-around-the-tree...")
    grafo_do_dataset, coordenadas = read_dataset(dataset_name)
    adjacency_matrix = pd.DataFrame(grafo_do_dataset)
    G = nx.from_pandas_adjacency(adjacency_matrix)

    try:
        before = time.time()
        hamiltonian_cycle, path_len = twice_around_the_tree.approx_tsp_tour(G, 'weight')
        after = time.time()
        timelapse = after - before

        print("Approximate Hamiltonian Cycle:", hamiltonian_cycle)
        plot_and_save_graph(coordenadas, G, hamiltonian_cycle, f'plots/tatt/{dataset_name}')
        add_line_on_file(dataset_name + ": " + "qualidade=" + str(path_len) + ", tempo decorrido=" + str(timelapse),
                                f'plots/tatt/Success.txt')
    except twice_around_the_tree.MaxExecTime as err:
        print(err)
        add_line_on_file(dataset_name, f'plots/tatt/NA.txt')


# Christofides
def main(queue, G):
    tour, tour_weight = christofides.christofides_tsp(G)

    # Enviar o resultado para a fila
    queue.put([tour, tour_weight])


if __name__ == "__main__":
    for line in tp_datasets:
        dataset_name = line.split('\t')[0]
        print("Lendo: " + dataset_name + " e aplicando Christofides...")
        grafo_do_dataset, coord = read_dataset(dataset_name)
        adjacency_matrix = pd.DataFrame(grafo_do_dataset)
        G = nx.from_pandas_adjacency(adjacency_matrix)

        # Criar uma fila para comunicação entre processos
        result_queue = multiprocessing.Queue()

        before = time.time()
        p = multiprocessing.Process(target=main, args=(result_queue, G))
        p.start()

        # Esperar por 30 minutos ou até que o processo termine
        p.join(30 * 60)

        # Se o processo ainda estiver ativo
        if p.is_alive():
            # Terminar - pode não funcionar se o processo estiver travado permanentemente
            p.terminate()
            p.join()

        after = time.time()
        timelapse = after - before

        # Recuperar o resultado da fila
        if not result_queue.empty():
            tour_result = result_queue.get()
            print("Tour aproximado: ", tour_result[0])
            plot_and_save_graph(coord, G, tour_result[0], f'plots/christofides/{dataset_name}')
            add_line_on_file(dataset_name + ": " + "qualidade=" + str(tour_result[1]) + ", tempo decorrido=" + str(timelapse),
                                    f'plots/christofides/Success.txt')
        else:
            print("Max execution time reached.")
            add_line_on_file(dataset_name, f'plots/christofides/NA.txt')

import math

import networkx as nx
import pandas as pd
import multiprocessing
import branch_and_bound
import christofides
import twice_around_the_tree
import matplotlib.pyplot as plt


def ler_tp_datasets(arquivo_path):
    with open(arquivo_path, 'r') as arquivo:
        linhas = arquivo.readlines()
    return linhas


def ler_dataset(nome_dataset):

    def convert_to_int(valor):
        return int(float(valor))

    caminho_dataset = f'data/{nome_dataset}.tsp'
    grafo = []

    with open(caminho_dataset, 'r') as arquivo:
        linhas = arquivo.readlines()
        coord_section = False
        coordenadas = {}

        for linha in linhas:
            partes = linha.split()

            if len(partes) > 0:
                if partes[0] == 'NODE_COORD_SECTION':
                    coord_section = True
                elif partes[0] == 'EOF':
                    coord_section = False
                elif coord_section:
                    no, x, y = map(convert_to_int, partes)
                    coordenadas[no] = (x, y)

    # Adicionar nós e arestas ao grafo
    for u, pos_u in coordenadas.items():
        node_row = []
        for v, pos_v in coordenadas.items():
            if u != v:
                distance = ((pos_u[0] - pos_v[0]) ** 2 + (pos_u[1] - pos_v[1]) ** 2) ** 0.5
                node_row.append(distance)
            else:
                node_row.append(-1)
        grafo.append(node_row)

    return grafo, coordenadas


def plotar_grafo_com_pesos(coord, grafo, cycle, caminho_salvar):
    posicoes = {i: (coord[i+1][0], coord[i+1][1]-1) for i in grafo.nodes}

    arestas_a_plotar = [(cycle[i], cycle[i+1]) for i in range(len(cycle)-1)]
    arestas_a_plotar.append((cycle[-1], cycle[0]))

    plt.clf()  # Limpar a figura anterior

    nx.draw(grafo, pos=posicoes, edgelist=arestas_a_plotar, with_labels=True, font_weight='light',
            node_size=int(math.log(19000 - len(posicoes))*3), node_color='skyblue', font_size=6)

    plt.savefig(caminho_salvar)


def adicionar_linha_arquivo(label, caminho):
    # Abre o arquivo no modo de escrita ('a' para adicionar ao final do arquivo)
    with open(caminho, 'a') as arquivo:
        # Escreve a linha no formato "{label}"
        arquivo.write(f'{label}\n')


tp_datasets = ler_tp_datasets('tp2_datasets.txt')
tp_datasets.pop(0)

# Branch and bound
for line in tp_datasets:
    dataset_name = line.split('\t')[0]
    print("Lendo: " + dataset_name + " e aplicando branch and bound...")
    G, coord = ler_dataset(dataset_name)

    bb_class = branch_and_bound.branch_and_bound(len(G))

    try:
        bb_class.TSP(G)
        print("Minimum cost :", bb_class.final_res)
        print("Path Taken : ", bb_class.final_path)
        plotar_grafo_com_pesos(coord, G, bb_class.final_path, f'plots/bb/{dataset_name}')
        adicionar_linha_arquivo(dataset_name + ": " + str(bb_class.final_path), f'plots/bb/Success.txt')
    except branch_and_bound.MaxExecTime as err:
        print(err)
        adicionar_linha_arquivo(dataset_name, f'plots/bb/NA.txt')

# Twice-Around-The-Tree
for line in tp_datasets:
    dataset_name = line.split('\t')[0]
    print("Lendo: " + dataset_name + " e aplicando twice-around-the-tree...")
    grafo_do_dataset, coordenadas = ler_dataset(dataset_name)
    adjacency_matrix = pd.DataFrame(grafo_do_dataset)
    G = nx.from_pandas_adjacency(adjacency_matrix)

    try:
        hamiltonian_cycle = twice_around_the_tree.approx_tsp_tour(G, 'weight')
        print("Approximate Hamiltonian Cycle:", hamiltonian_cycle)
        plotar_grafo_com_pesos(coordenadas, G, hamiltonian_cycle, f'plots/tatt/{dataset_name}')
        adicionar_linha_arquivo(dataset_name + ": " + str(hamiltonian_cycle), f'plots/tatt/Success.txt')
    except twice_around_the_tree.MaxExecTime as err:
        print(err)
        adicionar_linha_arquivo(dataset_name, f'plots/tatt/NA.txt')


# Christofides
def main(queue, G):
    tour = christofides.christofides_tsp(G)

    # Enviar o resultado para a fila
    queue.put(tour)


if __name__ == "__main__":
    for line in tp_datasets:
        dataset_name = line.split('\t')[0]
        print("Lendo: " + dataset_name + " e aplicando Christofides...")
        grafo_do_dataset, coord = ler_dataset(dataset_name)
        adjacency_matrix = pd.DataFrame(grafo_do_dataset)
        G = nx.from_pandas_adjacency(adjacency_matrix)

        # Criar uma fila para comunicação entre processos
        result_queue = multiprocessing.Queue()

        p = multiprocessing.Process(target=main, args=(result_queue, G))
        p.start()

        # Esperar por 30 minutos ou até que o processo termine
        p.join(30 * 60)

        # Se o processo ainda estiver ativo
        if p.is_alive():
            # Terminar - pode não funcionar se o processo estiver travado permanentemente
            p.terminate()
            p.join()

        # Recuperar o resultado da fila
        if not result_queue.empty():
            tour_result = result_queue.get()
            print("Tour aproximado: ", tour_result)
            plotar_grafo_com_pesos(coord, G, tour_result, f'plots/christofides/{dataset_name}')
            adicionar_linha_arquivo(dataset_name + ": " + str(tour_result), f'plots/christofides/Success.txt')
        else:
            print("Max execution time reached.")
            adicionar_linha_arquivo(dataset_name, f'plots/christofides/NA.txt')

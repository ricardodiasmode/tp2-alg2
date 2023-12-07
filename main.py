import networkx as nx
import pandas as pd
import multiprocessing
import branch_and_bound
import christofides
import twice_around_the_tree


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
                node_row.append(0)
        grafo.append(node_row)

    return grafo


tp_datasets = ler_tp_datasets('tp2_datasets.txt')
tp_datasets.pop(0)

# Branch and bound
# for line in tp_datasets:
#     print("Lendo: " + line.split('\t')[0] + " e aplicando branch and bound...")
#     grafo_do_dataset = ler_dataset(line.split('\t')[0])
#
#     bb_class = branch_and_bound.branch_and_bound(len(grafo_do_dataset))
#
#     try:
#         bb_class.TSP(grafo_do_dataset)
#         print("Minimum cost :", bb_class.final_res)
#         print("Path Taken : ", end=' ')
#         for i in range(bb_class.N + 1):
#             print(bb_class.final_path[i], end=' ')
#     except branch_and_bound.MaxExecTime as err:
#         print(err)

# Twice-Around-The-Tree
# for line in tp_datasets:
#     print("Lendo: " + line.split('\t')[0] + " e aplicando twice-around-the-tree...")
#     grafo_do_dataset = ler_dataset(line.split('\t')[0])
#     adjacency_matrix = pd.DataFrame(grafo_do_dataset)
#     G = nx.from_pandas_adjacency(adjacency_matrix)
#
#     try:
#         hamiltonian_cycle = twice_around_the_tree.approx_tsp_tour(G, 'weight')
#         print("Approximate Hamiltonian Cycle:", hamiltonian_cycle)
#     except twice_around_the_tree.MaxExecTime as err:
#         print(err)


# Christofides
def main(queue, G):
    tour = christofides.christofides_tsp(G)

    # Enviar o resultado para a fila
    queue.put(tour)


if __name__ == "__main__":
    for line in tp_datasets:
        print("Lendo: " + line.split('\t')[0] + " e aplicando Christofides...")
        grafo_do_dataset = ler_dataset(line.split('\t')[0])
        adjacency_matrix = pd.DataFrame(grafo_do_dataset)
        G = nx.from_pandas_adjacency(adjacency_matrix)

        # Criar uma fila para comunicação entre processos
        result_queue = multiprocessing.Queue()

        p = multiprocessing.Process(target=main, args=(result_queue, G))
        p.start()

        # Esperar por 10 segundos ou até que o processo termine
        p.join(10)

        # Se o processo ainda estiver ativo
        if p.is_alive():
            # Terminar - pode não funcionar se o processo estiver travado permanentemente
            p.terminate()
            p.join()

        # Recuperar o resultado da fila
        if not result_queue.empty():
            tour_result = result_queue.get()
            print("Tour aproximado: ", tour_result)
        else:
            print("Max execution time reached.")

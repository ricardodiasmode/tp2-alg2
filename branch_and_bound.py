import time
import math
import numpy as np
import sys
sys.setrecursionlimit(10000)

maxsize = float('inf')
max_execution_time = 30 * 60


class MaxExecTime(Exception):
    pass


class branch_and_bound:
    def __init__(self, n):
        self.N = n
        self.final_path = np.empty(n + 1, dtype=int)
        self.visited = np.zeros(n, dtype=bool)
        self.final_res = maxsize

    def copy_to_final(self, curr_path):
        self.final_path[:self.N + 1] = curr_path[:]
        self.final_path[self.N] = curr_path[0]

    def first_min(self, adj, i):
        return np.min(np.delete(adj[i], i))

    def second_min(self, adj, i):
        sorted_row = np.partition(adj[i], 1)
        return sorted_row[1]

    def tsp_util(self, adj, curr_bound, curr_weight, level, curr_path):
        current_time = time.time() - self.initial_exec_time
        if current_time > max_execution_time:
            raise MaxExecTime("Max execution time reached")

        if level == self.N:
            if adj[curr_path[level - 1]][curr_path[0]] != 0:
                curr_res = curr_weight + adj[curr_path[level - 1]][curr_path[0]]
                if curr_res < self.final_res:
                    self.copy_to_final(curr_path)
                    self.final_res = curr_res
            return

        for i in range(self.N):
            current_time = time.time() - self.initial_exec_time
            if current_time > max_execution_time:
                raise MaxExecTime("Max execution time reached")

            if adj[curr_path[level - 1]][i] != 0 and not self.visited[i]:
                temp = curr_bound
                curr_weight += adj[curr_path[level - 1]][i]

                if level == 1:
                    curr_bound -= (self.first_min(adj, curr_path[level - 1]) + self.first_min(adj, i)) / 2
                else:
                    curr_bound -= (self.second_min(adj, curr_path[level - 1]) + self.first_min(adj, i)) / 2

                if curr_bound + curr_weight < self.final_res:
                    curr_path[level] = i
                    self.visited[i] = True
                    self.tsp_util(adj, curr_bound, curr_weight, level + 1, curr_path)

                curr_weight -= adj[curr_path[level - 1]][i]
                curr_bound = temp
                self.visited[i] = False

    def TSP(self, adj):
        self.initial_exec_time = time.time()
        curr_bound = 0
        curr_path = np.full(self.N + 1, -1, dtype=int)
        self.visited[0] = True
        curr_path[0] = 0

        for i in range(self.N):
            curr_bound += self.first_min(adj, i) + self.second_min(adj, i)

        curr_bound = math.ceil(curr_bound / 2)
        self.tsp_util(adj, curr_bound, 0, 1, curr_path)

        return self.final_res, self.final_path
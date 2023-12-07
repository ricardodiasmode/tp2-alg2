import time
import math

maxsize = float('inf')
max_execution_time = 1

class MaxExecTime(Exception):
    pass

class branch_and_bound:
    N = 0
    final_path = []
    visited = []
    final_res = 0

    def __init__(self, n):
        self.N = n
        self.final_path = [None] * (n + 1)
        self.visited = [False] * n
        self.final_res = maxsize

    def copyToFinal(self, curr_path):
        self.final_path[:self.N + 1] = curr_path[:]
        self.final_path[self.N] = curr_path[0]

    def firstMin(self, adj, i):
        min_val = maxsize
        for k in range(self.N):
            if adj[i][k] < min_val and i != k:
                min_val = adj[i][k]
        return min_val

    def secondMin(self, adj, i):
        first, second = maxsize, maxsize
        for j in range(self.N):
            if i == j:
                continue
            if adj[i][j] <= first:
                second = first
                first = adj[i][j]
            elif adj[i][j] <= second and adj[i][j] != first:
                second = adj[i][j]
        return second

    def TSP(self, adj):
        curr_bound = 0
        curr_path = [-1] * (self.N + 1)
        visited = [False] * self.N
        initial_exec_time = time.time()

        for i in range(self.N):
            curr_bound += (self.firstMin(adj, i) + self.secondMin(adj, i))

        curr_bound = math.ceil(curr_bound / 2)

        visited[0] = True
        curr_path[0] = 0

        stack = []
        stack.append((curr_bound, 0, 1, curr_path[:], visited[:]))

        while stack:
            curr_bound, curr_weight, level, curr_path, visited = stack.pop()

            current_time = time.time() - initial_exec_time
            if current_time > max_execution_time:
                raise MaxExecTime("Max execution time reached")

            if level == self.N:
                if adj[curr_path[level - 1]][curr_path[0]] != 0:
                    curr_res = curr_weight + adj[curr_path[level - 1]][curr_path[0]]
                    if curr_res < self.final_res:
                        self.copyToFinal(curr_path)
                        self.final_res = curr_res
                continue

            for i in range(self.N):

                current_time = time.time() - initial_exec_time
                if current_time > max_execution_time:
                    raise MaxExecTime("Max execution time reached")

                if adj[curr_path[level - 1]][i] != 0 and not visited[i]:
                    temp = curr_bound
                    curr_weight += adj[curr_path[level - 1]][i]

                    if level == 1:
                        curr_bound -= (self.firstMin(adj, curr_path[level - 1]) + self.firstMin(adj, i)) / 2
                    else:
                        curr_bound -= (self.secondMin(adj, curr_path[level - 1]) + self.firstMin(adj, i)) / 2

                    if curr_bound + curr_weight < self.final_res:
                        curr_path[level] = i
                        visited[i] = True
                        stack.append((curr_bound, curr_weight, level + 1, curr_path[:], visited[:]))

                    curr_weight -= adj[curr_path[level - 1]][i]
                    curr_bound = temp
                    visited = [False] * len(visited)
                    for j in range(level):
                        if curr_path[j] != -1:
                            visited[curr_path[j]] = True

        return self.final_res, self.final_path
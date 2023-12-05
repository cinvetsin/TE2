import math
import psutil
import cProfile
from io import StringIO
import pstats
import csv

class BranchAndBoundKnapsack:
    def __init__(self, items, W):
        self.items = items  # List of (value, weight) tuples
        self.n = len(self.items)
        self.W = W
        self.M = None
        self.best_value = None
        self.best_solution = None

    def calculate_upper_bound(self, W_prime, V_N, idx):
        items = self.items
        n = self.n
        if idx + 2 < n:
            v1, w1 = items[idx]
            v2, w2 = items[idx + 1]
            v3, w3 = items[idx + 2]

            Z_prime = V_N + (W_prime // w2) * v2
            W_double_prime = W_prime - (W_prime // w2) * w2
            U_prime = Z_prime + math.floor(W_double_prime * v3 // w3)
            U_double_prime = Z_prime + math.floor((W_double_prime + math.ceil((w2 - W_double_prime) / w1) * w1) * (v2 / w2) - math.ceil((w2 - W_double_prime) / w1) * v1)
            return max(U_prime, U_double_prime)
        else:
            return V_N

    def eliminate_dominated_items(self):
        N = list(range(self.n))
        j = 0
        while j < len(N) - 1:
            k = j + 1
            while k < len(N):
                vj, wj = self.items[N[j]]
                vk, wk = self.items[N[k]]
                if (wk // wj) * vj >= vk:
                    N.pop(k)
                elif (wj // wk) * vk >= vj:
                    N.pop(j)
                    k = len(N)
                else:
                    k += 1
            j += 1
        self.items = [self.items[i] for i in N]
        self.n = len(self.items)

    def initialize(self):
        self.eliminate_dominated_items()
        self.items = sorted(self.items, key=lambda x: x[0] / x[1], reverse=True)
        self.M = [[0 for _ in range(self.W + 1)] for _ in range(self.n)]
        self.best_solution = [0 for _ in range(self.n)]
        self.best_value = 0

        x = [0 for _ in range(self.n)]
        i = 0
        x[0] = self.W // self.items[0][1]
        V_N = self.items[0][0] * x[0]
        W_prime = self.W - self.items[0][1] * x[0]
        upper_bound = self.calculate_upper_bound(W_prime, V_N, i)
        self.best_value = V_N
        self.best_solution = x.copy()
        m = [float('inf')] * self.n

        for it in range(self.n):
            for j in range(it + 1, self.n):
                v, w = self.items[j]
                if w < m[it]:
                    m[it] = w

        return x, i, V_N, W_prime, upper_bound, m

    def develop(self, x, i, V_N, W_prime, upper_bound, m):
        while True:
            if W_prime < m[i]:
                if V_N > self.best_value:
                    self.best_value = V_N
                    self.best_solution = x.copy()
                    if self.best_value == upper_bound:
                        return x, i, V_N, W_prime, "Finish"
                return x, i, V_N, W_prime, "Backtrack"
            else:
                min_j = min((j for j in range(i + 1, self.n) if self.items[j][1] <= W_prime), default=None)
                if (min_j is None) or (V_N + self.calculate_upper_bound(W_prime, V_N, min_j) <= self.best_value):
                    return x, i, V_N, W_prime, "Backtrack"

                if self.M[i][W_prime] >= V_N:
                    return x, i, V_N, W_prime, "Backtrack"

                x[min_j] = W_prime // self.items[min_j][1]
                V_N += self.items[min_j][0] * x[min_j]
                W_prime -= self.items[min_j][1] * x[min_j]
                self.M[i][W_prime] = V_N
                i = min_j

    def backtrack(self, x, i, V_N, W_prime, m):
        while True:
            max_j = max((j for j in range(i + 1) if x[j] > 0), default=None)
            if max_j is None:
                return x, i, V_N, W_prime, "Finish"
            i = max_j
            x[i] -= 1
            V_N -= self.items[i][0]
            W_prime += self.items[i][1]
            if W_prime < m[i]:
                continue
            if V_N + math.floor(W_prime * (self.items[i + 1][0] / self.items[i + 1][1])) <= self.best_value:
                V_N -= self.items[i][0] * x[i]
                W_prime += self.items[i][1] * x[i]
                x[i] = 0
                continue
            if W_prime >= m[i]:
                return x, i, V_N, W_prime, "Develop"

    def replace_item(self, x, i, V_N, W_prime, m):
        j = i
        h = j + 1
        while True:
            if self.best_value >= V_N + math.floor(W_prime * (self.items[h][0] / self.items[h][1])):
                return x, i, V_N, W_prime, "Backtrack"
            if self.items[h][1] >= self.items[j][1]:
                if (self.items[h][1] == self.items[j][1]) or (self.items[h][1] > W_prime) or (self.best_value >= V_N + self.items[h][0]):
                    h += 1
                    continue
                self.best_value = V_N + self.items[h][0]
                self.best_solution = x.copy()
                x[h] = 1
                if self.best_value == self.calculate_upper_bound(W_prime, V_N, h):
                    return x, i, V_N, W_prime, "Finish"
                j = h
                h += 1
                continue
            else:
                if W_prime - self.items[h][1] < m[h - 1]:
                    h += 1
                    continue
                i = h
                x[i] = W_prime // self.items[i][1]
                V_N += self.items[i][0] * x[i]
                W_prime -= self.items[i][1] * x[i]
                return x, i, V_N, W_prime, "Develop"

    def branch_and_bound(self):
        x, i, V_N, W_prime, upper_bound, m = self.initialize()
        next = "Develop"

        while True:
            if next == "Develop":
                x, i, V_N, W_prime, next = self.develop(x, i, V_N, W_prime, upper_bound, m)
            if next == "Backtrack":
                x, i, V_N, W_prime, next = self.backtrack(x, i, V_N, W_prime, m)
            if next == "Finish":
                break
        return self.best_solution, self.best_value

    def solve(self):
        return self.branch_and_bound()

def load_data_from_csv(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            W = int(row['W'])
            val = eval(row['val'])
            wt = eval(row['wt'])
            yield W, val, wt

# Custom profiler function to measure execution time of main() function
def profile_main():
    input_csv_filename = 'strongly_correlated_large.csv'

    for W, val, wt in load_data_from_csv(input_csv_filename):
        items = list(zip(val, wt))
        ukp = BranchAndBoundKnapsack(items, W)

        # Measure memory usage
        process = psutil.Process()
        start_memory = process.memory_info().rss

        # Measure execution time
        solution, value = ukp.solve()

        end_memory = process.memory_info().rss
        memory_usage = end_memory - start_memory

        print(f"W: {W}")
        print(f"Items (value, weight): {list(zip(val, wt))}")
        print(f"Best value: {value}")
        print(f"Best item configuration: {solution}")
        print(f"Memory usage: {memory_usage} bytes")

if __name__ == '__main__':
    # Run your code with cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    
    profile_main()  # This will only profile the execution time of the profile_main() function
    
    profiler.disable()
    
    # Redirect the profiler output to a StringIO object
    output_stream = StringIO()
    stats = pstats.Stats(profiler, stream=output_stream)
    
    # Specify the sorting order here (cumulative)
    stats.strip_dirs().sort_stats('cumulative')
    stats.print_stats()  # Print the profiling stats
    
    # Extract the desired part of the output
    output = output_stream.getvalue()
    lines = output.split('\n')
    
    for line in lines:
        if 'function calls' in line:
            parts = line.split()  # Split the line into words
            if len(parts) >= 4:
                execution_time = parts[4] + ' ' + parts[5]  # Concatenate the time part and the unit
                print(f"Execution time: {execution_time}")
                break
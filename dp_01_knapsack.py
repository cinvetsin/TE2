import cProfile
import csv
from io import StringIO
import pstats
import psutil

def unboundedKnapsack(W, n, val, wt): 
  
    # dp[i] is going to store maximum  
    # value with knapsack capacity i. 
    dp = [0 for i in range(W + 1)] 
  
    ans = 0
  
    # Fill dp[] using above recursive formula 
    for i in range(W + 1): 
        for j in range(n): 
            if (wt[j] <= i): 
                dp[i] = max(dp[i], dp[i - wt[j]] + val[j]) 
  
    return dp[W] 

def load_data_from_csv(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            W = int(row['W'])
            val = eval(row['val'])
            wt = eval(row['wt'])
            yield W, val, wt

def profile_main():
    input_csv_filename = 'strongly_correlated_small.csv'
    for W, val, wt in load_data_from_csv(input_csv_filename):
        n = len(val) 

        # Measure memory usage
        process = psutil.Process()
        start_memory = process.memory_info().rss

        print(f"Best value: {unboundedKnapsack(W, n, val, wt)}") 

        end_memory = process.memory_info().rss
        memory_usage = end_memory - start_memory

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

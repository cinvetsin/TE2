import csv
import random

# Define sizes
sizes = {
    "example": 10,
    "small": 10**2,
    "medium": 10**3,
    "large": 10**4
}

# Function to generate strongly correlated dataset
def generate_strongly_correlated(size):
    # Generate for values and weight
    values = [random.randint(1, 10 * size) * 3 for v in range(size)]
    weight = [random.randint(1, 2 * size) * 2 for w in range(size)]

    W = 10 * size + random.randint(1, size)
    return W, values, weight

# Export datasets to CSV files
csv_files_restructured = []

if __name__ == "__main__":
    for size_key, size_value in sizes.items():
        W, val, wt = generate_strongly_correlated(size_value)
        
        # Create a list of dictionaries to represent the data
        data = [{"W": W, "val": val, "wt": wt}]
        
        # Save the data to a CSV file with separate columns for W, val, and wt
        with open(f'strongly_correlated_{size_key}.csv', 'w', newline='') as csvfile:
            fieldnames = ["W", "val", "wt"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
            
        csv_files_restructured.append(f'strongly_correlated_{size_key}.csv')

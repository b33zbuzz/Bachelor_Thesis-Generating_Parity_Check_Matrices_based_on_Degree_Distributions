import numpy as np
import random
import h5py

def generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution):
    # Accounting for the degree distribution
    degree_2_count, degree_3_count, degree_5_count, degree_6_count, degree_12_count, degree_13_count = degree_distribution
    degrees = [2] * degree_2_count + [3] * degree_3_count + [5] * degree_5_count + [6] * degree_6_count + [12] * degree_12_count + [13] * degree_13_count

    # Checking if sum of degrees matches twice the number of check nodes
    assert sum(degrees) == 3 * num_check_nodes, "The degree distribution does not match the constraints."

    # Initialize the H matrix with zeros
    H = np.zeros((num_check_nodes, num_variable_nodes), dtype=int)

    # List of all edges
    edges = [(i, j) for i in range(num_check_nodes) for j in range(3)]

    # Assign edges based on the degree distribution
    variable_node_edges = []
    for node, degree in enumerate(degrees):
        variable_node_edges.extend([node] * degree)
    
    random.shuffle(variable_node_edges)
    
    # Now assign edges from variable_node_edges to check nodes
    check_node_index = 0
    while variable_node_edges:
        if len(edges) < 3:
            raise ValueError("Not enough edges to fulfill the degree distribution.")
        
        v_node = variable_node_edges.pop()
        
        # Assign the edge to a check node ensuring each check node gets exactly 3 edges
        while True:
            if check_node_index >= num_check_nodes:
                check_node_index = 0
            c_node = check_node_index
            check_node_index += 1
            if sum(H[c_node]) < 3:
                H[c_node, v_node] = 1
                break

    return H

def save_h_matrix_to_hdf5(H, filename):
    with h5py.File(filename, "w") as f:
        f.create_dataset("H3", data=H)



# Parameters
num_variable_nodes = 499
num_check_nodes = 1000
degree_distribution = (116, 129, 96, 18, 27, 113)

# Generate the parity check matrix
H = generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution)
save_h_matrix_to_hdf5(H, "H_matrix_3.hdf5")
print("Matrix was successfully saved to hdf5 file")
import numpy as np
import random
import h5py

def generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution):
    # Accounting for the degree distribution
    degree_2_count, degree_3_count, degree_6_count, degree_10_count, degree_11_count, degree_27_count, degree_28_count = degree_distribution
    degrees = [2] * degree_2_count + [3] * degree_3_count + [6] * degree_6_count + [10] * degree_10_count + [11] * degree_11_count + [27] * degree_27_count + [28] * degree_28_count

    # Checking if sum of degrees matches twice the number of check nodes
    assert sum(degrees) == 4 * num_check_nodes, "The degree distribution does not match the constraints."

    # Initialize the H matrix with zeros
    H = np.zeros((num_check_nodes, num_variable_nodes), dtype=int)

    # List of all edges
    edges = [(i, j) for i in range(num_check_nodes) for j in range(4)]

    # Assign edges based on the degree distribution
    variable_node_edges = []
    for node, degree in enumerate(degrees):
        variable_node_edges.extend([node] * degree)
    
    random.shuffle(variable_node_edges)
    
    # Now assign edges from variable_node_edges to check nodes
    check_node_index = 0
    while variable_node_edges:
        if len(edges) < 4:
            raise ValueError("Not enough edges to fulfill the degree distribution.")
        
        v_node = variable_node_edges.pop()
        
        # Assign the edge to a check node ensuring each check node gets exactly 4 edges
        while True:
            if check_node_index >= num_check_nodes:
                check_node_index = 0
            c_node = check_node_index
            check_node_index += 1
            if sum(H[c_node]) < 4:
                H[c_node, v_node] = 1
                break

    return H

def save_h_matrix_to_hdf5(H, filename):
    with h5py.File(filename, "w") as f:
        f.create_dataset("H4", data=H)



# Parameters
num_variable_nodes = 501
num_check_nodes = 1000
degree_distribution = (109, 140, 85, 92, 6, 66, 3)

# Generate the parity check matrix
H = generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution)
save_h_matrix_to_hdf5(H, "H_matrix_4.hdf5")
print("Matrix was successfully saved to hdf5 file")
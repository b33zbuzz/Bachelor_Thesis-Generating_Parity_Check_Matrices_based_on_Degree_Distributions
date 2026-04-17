def generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution):
    
    H_left = generate_parity_check_matrix_left(num_variable_nodes, num_check_nodes, degree_distribution)

    H_right = np.zeros((num_check_nodes, num_check_nodes), dtype=int)
    for i in range(num_check_nodes):
        H_right[i, i] = 1
        if(i+1)<num_check_nodes:
            H_right[i, i+1] = 1

    H_real = np.zeros((num_check_nodes, num_variable_nodes + num_check_nodes), dtype=int)
    H_real[:, :num_variable_nodes] = H_left
    H_real[:, num_variable_nodes:] = H_right

    return H_real, H_left
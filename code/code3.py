def get_transmitted_signal(H_left, initial_signal, num_check_nodes):
    # Element-wise multiplication of the vector with every row of the matrix
    redundancy_temp = H_left * initial_signal

    # Sum up each row
    redundancy_temp2 = np.sum(redundancy_temp, axis=1) % 2

    # Calculating the parity nodes
    redundancy = np.zeros((num_check_nodes), dtype=int)

    for i in range(len(redundancy_temp2) - 1):
        redundancy[i] = (redundancy_temp2[i] + redundancy_temp2[i+1]) % 2

    redundancy[len(redundancy_temp2)-1] = redundancy_temp2[len(redundancy_temp2)-1]

    # Compiling the full message signal
    transmitted_signal = np.concatenate((initial_signal, redundancy))

    return transmitted_signal
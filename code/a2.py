import numpy as np
import random
import matplotlib.pyplot as plt

def generate_parity_check_matrix_left(num_variable_nodes, num_check_nodes, degree_distribution):
    # Accounting for the degree distribution
    degree_2_count, degree_3_count, degree_6_count = degree_distribution
    degrees = [2] * degree_2_count + [3] * degree_3_count + [6] * degree_6_count

    # Checking if sum of degrees matches twice the number of check nodes
    assert sum(degrees) == 2 * num_check_nodes, "The degree distribution does not match the constraints."

    # Initialize the H matrix with zeros
    H = np.zeros((num_check_nodes, num_variable_nodes), dtype=int)

    # List of all edges
    edges = [(i, j) for i in range(num_check_nodes) for j in range(2)]

    # Assign edges based on the degree distribution
    variable_node_edges = []
    for node, degree in enumerate(degrees):
        variable_node_edges.extend([node] * degree)
    
    random.shuffle(variable_node_edges)
    
    # Now assign edges from variable_node_edges to check nodes
    check_node_index = 0
    while variable_node_edges:
        if len(edges) < 2:
            raise ValueError("Not enough edges to fulfill the degree distribution.")
        
        v_node = variable_node_edges.pop()
        
        # Assign the edge to a check node ensuring each check node gets exactly 2 edges
        while True:
            if check_node_index >= num_check_nodes:
                check_node_index = 0
            c_node = check_node_index
            check_node_index += 1
            if sum(H[c_node]) < 2:
                H[c_node, v_node] = 1
                break

    return H

def generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution):
    # Generate the parity check matrix
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

def add_awgn(signal, snr_dB):
    snr_linear = 10**(snr_dB / 10.0)
    power_signal = np.mean(signal**2)
    noise_power = power_signal / snr_linear
    noise = np.sqrt(noise_power) * np.random.randn(*signal.shape)
    noisy_signal = signal + noise
    return noisy_signal, noise_power

def get_llr_from_initial_signal(H_left, initial_signal, snrdB, num_check_nodes):
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
    generated_signal = np.concatenate((initial_signal, redundancy))

    # Adding noise to the signal
    bpsk_signal = 2 * generated_signal - 1  # Convert to BPSK: 0 -> -1, 1 -> +1
    noisy_signal, noise_power = add_awgn(bpsk_signal, snrdB)

    # Calculate LLRs
    llr = (2 * noisy_signal) / noise_power

    return llr

def belief_propagation(H_real, received_llr, max_iterations):
    
    eps=1e-6
    M, N = H_real.shape
    # Initialize messages

    
    r = np.zeros((M, N)) # messages from check nodes to variable nodes
    q = np.zeros((M, N)) # messages from variable nodes to check nodes
    
    # Initialize q messages with received LLRs
    for m in range(M):
        for n in np.where(H_real[m])[0]:
            q[m, n] = received_llr[n]
    
    for iteration in range(max_iterations):
        # Messages sent by check node to variable node
        for m in range(M):
            for n in np.where(H_real[m])[0]:
                neighbors = np.where(H_real[m])[0]
                neighbors = neighbors[neighbors != n]
                prod = np.prod(np.tanh(q[m, neighbors] / 2))
                prod = np.clip(prod, -1 + eps, 1 - eps)
                r[m, n] = 2 * np.arctanh(prod)
        
        # Messages sent by variable node to check node
        llr_updated = np.copy(received_llr)
        for n in range(N): # for each variable node
            for m in np.where(H_real[:, n])[0]: # for each check node connected to it
                neighbors = np.where(H_real[:, n])[0]
                neighbors = neighbors[neighbors != m]
                sum = np.sum(r[neighbors, n]) + received_llr[n]
                q[m, n] = sum
                llr_updated[n] += sum
        
        # Decision
        decoded_bits = (llr_updated > 0).astype(int)
        #decoded_bits = llr_updated
        
        # Check if all parity-check equations are satisfied
        syndrome = np.mod(H_real @ decoded_bits, 2)
        #print(np.sum(syndrome))
        if np.all(syndrome == 0):
            return decoded_bits, iteration + 1
        
        # Update q messages for next iteration
        #for m in range(M):
        #    for n in np.where(H_real[m])[0]:
        #        neighbors = np.where(H_real[:, n])[0]
        #        neighbors = neighbors[neighbors != m]
        #        q[m, n] = received_llr[n] + r[neighbors, n].sum()
    
    return decoded_bits, max_iterations

# calculate ber
def calculate_ber(original_bits, decoded_bits):
    # check if both inputs are the right dimensions
    if original_bits.shape != decoded_bits.shape:
        raise ValueError("Length of original_bits and decoded_bits must be the same.")

    # calculate and return ber
    return np.sum(original_bits != decoded_bits) / len(original_bits)


def simulate_ldpc(H, H_left, initial_signal, snr_values, max_iter, num_check_nodes):
    ber = []
    avg_iterations = []

    for snr_dB in snr_values:
        llr = get_llr_from_initial_signal(H_left, initial_signal, snr_dB, num_check_nodes)
        
        # Decode the received signal
        decoded_bits, iterations = belief_propagation(H, llr, max_iter)

        # Getting the message signal from the decoded bits
        decoded_message = decoded_bits[:len(initial_signal)]

        # Calculate BER and store results
        ber_snr = calculate_ber(initial_signal, decoded_message)
        ber.append(ber_snr)
        avg_iterations.append(iterations)

        # debugging
        print(f"SNR:                  {snr_dB}")
        print(f"Number of Iterations: {iterations}")
        print(f"Bit Error Rate (BER): {ber_snr}")
    
    return ber, avg_iterations


def plot_results(snr_values, ber, avg_iterations):
    plt.figure(figsize=(12, 6))

    # BER vs SNR plot
    plt.subplot(1, 2, 1)
    plt.semilogy(snr_values, ber, marker='o')
    plt.title('BER vs SNR')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.grid(True, which='both')
    plt.xlim(-4, 11)
    plt.ylim(10e-6, 1)

    # Average Iterations vs SNR plot
    plt.subplot(1, 2, 2)
    plt.plot(snr_values, avg_iterations, marker='o')
    plt.title('Average Iterations vs SNR')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Average Iterations')
    plt.grid(True)
    plt.xlim(-4, 11)
    plt.ylim(0, 50)

    plt.tight_layout()
    plt.show()



def main():

    # Setting parameters
    num_variable_nodes = 500
    num_check_nodes = 1000
    degree_distribution = (139, 148, 213)
    snr_values = np.arange(-3, 11, 1)
    max_iter = 50

    # Generating parity check matrix
    H_real, H_left = generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution)

    # Generating initial signal
    #initial_signal = np.random.randint(0, 2, num_variable_nodes)
    initial_signal = np.zeros(num_variable_nodes, dtype=int)

    # Performing the encoding, tranmission and decoding process
    ber, avg_iterations = simulate_ldpc(H_real, H_left, initial_signal, snr_values, max_iter, num_check_nodes)

    # Plotting the results
    plot_results(snr_values, ber, avg_iterations)


if __name__ == "__main__":
    main()
import numpy as np
import random
import h5py
import matplotlib.pyplot as plt


def generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution):
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

def save_h_matrix_to_hdf5(H, filename):
    with h5py.File(filename, "w") as f:
        f.create_dataset("H2", data=H)

# Parameters
num_variable_nodes = 500
num_check_nodes = 1000
degree_distribution = (139, 148, 213)

# Generate the parity check matrix
H_left = generate_parity_check_matrix(num_variable_nodes, num_check_nodes, degree_distribution)

H_right = np.zeros((num_check_nodes, num_check_nodes), dtype=int)
for i in range(num_check_nodes):
    H_right[i, i] = 1
    if(i+1)<num_check_nodes:
        H_right[i, i+1] = 1

H_real = np.zeros((num_check_nodes, num_variable_nodes + num_check_nodes), dtype=int)
H_real[:, :num_variable_nodes] = H_left
H_real[:, num_variable_nodes:] = H_right

# Generating initial signal
# initial_signal = np.random.randint(0, 2, num_variable_nodes)
initial_signal = np.zeros(num_variable_nodes, dtype=int)

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

# 
def add_awgn(signal, snr_dB):
    snr_linear = 10**(snr_dB / 10.0)
    power_signal = np.mean(signal**2)
    noise_power = power_signal / snr_linear
    noise = np.sqrt(noise_power) * np.random.randn(*signal.shape)
    noisy_signal = signal + noise
    return noisy_signal

def bit_flipping_decode(rx, H, max_iter=50):
    VN_max = get_max_VN(H)
    iter_count = 0
    rows, cols = rx.shape

    while iter_count < max_iter:
        iter_count += 1
        for j in range(rows):
            for b, bit_pos in enumerate(VN_max):
                if b == 0:
                    count = 0
                    numberOfSets = 0
                    for z in range(H.shape[0]):
                        N = np.where(H[z, :] == 1)[0]
                        q = np.sum(rx[j, N])
                        if bit_pos in N:
                            numberOfSets += 1
                            if q % 2 != 0:
                                count += 1
                    if count > (numberOfSets / 2):
                        rx[j, bit_pos] = (rx[j, bit_pos] + 1) % 2
                else:
                    counti = 0
                    numberOfSetsi = 0
                    for z in range(H.shape[0]):
                        N = np.where(H[z, :] == 1)[0]
                        q = np.sum(rx[j, N])
                        if bit_pos in N:
                            numberOfSetsi += 1
                            if q % 2 != 0:
                                counti += 1
                    if counti > (numberOfSetsi / 2):
                        rx[j, bit_pos] = (rx[j, bit_pos] + 1) % 2

        if np.sum(np.mod(np.dot(rx, H.T), 2)) == 0:
            break
    
    return rx, iter_count

def get_max_VN(H):
    VN_degrees = np.sum(H, axis=0)
    VN_max = np.argsort(-VN_degrees)
    return VN_max

def simulate_ldpc(H, transmitted_signal, snr_values, max_iter=50):
    ber = []
    avg_iterations = []

    for snr_dB in snr_values:
        errors = 0
        total_iterations = 0
        n_trials = transmitted_signal.shape[0]

        for i in range(n_trials):
            #transmitted_signal_flat = transmitted_signal[i].flatten()
            bpsk_signal = 2 * transmitted_signal - 1
            noisy_signal = add_awgn(bpsk_signal, snr_dB)
            received_bits = (noisy_signal >= 0).astype(int)
            received_signal = received_bits.reshape(transmitted_signal.shape)

            print(f"Trial {i+1}/{n_trials}")
            print(f"Original transmitted signal shape: {transmitted_signal[i].shape}")
            print(f"Flattened and BPSK signal shape: {bpsk_signal.shape}")
            print(f"Noisy signal shape: {noisy_signal.shape}")
            print(f"Received bits shape: {received_bits.shape}")
            print(f"Reshaped received signal shape: {received_signal.shape}")

            if received_signal.ndim == 1:
                received_signal = received_signal.reshape(1, -1)

            print(received_signal.shape)
            decoded_rx, iterations = bit_flipping_decode(received_signal, H, max_iter)
            total_iterations += iterations
            errors += np.sum(decoded_rx != transmitted_signal[i])

        ber.append(errors / (transmitted_signal.size))
        avg_iterations.append(total_iterations / n_trials)

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

    # Average Iterations vs SNR plot
    plt.subplot(1, 2, 2)
    plt.plot(snr_values, avg_iterations, marker='o')
    plt.title('Average Iterations vs SNR')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Average Iterations')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# Example usage:
if __name__ == "__main__":
    

    snr_values = np.arange(-3, 11, 1)
    max_iter = 50

    ber, avg_iterations = simulate_ldpc(H_real, transmitted_signal, snr_values, max_iter)
    plot_results(snr_values, ber, avg_iterations)



# Save H matrix to HDF5 file
save_h_matrix_to_hdf5(H_real, "H_matrix_2.hdf5")
print("Matrix was successfully saved to hdf5 file")
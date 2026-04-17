import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import circulant
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import inv



def getMaxVN(H, n):
    # This function should return variable nodes with maximum connections
    degree = np.sum(H, axis=0)
    return np.argsort(degree)[::-1]

def decodeParallel1(rx, H, Hn, Hm, rK, max_iter):
    # Decode received signals using parallel decoding algorithm
    VN_max = getMaxVN(H, Hn)
    iter_count = 0

    for iter in range(max_iter):
        for j in range(rK):
            for b in range(len(VN_max)):
                bit_pos = VN_max[b]
                count = 0
                numberOfSets = 0

                for z in range(Hm):
                    N = np.where(H[z, :] == 1)[0]
                    if bit_pos in N:
                        q = np.sum(rx[j, N])
                        numberOfSets += 1
                        if q % 2 != 0:
                            count += 1

                if count > (numberOfSets / 2):
                    rx[j, bit_pos] = (rx[j, bit_pos] + 1) % 2

        if np.sum(np.mod(rx @ H.T, 2)) == 0:
            break
        iter_count += 1

    return rx, iter_count

def main():
    import matplotlib
    matplotlib.use('TkAgg')


    EbN0dB = np.arange(-3, 11, 1)
    Mod_Type = 'BPSK'
    M = 2  # 2PSK

    H = cyclgen(7, [1, 0, 1])
    H_p = np.array([
        [1, 1, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 0],
        [1, 1, 1, 0, 0, 1, 0],
        [1, 0, 1, 0, 0, 0, 1]
    ])
    

    
    nbits = Gk * 10
    max_iter = 50

    # Initialize arrays to store BER and iteration count
    BER_LDPC_Code_AWGN = np.zeros(len(EbN0dB))
    iter_count_1 = np.zeros(len(EbN0dB))

    for i in range(len(EbN0dB)):
        x = np.random.rand(nbits) > 0.5
        m = x.reshape(-1, Gk)
        cB = np.mod(m @ G, 2)
        c = cB.flatten()
        y = 2 * c - 1

        # Add AWGN to the signal
        w = (1 / np.sqrt(2 * 10**(EbN0dB[i] / 10))) * np.random.randn(len(y))
        r = y + w
        r = (r >= 0).astype(int)
        rx = r.reshape(-1, Gn)

        # Decode using parallel decoding algorithm
        rx, iter_count = decodeParallel1(rx, H, Gn, Hm=H.shape[0], rK=rx.shape[0], max_iter=max_iter)

        iter_count_1[i] = iter_count

        remove_parity = rx[:, :Gk]
        xH = remove_parity.flatten()

        # Calculate Bit Error Rate (BER)
        bit_error = np.sum(xH != x[:len(xH)])
        BER_LDPC_Code_AWGN[i] = bit_error / nbits

    plt.figure()
    plt.semilogy(EbN0dB, BER_LDPC_Code_AWGN, 'g-')
    plt.grid(True)
    plt.legend(['Parallel'])
    plt.xlabel('SNR(dB)')
    plt.ylabel('BER')
    plt.title('BER of BPSK system in (4,7) LDPC Code')

    plt.figure()
    plt.plot(EbN0dB, iter_count_1, 'g')
    plt.grid(True)
    plt.legend(['Parallel'])
    plt.xlabel('SNR(dB)')
    plt.ylabel('Iteration')
    plt.title('Number of Iterations in (7,4) LDPC Code')

    plt.show()
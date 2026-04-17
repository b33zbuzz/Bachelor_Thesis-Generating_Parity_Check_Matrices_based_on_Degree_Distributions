def add_awgn(signal, snr_dB):
    snr_linear = 10**(snr_dB / 10.0)
    power_signal = np.mean(signal**2)
    noise_power = power_signal / snr_linear
    noise = np.sqrt(noise_power) * np.random.randn(*signal.shape)
    noisy_signal = signal + noise
    return noisy_signal, noise_power

def get_noisy_signal(transmitted_signal, snrdB):
    # Adding noise to the signal
    bpsk_signal = 2 * transmitted_signal - 1  # Convert to BPSK: 0 -> -1, 1 -> +1
    noisy_signal, noise_power = add_awgn(bpsk_signal, snrdB)

    return noisy_signal, noise_power
from tx_chain import *
from rx_chain import *
from channel import *
from plotting import *
from load_config import *

PA_GAIN = 1
LNA_GAIN = 30 # dB

A = -80 # received signal attenuation dB

def zero_pad(signal, target_length):
    pad_total = target_length - len(signal)
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left

    signal_padded = np.pad(signal, (pad_left, pad_right), mode='constant')
    return signal_padded

def main():
    config = load_config("config.yaml")
    print("App name:", config["app"]["name"])

    """
    Initialise parameters from config.yaml
    """
    sample_freq = config["params"]["sample_freq"]

    # Short Pulse S1
    s1_duration = config["sband_pulses"]["S1DurationTime"]
    s1_bandwidth = config["sband_pulses"]["S1Bandwidth"]
    s1_delay_samples = config["sband_pulses"]["S1Delay"]
    s1_amplitude = config["sband_pulses"]["S1Amplitude"]
    s1_kaiser_beta = config["sband_pulses"]["S1KaiserBeta"]

    # Medium Pulse M1
    m1_duration = config["sband_pulses"]["M1DurationTime"]
    m1_bandwidth = config["sband_pulses"]["M1Bandwidth"]
    m1_delay_samples = config["sband_pulses"]["M1Delay"]
    m1_amplitude = config["sband_pulses"]["M1Amplitude"]
    m1_kaiser_beta = config["sband_pulses"]["M1KaiserBeta"]

    # Long Pulse L1
    l1_duration = config["sband_pulses"]["L1DurationTime"]
    l1_bandwidth = config["sband_pulses"]["L1Bandwidth"]
    l1_delay_samples = config["sband_pulses"]["L1Delay"]
    l1_amplitude = config["sband_pulses"]["L1Amplitude"]
    l1_kaiser_beta = config["sband_pulses"]["L1KaiserBeta"]

    # IF params
    if_freq_s1 = config["if_conversion"]["if_freq_short_pulse"]
    if_freq_m1 = config["if_conversion"]["if_freq_medium_pulse"]
    if_freq_l1 = config["if_conversion"]["if_freq_long_pulse"]

    # RF params
    rf_freq_0 = config["rf_conversion"]["rf_freq_channel_0"]

    """
    TX Chain
    """
    N_S1 = round(s1_duration * sample_freq) # HOW MANY SAMPLE POINTS?? SAMPLES = PULSE DURATION * F_SAMPLE
    N_M1 = round(m1_duration * sample_freq) # HOW MANY SAMPLE POINTS?? SAMPLES = PULSE DURATION * F_SAMPLE
    N_L1 = round(l1_duration * sample_freq) # HOW MANY SAMPLE POINTS?? SAMPLES = PULSE DURATION * F_SAMPLE

    # S1 BB Signal Generation
    s1_tx_bb = generate_baseband_signal(s1_amplitude,0,s1_bandwidth,sample_freq,N_S1) 
    #plot_power_spectrum(s1_tx_bb, N_S1, sample_freq, "S1 BB Signal")

    I = np.real(s1_tx_bb)
    Q = np.imag(s1_tx_bb)
    #plot_IQ_time_domain(I,Q,"BB S1")

    # M1 BB Signal Generation
    m1_tx_bb = generate_baseband_signal(m1_amplitude,0,m1_bandwidth,sample_freq,N_M1) 
    #plot_power_spectrum(m1_tx_bb, N_M1, sample_freq, "M1 BB Signal")

    I = np.real(m1_tx_bb)
    Q = np.imag(m1_tx_bb)
    #plot_IQ_time_domain(I,Q,"BB M1")

    # L1 BB Signal Generation
    l1_tx_bb = generate_baseband_signal(l1_amplitude,0,l1_bandwidth,sample_freq,N_L1) 
    #plot_power_spectrum(l1_tx_bb, N_L1, sample_freq, "L1 BB Signal")

    I = np.real(l1_tx_bb)
    Q = np.imag(l1_tx_bb)
    #plot_IQ_time_domain(I,Q,"BB L1")
    
    # Kaiser Window
    s1_tx_windowed = window_function(s1_tx_bb, N_S1, s1_kaiser_beta)
    #plot_power_spectrum(s1_tx_windowed, N_S1, sample_freq, "Windowed S1 BB Signal")

    I = np.real(s1_tx_windowed)
    Q = np.imag(s1_tx_windowed)
    #plot_IQ_time_domain(I,Q,"Windowed S1 BB Signal")

    m1_tx_windowed = window_function(m1_tx_bb, N_M1, m1_kaiser_beta)
    #plot_power_spectrum(m1_tx_windowed, N_M1, sample_freq, "Windowed M1 BB Signal")

    I = np.real(m1_tx_windowed)
    Q = np.imag(m1_tx_windowed)
    #plot_IQ_time_domain(I,Q,"Windowed M1 BB Signal")

    l1_tx_windowed = window_function(l1_tx_bb, N_L1, l1_kaiser_beta)
    #plot_power_spectrum(l1_tx_windowed, N_L1, sample_freq, "Windowed L1 BB Signal")

    I = np.real(l1_tx_windowed)
    Q = np.imag(l1_tx_windowed)
    #plot_IQ_time_domain(I,Q,"Windowed L1 BB Signal")

    # Upconversion to IF
    s1_tx_IF = IF_upconversion(s1_tx_windowed, N_S1, sample_freq, if_freq_s1)
    m1_tx_IF = IF_upconversion(m1_tx_windowed, N_M1, sample_freq, if_freq_m1)
    l1_tx_IF = IF_upconversion(l1_tx_windowed, N_L1, sample_freq, if_freq_l1)

    # Zero pad short pulse for plotting
    s1_tx_IF_padded = zero_pad(s1_tx_IF, len(m1_tx_IF)) # BUT ADDING SAMPLE POINTS IS CONVOLVING WITH SINC 

    plot_power_spectrum(s1_tx_IF, N_S1, sample_freq, "S1 IF Signal")
    #plot_power_spectrum(s1_tx_IF_padded, len(s1_tx_IF_padded), sample_freq, "S1 IF Signal")
    plot_power_spectrum(m1_tx_IF, N_M1, sample_freq, "M1 IF Signal")
    plot_power_spectrum(l1_tx_IF, N_L1, sample_freq, "L1 IF Signal")

    # Upconversion to RF
    s1_tx_RF = RF_upconversion(s1_tx_IF, N_S1, sample_freq, rf_freq_0)
    #plot_power_spectrum(s1_tx_RF, N_S1, sample_freq, "S1 RF Signal")

    m1_tx_RF = RF_upconversion(m1_tx_IF, N_M1, sample_freq, rf_freq_0)
    #plot_power_spectrum(m1_tx_RF, N_M1, sample_freq, "M1 RF Signal")

    l1_tx_RF = RF_upconversion(l1_tx_IF, N_L1, sample_freq, rf_freq_0)
    #plot_power_spectrum(l1_tx_RF, N_L1, sample_freq, "L1 RF Signal")

    # PA modelling
    a_in_sweep = np.linspace(0.01,10.0,200) # input amplitude sweep
    Pin_dB = []
    Pout_dB = []

    for a in a_in_sweep:
        # Scale RF input
        s_in = a * m1_tx_RF 

        # PA output
        s_out = PA_linear(s_in, PA_GAIN)

        # Power calculation
        Pin = get_real_signal_power(s_in)
        Pout = get_real_signal_power(s_out)

        # Convert to dB
        Pin_dB.append(10 * np.log10(Pin))
        Pout_dB.append(10 * np.log10(Pout))
    
    #plot_AM_AM_curve(Pin_dB, Pout_dB)

    # PA
    s1_tx = PA_linear(s1_tx_RF, PA_GAIN)
    #plot_power_spectrum(s1_tx, N_S1, sample_freq, "PA Output")

    m1_tx = PA_linear(m1_tx_RF, PA_GAIN)
    #plot_power_spectrum(m1_tx, N_M1, sample_freq, "PA Output")

    l1_tx = PA_linear(l1_tx_RF, PA_GAIN)
    #plot_power_spectrum(l1_tx, N_L1, sample_freq, "PA Output")

    """
    RX Chain
    """
    s1_rx = apply_attenuation(s1_tx, A)
    s1_rx = apply_time_delay(s1_rx, s1_delay_samples)
    #plot_power_spectrum(s1_rx, N_S1, sample_freq, "S1 Received Signal")

    m1_rx = apply_attenuation(m1_tx, A)
    m1_rx = apply_time_delay(m1_rx, m1_delay_samples)
    #plot_power_spectrum(m1_rx, N_M1, sample_freq, "M1 Received Signal")

    l1_rx = apply_attenuation(l1_tx, A)
    l1_rx = apply_time_delay(l1_rx, l1_delay_samples)
    #plot_power_spectrum(l1_rx, N_L1, sample_freq, "L1 Received Signal")

    # LNA
    s1_rx = LNA_linear(s1_rx, LNA_GAIN)
    plot_power_spectrum(s1_rx, N_S1, sample_freq, "S1 Received Signal (Post LNA)")

    m1_rx = LNA_linear(m1_rx, LNA_GAIN)
    plot_power_spectrum(m1_rx, N_M1, sample_freq, "M1 Received Signal (Post LNA)")

    l1_rx = LNA_linear(l1_rx, LNA_GAIN)
    plot_power_spectrum(l1_rx, N_L1, sample_freq, "L1 Received Signal (Post LNA)")

    # Downconversion to IF
    s1_rx_IF = RF_downconversion(s1_rx, N_S1, sample_freq, rf_freq_0)
    plot_power_spectrum(s1_rx_IF, N_S1, sample_freq, "S1 Received Signal (IF)")

    m1_rx_IF = RF_downconversion(m1_rx, N_M1, sample_freq, rf_freq_0)
    plot_power_spectrum(m1_rx_IF, N_M1, sample_freq, "M1 Received Signal (IF)")

    l1_rx_IF = RF_downconversion(l1_rx, N_L1, sample_freq, rf_freq_0)
    plot_power_spectrum(l1_rx_IF, N_L1, sample_freq, "L1 Received Signal (IF)")

    # # Downconversion to BB
    # s_rx_BB = IF_downconversion(s_rx_IF, N, F_SAMPLE, F_IF)
    # plot_power_spectrum(s_rx_BB, N, F_SAMPLE, "Received Signal (BB)")

if __name__ == "__main__":
    main()
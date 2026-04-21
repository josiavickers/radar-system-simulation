from tx_chain import *
from rx_chain import *
from channel import *
from plotting import *
from load_config import *

# Parameters
# F_SAMPLE = 500e6 # 500MHz
# N = 4096 # Number of samples
# F_START = 0 # start freq (baseband)
# F_END = 10e6 # end freq
# F_IF = 40e6 # Intermediate freq
# F_RF = 60e6 # Radio freq

PA_GAIN = 1
LNA_GAIN = 100

A = 0.001 # received signal attenuation

# R = 100.0 # target range in metres
# TAU = 2*R/3e8 # time delay

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
    s1_start = config["sband_pulses"]["S1Start"]
    s1_delay_samples = config["sband_pulses"]["S1Delay"]
    s1_amplitude = config["sband_pulses"]["S1Amplitude"]
    s1_kaiser_beta = config["sband_pulses"]["S1KaiserBeta"]

    # Medium Pulse M1
    m1_duration = config["sband_pulses"]["M1DurationTime"]
    m1_bandwidth = config["sband_pulses"]["M1Bandwidth"]
    m1_start = config["sband_pulses"]["M1Start"]
    m1_delay_samples = config["sband_pulses"]["M1Delay"]
    m1_amplitude = config["sband_pulses"]["M1Amplitude"]
    m1_kaiser_beta = config["sband_pulses"]["M1KaiserBeta"]

    # IF params
    if_freq_s1 = config["if_conversion"]["if_freq_short_pulse"]
    if_freq_m1 = config["if_conversion"]["if_freq_medium_pulse"]

    # RF params
    rf_freq_0 = config["rf_conversion"]["rf_freq_channel_0"]

    """
    TX Chain
    """
    N_S1 = round(s1_duration * sample_freq) # HOW MANY SAMPLE POINTS?? SAMPLES = PULSE DURATION * F_SAMPLE
    N_M1 = round(m1_duration * sample_freq) # HOW MANY SAMPLE POINTS?? SAMPLES = PULSE DURATION * F_SAMPLE

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

    # Upconversion to IF
    s1_tx_IF = IF_upconversion(s1_tx_windowed, N_S1, sample_freq, if_freq_s1)
    #plot_power_spectrum(s1_tx_IF, N_S1, sample_freq, "S1 IF Signal")

    m1_tx_IF = IF_upconversion(m1_tx_windowed, N_M1, sample_freq, if_freq_m1)
    #plot_power_spectrum(m1_tx_IF, N_M1, sample_freq, "M1 IF Signal")

    # Upconversion to RF
    s1_tx_RF = RF_upconversion(s1_tx_IF, N_S1, sample_freq, rf_freq_0)
    plot_power_spectrum(s1_tx_RF, N_S1, sample_freq, "S1 RF Signal")

    m1_tx_RF = RF_upconversion(m1_tx_IF, N_M1, sample_freq, rf_freq_0)
    plot_power_spectrum(m1_tx_RF, N_M1, sample_freq, "M1 RF Signal")

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
    
    plot_AM_AM_curve(Pin_dB, Pout_dB)

    # PA
    s1_tx = PA_linear(s1_tx_RF, PA_GAIN)
    plot_power_spectrum(s1_tx, N_S1, sample_freq, "PA Output")

    m1_tx = PA_linear(m1_tx_RF, PA_GAIN)
    plot_power_spectrum(m1_tx, N_M1, sample_freq, "PA Output")

    """
    RX Chain
    """
    s1_rx = apply_attenuation(s1_tx, A)
    s1_rx = apply_time_delay(s1_rx, s1_delay_samples)
    plot_power_spectrum(s1_rx, N_S1, sample_freq, "S1 Received Signal")

    m1_rx = apply_attenuation(m1_tx, A)
    m1_rx = apply_time_delay(m1_rx, m1_delay_samples)
    plot_power_spectrum(m1_rx, N_M1, sample_freq, "M1 Received Signal")

    # # LNA
    # s_rx = LNA_linear(s_rx, LNA_GAIN)
    # plot_power_spectrum(s_rx, N, F_SAMPLE, "Received Signal (Post LNA)")

    # # Downconversion to IF
    # s_rx_IF = RF_downconversion(s_rx, N, F_SAMPLE, F_RF)
    # plot_power_spectrum(s_rx_IF, N, F_SAMPLE, "Received Signal (IF)")

    # # Downconversion to BB
    # s_rx_BB = IF_downconversion(s_rx_IF, N, F_SAMPLE, F_IF)
    # plot_power_spectrum(s_rx_BB, N, F_SAMPLE, "Received Signal (BB)")

if __name__ == "__main__":
    main()
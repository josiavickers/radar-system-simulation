from load_config import *
from signal_class import *
from signal_proc import *
from plotting import *
from filter import *
from power_amp import *
from scipy import signal

PA_GAIN = 1
LNA_GAIN = 30 # dB
RX_ATTENUATION = -80 # received signal attenuation dB

def main():
    config = load_config("config.yaml")
    print("App name:", config["app"]["name"])

    """
    Initialise parameters from config.yaml
    """
    rx_sample_freq = config["params"]["rx_sample_freq"]
    tx_sample_freq = config["params"]["tx_sample_freq"]

    # Short Pulse S1
    s1_duration = config["pulse_shape"]["S1DurationTime"]
    s1_bandwidth = config["pulse_shape"]["S1Bandwidth"]
    s1_delay_samples = config["pulse_shape"]["S1Delay"]
    s1_amplitude = config["pulse_shape"]["S1Amplitude"]
    s1_kaiser_beta = config["pulse_shape"]["S1KaiserBeta"]

    # Medium Pulse M1
    m1_duration = config["pulse_shape"]["M1DurationTime"]
    m1_bandwidth = config["pulse_shape"]["M1Bandwidth"]
    m1_delay_samples = config["pulse_shape"]["M1Delay"]
    m1_amplitude = config["pulse_shape"]["M1Amplitude"]
    m1_kaiser_beta = config["pulse_shape"]["M1KaiserBeta"]

    # Long Pulse L1
    l1_duration = config["pulse_shape"]["L1DurationTime"]
    l1_bandwidth = config["pulse_shape"]["L1Bandwidth"]
    l1_delay_samples = config["pulse_shape"]["L1Delay"]
    l1_amplitude = config["pulse_shape"]["L1Amplitude"]
    l1_kaiser_beta = config["pulse_shape"]["L1KaiserBeta"]

    # IF params
    if_freq_s1 = config["xband"]["if_conversion"]["if_freq_short_pulse"]
    if_freq_m1 = config["xband"]["if_conversion"]["if_freq_medium_pulse"]
    if_freq_l1 = config["xband"]["if_conversion"]["if_freq_long_pulse"]

    # RF params
    rf_freq_0 = config["xband"]["rf_conversion"]["rf_freq_channel_0"]

    '''
    M1 Medium Pulse
    '''
    # M1 BB signal
    m1 = Pulse(tx_sample_freq,0,m1_duration,m1_amplitude,m1_bandwidth,"M1")
    m1_t_samples, m1_t = m1.get_time_samples()
    m1_f_samples, m1_f = m1.get_freq_samples()

    plot_time_signal(m1_t_samples, m1_t,"M1")
    plot_power_spectrum(m1_f_samples, m1_f,"M1")

    # Windowing
    m1.update_samples(window_function(m1_t_samples, m1_kaiser_beta))
    m1_t_samples, m1_t = m1.get_time_samples()
    m1_tx_pulse_compression_samples = m1_t_samples.copy() # save for pulse compression
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_time_signal(m1_t_samples, m1_t,"Windowed M1")
    plot_power_spectrum(m1_f_samples, m1_f,"Windowed M1")

    # M1 IF upconversion
    m1.upconversion(if_freq_m1)
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"IF M1")

    # M1 RF upconversion
    m1.upconversion(rf_freq_0)
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"RF M1")

    # POWER AMPLIFIER
    # Apply Rapp model
    g = 1.5
    A_sat = 1.0
    p = 2.0

    m1_t_samples, m1_t = m1.get_time_samples()
    pa_input = m1_t_samples.copy()
    m1.update_samples(rapp_model(m1_t_samples, g, A_sat, p))

    m1_t_samples, m1_t = m1.get_time_samples()
    plot_time_signal(m1_t_samples, m1_t,"PA M1")
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"PA M1")
    plot_am_am_curve(pa_input, m1_t_samples, g)

    # M1 received signal
    m1_t_samples, m1_t = m1.get_time_samples()
    m1.update_samples(apply_channel(m1_t_samples,RX_ATTENUATION,m1_delay_samples))

    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"Rx M1")
    m1_t_samples, m1_t = m1.get_time_samples() 
    plot_time_signal(m1_t_samples, m1_t,"Rx M1")

    # M1 LNA
    m1_t_samples, m1_t = m1.get_time_samples()
    m1.update_samples(linear_gain(m1_t_samples,LNA_GAIN))

    m1_t_samples, m1_t = m1.get_time_samples() 
    plot_time_signal(m1_t_samples, m1_t,"LNA M1")
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"LNA M1")

    # M1 downconversion to IF
    m1.downconversion(rf_freq_0)
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"IF M1 before filtering")

    m1_t_samples, m1_t = m1.get_time_samples() 
    plot_time_signal(m1_t_samples, m1_t,"IF M1 before filtering")

    m1.update_samples(signal.sosfilt(get_if_filter_coeff(), m1_t_samples))

    m1_t_samples, m1_t = m1.get_time_samples() 
    plot_time_signal(m1_t_samples, m1_t,"IF M1 after filtering")
    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"IF M1 after filtering")

    # M1 downconversion to BB
    m1.downconversion(if_freq_m1)

    m1_f_samples, m1_f = m1.get_freq_samples()
    plot_power_spectrum(m1_f_samples, m1_f,"BB M1")

    # Pulse compression
    m1_t_samples, m1_t = m1.get_time_samples()
    plot_time_signal(m1_t_samples, m1_t,"BB M1")
    pulse_compression(m1_tx_pulse_compression_samples, m1_t_samples, tx_sample_freq, "M1")

    '''
    L1 Long Pulse
    '''
    # L1 BB signal
    l1 = Pulse(tx_sample_freq,0,l1_duration,l1_amplitude,l1_bandwidth,"L1")
    l1_t_samples, l1_t = l1.get_time_samples()
    l1_f_samples, l1_f = l1.get_freq_samples()

    # plot_time_signal(l1_t_samples, l1_t,"L1")
    # plot_power_spectrum(l1_f_samples, l1_f,"L1")

    # # Windowing
    # l1.update_samples(window_function(l1_t_samples, l1_kaiser_beta))
    # l1_t_samples, l1_t = l1.get_time_samples()
    # l1_tx_pulse_compression_samples = l1_t_samples.copy() # save for pulse compression
    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_time_signal(l1_t_samples, l1_t,"Windowed L1")
    # plot_power_spectrum(l1_f_samples, l1_f,"Windowed L1")

    # # L1 IF upconversion
    # l1.upconversion(if_freq_l1)
    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"IF L1")

    # # L1 RF upconversion
    # l1.upconversion(rf_freq_0)
    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"RF L1")

    # # L1 received signal
    # l1_t_samples, l1_t = l1.get_time_samples()
    # l1.update_samples(apply_channel(l1_t_samples,RX_ATTENUATION,l1_delay_samples))

    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"Rx L1")
    # l1_t_samples, l1_t = l1.get_time_samples() 
    # plot_time_signal(l1_t_samples, l1_t,"Rx L1")

    # # L1 LNA
    # l1_t_samples, l1_t = l1.get_time_samples()
    # l1.update_samples(linear_gain(l1_t_samples,LNA_GAIN))

    # l1_t_samples, l1_t = l1.get_time_samples() 
    # plot_time_signal(l1_t_samples, l1_t,"LNA L1")
    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"LNA L1")

    # # L1 downconversion to IF
    # l1.downconversion(rf_freq_0)
    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"IF L1 before filtering")

    # l1_t_samples, l1_t = l1.get_time_samples() 
    # plot_time_signal(l1_t_samples, l1_t,"IF L1 before filtering")

    # l1.update_samples(signal.sosfilt(get_if_filter_coeff(), l1_t_samples))

    # l1_t_samples, l1_t = l1.get_time_samples() 
    # plot_time_signal(l1_t_samples, l1_t,"IF L1 after filtering")
    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"IF L1 after filtering")

    # # L1 downconversion to BB
    # l1.downconversion(if_freq_l1)

    # l1_f_samples, l1_f = l1.get_freq_samples()
    # plot_power_spectrum(l1_f_samples, l1_f,"BB L1")

    # # Pulse compression
    # l1_t_samples, l1_t = l1.get_time_samples()
    # plot_time_signal(l1_t_samples, l1_t,"BB L1")
    # pulse_compression(l1_tx_pulse_compression_samples, l1_t_samples, tx_sample_freq, "L1")

    '''
    S1 Short Pulse
    '''
    # # S1 BB signal
    # s1 = Pulse(tx_sample_freq,0,s1_duration,s1_amplitude,s1_bandwidth,"S1")
    # s1_t_samples, s1_t = s1.get_time_samples()
    # s1_f_samples, s1_f = s1.get_freq_samples()

    # print("S1 samples:", len(s1_t_samples))
    # print("M1 samples:", len(m1_t_samples))
    # print("L1 samples:", len(l1_t_samples))

    # plot_time_signal(s1_t_samples, s1_t,"S1")
    # plot_power_spectrum(s1_f_samples, s1_f,"S1")

    # # # Increase signal length with zero padding
    # # s1_t_samples, s1_t = s1.get_time_samples()
    # # s1.update_samples(zero_pad(s1_t_samples, len(l1_t_samples)))
    # # s1_t_samples, s1_t = s1.get_time_samples()
    # # s1_f_samples, s1_f = s1.get_freq_samples()
    # # plot_time_signal(s1_t_samples, s1_t,"Zero-padded S1")
    # # plot_power_spectrum(s1_f_samples, s1_f,"Zero-padded S1")
    # # print("S1 Samples (zero padding):", len(s1_t_samples))

    # # Windowing
    # s1.update_samples(window_function(s1_t_samples, s1_kaiser_beta))
    # s1_t_samples, s1_t = s1.get_time_samples()
    # s1_tx_pulse_compression_samples = s1_t_samples.copy() # save for pulse compression
    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_time_signal(s1_t_samples, s1_t,"Windowed S1")
    # plot_power_spectrum(s1_f_samples, s1_f,"Windowed S1")

    # # S1 IF upconversion
    # s1.upconversion(if_freq_s1)
    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"IF S1")

    # # S1 RF upconversion
    # s1.upconversion(rf_freq_0)
    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"RF S1")

    # # S1 received signal
    # s1_t_samples, s1_t = s1.get_time_samples()
    # s1.update_samples(apply_channel(s1_t_samples,RX_ATTENUATION,s1_delay_samples))

    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"Rx S1")
    # s1_t_samples, s1_t = s1.get_time_samples() 
    # plot_time_signal(s1_t_samples, s1_t,"Rx S1")

    # # S1 LNA
    # s1_t_samples, s1_t = s1.get_time_samples()
    # s1.update_samples(linear_gain(s1_t_samples,LNA_GAIN))

    # s1_t_samples, s1_t = s1.get_time_samples() 
    # plot_time_signal(s1_t_samples, s1_t,"LNA S1")
    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"LNA S1")

    # # S1 downconversion to IF
    # s1.downconversion(rf_freq_0)
    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"IF S1 before filtering")

    # s1_t_samples, s1_t = s1.get_time_samples() 
    # plot_time_signal(s1_t_samples, s1_t,"IF S1 before filtering")

    # s1.update_samples(signal.sosfilt(get_if_filter_coeff(), s1_t_samples))

    # s1_t_samples, s1_t = s1.get_time_samples() 
    # plot_time_signal(s1_t_samples, s1_t,"IF S1 after filtering")
    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"IF S1 after filtering")

    # # S1 downconversion to BB
    # s1.downconversion(if_freq_s1)

    # s1_f_samples, s1_f = s1.get_freq_samples()
    # plot_power_spectrum(s1_f_samples, s1_f,"BB S1")

    # # Pulse compression
    # s1_t_samples, s1_t = s1.get_time_samples()
    # plot_time_signal(s1_t_samples, s1_t,"BB S1")
    # pulse_compression(s1_tx_pulse_compression_samples, s1_t_samples, tx_sample_freq, "S1")

if __name__ == "__main__":
    main()
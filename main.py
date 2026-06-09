from load_config import *
from signal_class import *
from signal_proc import *
from plotting import *

PA_GAIN = 1
LNA_GAIN = 30 # dB
RX_ATTENUATION = -80 # received signal attenuation dB

# def zero_pad(signal, target_length):
#     pad_total = target_length - len(signal)
#     pad_left = pad_total // 2
#     pad_right = pad_total - pad_left

#     signal_padded = np.pad(signal, (pad_left, pad_right), mode='constant')
#     return signal_padded

def main():
    config = load_config("config.yaml")
    print("App name:", config["app"]["name"])

    """
    Initialise parameters from config.yaml
    """
    rx_sample_freq = config["params"]["sample_freq"]
    tx_sample_freq = 2*rx_sample_freq

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
    t_samples, t = m1.get_time_samples()
    f_samples, f = m1.get_freq_samples()

    plot_time_signal(t_samples, t,"M1")
    plot_power_spectrum(f_samples, f,"M1")

    # Windowing
    m1.update_samples(window_function(t_samples, m1_kaiser_beta))
    t_samples, t = m1.get_time_samples()
    tx_pulse_compression_samples = t_samples.copy() # save for pulse compression
    f_samples, f = m1.get_freq_samples()
    plot_time_signal(t_samples, t,"Windowed M1")
    plot_power_spectrum(f_samples, f,"Windowed M1")

    # M1 IF upconversion
    m1.upconversion(if_freq_m1)
    f_samples, f = m1.get_freq_samples()
    plot_power_spectrum(f_samples, f,"IF M1")

    # M1 RF upconversion
    m1.upconversion(rf_freq_0)
    f_samples, f = m1.get_freq_samples()
    plot_power_spectrum(f_samples, f,"RF M1")

    # M1 received signal
    t_samples, t = m1.get_time_samples()
    m1.update_samples(apply_channel(t_samples,RX_ATTENUATION,m1_delay_samples))

    f_samples, f = m1.get_freq_samples()
    plot_power_spectrum(f_samples, f,"Rx M1")
    t_samples, t = m1.get_time_samples() 
    plot_time_signal(t_samples, t,"Rx M1")

    # M1 LNA
    t_samples, t = m1.get_time_samples()
    m1.update_samples(linear_gain(t_samples,LNA_GAIN))

    t_samples, t = m1.get_time_samples() 
    plot_time_signal(t_samples, t,"LNA M1")
    f_samples, f = m1.get_freq_samples()
    plot_power_spectrum(f_samples, f,"LNA M1")

    # M1 downconversion to IF
    m1.downconversion(rf_freq_0)
    f_samples, f = m1.get_freq_samples()
    plot_power_spectrum(f_samples, f,"IF M1")

    # M1 downconversion to BB
    m1.downconversion(if_freq_m1)

    f_samples, f = m1.get_freq_samples()
    plot_power_spectrum(f_samples, f,"BB M1")

    # Pulse compression
    t_samples, t = m1.get_time_samples()
    plot_time_signal(t_samples, t,"BB M1")
    pulse_compression(tx_pulse_compression_samples, t_samples, tx_sample_freq, "M1")

if __name__ == "__main__":
    main()
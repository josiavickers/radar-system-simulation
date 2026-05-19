from load_config import *
from BasebandSignal import *

PA_GAIN = 1
LNA_GAIN = 30 # dB
RX_ATTENUATION = -80 # received signal attenuation dB

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
    # M1 BB signal and windowing
    m1 = BasebandSignal(m1_amplitude, tx_sample_freq, 0, m1_duration, m1_bandwidth, m1_kaiser_beta, "M1")
    m1.plot_bb_time_signal()
    m1.plot_power_spectrum()

    # M1 IF upconversion
    m1.upconversion(if_freq_m1)
    m1.plot_power_spectrum()

    # M1 RF upconversion
    m1.upconversion(rf_freq_0)
    m1.plot_power_spectrum()

    # M1 received signal
    m1.apply_channel(RX_ATTENUATION, m1_delay_samples, tx_sample_freq) 
    # WHY SHOULD RX HAVE LOWER SAMPLING RATE? SEEMS TO HALF OUR SPECTRUM
    # AND RUINS PULSE COMPRESSION RESULTS
    m1.plot_power_spectrum()

    # M1 LNA
    m1.linear_gain(LNA_GAIN)
    m1.plot_power_spectrum()

    # M1 downconversion to IF
    m1.downconversion(rf_freq_0)
    m1.plot_power_spectrum()

    # M1 downconversion to BB
    m1.downconversion(if_freq_m1)
    m1.plot_power_spectrum()

    # Pulse compression
    m1.matched_filter()

if __name__ == "__main__":
    main()
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
    tx_spectrum_groups = []

    # M1 BB signal
    m1 = Pulse(tx_sample_freq,0,m1_duration,m1_amplitude,m1_bandwidth,"M1")
    m1_t_samples, m1_t = m1.get_time_samples()
    m1_f_samples, m1_f = m1.get_freq_samples()

    #plot_time_signal(m1_t_samples, m1_t,"M1")
    tx_spectrum_groups.append([(m1_f, m1_f_samples, "M1")])

    # Windowing
    m1.apply_window(m1_kaiser_beta)
    m1_t_samples, m1_t = m1.get_time_samples()
    m1_tx_pulse_compression_samples = m1_t_samples.copy() # save for pulse compression
    m1_f_samples, m1_f = m1.get_freq_samples()
    #plot_time_signal(m1_t_samples, m1_t,"Windowed M1")
    tx_spectrum_groups.append([(m1_f, m1_f_samples, "Windowed M1")])

    # M1 IF upconversion
    m1.upconversion(if_freq_m1)
    m1_f_samples, m1_f = m1.get_freq_samples()
    tx_spectrum_groups.append([(m1_f, m1_f_samples, "IF M1")])

    # M1 RF upconversion
    m1.upconversion(rf_freq_0)
    m1_f_samples, m1_f = m1.get_freq_samples()
    rf_f, rf_dbm = m1_f, m1_f_samples # save pre-PA snapshot for overlay with PA M1

#################################################################################################################
    # POWER AMPLIFIER
    g = 1.0

    m1_t_samples, m1_t = m1.get_time_samples()
    pa_input = m1_t_samples.copy()

    pa_model = 2
    if pa_model == 1: # Rapp Model
        model_name = "Rapp"
        m1.update_samples(rapp_model(pa_input, g, A_sat=5.0, p=10.0))
    elif pa_model == 2: # Saleh Model
        model_name = "Saleh"
        m1.update_samples(saleh_model(pa_input, g, alpha_a=1.5, beta_a=0.05, alpha_phi=10.0))

    m1_t_samples, m1_t = m1.get_time_samples()
    m1_f_samples, m1_f = m1.get_freq_samples()
    tx_spectrum_groups.append([
        (rf_f, rf_dbm, "RF M1 (pre-PA)"),
        (m1_f, m1_f_samples, f"PA M1 ({model_name}, post-PA)"),
    ])
    plot_power_spectrum_grid(tx_spectrum_groups, "M1 TX Path Spectra")
    plot_am_am_curve(pa_input, m1_t_samples, g, f"{model_name} AM/AM")
    plot_am_pm_curve(pa_input, m1_t_samples, f"{model_name} AM/PM")
#################################################################################################################

    rx_spectrum_groups = []

    # M1 received signal
    m1_t_samples, m1_t = m1.get_time_samples()
    m1.update_samples(apply_channel(m1_t_samples,RX_ATTENUATION,m1_delay_samples))
    m1_f_samples, m1_f = m1.get_freq_samples()
    rx_spectrum_groups.append([(m1_f, m1_f_samples, "Rx M1")])

    # M1 LNA
    m1_t_samples, m1_t = m1.get_time_samples()
    m1.update_samples(linear_gain(m1_t_samples,LNA_GAIN))
    m1_f_samples, m1_f = m1.get_freq_samples()
    rx_spectrum_groups.append([(m1_f, m1_f_samples, "LNA M1")])

    # M1 downconversion to IF
    m1.downconversion(rf_freq_0)
    m1_f_samples, m1_f = m1.get_freq_samples()
    rx_spectrum_groups.append([(m1_f, m1_f_samples, "IF M1 before filtering")])

    # IF Filter
    m1_t_samples, m1_t = m1.get_time_samples()
    m1.update_samples(signal.sosfilt(get_if_filter_coeff(), m1_t_samples))
    m1_f_samples, m1_f = m1.get_freq_samples()
    rx_spectrum_groups.append([(m1_f, m1_f_samples, "IF M1 after filtering")])

    # M1 downconversion to BB
    m1.downconversion(if_freq_m1)
    m1_f_samples, m1_f = m1.get_freq_samples()
    rx_spectrum_groups.append([(m1_f, m1_f_samples, "BB M1")])

    plot_power_spectrum_grid(rx_spectrum_groups, "M1 RX Path Spectra")

    # Pulse compression
    m1_t_samples, m1_t = m1.get_time_samples()
    pulse_compression(m1_tx_pulse_compression_samples, m1_t_samples, tx_sample_freq, "M1")

if __name__ == "__main__":
    main()
from tx_chain import *
from rx_chain import *
from channel import *
from plotting import *

# Parameters
F_SAMPLE = 500e6 # 500MHz
N = 4096 # Number of samples
F_START = 0 # start freq (baseband)
F_END = 10e6 # end freq
F_IF = 40e6 # Intermediate freq
F_RF = 60e6 # Radio freq

PA_GAIN = 1
LNA_GAIN = 100

R = 100.0 # target range in metres
TAU = 2*R/3e8 # time delay
A = 0.001 # received signal attenuation

def main():
    # TX Chain

    # BB Signal Generation
    s_tx_bb = generate_baseband_signal(F_START,F_END,F_SAMPLE,N)
    plot_power_spectrum(s_tx_bb, N, F_SAMPLE, "BB Signal")
    #plot_mag_and_phase_time_domain(s_bb, "Baseband Signal")
    
    # Windowing
    s_tx_windowed = window_function(s_tx_bb, N)
    plot_power_spectrum(s_tx_windowed, N, F_SAMPLE, "Windowed BB Signal")
    #plot_mag_and_phase_time_domain(s_windowed, "Windowed Baseband Signal")

    # Upconversion to IF
    s_tx_IF = IF_upconversion(s_tx_windowed, N, F_SAMPLE, F_IF)
    plot_power_spectrum(s_tx_IF, N, F_SAMPLE, "IF Signal")

    # Upconversion to RF
    s_tx_RF = RF_upconversion(s_tx_IF, N, F_SAMPLE, F_RF)
    plot_power_spectrum(s_tx_RF, N, F_SAMPLE, "RF Signal")

    # PA modelling
    a_in_sweep = np.linspace(0.01,10.0,200) # input amplitude sweep
    Pin_dB = []
    Pout_dB = []

    for a in a_in_sweep:
        # Scale RF input
        s_in = a * s_tx_RF 

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
    s_tx = PA_linear(s_tx_RF, PA_GAIN)
    plot_power_spectrum(s_tx, N, F_SAMPLE, "PA Output")

    # RX Chain
    s_rx = apply_attenuation(s_tx, A)
    s_rx = apply_time_delay(s_rx, TAU, F_SAMPLE)
    plot_power_spectrum(s_rx, N, F_SAMPLE, "Received Signal")

    # LNA
    s_rx = LNA_linear(s_rx, LNA_GAIN)
    plot_power_spectrum(s_rx, N, F_SAMPLE, "Received Signal (Post LNA)")

    # Downconversion to IF
    s_rx_IF = RF_downconversion(s_rx, N, F_SAMPLE, F_RF)
    plot_power_spectrum(s_rx_IF, N, F_SAMPLE, "Received Signal (IF)")

    # Downconversion to BB
    s_rx_BB = IF_downconversion(s_rx_IF, N, F_SAMPLE, F_IF)
    plot_power_spectrum(s_rx_BB, N, F_SAMPLE, "Received Signal (BB)")

if __name__ == "__main__":
    main()
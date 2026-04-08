from tx_chain import *
from rx_chain import *
from plotting import *

# Parameters
F_SAMPLE = 500e6 # 500MHz
N = 4096 # Number of samples
F_START = 0 # start freq (baseband)
F_END = 10e6 # end freq
F_IF = 40e6 # Intermediate freq
F_RF = 60e6 # Radio freq

PA_GAIN = 1

R = 100.0 # target range in metres
TAU = 2*R/3e8 # time delay
A = 0.001 # received signal attenuation

def main():
    s_bb = generate_baseband_signal(F_START,F_END,F_SAMPLE,N)
    #plot_mag_spectrum(s_bb, N, F_SAMPLE, "Baseband Signal")
    #plot_mag_and_phase_time_domain(s_bb, "Baseband Signal")
    
    s_windowed = window_function(s_bb, N)
    #plot_mag_spectrum(s_windowed, N, F_SAMPLE, "Windowed Baseband Signal")
    #plot_mag_and_phase_time_domain(s_windowed, "Windowed Baseband Signal")

    s_IF = IF_upconversion(s_windowed, N, F_SAMPLE, F_IF)
    #plot_mag_spectrum(s_IF, N, F_SAMPLE, "IF Signal")
    #plot_mag_and_phase_time_domain(s_IF, "IF Signal")

    s_RF = RF_upconversion(s_IF, N, F_SAMPLE, F_RF)
    #plot_mag_spectrum(s_RF, N, F_SAMPLE, "RF Signal")
    #plot_power_spectrum(s_RF, N, F_SAMPLE, "RF Signal")

    # PA modelling
    a_in_sweep = np.linspace(0.01,10.0,200) # input amplitude sweep
    Pin_dB = []
    Pout_dB = []

    for a in a_in_sweep:
        # Scale RF input
        s_in = a * s_RF 

        # PA output
        s_out = PA_linear(s_in, PA_GAIN)

        # Power calculation
        Pin = get_real_signal_power(s_in)
        Pout = get_real_signal_power(s_out)

        # Convert to dB
        Pin_dB.append(10 * np.log10(Pin))
        Pout_dB.append(10 * np.log10(Pout))
    
    #plot_AM_AM_curve(Pin_dB, Pout_dB)

    s_tx = PA_linear(s_RF, PA_GAIN)
    #plot_mag_spectrum(s_tx, N, F_SAMPLE, "PA Output")
    plot_power_spectrum(s_tx, N, F_SAMPLE, "PA Output")

    s_rx = s_tx*A # BUT ISN'T MULTIPLYING BY 1000 A 30DB JUMP?
    # DO I NEED TO IMPLEMENT A PHASE SHIFT DUE TO TIME DELAY TOO? PROBABLY BECAUSE OF AM/PM RIGHT?
    #plot_mag_spectrum(s_rx, N, F_SAMPLE, "Received Signal")
    plot_power_spectrum(s_rx, N, F_SAMPLE, "Received Signal")

if __name__ == "__main__":
    main()
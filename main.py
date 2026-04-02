from tx_chain import *
from plotting import *

# Parameters
F_SAMPLE = 500e6 # 500MHz
N = 4096 # Number of samples
F_START = 0 # start freq (baseband)
F_END = 10e6 # end freq
F_IF = 40e6 # Intermediate freq
F_RF = 60e6 # Radio freq

def main():
    s_bb = generate_baseband_signal(F_START,F_END,F_SAMPLE,N)
    plot_mag_spectrum(s_bb, N, F_SAMPLE, "Baseband Signal")
    #plot_mag_and_phase_time_domain(s_bb, "Baseband Signal")
    
    s_windowed = window_function(s_bb, N)
    plot_mag_spectrum(s_windowed, N, F_SAMPLE, "Windowed Baseband Signal")
    #plot_mag_and_phase_time_domain(s_windowed, "Windowed Baseband Signal")

    s_IF = IF_upconversion(s_windowed, N, F_SAMPLE, F_IF)
    plot_mag_spectrum(s_IF, N, F_SAMPLE, "IF Signal")
    #plot_mag_and_phase_time_domain(s_IF, "IF Signal")

if __name__ == "__main__":
    main()
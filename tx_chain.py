import numpy as np

def PA_linear(rf_signal, gain):
    return rf_signal*gain

# Upconversion to RF
def RF_upconversion(if_signal, num_samples, f_s, f_RF):
    n = np.arange(num_samples)
    I = np.real(if_signal)
    Q = np.imag(if_signal)

    cos_carrier = np.cos(2 * np.pi * f_RF * n / f_s)
    sin_carrier = np.sin(2 * np.pi * f_RF * n / f_s)

    # IQ modulation to RF (returns a real signal)
    s_RF = I * cos_carrier - Q * sin_carrier

    return s_RF

# Upconversion to IF 
def IF_upconversion(bb_signal, num_samples, f_s, f_IF):
    n = np.arange(num_samples) # sample points
    s_IF = bb_signal*np.exp(1j*2*np.pi*f_IF*n/f_s)
    return s_IF
 
# Apply Hanning window to input signals
def window_function(bb_signal, num_samples):
    window = np.hanning(num_samples)
    I = np.real(bb_signal)
    Q = np.imag(bb_signal)
    I_w = I*window
    Q_w = Q*window
    s_w = I_w + 1j*Q_w
    return s_w
 
# Baseband Signal Generation
def generate_baseband_signal(f_start, f_end, f_s, num_samples):
    n = np.arange(num_samples) # array of sample points
    T = num_samples/f_s # observation time
    k = (f_end - f_start)/T # f_start-f_end is bandwidth B, Chirp slope k: how many Hz the freq increases per second
   
    # Instantaneous baseband frequency
    phi = 2*np.pi*(f_start*n/f_s + 0.5*k*(n/f_s)**2) # 0.5*k*(n/f_s)**2 comes from integrating instantaneous freq f(t) = f0 + kt
    s_bb = np.exp(1j * phi)
    return s_bb

def get_real_signal_power(x):
    return np.mean(x**2)
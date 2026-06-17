import numpy as np

def rapp_model(x, g, A_sat, p):
    x = np.asarray(x)
    r = np.abs(x)

    compression = 1.0 / (1.0 + (r / A_sat)**(2 * p))**(1.0 / (2 * p))

    return g * compression * x

def saleh_model(x, g=1.0, alpha_a=1.2, beta_a=0.04,alpha_phi=0.0, beta_phi=9.0):
    '''
    alpha_phi = 0 - no phase distortion
    when beta_a is low, more linearity
    '''
    x = np.asarray(x)

    # Magnitude and phase of input
    r = np.abs(x)
    theta = np.angle(x)

    # AM/AM conversion
    A = (alpha_a * r) / (1.0 + beta_a * r**2)

    # AM/PM conversion
    phi = (alpha_phi * r**2) / (1.0 + beta_phi * r**2)

    # Reconstruct output signal
    y = g * A * np.exp(1j * (theta + phi))

    return y

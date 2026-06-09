import numpy as np

def rapp_model(x, g=1.0, A_sat=1.0, p=2.0):
    x = np.asarray(x, dtype=np.complex128)

    r = np.abs(x)

    gain_compression = g / (1 + (g * r / A_sat)**(2 * p))**(1 / (2 * p))

    y = gain_compression * x
    return y
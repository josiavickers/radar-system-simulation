import numpy as np

def rapp_model(x, g, A_sat, p):
    x = np.asarray(x)
    r = np.abs(x)

    compression = 1.0 / (1.0 + (r / A_sat)**(2 * p))**(1.0 / (2 * p))

    return g * compression * x
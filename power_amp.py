import numpy as np

def rapp_model(x, g=1.0, A_sat=8.0, p=2.0, a=1.0, b=-30.0, c=2.0, p1=0.1, p2=1.0, d=0.0):
    '''
    Rapp AM-AM model with the modified Honkanen and Häggman AM-PM model
    '''
    x = np.asarray(x, dtype=complex)

    # Magnitude and phase of input
    r = np.abs(x)
    theta = np.angle(x)

    # Rapp AM-AM model
    A = g*r / (1.0 + (g*r / A_sat)**(2 * p))**(1.0 / (2 * p))

    # Modified Honkanen and Häggman AM-PM model (degrees)
    phi_deg = b / (1.0 + np.exp(-c * (r - a))) * 1.0 / (p1*r + p2) - d

    # Reconstruct output signal
    y = A * np.exp(1j * (theta + np.deg2rad(phi_deg)))

    return y

def modified_saleh_model(x, g=1.0, alpha_a=2.1587, beta_a=1.1517, alpha_phi=4.0033, beta_phi=9.1040,
                         eta_a=1.0, gamma_a=2.0, nu_a=1.0, eps_a=0.0,
                         eta_phi=2.0, gamma_phi=2.0, nu_phi=1.0, eps_phi=0.0):
    '''
    Modified Saleh model (O'Droma, Meza and Lei)
    '''
    x = np.asarray(x)

    # Magnitude and phase of input
    r = np.abs(x)
    theta = np.angle(x)

    # AM/AM conversion
    A = (alpha_a * r**eta_a) / (1.0 + beta_a * r**gamma_a)**nu_a - eps_a

    # AM/PM conversion
    phi = (alpha_phi * r**eta_phi) / (1.0 + beta_phi * r**gamma_phi)**nu_phi - eps_phi

    # Reconstruct output signal
    y = g * A * np.exp(1j * (theta + phi))

    return y

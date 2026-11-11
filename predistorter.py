import numpy as np

def get_predistorted_pulse(x, power_amplifier, G, K=1000, peak_fraction=0.95):
    '''
    Iterative learning control (ILC) predistorter
    Learns the PA input u that makes the PA output follow the target y_d.
    Two targets are available (select one by commenting out the other
    y_d / u_max pair):
      Fully linear - the whole pulse is linear, its peak at peak_fraction of
                     the PA's maximum output (cascade gain below G)
      Clipped      - linear at the PA gain G up to the PA's saturation, flat
                     (clipped) above; drive limited to 2x the pulse peak

    x               - windowed pulse
    power_amplifier - function applying the selected PA model to its input
    G               - PA gain (small signal gain)
    K               - number of ILC iterations
    peak_fraction   - fully linear target only: peak output as a fraction of
                      the PA's maximum output (< 1, since saturation is only
                      reached at infinite drive)

    Returns the predistorted pulse u and the target linear gain of the
    predistorter + PA cascade.
    '''
    # PA output over a range of drive amplitudes
    r = np.linspace(0, 100 * np.max(np.abs(x)), 100001)
    pa_out = np.abs(power_amplifier(r.astype(complex)))

    # Maximum PA output (saturation, or roll-over peak)
    A_max = np.max(pa_out)

    # Target output y_d and drive limit u_max:
    # Fully linear - whole pulse linear, peak at peak_fraction of the PA's maximum output
    y_d = (peak_fraction * A_max / np.max(np.abs(x))) / G * x
    u_max = r[np.argmax(pa_out >= peak_fraction * A_max)] # drive reaching that peak
    # Clipped - linear at the PA gain G up to the PA's saturation, flat above
    #y_d = x
    #u_max = 2 * np.max(np.abs(x)) # drive limit 2x the pulse peak, PA output at saturation

    u = x.copy()

    for k in range(K):
        y = power_amplifier(u)          # send u to PA, capture output y_k
        e = y_d - y / G                 # error e_k
        u = u + e                       # update u_{k+1}

        # Limit drive magnitude, keep phase
        mag = np.abs(u)
        u = np.where(mag > u_max, u * u_max / np.maximum(mag, 1e-30), u)

    # Target linear gain of the predistorter + PA cascade
    G_target = G * np.max(np.abs(y_d)) / np.max(np.abs(x))

    return u, G_target

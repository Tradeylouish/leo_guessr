import numpy as np
from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
from skyfield.elementslib import osculating_elements_of

import plotting

if __name__ == '__main__':
    # Get a TLE for plotting
    TLE = """1 43205U 18017A   18038.05572532 +.00020608 -51169-6 +11058-3 0  9993
    2 43205 029.0165 287.1006 3403068 180.4827 179.1544 08.75117793000017"""
    L1, L2 = TLE.splitlines()

    #Load ephemeris data
    load = Loader('~/skyfield-data')
    data = load('de421.bsp')
    ts   = load.timescale()

    # Create the satellite object
    Roadster = EarthSatellite(L1, L2)

    # Calculate the period and produce a corresponding time series
    elements = osculating_elements_of(Roadster.at(Roadster.epoch))
    period = elements.period_in_days*24
    print(f"{period} hour orbit")
    hours = np.arange(0, period, 0.01)
    time = ts.utc(2024, 2, 7, hours)

    # Propagate the orbit through the time series
    Rpos    = Roadster.at(time).position.km
    Rposecl = Roadster.at(time).ecliptic_position().km

    plotting.plot_orbit(Rpos)
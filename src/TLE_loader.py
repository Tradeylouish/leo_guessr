import random

import numpy as np
from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
from skyfield.elementslib import osculating_elements_of

import plotting


def load_tle():
    #Load ephemeris data
    load = Loader('~/skyfield-data')
    data = load('de421.bsp')
    ts   = load.timescale()

    # Get TLEs from Celestrak
    stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
    satellites = load.tle_file(stations_url)
    print('Loaded', len(satellites), 'satellites')

    index = random.randint(0, len(satellites))
    rand_sat = satellites[index]
    print(rand_sat) 

    # Calculate the period
    elements = osculating_elements_of(rand_sat.at(rand_sat.epoch))
    period = elements.period_in_days*24
    print(f"{period} hour orbit")
    hours = np.arange(0, period, 0.01)

    # Produce a Time object spanning a series of timestamps on the current date
    today = ts.now()
    time = ts.utc(today.utc.year, today.utc.month, today.utc.day, hours)

    # Propagate the orbit through the time series
    return rand_sat.at(time).position.km

if __name__ == '__main__':
    Rpos = load_tle()
    plotting.plot_orbit(Rpos)
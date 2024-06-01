import random

import numpy as np
from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
from skyfield.elementslib import osculating_elements_of

import plotting


def calculate_score(period_guess, period, inclination_guess, inclination):
    MAX_POINTS = 30
    period_score = max(0, 1 - abs((period - period_guess) / period))
    inclination_score = max(0, 1 - abs((inclination - inclination_guess) / inclination))
    
    return round(MAX_POINTS * period_score * inclination_score)

def play_game(satellites, ts):
    index = random.randint(0, len(satellites))
    rand_sat = satellites[index]
    print(rand_sat) 

    # Calculate the period in hours
    elements = osculating_elements_of(rand_sat.at(rand_sat.epoch))
    period = elements.period_in_days*24

    # Create a time series representing hours - add a little to close gaps
    hours = np.arange(0, period+0.01, 0.01)

    # Calculate other elements
    inclination = elements.inclination

    # Produce a Time object spanning a series of timestamps from the epoch
    epoch = rand_sat.epoch
    time = ts.utc(epoch.utc.year, epoch.utc.month, epoch.utc.day, hours)

    # Propagate the orbit through the time series
    Rpos = rand_sat.at(time).position.km

    plotting.plot_orbit(Rpos)
    
    # TODO Input sanitisation and format support
    period_guess = float(input("Guess the period: "))
    inclination_guess = float(input("Guess the inclination: "))

    score = calculate_score(period_guess, period, inclination_guess, inclination.degrees)

    print(f"Correct period = {period:0.2f} hours")
    print(f"Correct inclination = {inclination.degrees}")
    print(f"+{score} points!")

    # TODO fix blocking on mayavi plots so they can be viewed while guessing
    # plotting.close_plots()

    return score

def load_tles(): # -> Array of earth satellite objects 

    #Load ephemeris data
    load = Loader('~/skyfield-data')
    data = load('de421.bsp')
    ts   = load.timescale()

    # Get TLEs from Celestrak
    stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
    satellites = load.tle_file(stations_url)
    print('Loaded', len(satellites), 'satellites')

    return satellites, ts

if __name__ == '__main__':

    satellites, ts = load_tles()
    num_games = 10
    running_score = 0
    for i in range(1, num_games+1):
        running_score += play_game(satellites, ts)
        print(f"Total score = {running_score} in {i} games")
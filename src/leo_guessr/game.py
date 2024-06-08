import random

import numpy as np
from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
from skyfield.elementslib import osculating_elements_of

import leo_guessr.plotting as plotting

class Game:  

    satellites, ts = '',''
    total_score = 0
    answers = {'semimajor_axis':0,
               'eccentricity':0,
               'inclination':0,
               'longitude_of_AN':0,
               'argument_of_periapsis':0
    }

    trajectory = []
    sub_trajectory = []

    def __init__(self) -> None:
        self.load_tles()

    def calculate_score(self, guesses : dict[str:float]):
        MAX_POINTS = 30
        score_multiplier = 1

        for key in guesses:
            answer = self.answers[key]
            # TODO change scoring algorithm to better avoid division by 0
            # Avoid division by 0
            if answer == 0:
                continue
            score_multiplier *= max(0, 1 - abs((answer - guesses[key]) / answer))

        return round(MAX_POINTS * score_multiplier)

    def get_random_satellite(self):
        index = random.randint(0, len(self.satellites))
        rand_sat = self.satellites[index]
        return rand_sat
    
    def propagate_orbit(self, satellite):
        # Calculate the period in hours
        elements = osculating_elements_of(satellite.at(satellite.epoch))
        period = elements.period_in_days*24

        # Create a time series representing hours - add a little to close gaps
        hours = np.arange(0, period+0.01, 0.01)

        # Calculate other elements
        self.answers['semimajor_axis'] = elements.semi_major_axis
        self.answers['eccentricity'] = elements.eccentricity
        self.answers['inclination'] = elements.inclination
        self.answers['longitude_of_AN'] = elements.longitude_of_ascending_node
        self.answers['argument_of_periapsis'] = elements.argument_of_periapsis

        # Produce a Time object spanning a series of timestamps from the epoch
        epoch = satellite.epoch
        time = self.ts.utc(epoch.utc.year, epoch.utc.month, epoch.utc.day, hours)

        # Propagate the orbit through the time series
        Rpos = satellite.at(time).position.km

        self.trajectory = Rpos
        
        # Select a random time of flight to produce a sub-trajectory
        index = random.randint(0, len(hours))
        self.time_of_flight = hours[index] - hours[0]
        print(self.trajectory.shape)

        self.sub_trajectory = self.trajectory[:, 0:index]
        #print(self.sub_trajectory)
        
    def get_trajectory(self):
        return self.trajectory
    
    def get_sub_trajectory(self):
        return self.sub_trajectory
    
    def get_lambert_points(self):

        print(self.sub_trajectory.shape)
        print(self.sub_trajectory[:, 0].shape)
        return self.sub_trajectory[:, 0], self.sub_trajectory[:, -1]
    
    def get_time_of_flight(self) -> str:
        hours = int(self.time_of_flight // 1)
        minutes = round((self.time_of_flight % 1) * 60)

        return f"{hours}h {minutes}m"
    
    def new_round(self) -> None:
        satellite = self.get_random_satellite()
        self.propagate_orbit(satellite)
        
    
    def finish_round(self, guesses) -> None:
        round_score = self.calculate_score(guesses)
        self.total_score += round_score

        #print(f"Correct period = {period:0.2f} hours")
        #print(f"Correct inclination = {inclination.degrees}")
        #print(f"+{score} points!")

        return round_score

    def load_tles(self): # -> Array of earth satellite objects 

        #Load ephemeris data
        load = Loader('~/skyfield-data')
        data = load('de421.bsp')
        self.ts   = load.timescale()

        # Get TLEs from Celestrak
        stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
        self.satellites = load.tle_file(stations_url)
        print('Loaded', len(self.satellites), 'satellites')

    def basic_prompts(self):
        guesses = self.answers
        for key in guesses:
            guesses[key] = float(input(f"Guess the {key}: "))
        return guesses
    
    def print_answers(self):
        for key in self.answers:
            print(f"Correct {key} = {self.answers[key]}")

    def run(self):
        while True:
            trajectory = self.new_round()
            #plotting.plot_orbit(trajectory, mlab.)
            guesses = self.basic_prompts()
            round_score = self.finish_round(guesses)
            print(f"+ {round_score} points!")
            self.print_answers()
            print(f"Total score = {self.total_score}")

    # def get_time_of_flight(self):

    #     return f"{random.randint(0, 5)}h {random.randint(0, 60)}m"
    
    def get_two_random_positions(RPos):
        index1 = random.int(0, len(RPos))
        index2 = random.int(0, len(RPos))

        return RPos[index1], RPos[index2]

if __name__ == '__main__':

    game = Game()
    game.run()
    
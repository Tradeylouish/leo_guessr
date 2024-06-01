import numpy as np

import leo_guessr.plotting as plotting

if __name__ == '__main__':
    # Using SI units

    EARTH_RADIUS = 6371e3
    EARTH_MASS = 5.972e24
    G = 6.67430e-11
    mu = G*EARTH_MASS

    altitude = 400e3
    inclination = 0

    position = np.array([EARTH_RADIUS + altitude, 0, 0])
    positions = np.empty(3)
    velocity = np.array([0, 7.6e3, 0])

    # 90 minutes, 1 sec steps
    timestep = 1
    time = np.arange(0, 90*60, timestep)

    for t in time:
        abs_position = np.linalg.norm(position)
        if abs_position <= EARTH_RADIUS:
            print("Crashed")
            break
        acceleration = -position*mu/(abs_position**3)
        positions = np.vstack((positions, position))
        position = np.add(position, velocity*timestep)
        velocity = np.add(velocity, acceleration*timestep)

    positions = np.delete(positions, (0), axis=0).T

    # Convert from m to km
    plotting.plot_orbit(positions/1000)
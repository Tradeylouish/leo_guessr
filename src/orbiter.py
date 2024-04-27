import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mayavi import mlab
from tvtk.api import tvtk
import numpy as np

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
#print(positions[1])

fig = mlab.figure()
#ax = fig.add_subplot(111, projection = '3d')
mlab.plot3d(positions[0], positions[1], positions[2], color=(1.0,0,0), tube_radius=30000.)

 # load and map the texture
img = tvtk.JPEGReader()
img.file_name = 'blue_marble_spherical.jpg'
texture = tvtk.Texture(input_connection=img.output_port, interpolate=1)
# (interpolate for a less raster appearance when zoomed in)

# use a TexturedSphereSource, a.k.a. getting our hands dirty
R = EARTH_RADIUS
Nrad = 180

# create the sphere source with a given radius and angular resolution
sphere = tvtk.TexturedSphereSource(radius=R, theta_resolution=Nrad,
                                    phi_resolution=Nrad)

# assemble rest of the pipeline, assign texture    
sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port)
sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=texture)
fig.scene.add_actor(sphere_actor)

mlab.show()

# draw sphere
u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:50j]
x = EARTH_RADIUS*np.cos(u)*np.sin(v)
y = EARTH_RADIUS*np.sin(u)*np.sin(v)
z = EARTH_RADIUS*np.cos(v)
#ax.plot_wireframe(x, y, z, color="r")


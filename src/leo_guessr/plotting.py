from mayavi import mlab
from tvtk.api import tvtk

def close_plots():
    mlab.close()

def plot_earth(scene) -> None:
    # Load and map texture for Earth
    img = tvtk.JPEGReader()
    img.file_name = 'blue_marble_spherical.jpg'
    texture = tvtk.Texture(input_connection=img.output_port, interpolate=1)

    R = 6371
    Nrad = 180

    # Create the sphere source with a given radius and angular resolution
    sphere = tvtk.TexturedSphereSource(radius=R, theta_resolution=Nrad,
                                        phi_resolution=Nrad)

    # Assemble rest of the pipeline, assign texture    
    sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port)
    sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=texture)
    scene.add_actor(sphere_actor)

def plot_orbit(Rpos, scene) -> None:
    x, y, z = Rpos

    # Plot the trajectory
    mlab.plot3d(x, y, z, color=(1.0,0,0), tube_radius=30., figure=scene.mayavi_scene)

import numpy as np

from traits.api import HasTraits, Instance, Button, String, Range, \
    on_trait_change
from traitsui.api import View, Item, HSplit, Group

from mayavi import mlab
from mayavi.core.ui.api import MlabSceneModel, SceneEditor

import plotting
import game


class MyDialog(HasTraits):

    game = game.Game()

    scene1 = Instance(MlabSceneModel, ())
    scene2 = Instance(MlabSceneModel, ())

    # Game stuff to load once

    time_of_flight = String("0 seconds")

    semimajor_axis = Range(6371, 50000, 7000)
    eccentricity = Range(0.0, 1.0, 0.0)
    inclination = Range(0.0, 180.0,  45.0)
    longitude_of_AN = Range(0, 360,  0)
    argument_of_periapsis = Range(0, 360,  0)

    guessbutton = Button('Guess')

    def __init__(self):
        HasTraits.__init__(self)
        self.start_round()

    @on_trait_change('semimajor_axis, eccentricity, inclination, longitude_of_AN, argument_of_periapsis')
    def redraw_guess_plot(self):
        mlab.clf(figure=self.scene2.mayavi_scene)
        plotting.plot_earth(self.scene2)

    @on_trait_change('guessbutton')
    def make_guess(self):
        print("Pressed")
        self.game.finish_game_round({})
        self.start_round()

    def start_round(self):
        mlab.clf(figure=self.scene1.mayavi_scene)
        plotting.plot_earth(self.scene1)
        RPos = self.game.start_game_round()
        plotting.plot_orbit(RPos, self.scene1)

    # The layout of the dialog created
    view = View(HSplit(
                  Group(
                      'time_of_flight',
                       Item('scene1',
                            editor=SceneEditor(), height=400,
                            width=800),
                       show_labels=False,
                  ),
                  Group(
                       'semimajor_axis',
                       'eccentricity',
                       'inclination',
                       'longitude_of_AN',
                       'argument_of_periapsis',
                       'guessbutton',
                       Item('scene2',
                            editor=SceneEditor(), height=250,
                            width=300, show_label=False),
                       show_labels=True,
                  ),
                ),
                resizable=True,
                )


m = MyDialog()
m.configure_traits()
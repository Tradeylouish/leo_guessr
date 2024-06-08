import numpy as np

from traits.api import HasTraits, Instance, Button, String, Range, \
    on_trait_change
from traitsui.api import View, Item, UItem, HSplit, Group, Readonly

from mayavi import mlab
from mayavi.core.ui.api import MlabSceneModel, SceneEditor

import leo_guessr.plotting as plotting
import leo_guessr.game as game


class MyDialog(HasTraits):

    game = game.Game()

    scene1 = Instance(MlabSceneModel, ())
    scene2 = Instance(MlabSceneModel, ())

    # Game stuff to load once

    time_of_flight = String("Time of Flight: 1h 30m")

    semimajor_axis = Range(6371, 50000, 7000)
    eccentricity = Range(0.0, 1.0, 0.0)
    inclination = Range(0.0, 180.0,  45.0)
    longitude_of_AN = Range(0, 360,  0)
    argument_of_periapsis = Range(0, 360,  0)

    guessbutton = Button('Make guess')
    hintbutton = Button('Hint')

    hint_flag = 0

    def __init__(self):
        HasTraits.__init__(self)
        self.start_round()

    @on_trait_change('semimajor_axis, eccentricity, inclination, longitude_of_AN, argument_of_periapsis')
    def redraw_guess_plot(self):
        mlab.clf(figure=self.scene2.mayavi_scene)
        plotting.plot_earth(self.scene2)

    @on_trait_change('guessbutton')
    def make_guess(self):
        self.game.finish_round({})
        self.start_round()

    @on_trait_change('hintbutton')
    def give_hint(self):
        if self.hint_flag == 2:
            return
        # TODO - Try to clear just the lines/points and not the full figure
        mlab.clf(figure=self.scene1.mayavi_scene)
        if self.hint_flag == 0:
            plotting.plot_orbit(self.game.get_sub_trajectory(), self.scene1)
        elif self.hint_flag == 1:
            plotting.plot_orbit(self.game.get_trajectory(), self.scene1)

        self.hint_flag += 1

    def start_round(self):
        mlab.clf(figure=self.scene1.mayavi_scene)
        mlab.clf(figure=self.scene2.mayavi_scene)
        plotting.plot_earth(self.scene1)
        plotting.plot_earth(self.scene2)
        self.game.new_round()
        plotting.plot_lambert(self.game.get_lambert_points(), self.scene1)
        plotting.plot_orbit(self.game.get_trajectory(), self.scene2)
        self.time_of_flight = f"Time of Flight: {self.game.get_time_of_flight()}"
        self.hint_flag = 0

    # The layout of the dialog created
    view = View(HSplit(
                  Group(
                      Readonly('time_of_flight', style_sheet='*{font-size:24px}'),
                      UItem('hintbutton'),
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
import numpy as np

from traits.api import HasTraits, Instance, Button, String, Range, \
    on_trait_change
from traitsui.api import View, Item, UItem, HSplit, HGroup, Group, Readonly, VGroup

from PyQt5 import QtCore
import sys

from mayavi import mlab
from mayavi.core.ui.api import MlabSceneModel, SceneEditor

import leo_guessr.plotting as plotting
import leo_guessr.game as game

class MyDialog(HasTraits):

    game = game.Game()

    scene1 = Instance(MlabSceneModel, ())
    scene2 = Instance(MlabSceneModel, ())

    timer = QtCore.QTimer()
    time = QtCore.QTime(0, 0, 0)

    time_of_flight = String("Time of Flight: 1h 30m")
    countdown = String("")
    map = String("Geocentric", label="MAP")
    round = String("", label="ROUND")
    score = String("0", label="SCORE")

    semimajor_axis = Range(6371, 50000, 7000)
    eccentricity = Range(0.0, 1.0, 0.0)
    inclination = Range(0.0, 180.0,  45.0)
    #longitude_of_AN = Range(0, 360,  0)
    argument_of_periapsis = Range(0, 360,  0)

    guessbutton = Button('GUESS')
    hintbutton = Button('Hint')

    hint_flag = 0

    def __init__(self):
        HasTraits.__init__(self)
        self.start_round()

        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(1000)

    def timerEvent(self):
        self.time = self.time.addSecs(-1)
        #print(self.time.toString("mm:ss"))
        self.countdown = self.time.toString("mm:ss")

        if self.countdown == "00:00":
            self.make_guess()

    @on_trait_change('semimajor_axis, eccentricity, inclination')
    def redraw_guess_plot(self):
        mlab.clf(figure=self.scene2.mayavi_scene)
        plotting.plot_earth(self.scene2)

    @on_trait_change('guessbutton')
    def make_guess(self):
        # Build a dict of guesses from the GUI
        guesses = {'semimajor_axis':self.semimajor_axis,
               'eccentricity':self.eccentricity,
               'inclination':self.inclination,
        }
        self.game.finish_round(guesses)
        self.score = self.game.get_total_score()
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
        self.round = self.game.get_round_number()
        self.reset_countdown()

    def reset_countdown(self):
        self.time.setHMS(0, self.game.round_length // 60, self.game.round_length % 60)

    # The layout of the dialog created
    view = View(HSplit(
                  Group(
                      Readonly('time_of_flight', style_sheet='*{font-size:24px}'),
                      Readonly('countdown', style_sheet='*{font: Futura; font-size:20px; font-weight:bold; background-color:black; color: white; }'),
                      UItem('hintbutton'),
                       Item('scene1',
                            editor=SceneEditor(), height=400,
                            width=800),
                       show_labels=False,
                  ),
                  Group(
                      HGroup(
                          Readonly('map'),
                          Readonly('round'),
                          Readonly('score'),
                          show_border=True,
                          style_sheet='*{font: Futura; font-size:20px; font-weight:bold; font-style:italic; background-color: #6c57ab; color: white; }',
                          show_labels=True
                      ),
                       'semimajor_axis',
                       'eccentricity',
                       'inclination',
                       Item('scene2',
                            editor=SceneEditor(), height=250,
                            width=300, show_label=False),
                        UItem('guessbutton', style_sheet='*{font: Futura; font-size:12px; font-weight:bold; font-style:italic; background-color:#70b92d; color: white;}'),
                       show_labels=True,
                       padding=15
                  ),
                ),
                resizable=True,
                )


m = MyDialog()
m.configure_traits()
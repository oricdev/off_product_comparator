# coding=utf-8
from __future__ import division
from numpy import pi
import numpy


# The algorithm below is strongly inspired from the one available here:
# http://stackoverflow.com/questions/5408276/sampling-uniformly-distributed-random-points-inside-a-spherical-volume
# This is here a repartition on a disk instead on a sphere (1 angle required and 2 coordinates)
class PointRepartition:
    def __init__(self, nb_particles):
        self.number_of_particles = nb_particles

    def new_positions_spherical_coordinates(self):
        """
        Sample of returns:
        x = array([[-0.01886142], [-0.04094547], [-0.53896705]]) //
        y = array([[-0.11048884], [-0.42567348], [ 0.557865  ]])
        :return:
        """
        radius = numpy.random.uniform(0.0, 1.0, (self.number_of_particles, 1))
        theta = numpy.random.uniform(-1., 1., (self.number_of_particles, 1)) * pi
        x = radius * numpy.sin(theta)
        y = radius * numpy.cos(theta)
        return x, y


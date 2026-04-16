# ruff: noqa
# type: ignore
import numpy as np
from cmu_graphics import *


def onAppStart(app):  # type: ignore
    app.stimuliRadius = 100
    app.dots = generateDotVelocities(app, 0.1, 100, dir=-1, vel=5)
    pass


class Dot:
    def __init__(self, vel, stimuliRadius):
        self.vel = vel
        self.pos = generatePosition(stimuliRadius)


def generatePosition(stimuliRadius):
    r = np.random.uniform(0, stimuliRadius)
    theta = np.random.uniform(0, 2 * np.pi)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return [x, y]


def generateDotVelocities(app, coherence, numDots, dir=1, vel=1):
    stimuliRadius = app.stimuliRadius
    numCoherent = int(coherence * numDots)
    numRand = numDots - numCoherent

    dots = []
    for _ in range(numCoherent):
        velocity = (dir * vel, 0)
        dots.append(
            Dot(
                velocity,
                stimuliRadius,
            )
        )
    for _ in range(numRand):
        speed = vel  # np.random.uniform(0, vel)
        theta = np.random.uniform(0, 2 * np.pi)
        velocity = (speed * np.cos(theta), speed * np.sin(theta))
        dots.append(
            Dot(
                velocity,
                stimuliRadius,
            )
        )
    return dots


def redrawAll(app):

    for dot in app.dots:
        cx, cy = dot.pos
        drawCircle(app.width / 2 + cx, app.height / 2 + cy, 3)


def onStep(app):
    for dot in app.dots:
        dot.pos[0] += dot.vel[0]
        dot.pos[1] += dot.vel[1]
        if outsideCircle(app, dot):
            theta = np.arctan2(dot.pos[1], dot.pos[0])
            r = np.sqrt(dot.pos[0] ** 2 + dot.pos[1] ** 2)

            if r >= app.stimuliRadius:
                r = 0.95 * app.stimuliRadius
            dot.pos[0] = r * np.cos(theta + np.pi)
            dot.pos[1] = r * np.sin(theta + np.pi)


def outsideCircle(app, dot):
    cx, cy = dot.pos
    return cx**2 + cy**2 >= app.stimuliRadius**2


runApp()
# cmu_graphics.run()

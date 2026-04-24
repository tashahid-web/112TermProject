###############################################
# Contains Utils to handle dot motion

import numpy as np


class Dot:
    def __init__(self, vel, stimuliRadius):
        self.vel = vel
        self.stimuliRadius = stimuliRadius
        self.pos = self.generatePosition(stimuliRadius)
        self.age = 0

    def generatePosition(
        self, stimuliRadius
    ):  #### Used VSCode AI debugger to fix missing self argument in function ####
        r = np.random.uniform(0, stimuliRadius)
        theta = np.random.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return [x, y]

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.age += 1

    def outsideCircle(self):
        cx, cy = self.pos
        return cx**2 + cy**2 >= self.stimuliRadius**2


def generateDots(app, coherence, numDots=50, dir=1, vel=1):
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


def updateDots(app):
    dots = app.dots
    for i, dot in enumerate(dots):
        dot.update()
        if dot.age == 3 or dot.outsideCircle():
            dot.pos = dot.generatePosition(dot.stimuliRadius)
    return dots

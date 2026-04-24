import numpy as np
from cmu_graphics import *
from dots import updateDots, generateDots
import cv2
from gaze_tracking import GazeTracking

"""
Rather than using screens, use strings for app.state:

"menu"

"""

gaze = GazeTracking()
webcam = cv2.VideoCapture(1)


def onAppStart(app):
    app.velocity = 50
    app.stimuliRadius = 300
    dir = np.random.choice([-1, 1])
    app.dots = generateDots(app, 0.4, dir=dir, vel=app.velocity)


def redrawAll(app):
    drawDots(app)


def drawDots(app):
    for dot in app.dots:
        cx, cy = dot.pos
        drawCircle(app.width / 2 + cx, app.height / 2 + cy, 3)


def onStep(app):
    # _, frame = webcam.read()
    # gaze.refresh(frame)
    app.dots = updateDots(app)


runApp(width=1600, height=1000)
# cmu_graphics.run()

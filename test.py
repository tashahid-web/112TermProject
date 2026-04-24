from cmu_graphics import *
import cv2
from gaze_tracking import GazeTracking
from dots import updateDots, generateDots
from utils import generateTrials, generateTutorialTrials

"""
Rather than using screens, use strings for app.state:

"menu"
"instructions"
"tutorialTask"
    "fix"
    "stimulus"
    "decision"
    "debrief"
"task"
    "fix"
    "stimulus"
    "decision"
    "debrief"

"""

gaze = GazeTracking()
webcam = cv2.VideoCapture(1)


def onAppStart(app):
    app.velocity = 50
    app.stimuliRadius = 300
    # dir = np.random.choice([-1, 1])
    dir = 1
    app.dots = generateDots(app, 0.3, dir=dir, vel=app.velocity)
    app.trials = generateTrials()
    app.tutorialTrials = generateTutorialTrials()


def redrawAll(app):

    if app.state == "":
        pass
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

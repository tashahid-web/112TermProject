from cmu_graphics import *
import cv2
from gaze_tracking import GazeTracking
from dots import updateDots, generateDots
from utils import generateTrials, generateTutorialTrials, transformRatio, getDecision
import time
import numpy as np

STIMULUSFRAMES = 24
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
"calibrate"
    "center"
    "left"
    "right"
"""

gaze = GazeTracking()
webcam = cv2.VideoCapture(1)


def onAppStart(app):
    app.decisions = []
    app.velocity = 50
    app.stimuliRadius = 300
    app.currCoherence = 0.3
    app.currDir = 1
    app.dots = generateDots(app, app.currCoherence, dir=app.currDir, vel=app.velocity)
    app.trials = generateTrials()
    app.tutorialTrials = generateTutorialTrials()
    app.state = "calibrate"
    app.substate = "center"
    app.decision = None
    app.stateTimer = 0
    app.ratio = 0
    app.calibrations = {"center": [], "left": [], "right": []}
    app.finalCalibratedPositions = []
    app.correct = None
    app.integratedInformation = []


def redrawAll(app):

    if app.state == "menu":
        drawLabel("hi", app.width / 2, app.height / 2)

    if app.state == "calibrate":
        if app.substate == "center":
            drawFixation(app, app.width / 2, app.height / 2)
        if app.substate == "left":
            drawFixation(app, app.width / 8, app.height / 2)
        if app.substate == "right":
            drawFixation(app, 7 * app.width / 8, app.height / 2)
    if app.state == "task":
        pass
        # drawDots(app)

    if app.substate == "fix":
        drawFixation(app, app.width / 2, app.height / 2)

    if app.substate == "stimulus":
        drawDots(app)

    if app.substate == "decision":
        drawLabel(
            "O",
            app.ratio,
            app.height / 4,
            bold=True,
            size=50,
            fill="red",
            align="center",
        )
    if app.substate == "debrief":
        drawDebrief(app)


def drawDots(app):
    for dot in app.dots:
        cx, cy = dot.pos
        drawCircle(app.width / 2 + cx, app.height / 2 + cy, 3)


def drawFixation(app, cx, cy):
    drawLine(cx, cy - 25, cx, cy + 25)
    drawLine(cx - 25, cy, cx + 25, cy)


def drawDebrief(app):
    drawLabel("debrief", app.width / 2, app.height / 2)
    pass


def onStep(app):
    app.stateTimer += 1
    app.dots = updateDots(app)

    if app.state == "calibrate":
        _, frame = webcam.read()
        gaze.refresh(frame)
        if gaze.horizontal_ratio() is not None:
            app.ratio = 1 - gaze.horizontal_ratio()

        if app.ratio is not None:
            app.calibrations[app.substate].append(app.ratio)

        if app.stateTimer / app.stepsPerSecond > 1:
            app.finalCalibratedPositions.append(
                np.median(app.calibrations[app.substate])
            )
            if app.substate == "center":
                updateState(app, None, "left")
            elif app.substate == "left":
                updateState(app, None, "right")
            elif app.substate == "right":
                app.finalCalibratedPositions[0], app.finalCalibratedPositions[1] = (
                    app.finalCalibratedPositions[1],
                    app.finalCalibratedPositions[0],
                )  # Flipping index 0 and 1 to get calibrated positions from left to right
                updateState(app, "menu", None)
    if app.substate == "fix":
        time.sleep(0.5)
        updateState(app, None, "stimulus")

    if app.substate == "stimulus":
        if app.stateTimer > STIMULUSFRAMES:
            updateState(app, None, "decision")

    if app.substate == "decision":
        _, frame = webcam.read()
        gaze.refresh(frame)
        horizontalRatio = gaze.horizontal_ratio()
        if app.ratio is not None:
            app.ratio = transformRatio(app, horizontalRatio)
            app.integratedInformation.append(app.ratio)
        decision, correct = getDecision(app)
        if decision is not None:
            app.decision = decision
            app.correct = correct
            updateState(app, None, "debrief")
        if app.stateTimer / app.stepsPerSecond >= 3:
            app.decision = None
            updateState(app, None, "debrief")

    if app.substate == "debrief":
        if app.stateTimer == 1:
            if app.state == "task" and len(app.trials["coherences"]) > 0:
                currCoherence = app.trials["coherences"].pop()
                currDir = app.trials["dirs"].pop()
            elif (
                app.state == "tutorialTask"
                and len(app.tutorialTrials["coherences"]) > 0
            ):
                app.currCoherence = app.tutorialTrials["coherences"].pop()
                app.currDir = app.tutorialTrials["dirs"].pop()
            app.dots = generateDots(
                app, currCoherence, 50, dir=currDir, vel=app.velocity
            )
        if app.stateTimer / app.stepsPerSecond > 1:
            app.integratedInformation = []
            updateState(app, None, "fix")


def updateState(app, newState, newSubstate):
    if newState is not None:
        app.state = newState
    if newSubstate is not None:
        app.substate = newSubstate
    app.stateTimer = 0


runApp(width=1600, height=1000)
# cmu_graphics.run()

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


class Button:
    def __init__(self, cx, cy, width, height, label):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.label = label
        self.size = 1

    def overButton(self, mouseX, mouseY):
        return (
            abs(mouseX - self.cx) <= self.width // 2
            and abs(mouseY - self.cy) <= self.height // 2
        )


def onAppStart(app):
    app.decisions = []
    app.velocity = 50
    app.stimuliRadius = 300
    app.currCoherence = 0.3
    app.currDir = 1
    app.dots = generateDots(app, app.currCoherence, dir=app.currDir, vel=app.velocity)
    app.trials = generateTrials()
    app.tutorialTrials = generateTutorialTrials()
    print(app.tutorialTrials)
    app.state = "menu"
    app.substate = "None"
    app.decision = None
    app.stateTimer = 0
    app.ratio = 0
    app.calibrations = {"center": [], "left": [], "right": []}
    app.finalCalibratedPositions = [0.35, 0.5, 0.65]
    app.correct = None
    app.integratedInformation = []
    app.buttons = [
        Button(app.width / 2, 1.15 * app.height / 2, 200, 50, "Tutorial"),
        Button(app.width / 2, 1.3 * app.height / 2, 200, 50, "Calibration"),
        Button(app.width / 2, 1.45 * app.height / 2, 200, 50, "Start Task"),
    ]


def drawButton(app, button):
    drawRect(
        button.cx,
        button.cy,
        button.size * button.width,
        button.size * button.height,
        fill=rgb(149, 17, 32),
        border="black",
        borderWidth=3,
        align="center",
    )
    drawLabel(
        button.label,
        button.cx,
        button.cy,
        size=35 * button.size,
        align="center",
        font="times new roman",
        fill="white",
        bold=True,
    )


def redrawAll(app):

    if app.state == "menu":
        drawLabel(
            "Random Dot Motion",
            app.width / 2,
            0.75 * app.height / 2,
            size=100,
            align="center",
            font="times new roman",
            bold=True,
        )
        for button in app.buttons:
            drawButton(app, button)
        drawLabel(
            "Psychometric Task",
            app.width / 2,
            1 * app.height / 2,
            size=100,
            align="center",
            font="times new roman",
            bold=True,
        )
        drawImage(
            "https://events.mcs.cmu.edu/scan2022-temp/wp-content/uploads/sites/29/2022/07/scan_ni.png",
            10,
            10,
            width=250,
            height=200,
            align="left-top",
        )

    if app.state == "calibrate":
        if app.substate == "center":
            drawFixation(app, app.width / 2, app.height / 2)
        if app.substate == "left":
            drawFixation(app, app.width / 8, app.height / 2)
        if app.substate == "right":
            drawFixation(app, 7 * app.width / 8, app.height / 2)

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
    if app.decision is None:
        drawLabel(
            "Ran out of time",
            app.width / 2,
            app.height / 2,
            size=50,
            fill="red",
            bold=True,
            font="times new roman",
        )
    else:
        if app.correct:
            drawLabel(
                "Correct",
                app.width / 2,
                app.height / 2,
                size=50,
                fill="green",
                bold=True,
                font="times new roman",
            )
        else:
            drawLabel(
                "Wrong",
                app.width / 2,
                app.height / 2,
                size=50,
                fill="red",
                bold=True,
                font="times new roman",
            )


def onStep(app):
    app.stateTimer += 1
    app.dots = updateDots(app)

    if app.state == "menu":
        if app.stateTimer == 1:
            app.trials = generateTrials()
            app.tutorialTrials = generateTutorialTrials()

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
        if app.state == "tutorialTask":
            time.sleep(1)
        else:
            time.sleep(0.5)
        updateState(app, None, "stimulus")

    if app.substate == "stimulus":
        if app.stateTimer > STIMULUSFRAMES:
            updateState(app, None, "decision")

    if app.substate == "decision":
        _, frame = webcam.read()
        gaze.refresh(frame)
        print(app.trials)
        horizontalRatio = gaze.horizontal_ratio()
        if horizontalRatio is not None:
            app.ratio = transformRatio(app, horizontalRatio)
            app.integratedInformation.append(app.ratio)
        decision, correct = getDecision(app)
        if decision is not None:
            app.decision = decision
            app.correct = correct
            updateState(app, None, "debrief")
        if app.stateTimer / app.stepsPerSecond >= 1:
            app.decision = None
            updateState(app, None, "debrief")

    if app.substate == "debrief":
        if app.stateTimer == 1:
            if app.state == "task" and len(app.trials["coherences"]) > 0:
                app.currCoherence = app.trials["coherences"].pop()
                app.currDir = app.trials["dirs"].pop()
            elif app.state == "task":  # Done with trials
                updateState(app, "menu", "None")
            elif (
                app.state == "tutorialTask"
                and len(app.tutorialTrials["coherences"]) > 0
            ):
                app.currCoherence = app.tutorialTrials["coherences"].pop()
                app.currDir = app.tutorialTrials["dirs"].pop()
            else:  # Done with tutorial
                time.sleep(0.5)
                updateState(app, "menu", "None")

            app.dots = generateDots(
                app, app.currCoherence, 50, dir=app.currDir, vel=app.velocity
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


def onMouseMove(app, mouseX, mouseY):
    for button in app.buttons:
        if button.overButton(mouseX, mouseY):
            button.size = 1.2
        else:
            button.size = 1


def onMousePress(app, mouseX, mouseY):
    for button in app.buttons:
        if button.overButton(mouseX, mouseY):
            if button.label == "Tutorial":
                updateState(app, "tutorialTask", "fix")

            if button.label == "Calibration":
                updateState(app, "calibrate", "center")

            if button.label == "Start Task":
                updateState(app, "task", "fix")


runApp(width=1600, height=1000)
# cmu_graphics.run()

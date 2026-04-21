# ruff: noqa
# type: ignore
import numpy as np
from cmu_graphics import *
import cv2
from gaze_tracking import GazeTracking
import time

gaze = GazeTracking()
webcam = cv2.VideoCapture(1)


def onAppStart(app):  # type: ignore
    app.startButton = {"size": 1, "cx": app.width // 2, "cy": 3 * app.height / 4}
    app.state = "menu"
    app.stimuliRadius = 100
    app.dots = generateDotVelocities(app, 0.5, 50, dir=-1, vel=20)
    app.gaze = None
    app.ratio = 0
    app.stepsPerSecond = 30
    app.centerCalibration = []
    app.leftCalibration = []
    app.rightCalibration = []
    app.calibrationFrames = 0
    app.finalCalibratedPositions = []
    app.integratedInformation = []
    app.decision = None
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

    if app.state == "menu":
        drawRect(
            app.width // 2,
            app.startButton["cy"],
            app.startButton["size"] * 100,
            app.startButton["size"] * 50,
            fill="lightBlue",
            border="black",
            borderWidth=3,
            align="center",
        )
        drawLabel(
            "Start",
            app.width // 2,
            app.startButton["cy"],
            size=35 * app.startButton["size"],
            align="center",
        )
    if app.state == "task":
        if app.ratio is not None:
            ratio = app.ratio
            transformedRatio = (
                (ratio - app.finalCalibratedPositions[0])
                / (app.finalCalibratedPositions[2] - app.finalCalibratedPositions[0])
                * app.width
            )
            if app.ratio < app.finalCalibratedPositions[0]:
                ratio = app.finalCalibratedPositions[0]
            if app.ratio > app.finalCalibratedPositions[2]:
                ratio = app.finalCalibratedPositions[2]
            drawLabel(
                "O",
                transformedRatio,
                app.height / 4,
                bold=True,
                size=50,
                fill="red",
                align="center",
            )
        for dot in app.dots:
            cx, cy = dot.pos
            drawCircle(app.width / 2 + cx, app.height / 2 + cy, 3)

    if app.state == "calibrateCenter":
        drawLabel(f"Stare Here", app.width / 2, app.height / 2)
    if app.state == "calibrateLeft":
        drawLabel(f"Stare Here", app.width / 4, app.height / 2)
    if app.state == "calibrateRight":
        drawLabel(f"Stare Here", 3 * app.width / 4, app.height / 2)


def overButton(button, mouseX, mouseY, width, height):
    buttonX = button["cx"]
    buttonY = button["cy"]
    return (
        abs((mouseX + 50) - buttonX) <= width // 2
        and abs(mouseY - buttonY) <= height // 2
    )


def onStep(app):
    if app.state == "task":
        _, frame = webcam.read()
        gaze.refresh(frame)
        oldRatio = app.ratio
        app.ratio = gaze.horizontal_ratio()
        if app.ratio is not None:
            app.ratio = 1 - app.ratio
            transformedRatio = (
                (app.ratio - app.finalCalibratedPositions[0])
                / (app.finalCalibratedPositions[2] - app.finalCalibratedPositions[0])
                * app.width
            )
            app.integratedInformation.append(transformedRatio)
        else:
            app.ratio = oldRatio
        ################################################################
        if len(app.integratedInformation) >= 5:
            avg = np.mean(app.integratedInformation)
            if avg <= app.width // 8:
                app.decision = "left"
            elif avg >= app.width * 7 // 8:
                app.decision = "right"
            if app.decision is not None:
                print(app.decision)
                app.state = "menu"
        ################################################################
        if gaze.is_center():
            app.gaze = "center"
        elif gaze.is_left():
            app.gaze = "left"
        elif gaze.is_right():
            app.gaze = "right"

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
    if app.state in ["calibrateCenter", "calibrateLeft", "calibrateRight"]:
        app.calibrationFrames += 1
        _, frame = webcam.read()
        gaze.refresh(frame)
        app.ratio = gaze.horizontal_ratio()
        if app.ratio is not None:
            app.ratio = 1 - app.ratio

        if app.state == "calibrateCenter":
            if app.ratio is not None:
                app.centerCalibration.append(app.ratio)
            if app.calibrationFrames // app.stepsPerSecond == 1:
                app.state = "calibrateLeft"
                app.finalCalibratedPositions.append(np.median(app.centerCalibration))
                app.calibrationFrames = 0
        if app.state == "calibrateLeft":
            if app.ratio is not None:
                app.leftCalibration.append(app.ratio)
            if app.calibrationFrames // app.stepsPerSecond == 1:
                app.state = "calibrateRight"
                app.finalCalibratedPositions.append(np.median(app.leftCalibration))
                app.calibrationFrames = 0
        if app.state == "calibrateRight":
            if app.ratio is not None:
                app.rightCalibration.append(app.ratio)
            if app.calibrationFrames // app.stepsPerSecond == 1:
                app.state = "task"
                app.finalCalibratedPositions.append(np.median(app.rightCalibration))
                app.calibrationFrames = 0
                print(app.finalCalibratedPositions)


def onMouseMove(app, mouseX, mouseY):
    if overButton(
        app.startButton,
        mouseX,
        mouseY,
        100 * app.startButton["size"],
        50 * app.startButton["size"],
    ):
        app.startButton["size"] = 1.2
    else:
        app.startButton["size"] = 1


def onMousePress(app, mouseX, mouseY):
    if (
        overButton(
            app.startButton,
            mouseX,
            mouseY,
            100 * app.startButton["size"],
            50 * app.startButton["size"],
        )
        and app.state == "menu"
    ):
        app.state = "calibrateCenter"


def outsideCircle(app, dot):
    cx, cy = dot.pos
    return cx**2 + cy**2 >= app.stimuliRadius**2


runApp(width=1600, height=1000)
# cmu_graphics.run()

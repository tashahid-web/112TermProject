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
    app.startButton = {"size": 1, "cx": app.width / 2, "cy": 3 * app.height / 4}
    app.state = "menu"
    app.stimuliRadius = 100
    app.dots = generateDotVelocities(app, 0.5, 50, dir=-1, vel=20)
    app.gaze = None
    app.ratio = 0
    app.stepsPerSecond = 1000
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
            app.startButton["cx"],
            app.startButton["cy"],
            app.startButton["size"] * 100,
            app.startButton["size"] * 50,
            align="center",
            fill="lightBlue",
            border="black",
            borderWidth=3,
        )
        drawLabel(
            "Start",
            app.startButton["cx"],
            app.startButton["cy"],
            size=35 * app.startButton["size"],
        )
    if app.state == "task":
        if app.ratio is not None:
            drawLabel(
                "point",
                app.width * (1 - app.ratio),
                app.height / 4,
                bold=True,
                size=50,
                fill="red",
            )

        for dot in app.dots:
            cx, cy = dot.pos
            drawCircle(app.width / 2 + cx, app.height / 2 + cy, 3)

        if app.gaze == "center":
            pass
            # drawLabel(
            #     "center", app.width / 2, app.height / 4, bold=True, size=50, fill="red"
            # )
        elif app.gaze == "left":
            pass
            # drawLabel("left", app.width / 8, app.height / 4, bold=True, size=50, fill="red")
        elif app.gaze == "right":
            pass
            # drawLabel(
            #     "right", app.width * 7 / 8, app.height / 4, bold=True, size=50, fill="red"
            # )


def overButton(button, mouseX, mouseY, width, height):
    buttonX = button["cx"]
    buttonY = button["cy"]
    return abs(mouseX - buttonX) <= width // 2 and abs(mouseY - buttonY) <= height // 2


def onStep(app):
    if app.state == "task":
        _, frame = webcam.read()
        gaze.refresh(frame)
        app.ratio = gaze.horizontal_ratio()
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
    if overButton(
        app.startButton,
        mouseX,
        mouseY,
        100 * app.startButton["size"],
        50 * app.startButton["size"],
    ):
        app.state = "task"


def outsideCircle(app, dot):
    cx, cy = dot.pos
    return cx**2 + cy**2 >= app.stimuliRadius**2


runApp()
# cmu_graphics.run()

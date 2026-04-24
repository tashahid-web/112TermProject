###############################################
# Contains general utility functions
# From testing, seems that 0.30 coherence is safely an "easy" upper bound, sample
# coherences of 0, 0.05, 0.1, 0.2, 0.25, 0.3 ==> 11 total coherences for both dirs

import numpy as np

COHERENCES = [0.1, 0.9]  # fmt: off
TRIALSPERCOHERENCE = 6


def generateTrials():
    trialCoherences = []
    for coherence in COHERENCES:
        trialCoherences.extend([coherence] * TRIALSPERCOHERENCE * 2)
    np.random.shuffle(trialCoherences)

    trialDirs = [np.random.choice([-1, 1]) for _ in range(len(trialCoherences))]

    trials = {"coherences": trialCoherences, "dirs": trialDirs}
    return trials


def generateTutorialTrials():
    trialCoherences = []
    for coherence in [0, 0.2, 0.4, 0.9]:
        trialCoherences.extend([coherence] * 2)
    np.random.shuffle(trialCoherences)

    trialDirs = [np.random.choice([-1, 1]) for _ in range(len(trialCoherences))]

    trials = {"coherences": trialCoherences, "dirs": trialDirs}
    return trials


def transformRatio(app, horizontalRatio):
    horizontalRatio = 1 - horizontalRatio
    transformedRatio = (
        (horizontalRatio - app.finalCalibratedPositions[0])
        / (app.finalCalibratedPositions[2] - app.finalCalibratedPositions[0])
        * app.width
    )
    return transformedRatio


def getDecision(app):
    if len(app.integratedInformation) >= 5:
        avg = np.mean(app.integratedInformation[-10:])
        if avg <= app.width // 6:
            decision = "left"
            correct = True if app.currDir == -1 else False
        elif avg >= app.width * 5 // 6:
            decision = "right"
            correct = True if app.currDir == 1 else False
        else:
            return None, None
        return decision, correct
    return None, None

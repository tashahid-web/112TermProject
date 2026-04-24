###############################################
# Contains general utility functions
# From testing, seems that 0.30 coherence is safely an "easy" upper bound, sample
# coherences of 0, 0.05, 0.1, 0.2, 0.25, 0.3 ==> 11 total coherences for both dirs

import numpy as np

COHERENCES = [-0.3, -0.25, -0.2, -0.15, -.1, -.05, 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.30]  # fmt: off
TRIALSPERCOHERENCE = 6


def generateTrials():
    trialCoherences = []
    for coherence in COHERENCES:
        trialCoherences.extend([coherence] * TRIALSPERCOHERENCE)
    np.random.shuffle(trialCoherences)

    trialDirs = [np.random.choice([-1, 1]) for _ in range(len(trialCoherences))]

    trials = {"coherences": trialCoherences, "dirs": trialDirs}
    return trials


def generateTutorialTrials():
    trialCoherences = []
    for coherence in [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]:
        trialCoherences.extend([coherence] * 2)
    np.random.shuffle(trialCoherences)

    trialDirs = [np.random.choice([-1, 1]) for _ in range(len(trialCoherences))]

    trials = {"coherences": trialCoherences, "dirs": trialDirs}
    return trials

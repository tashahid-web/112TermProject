import numpy as np
from pymer4.models import glm
import pandas as pd
import polars as pl
import plotly.express as px


def processData(data):

    trialMat = pd.DataFrame(data)
    trialMat["signedCoherence"] = trialMat["coherence"] * trialMat["correctChoice"]
    trialMat["choiceRight"] = [1 if dir == "right" else 0 for dir in trialMat["choice"]]

    return trialMat


def fitGLM(data):
    trialMat = processData(data)
    trialMat = pl.DataFrame(trialMat)
    glmModel = glm(
        "choiceRight ~ signedCoherence", data=trialMat, family="binomial", link="logit"
    )
    glmModel.fit()

    return glmModel


def getPsychometricCurvePlot(data):
    glmModel = fitGLM(data)
    coherenceBound = np.max(data["coherence"])
    plotPoints = np.linspace(-coherenceBound, coherenceBound, 1000)
    predData = {"signedCoherence": plotPoints}
    predictionData = glmModel.empredict(predData)
    choiceRight = predictionData.get_column("prob").to_list()

    assert np.shape(plotPoints) == np.shape(choiceRight)
    return plotPoints, choiceRight, glmModel


def createPsychometricCurveFigure(data):
    plotPoints, choiceRight, glmModel = getPsychometricCurvePlot(data)
    fig = px.scatter(x=plotPoints, y=choiceRight, title="Simple Array Scatter")
    fig.update_layout(
        {"plot_bgcolor": "rgba(255,255,255,1)", "paper_bgcolor": "rgba(255,255,255,1)"}
    )
    fig.update_layout(
        title=dict(text="Your Psychometric Curve", x=0.5),
        xaxis=dict(title=dict(text="Coherence")),
        yaxis=dict(title=dict(text="% Choice Right")),
        font=dict(family="Times New Roman", size=18, color="Black"),
    )  # TAKEN FROM: https://plotly.com/python/figure-labels/
    fig.update_layout(title_x=0.5)

    fig.update_traces(marker=dict(color="red"))
    fig.add_vline(0, line_dash="dash", line_color="black")
    fig.add_hline(0.5, line_dash="dash", line_color="black")
    fig.write_image("PsychometricCurve.png")
    return glmModel

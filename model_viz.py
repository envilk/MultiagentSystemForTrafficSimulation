"""
The full code should now look like:
"""
import mesa
from model import TrafficModel
from agents import TrafficLightAgent, VehicleAgent
from overload_canvas_grid import CanvasGrid


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 1}

    if type(agent) is TrafficLightAgent:
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 0
    elif type(agent) is VehicleAgent:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal

width = 6
height = 7
# in python [height, width] for grid, in js [width, height]
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)
server = mesa.visualization.ModularServer(
    TrafficModel, [grid], "Money Model", {"width": width, "height": height, "max_steps": 10,
                                          "non_transitable_cells": 6,  "vehicles": 10}
)
server.port = 8521  # The default
server.launch()

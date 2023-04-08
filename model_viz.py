"""
The full code should now look like:
"""
import mesa
from model import TrafficModel
from agents import TrafficLightAgent, VehicleAgent
from overload_canvas_grid import CanvasGrid


def agent_portrayal(agent, cell):
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "h": 1,
                 "w": 1}

    # if agent == true, the code bellow is useless
    if cell == -1:
        portrayal["Color"] = "Darkblue"
        portrayal["Layer"] = 0
    else:
        pos_x = [1, 0, -1, 0]
        pos_y = [0, -1, 0, 1]
        portrayal["Shape"] = "arrowHead"
        portrayal["Color"] = "grey"
        portrayal["scale"] = 0.3
        portrayal["heading_x"] = pos_x[cell]
        portrayal["heading_y"] = pos_y[cell]
        portrayal["Layer"] = 1

    if agent:
        if type(agent) is TrafficLightAgent and agent.state():
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
            portrayal["Color"] = "lightgreen"
            portrayal["Layer"] = 0
        elif type(agent) is TrafficLightAgent and not agent.state():
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
            portrayal["Color"] = "#FF5F5F"
            portrayal["Layer"] = 0
        elif type(agent) is VehicleAgent:
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
            portrayal["Color"] = "black"
            portrayal["Layer"] = 2
            portrayal["h"] = 0.4
            portrayal["w"] = 0.4

    return portrayal

width = 24
height = 12

chart = mesa.visualization.ChartModule([{"Label": "Total waiting time for vehicles",
                                         "Color": "Black"},
                                        {"Label": "Waiting time for vehicles in front",
                                         "Color": "Blue"},
                                        {"Label": "Waiting time for traffic lights",
                                         "Color": "Red"}
                                        ],
                                       data_collector_name='datacollector')

# in python [height, width] for grid, in js [width, height]
grid = CanvasGrid(agent_portrayal, width, height, 35 * width, 35 * height)
server = mesa.visualization.ModularServer(
    TrafficModel, [grid, chart], "Traffic Model", {"width": width, "height": height, "max_steps": 50,
                                                   "non_transitable_cells": 10, "vehicles": 10,
                                                   "max_waiting_time_non_transitable_in_steps": 5}
)
server.port = 8521  # The default
server.launch()

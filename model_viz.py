"""
The full code should now look like:
"""
import mesa
from model import TrafficModel
from agents import TrafficLightAgent, VehicleAgent
from overload_canvas_grid import CanvasGrid


def agent_portrayal(agent):
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "h": 1,
                 "w": 1}

    if type(agent) is TrafficLightAgent and agent.state():
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0
    elif type(agent) is TrafficLightAgent and not agent.state():
        portrayal["Color"] = "#FF5F5F"
        portrayal["Layer"] = 0
    elif type(agent) is VehicleAgent:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["h"] = 0.3
        portrayal["w"] = 0.3
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
    TrafficModel, [grid, chart], "Traffic Model", {"width": width, "height": height, "max_steps": 10,
                                                   "non_transitable_cells": 3, "vehicles": 10,
                                                   "max_waiting_time_non_transitable_in_steps": 5}
)
server.port = 8521  # The default
server.launch()

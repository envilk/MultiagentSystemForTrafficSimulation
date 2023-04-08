"""
Author: Enrique Vilchez Campillejo
"""

import mesa
from model import TrafficModel
from agents import TrafficLightAgent, VehicleAgent
from overload_canvas_grid import CanvasGrid


# creates agent dictionary for rendering it on Canvas Gird
def agent_portrayal(agent, cell):
    portrayal = {"Shape": "rect", "Filled": "true", "h": 1, "w": 1}
    if cell == -1:
        portrayal.update({"Color": "Darkblue", "Layer": 0})
    else:
        pos_x, pos_y = [[1, 0, -1, 0], [0, -1, 0, 1]]
        portrayal.update({
            "Shape": "arrowHead", "Color": "grey", "scale": 0.3,
            "heading_x": pos_x[cell], "heading_y": pos_y[cell], "Layer": 1})
    if isinstance(agent, TrafficLightAgent):
        if agent.state():
            portrayal.update({"Shape": "rect", "Color": "lightgreen", "Layer": 0})
        else:
            portrayal.update({"Shape": "rect", "Color": "#FF5F5F", "Layer": 0})
    elif isinstance(agent, VehicleAgent):
        portrayal.update({"Shape": "rect", "Color": "black", "Layer": 2, "h": 0.4, "w": 0.4})
    return portrayal


width = 24
height = 12

# chart for metrics visualization
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
# initizalize Modular server for mesa Python visualization
server = mesa.visualization.ModularServer(
    TrafficModel, [grid, chart], "Traffic Model", {"width": width, "height": height, "max_steps": 100,
                                                   "non_transitable_cells": 10, "vehicles": 5,
                                                   "max_waiting_time_non_transitable_in_steps": 2,
                                                   "second_scenario": True, "third_scenario": True}
)
server.port = 8521  # The default
server.launch()

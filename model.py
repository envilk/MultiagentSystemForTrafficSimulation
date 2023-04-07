"""
Author: Enrique Vilchez Campillejo
"""

import mesa
from agents import TrafficLightAgent, VehicleAgent
import matplotlib.pyplot as plt
import numpy as np
import random


class TrafficModel(mesa.Model):
    """A model with some number of agents."""

    def compute_waiting_time_for_vehicles_in_front(self):
        waiting_for_vehicles_in_front = [agent.waiting_for_cars for agent in self.schedule.agents if type(agent) is VehicleAgent]
        return sum(waiting_for_vehicles_in_front)

    def compute_total_waiting_time_traffic_lights(self):
        waiting_traffic_lights = [agent.waiting_traffic_lights for agent in self.schedule.agents if type(agent) is VehicleAgent]
        return sum(waiting_traffic_lights)

    def compute_total_waiting_time(self):
        waiting_for_vehicles_in_front = [agent.waiting_for_cars for agent in self.schedule.agents if type(agent) is VehicleAgent]
        waiting_traffic_lights = [agent.waiting_traffic_lights for agent in self.schedule.agents if type(agent) is VehicleAgent]
        total_waiting_time = sum(waiting_for_vehicles_in_front) + sum(waiting_traffic_lights)
        return total_waiting_time

    def __init__(self, width, height, max_steps, non_transitable_cells,
                 vehicles, max_waiting_time_non_transitable_in_steps):
        self.width = width
        self.height = height
        self.restriction_matrix = []

        # Inverted width and height order, because of matrix accessing purposes, like in many examples:
        #   https://snyk.io/advisor/python/Mesa/functions/mesa.space.MultiGrid
        self.grid = mesa.space.MultiGrid(height, width, False)
        self.max_steps = max_steps
        self.max_waiting_time_non_transitable_in_steps = max_waiting_time_non_transitable_in_steps
        self.schedule = mesa.time.BaseScheduler(self)

        self.total_amount_cells = width * height
        self.steps_counter = 0
        self.non_transitable_cells = int((non_transitable_cells / 100) *
                                        self.total_amount_cells)
        self.transitable_cells = self.total_amount_cells - self.non_transitable_cells

        self.generate_matrix()
        self.total_amount_vehicles = int((vehicles / 100) *
                                         self.transitable_cells)
        self.total_amount_traffic_lights = self.set_traffic_lights()
        self.num_agents = self.total_amount_vehicles \
                          + self.total_amount_traffic_lights
        print('Agents: ', self.num_agents, ' Vehicles: ', self.total_amount_vehicles,
              ' Traffic lights: ', self.total_amount_traffic_lights)
        print('Total cells: ', self.total_amount_cells, ' Transitable cells: ', self.transitable_cells,
              ' Non transitable cells: ', self.non_transitable_cells)

        # Generate vehicles
        self.agents_list = []
        for i in range(self.total_amount_vehicles):
            unique_id = self.last_unique_id + i + 1
            a = VehicleAgent(unique_id, self)
            self.agents_list.append(a)

        # Traffic light and vehicle in front waiting time
        self.datacollector = mesa.DataCollector(
            model_reporters={"Total waiting time for vehicles": self.compute_total_waiting_time,
                             "Waiting time for vehicles in front": self.compute_waiting_time_for_vehicles_in_front,
                             "Waiting time for traffic lights": self.compute_total_waiting_time_traffic_lights}
        )

    # TODO al generar tener en cuenta 70% recto, 30% izq der, teniendo en cuenta
    # dentro de cada casilla de la que se procede (si en la casilla
    # actual hay dirección de la derecha, pues habrá que tener en cuenta
    # el vecino de la izquierda para ir recto, izq y der serían direcciones arriba
    # y abajo respectivamente)
    def generate_matrix(self):
        # creada de la misma manera que un numpy array (matrix[width][height]), y uso de
        # reversed para iterarla
        self.restriction_matrix = []
        non_transitable_cells_counter = 0

        for x in range(0, self.height):
            row = [0] * self.width
            for y in range(0, self.width):
                if x == self.height - 1 and y == 0:  # beginning cell
                    row[y] = 0  # first direction and cell is right and transitable
                else:
                    if random.random() <= 0.15 and non_transitable_cells_counter < self.non_transitable_cells:  # 15% probability to have a cell non transitable
                        row[y] = -1
                        non_transitable_cells_counter = + 1
                    else:
                        row[y] = 0
            self.restriction_matrix.append(row)

        previous_direction = 0

        for x, row in enumerate(reversed(self.restriction_matrix)):
            for y, cell in enumerate(row):
                if x == 0 and y == 0:
                    previous_direction = 0
                elif cell != -1:
                    if random.random() <= 0.80:
                        self.restriction_matrix[x][y] = previous_direction
                    elif random.random() <= 0.90:
                        self.restriction_matrix[x][y] = (previous_direction - 1) % 4
                    else:
                        self.restriction_matrix[x][y] = abs(previous_direction + 1) % 4

                previous_direction = self.restriction_matrix[x][y]

    # method for automatically setting traffic lights
    def set_traffic_lights(self):
        amount_traffic_lights = 0
        for x, row in enumerate(reversed(self.restriction_matrix)):
            for y, cell in enumerate(row):
                X = self.height - x - 1  # accessing rows from bottom to top
                if cell != -1:
                    unique_id = (x * self.width) + y  # 'normal' x for index purposes
                    self.last_unique_id = unique_id
                    new_traffic_light = TrafficLightAgent(unique_id, self, [0, 0])
                    crossing, _ = self.crossing_adjacent([X, y])
                    if crossing and random.random() <= 0.5:
                        self.schedule.add(new_traffic_light)
                        self.grid.place_agent(new_traffic_light, [x, y])  # 'normal' x for grid
                        amount_traffic_lights += 1
        return amount_traffic_lights

    def is_transitable(self, pos):
        transitable = False
        if self.restriction_matrix[self.height - pos[0] - 1][pos[1]] != -1:
            transitable = True
        return transitable

    def check_limits(self, pos):
        inside = False
        if pos[0] < 0 or pos[0] > self.height or pos[1] < 0 or pos[1] > self.width:
            inside = True
        return inside

    # when calling method, take care of returned value
    def get_direction(self, pos):
        direction = -1
        if self.is_transitable(pos):
            direction = self.restriction_matrix[self.height - pos[0] - 1][pos[1]]
        return direction

    # Possible uses:
    # 1: checks subtractions of an actual cell direction and
    #    the crossing adjacent (if actual dir is right, then adjacent cell is matrix[x][y+1],
    #    plus if abs(subtraction) is 2, then actual cell needs a traffic light
    # 2: obtains the position of the cell that the one passed by parameters is pointing to
    def crossing_adjacent(self, pos):
        crossing = False
        actual_dir = self.restriction_matrix[pos[0]][pos[1]]
        crossing_pos = []
        if actual_dir == 0:  # right
            crossing_pos = [pos[0], pos[1] + 1]
        elif actual_dir == 1:  # down
            crossing_pos = [pos[0] + 1, pos[1]]
        elif actual_dir == 2:  # left
            crossing_pos = [pos[0], pos[1] - 1]
        elif actual_dir == 3:  # up
            crossing_pos = [pos[0] - 1, pos[1]]

        # if adjacent is empty, then it is non transitable, not enter if statement
        # if adjacent is out of map limit, not enter if statement
        if crossing_pos and crossing_pos[0] < self.height and crossing_pos[1] < self.width \
                and crossing_pos[0] > -1 and crossing_pos[1] > -1:
            subtraction = abs(actual_dir - self.restriction_matrix[crossing_pos[0]][crossing_pos[1]])
            # 3 because of checking the case where dirs are 0 and 3 (right and up, independent of the order)
            if subtraction == 1 or subtraction == 3:
                crossing = True

        return crossing, crossing_pos

    def show_grid(self):
        agent_counts = np.zeros((self.grid.width, self.grid.height))
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            agent_count = len(cell_content)
            X = self.height - x - 1  # Access from bottom to top
            agent_counts[X][y] = agent_count
        plt.imshow(agent_counts, interpolation="nearest")
        plt.colorbar()
        plt.show()

    def step(self):
        if self.steps_counter < self.max_steps:
            self.datacollector.collect(self)
            # First, introduce all vehicles in the grid
            self.schedule.step()
            if self.agents_list:
                a = self.agents_list.pop(0)
                self.schedule.add(a)
                self.grid.place_agent(a, (0, 0))
            # self.show_grid()

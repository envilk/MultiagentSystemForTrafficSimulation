import mesa
import random

import agents


class TrafficLightAgent(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.time_green = random.randint(1, 3)
        self.time_red = random.randint(1, 10)
        self.time_green_counter = self.time_green
        self.time_red_counter = 0

    def state(self):
        state = True  # True is green, False is red
        if self.time_red_counter > 0:
            state = False
        return state

    def step(self):
        if self.time_red_counter == 0:
            if self.time_green_counter > 0:
                self.time_green_counter = self.time_green_counter - 1
            elif self.time_green_counter == 0:
                self.time_red_counter = self.time_red
        elif self.time_green_counter == 0:
            if self.time_red_counter > 0:
                self.time_red_counter = self.time_red_counter - 1
            elif self.time_red_counter == 0:
                self.time_green_counter = self.time_green
        #print(self.unique_id, self.time_green_counter, self.time_red_counter)


class VehicleAgent(mesa.Agent):
    """A vehicle agent with fixed ."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # starts at bottom left cell, like specified in mesa Docs,
        # MultiGrid has position [0, 0] in the bottom-left, and
        # [width-1, height-1] in the top-right

    def move(self):
        # TODO
        # 1: Check for traffic lights
        # 2: Check whether there are cars in neighborhood
        # 3: Check if cell where vehicle is moving is transitable
        # 4: move
        # ?
        direction = self.model.get_direction(self.pos)
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )

        # 1: check for traffic lights in actual self.pos
        traffic_light, state = self.traffic_light()
        # code can keep going checking if vehicle can move,
        # if there is not a traffic light, or there is one but is green
        if not traffic_light or (traffic_light and state):
            definitive_possible_steps = self.obtain_possible_steps_from_restriction_matrix(direction, possible_steps)

            #not_vehicle_in_front =
            if definitive_possible_steps:
                new_position = random.choice(definitive_possible_steps)
                self.model.grid.move_agent(self, tuple(new_position))
        elif traffic_light and not state: # there is a traffic light, and it's red
            print('Count waiting time for certain vehicle, in a traffic light')

    def obtain_possible_steps_from_restriction_matrix(self, direction, possible_steps):
        definitive_possible_steps = []
        for adjacent_position in possible_steps:
            aux = list(adjacent_position)
            aux2 = list(self.pos)
            adjacent_direction = self.model.get_direction(aux)
            # needed to put it here, DON'T PUT IT BEFORE
            aux[0] = self.model.height - aux[0] - 1
            aux2[0] = self.model.height - aux2[0] - 1
            _, crossing_from_adjacent_from_pos = self.model.crossing_adjacent(aux2)
            _, crossing_from_adjacent = self.model.crossing_adjacent(aux)
            crossing_from_adjacent_from_pos_bool = (crossing_from_adjacent_from_pos == aux)
            # revert matrix adaptation, to adapt to grid, DON'T PUT IT BEFORE
            aux[0] = abs(aux[0] - self.model.height + 1)
            if crossing_from_adjacent != aux2 and abs(direction - adjacent_direction) != 2 and \
                    abs(direction - adjacent_direction) != 0 or \
                    crossing_from_adjacent_from_pos_bool:
                if not self.model.check_limits(aux):
                    definitive_possible_steps.append(aux)
        return definitive_possible_steps

    def traffic_light(self):
        traffic_light = False
        state = False
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for a in cellmates:
            if type(a) is agents.TrafficLightAgent:
                traffic_light = True
                state = a.state()
        return traffic_light, state

    def step(self):
        self.move()

import mesa
import random


class TrafficLightAgent(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.time_green = random.randint(1, 10)
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
                self.time_green_counter = - 1
            elif self.time_green_counter == 0:
                self.time_red_counter = self.time_red
        elif self.time_green_counter == 0:
            if self.time_red_counter > 0:
                self.time_red_counter = - 1
            elif self.time_red_counter == 0:
                self.time_green_counter = self.time_green


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
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        print(possible_steps)
        new_position = self.model.get_direction(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    def step(self):
        #self.move()
        print('moving')

import pygame
from sensor import Sensor
from world import World
# robot is simply a blob of color that can move in any direction

class Robot:
    def __init__(self, world : World, start_pos) -> None:
        self.color = (255, 0, 0)
        self.position = list(start_pos)
        self.radius = 15
        self.sensor = Sensor(self)
        self.world : World = world

    def move(self, dx, dy):
        new_x = dx + self.get_pos_x()
        new_y = dy + self.get_pos_y()
        
        if not self.world.get_world()[new_y][new_x]: #0 is free space
            self.set_pos( new_x,  new_y )
            return True
        return False
    
    def move_up(self): return self.move(0, -1)
    def move_down(self): return self.move(0, 1)
    def move_left(self): return self.move(-1, 0)
    def move_right(self): return self.move(1, 0)


    def render(self, screen, cell_size):
        # Convert grid coordinates to pixel coordinates (center of cell)
        x = self.position[0] * cell_size + cell_size // 2
        y = self.position[1] * cell_size + cell_size // 2
        pygame.draw.circle(screen, self.color, (x, y), self.radius)
        
        # Render sensor
        self.sensor.render(screen, cell_size)
    
    #get and setters
    
    def get_pos(self):
        return self.position
    
    def get_pos_y(self):
        return self.get_pos()[1]
    
    def get_pos_x(self):
        return self.get_pos()[0]
    
    def set_pos(self, x, y):
        self.position[0] = x
        self.position[1] = y
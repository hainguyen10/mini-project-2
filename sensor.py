import math
import pygame

class Sensor:
    def __init__(self, robot) -> None:
        self.robot = robot
        self.radius = 10
        self.color = (0, 0, 255)
        self.ray_count = 250
        self.sensed_cells = set()

    def ray_trace(self, start_x, start_y, angle, max_dist):
        dx = math.cos(angle)
        dy = math.sin(angle)
        x, y = start_x, start_y
        dist = 0
        
        while dist < max_dist:
            grid_x = int(x)
            grid_y = int(y)
            
            # Check if we hit a wall
            if grid_y < len(self.robot.world.world) and grid_x < len(self.robot.world.world[0]):
                if self.robot.world.world[grid_y][grid_x]:
                    return (grid_x, grid_y)
                self.sensed_cells.add((grid_x, grid_y))
            
            x += dx * 0.1  # Small steps for accuracy
            y += dy * 0.1
            dist += 0.1
        
        return (int(x), int(y))\
        
    def update_map(self, occupancy_map):
        self.sensed_cells.clear() # clear cache and recompute

        start_x, start_y = self.robot.position
        
        # Cast rays in all directions
        for i in range(self.ray_count):
            angle = (2 * math.pi * i) / self.ray_count
            end_point = self.ray_trace(start_x, start_y, angle, self.radius)

            for cell in self.sensed_cells:
                grid_x, grid_y = cell
                if 0 <= grid_y < len(occupancy_map) and 0 <= grid_x < len(occupancy_map[0]):
                    occupancy_map[grid_y][grid_x] = 0  # Mark as free
            
            # Update end points (walls)
            if end_point:
                grid_x, grid_y = end_point
                if 0 <= grid_y < len(occupancy_map) and 0 <= grid_x < len(occupancy_map[0]):
                    if self.robot.world.world[grid_y][grid_x]:
                        occupancy_map[grid_y][grid_x] = 1  # Occupied



    def render(self, screen, cell_size):
        # Draw sensor range circle
        x = self.robot.position[0] * cell_size + cell_size // 2
        y = self.robot.position[1] * cell_size + cell_size // 2
        pygame.draw.circle(screen, self.color, (x, y), self.radius * cell_size, 1)
        
        # Draw sensed cells
        for cell in self.sensed_cells:
            rect = pygame.Rect(
                cell[0] * cell_size,
                cell[1] * cell_size,
                cell_size,
                cell_size
            )
            pygame.draw.rect(screen, (200, 200, 255), rect, 1)
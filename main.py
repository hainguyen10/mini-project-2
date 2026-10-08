import pygame
import sys


from world import World
from map import Map
from robot import Robot

from exercise import detect_frontiers, calculate_frontier_centroids, find_closest_frontier

import argparse

parser = argparse.ArgumentParser(description="Exploration Planner")
parser.add_argument("--world", type=str, default="world_20250922_125003.txt", help="Path to the world file")
# parser.add_argument("--world", type=str, default=None, help="Path to the world file")
args = parser.parse_args()

class ExplorationPlanner:
    def __init__(self, world_path=None, map_width=50, map_height=30):
        # World and Robot
        self.world = World(path=world_path, init_pygame=False, width=map_width, height=map_height)
        start_pos = (map_width // 2, map_height // 2)
        self.robot = Robot(self.world, start_pos)

        # Occupancy Map
        self.map = Map(map_width, map_height, init_pygame=False)
        self.occupancy_map = self.map.map
        
        # Pygame for visualization
        self.cell_size = 20
        pygame.init()
        self.screen_width = map_width * self.cell_size
        self.screen_height = map_height * self.cell_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height + 40)) # Extra space for text
        pygame.display.set_caption("Exploration Planner")
        self.font = pygame.font.Font(None, 24)

        # Planner state
        self.frontiers = []
        self.path_to_frontier = []
        self.target_frontier = None
        self.path_index = 0

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        # Initial sensor sweep
        self.robot.sensor.update_map(self.occupancy_map)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # --- Main Exploration Logic ---
            # If we don't have a path, plan a new one
            if not self.path_to_frontier:
                self.plan()

            # If we have a path, execute the next step
            if self.path_to_frontier:
                self.move_robot_along_path()
            else:
                # No reachable frontiers left
                print("Exploration complete or no reachable frontiers.")
                # You might want to add a delay or exit condition here
                pygame.time.wait(1000)
                running = False


            # --- Rendering ---
            self.render()
            pygame.display.flip()
            
            clock.tick(10) # Control the speed of the simulation

        pygame.quit()
        sys.exit()

    def plan(self):
        """Finds frontiers and plans a path to the closest one."""
        robot_pos = tuple(self.robot.get_pos())
        map_w = len(self.occupancy_map[0])
        map_h = len(self.occupancy_map)

        # 1. Detect frontiers
        self.frontiers = detect_frontiers(self.occupancy_map, map_w, map_h)

        if not self.frontiers:
            self.path_to_frontier = []
            self.target_frontier = None
            return

        # 2. Group frontiers and find centroids
        frontier_centroids = calculate_frontier_centroids(self.frontiers, self.occupancy_map, map_w, map_h)
        
        # 3. Find the closest reachable frontier and a path to it
        self.target_frontier, self.path_to_frontier = find_closest_frontier(robot_pos, frontier_centroids, self.occupancy_map, map_w, map_h)
        
        self.path_index = 0

    def move_robot_along_path(self):
        """Moves the robot one step along the planned path."""
        if self.path_to_frontier and self.path_index < len(self.path_to_frontier):
            next_pos = self.path_to_frontier[self.path_index]
            self.robot.set_pos(next_pos[0], next_pos[1])
            self.path_index += 1
            
            # New sensor data is acquired after moving
            self.robot.sensor.update_map(self.occupancy_map)

            # If we've reached the end of the path, clear it to trigger replanning
            if self.path_index >= len(self.path_to_frontier):
                self.path_to_frontier = []
                self.target_frontier = None

    def render(self):
        """Draws the current state of the planner and map."""
        self.screen.fill((50, 50, 50)) # Dark grey background

        # Draw the occupancy map
        for y in range(len(self.occupancy_map)):
            for x in range(len(self.occupancy_map[0])):
                cell = self.occupancy_map[y][x]
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                if cell == 1: # Occupied
                    color = (0, 0, 0)
                elif cell == 0: # Free
                    color = (255, 255, 255)
                else: # Unknown
                    color = (128, 128, 128)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1) # Grid lines

        # Draw the frontiers
        for fx, fy in self.frontiers:
            rect = pygame.Rect(fx * self.cell_size, fy * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, (255, 165, 0), rect, 1) # Orange outline for frontiers

        # Draw the path
        if self.path_to_frontier:
            for px, py in self.path_to_frontier:
                pygame.draw.circle(self.screen, (0, 100, 255), 
                                   (px * self.cell_size + self.cell_size // 2, 
                                    py * self.cell_size + self.cell_size // 2), 2)

        # Draw the target frontier
        if self.target_frontier:
            gx, gy = self.target_frontier
            goal_rect = pygame.Rect(gx * self.cell_size, gy * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, (0, 255, 0), goal_rect, 2) # Green box for target

        # Draw the robot on top of everything
        self.robot.render(self.screen, self.cell_size)

        # Draw text overlay
        text_y = self.screen_height + 5
        robot_pos_text = self.font.render(f"Robot Pose: {self.robot.get_pos()}", True, (255, 255, 255))
        self.screen.blit(robot_pos_text, (5, text_y))
        
        target_text = self.font.render(f"Target: {self.target_frontier}", True, (255, 255, 255))
        self.screen.blit(target_text, (200, text_y))
        
        path_len_text = self.font.render(f"Path Length: {len(self.path_to_frontier)}", True, (255, 255, 255))
        self.screen.blit(path_len_text, (400, text_y))


if __name__ == "__main__":
    # You can specify a world file to load, or None to use a default empty one.
    # To use the world from create_world.py, run that first and use the generated filename.
    planner = ExplorationPlanner(world_path=args.world, map_width=50, map_height=30) 
    planner.run()
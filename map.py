import pygame
import sys
from robot import Robot
class Map:
    def __init__(self, width, height, init_pygame = False):
        # Initialize map properties
        self.width = width
        self.height = height
        self.default = 0.5
        self.occ = 1
        self.free = 0
        self.cell_size = 10
        self.goal_pos = None
        self.robot : Robot = None
        
        # Create the map grid
        self.map = [[self.default for _ in range(width)] for _ in range(height)]
        if init_pygame:
            self.window_width = width * self.cell_size
            self.window_height = height * self.cell_size + 50  # Extra space for potential UI elements
            pygame.init()
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption("Map Renderer")
        
        # Calculate window dimensions
        
    def set_robot(self, robot):
        self.robot = robot

    def set_goal(self, goal_pos):
        self.goal_pos = goal_pos

    def render_map(self):
        self.screen.fill((200, 200, 200))  # Fill background
        
        for y in range(self.height):
            for x in range(self.width):
                # Get cell value and determine color
                cell = self.map[y][x]
                if cell == self.occ:
                    color = (0, 0, 0)  # Black for occupied
                elif cell == self.free:
                    color = (255, 255, 255)  # White for free
                else:
                    color = (128, 128, 128)  # Gray for default
                
                # Calculate rectangle position and size
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Draw filled rectangle and border
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)  # Grid lines
                
        if self.goal_pos is not None:
            goal_x, goal_y = self.goal_pos
            goal_rect = pygame.Rect(
                goal_x * self.cell_size,
                goal_y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            # Draw green rectangle for goal
            pygame.draw.rect(self.screen, (0, 255, 0), goal_rect, 3)  # Thick green border
        if self.robot:
            self.robot.render(self.screen, self.cell_size)
            self.robot.sensor.update_map(self.map)
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        movement_delay = 100  # Milliseconds between moves
        last_move_time = 0
        
        while True:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Handle continuous key presses
            if self.robot and current_time - last_move_time > movement_delay:
                keys = pygame.key.get_pressed()
                moved = False
                
                if keys[pygame.K_UP]:
                    moved = self.robot.move_up()
                if keys[pygame.K_DOWN]:
                    moved = self.robot.move_down()
                if keys[pygame.K_LEFT]:
                    moved = self.robot.move_left()
                if keys[pygame.K_RIGHT]:
                    moved = self.robot.move_right()
                    
                if moved:
                    last_move_time = current_time
            
            self.render_map()
            pygame.display.flip()
            clock.tick(60)

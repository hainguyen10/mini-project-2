import pygame
import json
from datetime import datetime
import sys

class World:
    def __init__(self, init_pygame = False, path = "world_20241101_134921.txt", width = 80, height = 40, ) -> None:
        self.path = path
        self.world = self.init_world(width, height)
        self.cell_size = 30

        self.width = len(self.world[0]) * self.cell_size
        self.height = len(self.world) * self.cell_size + 50
        self.font = None
        self.save_button = None
        if init_pygame:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("World Renderer")
            
            # Initialize font for the save button
            self.font = pygame.font.Font(None, 36)
            self.save_button = pygame.Rect(10, self.height - 40, 100, 30)

    def get_world(self):
        return self.world

    def init_world(self, width = None, height = None):
        if self.path == None:
            return self.load_empty_world(width, height)
        else:
            try:
                return self.load_world(self.path)  # You can specify the filename to load
            except FileNotFoundError:
                print("No saved world found, creating new world")
                return self.load_empty_world( width, height)
         
        # read from world or create world
    def load_empty_world(self, width, height):
        world = []
        row_cache = self.create_empty_row( width )

        world.append(self.create_border_vertical(width))
        for _ in range(height - 2):
            world.append(row_cache.copy())
        world.append(self.create_border_vertical(width))
        return world

        
    def create_border_vertical(self, n):
        return [1] * n
    
    def create_empty_row(self, n):
        row =  [0] * (n - 2)
        return [1] + row + [1]
    
    def render_map(self):
        for y, row in enumerate(self.world):
            for x, cell in enumerate(row):
                color = (0, 0, 0) if cell == 1 else (255, 255, 255)
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (128, 128, 128), rect, 1)  # Grid lines

    def get_clicked_cell(self, pos):
        x, y = pos
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        return grid_x, grid_y

    def render_save_button(self):
        pygame.draw.rect(self.screen, (100, 100, 100), self.save_button)
        # Add text to the button
        text = self.font.render('Save', True, (255, 255, 255))
        text_rect = text.get_rect(center=self.save_button.center)
        self.screen.blit(text, text_rect)


    def save_world(self):
        # Generate filename with timestamppath
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"world_{timestamp}.txt"
        
        # Save the world data as JSON
        with open(filename, 'w') as f:
            json.dump({
                'width': len(self.world[0]),
                'height': len(self.world),
                'data': self.world
            }, f)
        return filename
    
    def load_world(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.world = data['data']
            return self.world

    def run(self):
        clock = pygame.time.Clock()
        dragging = False  
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # print(self.world)
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button

                        if self.save_button.collidepoint(event.pos):
                            filename = self.save_world()
                            print(f"World saved to {filename}")
                        else:
                            dragging = True
                            clicked_cell = self.get_clicked_cell(event.pos)
                            if clicked_cell:  # Check if the click was within the grid
                                y, x = clicked_cell
                                if x < len(self.world) and y < len(self.world[0]):  # Additional boundary check
                                    self.world[x][y] = 1
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if dragging:  # Update cells if the mouse is being dragged
                        dragged_cell = self.get_clicked_cell(event.pos)
                        y, x = dragged_cell
                        if x < len(self.world) and y < len(self.world[0]):  # Additional boundary check
                            self.world[x][y] = 1


            self.screen.fill((200, 200, 200))
            self.render_map()
            self.render_save_button() 
            pygame.display.flip()
            clock.tick(60)
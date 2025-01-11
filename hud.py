import datetime
import pygame

class HUD:
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        mono = pygame.font.match_font('mono')
        self._font_mono = pygame.font.Font(mono, 14)
        self._notifications = []
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0

    def on_world_tick(self, timestamp):
        self.server_fps = self.server_fps
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        pass

    def render(self, display):
        pass

import pygame
import random
import math

class Zombie(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((200, 0, 0))
        # Spawn at left or right edge
        self.rect = self.image.get_rect(center=(random.choice([0, 800]), random.randint(0, 600)))
        self.speed = 2
        self.health = 1

    def update(self, player):
        # Use centers for correct homing behavior
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.centerx += dx / dist * self.speed
            self.rect.centery += dy / dist * self.speed


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((80, 80))
        self.image.fill((100, 0, 200))
        self.rect = self.image.get_rect(center=(random.randint(100, 700), random.randint(100, 500)))
        self.speed = 1
        self.health = 20

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.centerx += dx / dist * self.speed
            self.rect.centery += dy / dist * self.speed
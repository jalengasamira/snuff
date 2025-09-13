import pygame
import math
import time
from pygame.math import Vector2

SCREEN_RECT = pygame.Rect(0, 0, 800, 600)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, imagen_path, character="Lau L"):
        super().__init__()
        self.character = character
        self.original_image = pygame.image.load(imagen_path).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (100, 100))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center= (x,y))
        self.speed = 5 
        self.bullets = pygame.sprite.Group()
        self.explosives = pygame.sprite.Group()
        self.shots_fired = 0
   
        

    def update(self, keys):
        
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.clamp_ip(SCREEN_RECT)

    def shoot(self, target):
        if self.character == "Lau L": 
            bullet = Bullet(self.rect.centerx, self.rect.centery, target, speed=14, damage=2)
            self.bullets.add(bullet)

        elif self.character == "Facu":  
            for spread in [-0.2, -0.1, 0, 0.1, 0.2]:
                bullet = Bullet(self.rect.centerx, self.rect.centery, target, spread=spread, speed=9, damage=1)
                self.bullets.add(bullet)

        elif self.character == "Lau S": 
            bullet = Bullet(self.rect.centerx, self.rect.centery, target, speed=8, size=12, damage=1)
            self.bullets.add(bullet)

       
        elif self.character == "Samira": 
            explosive = Explosive(self.rect.centerx, self.rect.centery, target, damage=10, radius=200)
            self.explosives.add(explosive)


        self.shots_fired += 1


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target, spread=0.0, speed=10, size=8, damage=1):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        dx, dy = target[0] - x, target[1] - y
        dist = math.hypot(dx, dy) or 1.0
        angle = math.atan2(dy, dx) + spread
        self.velx = math.cos(angle) * speed
        self.vely = math.sin(angle) * speed
        self._px, self._py = float(x), float(y)
        self.damage = damage

    def update(self):
        self._px += self.velx
        self._py += self.vely
        self.rect.centerx = int(self._px)
        self.rect.centery = int(self._py)
        if not (0 <= self.rect.centerx <= 800 and 0 <= self.rect.centery <= 600):
            self.kill()

class Explosive(pygame.sprite.Sprite):
    def __init__(self, x, y, target, damage=3, radius=80):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self._px, self._py = float(x), float(y)

        self.target = (float(target[0]), float(target[1]))
        dx, dy = self.target[0] - x, self.target[1] - y
        dist = math.hypot(dx, dy) or 1.0
        self.speed = 6
        self.velx = dx / dist * self.speed
        self.vely = dy / dist * self.speed

        self.landed = False
        self.land_time = None
        self.damage = damage
        self.radius = radius
        self.exploded = False       #acá se define el flag
        self.exploded_at = None     #y la posición de la explosión

    def update(self):
        if not self.landed:
            dx = self.target[0] - self._px
            dy = self.target[1] - self._py
            dist = math.hypot(dx, dy)

            if dist <= self.speed:
                self._px, self._py = self.target
                self.rect.center = (int(self._px), int(self._py))
                self.landed = True
                self.land_time = time.time()
            else:
                self._px += self.velx
                self._py += self.vely
                self.rect.center = (int(self._px), int(self._py))
        else:
            if not self.exploded and (time.time() - self.land_time >= 1):
                self.exploded_at = (self.rect.centerx, self.rect.centery)
                self.exploded = True

    def __init__(self, x, y, target, damage=3, radius=80):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self._px, self._py = float(x), float(y)

        self.target = (float(target[0]), float(target[1]))
        dx, dy = self.target[0] - x, self.target[1] - y
        dist = math.hypot(dx, dy) or 1.0
        self.speed = 6
        self.velx = dx / dist * self.speed
        self.vely = dy / dist * self.speed

        self.landed = False
        self.land_time = None
        self.damage = damage
        self.radius = radius
        self.exploded = False
        self.exploded_at = None

    def update(self):
        if not self.landed:
            dx = self.target[0] - self._px
            dy = self.target[1] - self._py
            dist = math.hypot(dx, dy)

            if dist <= self.speed:
                self._px, self._py = self.target
                self.rect.center = (int(self._px), int(self._py))
                self.landed = True
                self.land_time = time.time()
            else:
                self._px += self.velx
                self._py += self.vely
                self.rect.center = (int(self._px), int(self._py))
        else:
            if not self.exploded and (time.time() - self.land_time >= 1):
                self.exploded_at = (self.rect.centerx, self.rect.centery)
                self.exploded = True

    def __init__(self, x, y, target, damage=3, radius=80):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self._px, self._py = float(x), float(y)

        #velocidaddd
        self.speed = 6
        self.target = (float(target[0]), float(target[1]))
        dx, dy = self.target[0] - x, self.target[1] - y
        dist = math.hypot(dx, dy) or 1.0
        self.velx = dx / dist * self.speed
        self.vely = dy / dist * self.speed

        self.landed = False
        self.land_time = None
        self.damage = damage
        self.radius = radius
        self.exploded = False
        self.exploded_at = None

    def update(self):
        if not self.landed:
            dx = self.target[0] - self._px
            dy = self.target[1] - self._py
            dist = math.hypot(dx, dy)

            if dist <= self.speed:
                self._px, self._py = self.target
                self.rect.center = (int(self._px), int(self._py))
                self.landed = True
                self.land_time = time.time()
                self.velx = self.vely = 0
            else:
                #
                self._px += self.velx
                self._py += self.vely
                self.rect.center = (int(self._px), int(self._py))
        else:
            if not self.exploded and (time.time() - self.land_time >= 1):
                self.exploded_at = (self.rect.centerx, self.rect.centery)
                self.exploded = True

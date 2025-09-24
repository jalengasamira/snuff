import pygame
import math
import time

SCREEN_RECT = pygame.Rect(0, 0, 800, 600)


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, size=(320, 320), cuerpo_centro=(160, 160), speed=5):
        super().__init__()
        self.original_image = cargar_sprite_centrado(image_path, size, cuerpo_centro)
        self.image = self.original_image.copy()
        self.original_image = pygame.transform.scale(self.original_image, size)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
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
        # Este método debe ser sobreescrito por cada personaje
        pass


class LauL(Character):
    def __init__(self, x, y, image_path, size=(320, 320), cuerpo_centro=(160, 160), speed=5):
        super().__init__(x, y, image_path, size, cuerpo_centro, speed)
        self.revolver_side = True  # True = derecha, False = izquierda

    def shoot(self, target):
        # Distancia lateral desde el centro del personaje
        offset = 30
        # Calcula el ángulo hacia el mouse
        mx, my = target
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        angle = math.atan2(dy, dx)
        # Calcula la posición de salida (izquierda o derecha)
        if self.revolver_side:
            # Derecha
            px = self.rect.centerx + math.cos(angle + math.pi/2) * offset
            py = self.rect.centery + math.sin(angle + math.pi/2) * offset
        else:
            # Izquierda
            px = self.rect.centerx + math.cos(angle - math.pi/2) * offset
            py = self.rect.centery + math.sin(angle - math.pi/2) * offset
        # Alterna el lado para el próximo disparo
        self.revolver_side = not self.revolver_side

        bullet = Bullet(px, py, target, speed=14, damage=2)
        self.bullets.add(bullet)
        self.shots_fired += 1


class Facu(Character):
    def __init__(self, x, y, image_path, size=(320, 320), cuerpo_centro=(160, 160), speed=5):
        super().__init__(x, y, image_path, size, cuerpo_centro, speed)

    def shoot(self, target):
        for spread in [-0.2, -0.1, 0, 0.1, 0.2]:
            bullet = Bullet(self.rect.centerx, self.rect.centery, target, spread=spread, speed=9, damage=1)
            self.bullets.add(bullet)
        self.shots_fired += 1


class LauS(Character):
    def __init__(self, x, y, image_path, size=(320, 320), cuerpo_centro=(160, 160), speed=5):
        super().__init__(x, y, image_path, size, cuerpo_centro, speed)

    def shoot(self, target):
        bullet = Bullet(self.rect.centerx, self.rect.centery, target, speed=8, size=12, damage=1)
        self.bullets.add(bullet)
        self.shots_fired += 1


class Samira(Character):
    def __init__(self, x, y, image_path, size=(320, 320), cuerpo_centro=(160, 160), speed=5):
        super().__init__(x, y, image_path, size, cuerpo_centro, speed)

    def shoot(self, target):
        explosive = Explosive(self.rect.centerx, self.rect.centery, target, damage=10, radius=200)
        self.explosives.add(explosive)
        self.shots_fired += 1


class Shoot(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self._px, self._py = float(x), float(y)
        self.target = (float(target[0]), float(target[1]))

    def update(self):
        pass


class Bullet(Shoot):
    def __init__(self, x, y, target, spread=0.0, speed=10, size=8, damage=1):
        super().__init__(x, y, target)
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        dx, dy = target[0] - x, target[1] - y
        dist = math.hypot(dx, dy) or 1.0
        angle = math.atan2(dy, dx) + spread
        self.velx = math.cos(angle) * speed
        self.vely = math.sin(angle) * speed
        self.damage = damage

    def update(self):
        self._px += self.velx
        self._py += self.vely
        self.rect.centerx = int(self._px)
        self.rect.centery = int(self._py)
        if not (0 <= self.rect.centerx <= 800 and 0 <= self.rect.centery <= 600):
            self.kill()


class Explosive(Shoot):
    def __init__(self, x, y, target, damage=3, radius=80):
        super().__init__(x, y, target)
        self.image = pygame.Surface((16, 16))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(center=(x, y))
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


def cargar_sprite_centrado(ruta_imagen, size=(320, 320), cuerpo_centro=(160, 160)):
    imagen = pygame.image.load(ruta_imagen).convert_alpha()
    superficie = pygame.Surface(size, pygame.SRCALPHA)
    rect = imagen.get_rect(center=cuerpo_centro)
    superficie.blit(imagen, rect)
    return superficie

import pygame
import math
import time
from roengine.config import USE_ROTOZOOM

__all__ = ["Projectile", ]


class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, life, pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)

        self.position = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(3, 3)
        self.rotation = 0
        self.speed = 3
        self.life = time.time() + life

        self.image = image
        self.master_image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.snap_rect()

    def snap_rect(self):
        self.rect.center = [int(self.position.x), int(self.position.y)]

    def snap_pos(self):
        self.position = pygame.math.Vector2(self.rect.center)

    def req_kill(self):
        self.kill()

    def update(self):
        self.position += self.velocity
        self.snap_rect()
        if time.time() >= self.life:
            self.req_kill()

    def vel_from_rot(self):  # EXPERIMENTAL: DOESN'T WORK. >:(
        x = self.velocity.x * math.cos(self.rotation) - self.velocity.y * math.sin(self.rotation)
        y = self.velocity.x * math.sin(self.rotation) + self.velocity.y * math.cos(self.rotation)
        self.velocity = pygame.math.Vector2(x, y)
        return self.velocity

    def vel_to_target(self, target_pos):
        target_pos = pygame.math.Vector2(target_pos)
        mypos = pygame.math.Vector2(self.rect.center)
        dx, dy = (target_pos.x - mypos.x, target_pos.y - mypos.y)
        travelTime = mypos.distance_to(target_pos) / self.speed
        if travelTime != 0:
            self.velocity = pygame.math.Vector2((dx / travelTime), (dy / travelTime))
        return self.velocity

    def rot_to_target(self, target_pos, scale=1.0, update_rect=True):
        delta_pos = [target_pos[0] - self.position.x, target_pos[1] - self.position.y]
        self.rotation = math.degrees(math.atan2(-delta_pos[1], delta_pos[0])) - 90
        if USE_ROTOZOOM:
            self.image = pygame.transform.rotozoom(self.master_image, self.rotation, scale)
        else:
            self.image = pygame.transform.rotate(self.master_image, self.rotation)
        if update_rect:
            self.rect = self.image.get_rect()
            self.snap_rect()

# -*- coding: UTF-8 -*-
import random
import time

import pygame


class _ParticleManager(object):
    def __init__(self):
        self._group = pygame.sprite.Group()

    def register(self, particle):
        self._group.add(particle)

    def blit(self, screen):
        self._group.draw(screen)

    def update(self, to, accel):
        self._group.update(to, accel)


particles = _ParticleManager()


class Particle(pygame.sprite.Sprite):
    def __init__(self, img, pos, velX, velY, wobbleX, wobbleY, life):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.start = time.time()
        self.life = life

        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.velocity = pygame.math.Vector2(random.uniform(velX[0], velX[1]) * random.choice([-1, 1]),
                                            random.uniform(velY[0], velY[1]) * random.choice([-1, 1]))
        self.wobble = [wobbleX, wobbleY]
        self.position = pygame.math.Vector2(pos)

    def update(self, to, accelSpeed):
        self.velocity += pygame.math.Vector2(
            random.uniform(self.wobble[0][0], self.wobble[0][1]) * random.choice([-1, 1]),
            random.uniform(self.wobble[1][0], self.wobble[1][1]) * random.choice([-1, 1]))

        self.velocity += pygame.math.Vector2(accelSpeed if to[0] > self.position.x else -accelSpeed,
                                             accelSpeed if to[1] > self.position.y else -accelSpeed)
        self.position += self.velocity
        self.rect.center = [int(self.position.x), int(self.position.y)]

        if time.time() - self.start > self.life:
            self.kill()


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode([640, 480], pygame.RESIZABLE)

    running = True
    while running:
        screen.fill([255, 255, 255])
        particles.blit(screen)
        pygame.display.flip()

        particles.update(pygame.mouse.get_pos(), 0.3)
        particles.register(
            Particle(pygame.Surface([10, 10]), [screen.get_width() / 2, screen.get_height() / 2], [0, 5], [0, 5],
                     [0, 1.5], [0, 1.5], 3))
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                particles.register(Particle(pygame.Surface([10, 10]), event.pos, [0, 15], [0, 15], [0, 3], [0, 3], 1))

    pygame.quit()

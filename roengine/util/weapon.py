# -*- coding: UTF-8 -*-

import pygame
import time

__all__ = ["Weapon", "bullets"]


class _BulletRegistry(object):
    def __init__(self):
        self.bullets = pygame.sprite.Group()

    def register(self, bullet):
        self.bullets.add(bullet)

    def unregister(self, bullet):
        self.bullets.remove(bullet)


bullets = _BulletRegistry()


class Clock(object):
    def __init__(self):
        self.lastCall = time.time()
        self.callDiff = 0
        self.roc = 0

    def get_fps(self):
        return 1.0/self.callDiff if self.callDiff != 0 else 0

    def tick(self):
        now = time.time()
        self.callDiff = now-self.lastCall
        self.lastCall = now
        self.roc = self.get_fps()


class Weapon(object):
    def __init__(self, dps, rof, bullet_class, clockMode='accurate'):
        self.dps = float(dps)
        self.rof = float(rof)
        self.cool = 1.0/rof
        self.lastFire = 0
        self.bullet = bullet_class
        self.clock = Clock() if clockMode == 'accurate' else pygame.time.Clock()
        self.shot_damage = self.dps/rof
        # damage per second / shots per second = damage per shot

    def tick(self):
        self.clock.tick()

    def indp_fire(self, target_pos):
        self.clock.tick()
        rof = self.clock.get_fps()
        damage = self.dps / rof if rof != 0 else 0
        self._fire(damage, target_pos)

    def _fire(self, damage, target_pos):
        bullets.register(self.bullet(damage, target_pos))

    def tick_fire(self, target_pos, recal_damage=False):
        now = time.time()
        if now-self.lastFire > self.cool:
            if recal_damage:
                self.indp_fire(target_pos)
            else:
                self._fire(self.shot_damage, target_pos)
            self.lastFire = now


if __name__ == "__main__":
    from roengine import Text

    class TestWeapon(Weapon):
        def _fire(self, dam, pos):
            global counter, damage
            counter += 1
            damage = dam

    weapon = TestWeapon(34.65, 0.8, None, 'pygame')
    pygame.init()
    screen = pygame.display.set_mode([640, 480])
    running = True
    counter = 0
    damage =0
    while running:
        screen.fill([255, 255, 255])
        screen.blit(Text(str(counter)+":"+str(damage)).image, [10, 10])
        weapon.tick_fire((0, 0), True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN: pass
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

# -*- coding: UTF-8 -*-

import pygame
import time

from roengine.gameplay.projectile import Projectile

__all__ = ["Weapon", "bullets", "Bullet"]


class _BulletRegistry(object):
    def __init__(self):
        self.shootables = pygame.sprite.Group()
        self._bullets = pygame.sprite.Group()

    def set_shootables(self, group):
        self.shootables = group

    def register(self, bullet):
        self._bullets.add(bullet)

    def unregister(self, bullet):
        self._bullets.remove(bullet)

    def draw(self, surf):
        self._bullets.draw(surf)

    def update(self):
        self._bullets.update()
        col = pygame.sprite.groupcollide(self._bullets, self.shootables, False, False)
        for key in col.keys():
            key.on_collide(col[key])


bullets = _BulletRegistry()


class Bullet(Projectile):
    def __init__(self, damage, target, parent):
        Projectile.__init__(self, pygame.Surface([10, 10]).convert(), 5, parent.rect.center)
        self.parent = parent
        self.damage = damage
        self.target = target
        self.speed = 12
        self.velocity = self.vel_to_target(self.target)
        # print (parent.rect.center)

    def on_collide(self, col_list):
        for i in col_list:
            if i != self.parent:
                i.damage(self.damage)
                self.kill()
                return

    def update(self):
        Projectile.update(self)


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
    def __init__(self, dps, rof, bullet_class, parent, clockMode='accurate'):
        self.dps = float(dps)
        self.rof = float(rof)
        self.cool = 1.0/rof
        self.lastFire = 0
        self.parent = parent
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
        bullets.register(self.bullet(damage, target_pos, self.parent))

    def tick_fire(self, target_pos, recal_damage=False):
        now = time.time()
        if now-self.lastFire > self.cool:
            if not recal_damage:
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

    weapon = TestWeapon(34.65, 0.8, None, 'xxx')
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

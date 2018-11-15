# -*- coding: UTF-8 -*-

import pygame
import time
import random

from roengine.gameplay.projectile import Projectile

__all__ = ["Weapon", "bullets", "Bullet", "Shotgun"]


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
    def __init__(self, damage, target, parent, wobble=(0, 0), blume=(1.25, 1.25), size=10, life=2):
        Projectile.__init__(self, pygame.Surface([size, size]).convert(), life, parent.rect.center)
        self.parent = parent
        self.damage = damage
        self.target = target
        self.speed = 12
        self.blume = blume
        self.wobble = wobble
        ablume = (random.uniform(-blume[0], blume[0]),
                  random.uniform(-blume[1], blume[1]))
        self.velocity = self.vel_to_target(self.target) + pygame.math.Vector2(ablume)
        # print (parent.rect.center)

    def on_collide(self, col_list):
        for i in col_list:
            if i != self.parent:
                i.damage(self.damage)
                self.kill()
                return

    def update(self):
        if self.wobble[0] != 0 or self.wobble[1] != 0:
            wobble = (random.uniform(-self.wobble[0], self.wobble[0]),
                      random.uniform(-self.wobble[1], self.wobble[1]))
            self.velocity += pygame.math.Vector2(wobble)
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
    def __init__(self, dps, rof, bullet_class, parent, mag=40, reserve=190, reload_time=2, blume=(0, 0)):
        self.dps = float(dps)
        self.rof = float(rof)
        self.cool = 1.0/rof
        self.lastFire = 0
        self.parent = parent

        self.blume = blume

        self.bullet = bullet_class
        self.maxMag, self.ammo = mag, mag
        self.reserve = reserve

        self.clock = Clock()
        self.shot_damage = self.dps/rof

        self.reloading = False
        self.reload = reload_time
        self.started_reloading = 0
        # damage per second / shots per second = damage per shot

    def force_reload(self):
        if self.ammo < self.maxMag:
            self.reloading = True
            self.started_reloading = time.time()
        else:
            print ("ERR: Magazine already full.")

    def tick(self):
        now = time.time()
        if self.ammo <= 0 and self.reloading == False:
            self.reloading = True
            self.started_reloading = now
        if self.reloading and now-self.started_reloading >= self.reload:
            self.reloading = False
            if self.reserve < self.maxMag:
                self.ammo = self.reserve
                self.reserve = 0
                return
            s_reserve = self.maxMag-self.ammo
            self.reserve -=  s_reserve if s_reserve >= 0 else 0
            self.ammo = self.maxMag
        #self.clock.tick()

    def indp_fire(self, target_pos):
        if self.reloading or self.ammo <= 0:
            return
        self.clock.tick()
        rof = self.clock.get_fps()
        damage = self.dps / rof if rof != 0 else 0
        self._fire(damage, target_pos)

    def _fire(self, damage, target_pos):
        target_pos = list(target_pos)
        target_pos[0] += random.randint(-self.blume[0], self.blume[0])
        target_pos[1] += random.randint(-self.blume[1], self.blume[1])
        bullets.register(self.bullet(damage, target_pos, self.parent))
        self.ammo -= 1

    def tick_fire(self, target_pos, recal_damage=True):
        if self.reloading or self.ammo <= 0:
            return
        now = time.time()
        if now-self.lastFire > self.cool:
            if not recal_damage:
                self.indp_fire(target_pos)
            else:
                self._fire(self.shot_damage, target_pos)
            self.lastFire = now


class Shotgun(Weapon):
    def __init__(self, dps, rof, bullet_class, parent, pellet_num=5, mag=8, reserve=200, reload_time=2, blume=(0, 0)):
        self.pellet_num = pellet_num
        Weapon.__init__(self, dps, rof, bullet_class, parent, mag, reserve, reload_time, blume)

    def _fire(self, damage, target_pos):
        for i in range(self.pellet_num):
            target_pos = list(target_pos)
            target_pos[0] += random.randint(-self.blume[0], self.blume[0])
            target_pos[1] += random.randint(-self.blume[1], self.blume[1])
            bullets.register(self.bullet(damage/float(self.pellet_num), target_pos, self.parent))
        self.ammo -= 1


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

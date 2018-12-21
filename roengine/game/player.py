import pygame
import math
from roengine.util import Dummy

__all__ = ["PlatformerPlayer", 'PLAYER_KEYBINDS']

PLAYER_KEYBINDS = {'jump': (pygame.K_SPACE, pygame.K_w), 'forward': (pygame.K_d, ), 'backward': (pygame.K_a, )}


class PlatformerPlayer(pygame.sprite.Sprite):
    def __init__(self, image, pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)

        self.position = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.rotation = 0

        self.collidables = pygame.sprite.Group()
        self.gravity = 0.5

        self.speed = 5
        self.jump_power = 10

        self.is_climbing = False
        self.climb_velocity = 5
        self.climb_skill = 1

        self.grounded = False
        self.firing = False
        self.bounds_checks = ('+y', '-x', '+x')
        self.term_y = 10
        self.bounds = None

        self.input_state = {"forward": False, "backward": False, "jump": False}

        self.image = image
        self.master_image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        self.grounded = False
        self.is_climbing = False
        self.check_y_collisions()
        if self.bounds is not None:
            self.check_bounds(self.bounds, ('+y', '-y') if "+y" in self.bounds_checks else ('-y', ))
        self.update_input_state()
        self.apply_gravity()
        self.clamp_velocity()
        if self.bounds is not None:
            self.check_bounds(self.bounds, ('-y', ))
        self.position.y += self.velocity.y
        self.update_rect()

    def update_rot(self, target_pos):
        delta_pos = [target_pos[0] - self.position.x, target_pos[1] - self.position.y]
        self.rotation = math.degrees(math.atan2(-delta_pos[1], delta_pos[0])) - 90
        self.image = pygame.transform.rotate(self.master_image, self.rotation)
        # self.rect = self.image.get_rect()
        # self.update_rect()

    def update_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.firing = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.firing = False
        if event.type == pygame.KEYDOWN:
            if event.key in PLAYER_KEYBINDS['forward']:
                self.input_state["forward"] = True
            if event.key in PLAYER_KEYBINDS['backward']:
                self.input_state["backward"] = True
            if event.key in PLAYER_KEYBINDS["jump"]:
                self.input_state["jump"] = True
        if event.type == pygame.KEYUP:
            if event.key in PLAYER_KEYBINDS['forward']:
                self.input_state["forward"] = False
            if event.key in PLAYER_KEYBINDS['backward']:
                self.input_state["backward"] = False
            if event.key in PLAYER_KEYBINDS["jump"]:
                self.input_state["jump"] = False

    def clamp_velocity(self):
        self.velocity.y = max(-self.term_y, min(self.velocity.y, self.term_y))

    def apply_gravity(self):
        if not (self.grounded or self.is_climbing):
            self.velocity.y += self.gravity

    def update_input_state(self):
        if self.input_state["forward"]:
            self.position.x += self.speed
            self.update_rect()
            self.check_px_cols()
            if self.bounds is not None and "+x" in self.bounds_checks:
                self.check_bounds(self.bounds, ('+x',))
        if self.input_state["backward"]:
            self.position.x -= self.speed
            self.update_rect()
            self.check_nx_cols()
            if self.bounds is not None and "-x" in self.bounds_checks:
                self.check_bounds(self.bounds, ('-x',))
        if self.input_state["jump"] and self.grounded:
            self.velocity.y -= self.jump_power

        if self.is_climbing:
            self.velocity.y = -self.climb_velocity

    def update_rect(self):
        self.rect.center = [int(self.position.x), int(self.position.y)]

    def update_pos(self):
        self.position = pygame.math.Vector2(self.rect.center)

    def check_y_collisions(self):
        self.update_rect()
        if self.velocity.y > 0:
            hit = pygame.sprite.spritecollide(self, self.collidables, False)
            if hit:
                getattr(hit[0], 'on_collide', Dummy)('+y', self)
                self.rect.bottom = hit[0].rect.top
                self.update_pos()
                self.grounded = True
                self.velocity.y = 0
        if self.velocity.y < 0:
            hit = pygame.sprite.spritecollide(self, self.collidables, False)
            if hit:
                getattr(hit[0], 'on_collide', Dummy)('-y', self)
                self.rect.top = hit[0].rect.bottom
                self.update_pos()
                self.velocity.y = 0

    def check_px_cols(self):
        self.update_rect()
        hit = pygame.sprite.spritecollide(self, self.collidables, False)
        if hit:
            getattr(hit[0], 'on_collide', Dummy)('+x', self)
            self.is_climbing = getattr(hit[0], 'climb_difficulty', float('inf')) <= self.climb_skill
            self.rect.right = hit[0].rect.left
            self.update_pos()

    def check_nx_cols(self):
        self.update_rect()
        hit = pygame.sprite.spritecollide(self, self.collidables, False)
        if hit:
            getattr(hit[0], 'on_collide', Dummy)('-x', self)
            self.is_climbing = getattr(hit[0], 'climb_difficulty', float('inf')) <= self.climb_skill
            self.rect.left = hit[0].rect.right
            self.update_pos()

    def check_bounds(self, surface, checks=("+y", "-y", "+x", "-x")):
        self.update_rect()
        if self.rect.left < 0 and "-x" in checks:
            self.is_climbing = True
            self.rect.left = 0
        if self.rect.right > surface.get_width() and "+x" in checks:
            self.is_climbing = True
            self.rect.right = surface.get_width()

        if self.rect.top < 0 and "-y" in checks:
            self.rect.top = 0
            self.velocity.y = 0
        if self.rect.bottom > surface.get_height() and "+y" in checks:
            self.rect.bottom = surface.get_height()
            self.velocity.y = 0
            self.grounded = True
        self.position = pygame.math.Vector2(self.rect.center)
        #self.update_rect()

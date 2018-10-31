import pygame
import math

__all__ = ["PlatformerPlayer", ]


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
        self.grounded = False
        self.term_y = 10

        self.input_state = {"forward": False, "backward": False, "jump": False}

        self.image = image
        self.master_image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        self.grounded = False
        self.check_y_collisions()
        self.update_input_state()
        self.apply_gravity()
        self.clamp_velocity()
        self.position.y += self.velocity.y
        self.update_rect()

    def update_rot(self, target_pos):
        delta_pos = [target_pos[0] - self.position.x, target_pos[1] - self.position.y]
        self.rotation = math.degrees(math.atan2(-delta_pos[1], delta_pos[0])) - 90
        self.image = pygame.transform.rotate(self.master_image, self.rotation)
        # self.rect = self.image.get_rect()
        # self.update_rect()

    def update_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.input_state["forward"] = True
            if event.key == pygame.K_a:
                self.input_state["backward"] = True
            if event.key == pygame.K_SPACE:
                self.input_state["jump"] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                self.input_state["forward"] = False
            if event.key == pygame.K_a:
                self.input_state["backward"] = False
            if event.key == pygame.K_SPACE:
                self.input_state["jump"] = False

    def clamp_velocity(self):
        self.velocity.y = max(-self.term_y, min(self.velocity.y, self.term_y))

    def apply_gravity(self):
        if not self.grounded:
            self.velocity.y += self.gravity

    def update_input_state(self):
        if self.input_state["forward"]:
            self.position.x += self.speed
            self.update_rect()
            self.check_px_cols()
        if self.input_state["backward"]:
            self.position.x -= self.speed
            self.update_rect()
            self.check_nx_cols()
        if self.input_state["jump"] and self.grounded:
            self.velocity.y -= self.jump_power

    def update_rect(self):
        self.rect.center = [int(self.position.x), int(self.position.y)]

    def check_y_collisions(self):
        self.update_rect()
        if self.velocity.y > 0:
            while pygame.sprite.spritecollide(self, self.collidables, False):
                self.grounded = True
                self.position.y -= 1
                self.update_rect()
                self.velocity.y = 0
        if self.velocity.y < 0:
            while pygame.sprite.spritecollide(self, self.collidables, False):
                self.position.y += 1
                self.update_rect()
                self.velocity.y = 0

    def check_px_cols(self):
        self.update_rect()
        while pygame.sprite.spritecollide(self, self.collidables, False):
            self.position.x -= 1
            self.update_rect()
            self.velocity.x = 0

    def check_nx_cols(self):
        self.update_rect()
        while pygame.sprite.spritecollide(self, self.collidables, False):
            self.position.x += 1
            self.update_rect()
            self.velocity.x = 0

    def check_bounds(self, surface, checks=("+y", "-y", "+x", "-x")):
        self.update_rect()
        if self.rect.left < 0 and "-x" in checks:
            self.rect.left = 0
        if self.rect.right > surface.get_width() and "+x" in checks:
            self.rect.right = surface.get_width()

        if self.rect.top < 0 and "-y" in checks:
            self.rect.top = 0
            self.velocity.y = 0
        if self.rect.bottom > surface.get_height() and "+y" in checks:
            self.rect.bottom = surface.get_width()
            self.velocity.y = 0
        self.position = pygame.math.Vector2(self.rect.center)

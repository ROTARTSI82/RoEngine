import pygame
from pygame.locals import *
import random

pygame.init()


screen = pygame.display.set_mode([800, 480], pygame.RESIZABLE)
map_relScreen = [2, 1]
screen_relMap = [1/3.0, 1]
MAP = pygame.Surface([int(screen.get_width()*map_relScreen[0]),
                      int(screen.get_height()*map_relScreen[1])])


class Marker(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([10, 10])
        self.rect = self.image.get_rect()
        self.rect.center = pos


class Bullet(pygame.sprite.Sprite):
    def __init__(self, targetpos, pos, parent, damage=0, image=pygame.Surface([10, 10])):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.targetpos = pygame.math.Vector2(targetpos)
        self.image = image
        self.damage = damage
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 25
        self.position = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2([0, 0])
        self.lifetime = 120
        self.time = 0

        dX, dY = list(self.targetpos - self.position)
        time = float(self.position.distance_to(self.targetpos) / self.speed)
        self.velocity = pygame.math.Vector2([dX / time, dY / time] if time != 0 and time != 0 else [0, 0])

    def update(self):
        self.position += self.velocity
        self.rect.center = [int(self.position.x), int(self.position.y)]
        self.time += 1
        if self.time > self.lifetime:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, playersize=40, pos=(0, 0), vel=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([playersize, playersize], SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(self.image, [0, 0, 255], [playersize // 2, playersize // 2], playersize // 2, 0)

        self.position = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(vel)

        self.speed = 1
        self.term_xVEL = 5
        self.term_yVEL = 15
        self.jumpPower = 15
        self.grounded = False

        self.state = {"jump": False, "right": False, "left": False}
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):

        self.rect.center = [int(self.position.x), int(self.position.y)]
        hit = pygame.sprite.spritecollide(self, obstacles, False)
        #print self.velocity.y

        #print self.grounded
        if self.velocity.y > 0 and hit:
            if hit[0].col['+y']:
                while pygame.sprite.spritecollide(self, obstacles, False):
                    self.position.y -= 1
                    self.velocity.y = 0
                    self.grounded = True
                    self.rect.center = [int(self.position.x), int(self.position.y)]
        if self.velocity.y < 0 and hit:
            if hit[0].col['-y']:
                while pygame.sprite.spritecollide(self, obstacles, False):
                    self.position.y += 1
                    self.velocity.y = 0
                    self.rect.center = [int(self.position.x), int(self.position.y)]
                    self.grounded = False

        if self.velocity.x > 0:
            self.velocity.x -= GROUND_FRICTION if self.grounded else AIR_FRICTION
        elif self.velocity.x < 0:
            self.velocity.x += GROUND_FRICTION if self.grounded else AIR_FRICTION

        if self.state['right']:
            self.velocity.x += self.speed
            self.position.x += self.velocity.x
            self.rect.center = [int(self.position.x), int(self.position.y)]
            hit = pygame.sprite.spritecollide(self, obstacles, False)
            if hit:
                while pygame.sprite.spritecollide(self, obstacles, False):
                    self.position.x -= 1
                    if hit[0].allow_wall_jump["+x"]:
                        self.grounded = True
                        self.velocity.x = -self.term_xVEL
                    self.rect.center = [int(self.position.x), int(self.position.y)]
                    #self.velocity.y = 0
        if self.state['left']:
            self.velocity.x -= self.speed
            self.position.x += self.velocity.x
            self.rect.center = [int(self.position.x), int(self.position.y)]
            hit = pygame.sprite.spritecollide(self, obstacles, False)
            if hit:
                while pygame.sprite.spritecollide(self, obstacles, False):
                    self.position.x += 1
                    if hit[0].allow_wall_jump["-x"]:
                        self.grounded = True
                        self.velocity.x = self.term_xVEL
                    self.rect.center = [int(self.position.x), int(self.position.y)]
                    #self.velocity.y = 0
        if self.state['jump'] and self.grounded:
            self.velocity.y -= self.jumpPower
            self.grounded = False

        self.grounded = False
        self.rect.center = [int(self.position.x), int(self.position.y)]
        if self.position.y >= MAP.get_height() - self.image.get_height() / 2:
            self.position.y = MAP.get_height() - self.image.get_height() / 2
            self.rect.center = [int(self.position.x), int(self.position.y)]
            if not self.state['jump']:
                self.velocity.y = 0
            self.grounded = True
        if self.position.x > MAP.get_width() - self.image.get_width() / 2:
            self.position.x = MAP.get_width() - self.image.get_width() / 2
            self.grounded = True
            self.velocity.x = -self.term_xVEL
            #self.velocity.y = 0
            self.velocity.y += GRAVITY
            self.rect.center = [int(self.position.x), int(self.position.y)]
        if self.position.x < self.image.get_width() / 2:
            self.position.x = self.image.get_width() / 2
            self.grounded = True
            #self.velocity.y = 0
            self.velocity.y += GRAVITY
            self.velocity.x = self.term_xVEL
            self.rect.center = [int(self.position.x), int(self.position.y)]
        if self.position.y <= self.image.get_height() / 2:
            self.position.y = self.image.get_height() / 2
            self.rect.center = [int(self.position.x), int(self.position.y)]
            self.velocity.y = 0
            self.grounded = False

        #print self.grounded
        if not self.grounded:
            self.velocity.y += GRAVITY
        #if self.grounded and not self.state['jump']:
        #    self.velocity.y = 0

        self.velocity.x = self.term_xVEL if self.velocity.x > self.term_xVEL else self.velocity.x
        self.velocity.x = -self.term_xVEL if self.velocity.x < -self.term_xVEL else self.velocity.x
        self.velocity.y = self.term_yVEL if self.velocity.y > self.term_yVEL else self.velocity.y
        self.velocity.y = -self.term_yVEL if self.velocity.y < -self.term_yVEL else self.velocity.y
        #if self.grounded:
        #    self.velocity.y = 0
        #print self.velocity.y
        self.position.y += self.velocity.y
        self.rect.center = [int(self.position.x), int(self.position.y)]


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.col = {"+x": True, "-x": True, "+y": True, "-y": True}
        self.allow_wall_jump = {"-x": True, "+x": True}
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(pos)
        self.rect.center = pos


GRAVITY = 1
GROUND_FRICTION = 0.25
AIR_FRICTION = 0.125
player = Player(30, [320, 240])
ytest = pygame.Surface([500, 25])
xtest = pygame.Surface([25, 500])
obstacles = pygame.sprite.Group(Obstacle(ytest, [320, 460]), Obstacle(ytest, [320, 360]),
                                Obstacle(xtest, [800, 240]))
#for i in range(random.randint(10, 50)):
#    plat = pygame.Surface([random.randint(50, 200), random.randint(50, 200)])
#    ob = Obstacle(plat, [random.randint(0, MAP.get_width()), random.randint(0, MAP.get_height())])
#    ob.col = {"+x": random.choice([True, False]), "-x": random.choice([True, False]),
#              "+y": random.choice([True, False]), "-y": random.choice([True, False])}
#    ob.col = {"+x": True, "-x": True, "+y": True, "-y": True}
#    obstacles.add(ob)
bullets = pygame.sprite.Group()
debug_markers = []

running = True
while running:
    player.update()
    MAP.fill([255, 255, 255])
    MAP.blit(player.image, player.rect)
    obstacles.draw(MAP)
    bullets.update()
    bullets.draw(MAP)
    pygame.draw.rect(MAP, [0,0,0], player.rect, 1)
    screen.fill([0, 0, 0])
    # D R M F S L T D
    #[MAP.blit(i.image, i.rect) for i in debug_markers]
    scaledMAP = pygame.transform.scale(MAP, (int(screen.get_width()*map_relScreen[0]),
                                             int(screen.get_height()*map_relScreen[1])))
    CENTER_PLAYER_AT = screen.get_width()/2
    scroll = [-(player.position.x*scaledMAP.get_width()/MAP.get_width())+CENTER_PLAYER_AT, 0]
    scroll[0] = max(-(scaledMAP.get_width()-screen.get_width()), min(0, scroll[0]))
    screen.blit(scaledMAP, scroll)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict['size'], RESIZABLE)
            #MAP = pygame.Surface([map_relScreen[0]*event.dict['size'][0], map_relScreen[1]*event.dict['size'][1]])
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                player.state['right'] = True
            if event.key == K_LEFT:
                player.state['left'] = True
            if event.key == K_UP:
                player.state['jump'] = True
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                player.state['right'] = False
            if event.key == K_LEFT:
                player.state['left'] = False
            if event.key == K_UP:
                player.state['jump'] = False
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            pos = [(event.pos[0]-scroll[0])*MAP.get_width()/scaledMAP.get_width(),
                   (event.pos[1] - scroll[1]) * MAP.get_height() / scaledMAP.get_height()]
            #debug_markers.append(Marker(pos))
            bullets.add(Bullet(pos, player.rect.center, player))
pygame.quit()

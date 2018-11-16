import pygame

from pygame.locals import *
from roengine import *


class ScaleTest(Game):

    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode([640, 480], RESIZABLE)
        self.MAP = pygame.Surface([1000, 480])
        self.player = PlatformerPlayer(pygame.Surface([15, 15]).convert())

        self.COLLIDABLES = pygame.sprite.Group(DummySprite([100, 10], [100, 400]),
                                               DummySprite([100, 10], [150, 428]),
                                               DummySprite([10, 400], [250, 28]),
                                               DummySprite([1920, 50], [320, 480]),
                                               DummySprite([100, 100], [320, 405]))

        self.player.collidables = self.COLLIDABLES
        self.running = True

        self.markers = pygame.sprite.Group()

    def tick_main(self):
        self.screen.fill([255, 255, 255])
        self.MAP.fill([255, 255, 255])
        self.MAP.blit(self.player.image, self.player.rect)
        self.markers.draw(self.MAP)
        self.COLLIDABLES.draw(self.MAP)

        SCALED = pygame.transform.scale(self.MAP, (self.screen.get_width() * 2, self.screen.get_height() * 1))
        CENTER_AT = [self.screen.get_width()/2, self.screen.get_height()/2]
        scroll = [-(self.player.position.x * SCALED.get_width() / self.MAP.get_width()) + CENTER_AT[0],
                  -(self.player.position.y * SCALED.get_height() / self.MAP.get_height()) + CENTER_AT[1]]
        scroll[0] = max(-(SCALED.get_width() - self.screen.get_width()), min(0, scroll[0]))
        scroll[1] = max(-(SCALED.get_height() - self.screen.get_height()), min(0, scroll[1]))
        # scroll[1] = 0

        #print scroll

        self.screen.blit(SCALED, scroll)
        pygame.display.flip()

        mp = pygame.mouse.get_pos()
        mp = [(mp[0]-scroll[0])*self.MAP.get_width()/SCALED.get_width(),
              (mp[1] - scroll[1]) * self.MAP.get_height() / SCALED.get_height()]

        self.player.update()
        for event in pygame.event.get():
            self.player.update_event(event)
            if event.type == QUIT:
                self.terminate()
            if event.type == VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.dict['size'], RESIZABLE)
            if event.type == MOUSEBUTTONDOWN:
                self.COLLIDABLES.add(DummySprite([10, 10], mp))
                self.player.collidables = self.COLLIDABLES



if __name__ == "__main__":
    game = ScaleTest()
    game.load()
    reactor.run()
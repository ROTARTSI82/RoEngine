import pygame

from pygame.locals import *
from roengine import *


class ClickableBt(CheckBox):
    def __init__(self, text):
        CheckBox.__init__(self, text)
        self.hovering = False
    def event_update(self, hovering):
        if hovering and not self.hovering:
            self.hovering = True
            pygame.mouse.set_cursor(*clickable)
        if (not hovering) and self.hovering:
            self.hovering = False
            pygame.mouse.set_cursor(*default)
class StateBt(Button):
    def __init__(self, image, pos, state, hov_color):
        Button.__init__(self, image, pos)
        self.state = state
        self.hov_color = hov_color
        self.orig_image = image
        self.hov_image = pygame.Surface([110, 35]).convert()
        self.hov_image.fill(hov_color)
        self.old_cursor = default

    def on_click_start(self, event):
        print ("II")
        game.update_state(self.state)

    def on_click_end(self, event):
        print ("OI", self.state)

    def event_update(self, hovering):
        if hovering and self.image == self.orig_image:
            self.image = self.hov_image
            orig_pos = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = orig_pos
            # self.old_cursor = pygame.mouse.get_cursor()
            pygame.mouse.set_cursor(*clickable)
        if (not hovering) and self.image == self.hov_image:
            self.image = self.orig_image
            orig_pos = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = orig_pos
            pygame.mouse.set_cursor(*default)


class MyGame(Game):
    def start(self):
        pygame.init()
        pygame.mouse.set_cursor(*default)
        self.screen = pygame.display.set_mode([640, 480])
        bt1image = pygame.Surface([100, 25]).convert()
        bt1image.fill([255, 0, 0])
        self.bt1 = StateBt(bt1image, (400, 400), "state1", (0, 255, 255))
        bt2image = pygame.Surface([100, 25]).convert()
        bt2image.fill([255, 255, 0])
        self.bt2 = StateBt(bt2image, (200, 200), "state2", (0, 255, 0))
        self.check = ClickableBt("Why do you do this?!")
        self.check.rect.center = (300, 300)
        self.running = True

    def tick_state1(self):
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.bt2.image, self.bt2.rect)
        self.screen.blit(self.check.image, self.check.rect)
        pygame.display.flip()
        for event in pygame.event.get():
            [bt.update_event(event) for bt in buttons.visible_bts]
            if event.type == QUIT:
                self.terminate()

    def tick_state2(self):
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.bt1.image, self.bt1.rect)
        pygame.display.flip()
        for event in pygame.event.get():
            [bt.update_event(event) for bt in buttons.visible_bts]
            if event.type == QUIT:
                self.terminate()

    def state1_to_state2(self):
        buttons.set_buttons([self.bt1,])

    def state2_to_state1(self):
        buttons.set_buttons([self.bt2, self.check])


if __name__ == "__main__":
    game = MyGame(fps=60, state='state1')
    game.load()
    reactor.run()

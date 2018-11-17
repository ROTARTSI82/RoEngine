# -*- coding: UTF-8 -*-

import time

__all__ = ['ActionManager', 'Action']


class Action(object):
    def __init__(self, action_type, action_id, duration):
        self.duration = duration
        self.action_type = action_type
        self.action_id = action_id

    def start(self): pass

    def finish(self): pass

    def interrupted(self): pass

    def reject(self, reason): pass


class ActionManager(object):
    def __init__(self, reject_duplicates=True):
        self.reject_dups = reject_duplicates
        self.current_action = None
        self.action_start = 0
        self.action_duration = 0
        self.progress = 0

    def tick(self):
        #print self.action_duration-self.progress
        if self.current_action is not None:
            self.progress = time.time()-self.action_start
            if self.progress > self.action_duration:
                self.current_action.finish()
                self.__init__(self.reject_dups)

    def do_action(self, action, interrupt=False):
        if self.current_action is None:
            self.current_action = action
            self.action_start = time.time()
            action.start()
            self.action_duration = action.duration
            return
        if action.action_id == self.current_action.action_id and self.reject_dups:
            action.reject("duplicate")
            return  # CASE: Already doing that action!
        if interrupt:
            self.current_action.interrupted()
            self.current_action = action
            self.action_start = time.time()
            action.start()
            self.action_duration = action.duration
            return
        action.reject("busy")  # CASE: Another action is busy, and interrupt == False


if __name__ == "__main__":
    import pygame
    from roengine import *
    pygame.init()

    screen = pygame.display.set_mode([640, 480])

    class DummyAction(Action):
        def start(self):
            print ("START: Action %s" % self.action_id)
        def finish(self):
            print ("DONE: Action %s" % self.action_id)
        def interrupted(self):
            print ("INTERRUPTED: Action %s" % self.action_id)
        def reject(self, reason):
            print ("REJECT[%s]: Action %s" % (reason, self.action_id))

    a0 = DummyAction('testaction', 0, 5)
    a1 = DummyAction('testaction', 1, 0)

    manager = ActionManager()

    running = True
    while running:
        screen.fill([255, 255, 255])
        manager.tick()
        screen.blit(Text(str(manager.action_duration-manager.progress)).image, [10,10])
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    manager.do_action(a0, False)
                if event.key == pygame.K_2:
                    manager.do_action(a1, False)
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

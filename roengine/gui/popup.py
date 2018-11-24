# -*- coding: UTF-8 -*-

__all__ = ['PopUp', 'popups']


class _PopUpManager(object):
    def __init__(self):
        self._current = None

    def open(self, popup):
        if self._current is not None:
            self._current.close("override")
        self._current = popup
        self._current.open()

    def close(self):
        self._current.close("user")
        self._current = None

    def tick(self, *args):
        if self._current is not None:
            self._current.mtick(*args)
            return self._current.pause if self._current is not None else False
        return False


popups = _PopUpManager()


class PopUp(object):
    def __init__(self, pause=True, state='main'):
        self._state = state
        self.is_open = False
        self.pause = pause

    def open(self):
        self.is_open = True

    def close(self, reason):
        self.is_open = False

    def tick_arbitrary(self, state, args): pass

    def unhandled_update_state(self, old, new): pass

    def tick_main(self, *args): pass

    def update_state(self, newstate):
        assert type(newstate) == str
        oldstate = self._state[:]
        self._state = newstate
        if hasattr(self, "%s_to_%s" % (oldstate, newstate)):
            eval("self.%s_to_%s" % (oldstate, newstate))()
        else:
            self.unhandled_update_state(oldstate, newstate)

    def mtick(self, *args):
        if not self.is_open:
            return
        if hasattr(self, "tick_"+self._state):
            eval("self.tick_" + self._state)(*args)
        else:
            self.tick_arbitrary(self._state, args)

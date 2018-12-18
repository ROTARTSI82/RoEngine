import pygame

__all__ = ["Map", ]


class Map(object):
    def __init__(self, size):
        self._map = pygame.Surface(size).convert()
        self.scaled = self._map
        self.rects = []
        self._scroll = [0, 0]

    def blit(self, *args, **kwargs):
        self.rects.append(self._map.blit(*args, **kwargs))

    def draw_sprite(self, obj):
        self.rects.append(self._map.blit(obj.image, obj.rect))

    def fill(self, color):
        self._map.fill(color)

    def draw_group(self, group, get_rects=True):
        if not get_rects:
            return group.draw(self._map)
        for sprite in group:
            self.rects.append(self._map.blit(sprite.image, sprite.rect))

    def scale_to(self, screen, multiplier):
        self.scaled = pygame.transform.scale(self._map, (int(screen.get_width() * multiplier[0]),
                                                         int(screen.get_height() * multiplier[1])))#.convert()
        return self.scaled

    def get_scroll(self, target_coord, screen, center_at, lock_mode=(True, True)):
        scroll = [-(target_coord[0] * self.scaled.get_width() / self._map.get_width()) + center_at[0],
                  -(target_coord[1] * self.scaled.get_height() / self._map.get_height()) + center_at[1]]
        scroll[0] = max(-(self.scaled.get_width() - screen.get_width()), min(0, scroll[0]))
        scroll[1] = max(-(self.scaled.get_height() - screen.get_height()), min(0, scroll[1]))

        scroll[0] = scroll[0] if lock_mode[0] else 0
        scroll[1] = scroll[1] if lock_mode[1] else 0

        self._scroll = scroll

        return scroll

    def get_map(self):
        return self._map

    def blit_to(self, surf):
        return surf.blit(self.scaled, self._scroll)

    def translate_pos(self, pos):
        ret = [(pos[0] - self._scroll[0]) * self._map.get_width() / self.scaled.get_width(),
               (pos[1] - self._scroll[1]) * self._map.get_height() / self.scaled.get_height()]
        return ret

    def flush_rects(self):
        if self.rects:
            ret = self.rects
            self.rects = []
            return ret
        return []

    def get_pos(self, pos):
        ret = [pos[0] * self.scaled.get_width() / self._map.get_width() + self._scroll[0],
               pos[1] * self.scaled.get_height() / self._map.get_height() + self._scroll[1]]
        return ret

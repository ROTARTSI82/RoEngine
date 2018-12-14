# -*- coding: UTF-8 -*-


def dummy():
    return None


class ListNode(object):
    def __init__(self, prev=None, val=None, next=None):
        self.prev, self.val, self.next = prev, val, next

    def deepcopy(self):  # Unneccassary.
        return ListNode(self.prev.deepcopy() if self.prev is not None else None, self.val,
                        self.next.deepcopy() if self.next is not None else None)
    """  # DEBUG funcs. Waste of memory in most cases.
    def get_str(self, cpymode):
        if not self:
            return '[]'
        head_cpy = getattr(self, cpymode)()
        ret = '['
        while head_cpy is not None:
            ret += str(head_cpy.val) + ", "
            head_cpy = head_cpy.next
        return ret + ']'

    def get_tail(self, cpymode):
        if not self:
            return '[]'
        head_cpy = getattr(self, cpymode)()
        ret = '['
        while head_cpy is not None:
            ret += str(head_cpy.val) + ", "
            head_cpy = head_cpy.prev
        return ret + ']'
    """

    def surfcopy(self):
        return ListNode(self.prev, self.val, self.next)


class LinkedList(object):
    def __init__(self, iterator=(), cpymode=0):
        self.head = None
        self.tail = None
        self.cpymode = max(min(cpymode, 1), 0)  # Clamp to 0 - 1
        self.cpyattr = "surfcopy" if self.cpymode == 0 else "deepcopy"
        for i in iterator:
            self.append(i)

    def reset_head(self):
        if self.head is None:
            return
        while self.head.prev is not None:
            self.head = self.head.prev

    def reset_tail(self):
        if self.tail is None:
            return
        while self.tail.next is not None:
            self.tail = self.tail.next

    def pop(self):
        if self.tail is None:
            raise RuntimeError("List is empty. Nothing to pop")
        ret = self.tail.val
        self.tail = self.tail.prev
        self.tail.next = None
        self.sync_head()
        self.sync_tail()
        return ret

    def pop_first(self):
        if self.head is None:
            return RuntimeError("List empty. Nothing to pop")
        ret = self.head.val
        self.head = self.head.next
        self.head.prev = None
        self.sync_tail()
        self.sync_head()
        return ret

    def append(self, val):
        self.tail = ListNode(getattr(self.tail, self.cpyattr, dummy)(), val)
        if self.tail.prev is not None:
            self.tail.prev.next = getattr(self.tail, self.cpyattr, dummy)()
        self.sync_head()
        self.sync_tail()

    def prepend(self, val):
        self.head = ListNode(None, val, getattr(self.head, self.cpyattr, dummy)())
        if self.head.next is not None:
            self.head.next.prev = getattr(self.head, self.cpyattr, dummy)()
        self.sync_tail()
        self.sync_head()

    def sync_head(self):
        if self.tail is None:
            self.head = None
            return
        tail_cpy = getattr(self.tail, self.cpyattr, dummy)()
        while tail_cpy.prev is not None:
            tail_cpy.prev.next = getattr(tail_cpy, self.cpyattr, dummy)()
            tail_cpy = tail_cpy.prev
        self.head = tail_cpy

    def sync_tail(self):
        if self.head is None:
            self.tail = None
            return
        headcpy = getattr(self.head, self.cpyattr, dummy)()
        while headcpy.next is not None:
            headcpy.next.prev = getattr(headcpy, self.cpyattr, dummy)()
            headcpy = headcpy.next
        self.tail = headcpy

    def __iter__(self):
        headcpy = getattr(self.head, self.cpyattr, dummy)()
        ret = []
        while headcpy is not None:
            ret.append(headcpy.val)
            headcpy = headcpy.next
        return iter(ret)

    def __len__(self):
        l = 0
        headcpy = getattr(self.head, self.cpyattr, dummy)()
        while headcpy is not None:
            l += 1
            headcpy = headcpy.next
        return l

    def __getitem__(self, item):
        assert type(item) == int, "item type is not int"
        current_len = 0
        if item < 0:
            current_len -= 1
            tailcpy = getattr(self.tail, self.cpyattr, dummy)()
            while tailcpy is not None:
                if current_len == item:
                    return tailcpy.val
                tailcpy = tailcpy.prev
                current_len -= 1
        else:
            headcpy = getattr(self.head, self.cpyattr, dummy)()
            while headcpy is not None:
                if current_len == item:
                    return headcpy.val
                headcpy = headcpy.next
                current_len += 1
        raise IndexError(str(item)+" is out of range")

    def __str__(self):
        if not self.head:
            return '[]'
        head_cpy = getattr(self.head, self.cpyattr, dummy)()
        ret = '['
        while head_cpy is not None:
            ret += str(head_cpy.val) + ", "
            head_cpy = head_cpy.next
        return ret + ']'

while True:
    exec (raw_input(">>> "))

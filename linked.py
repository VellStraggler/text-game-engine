class Linked():
    """A one-way linked list. Uses a boolean to check if it's circular. Check
    for self.curr.next to find out if an animation is complete."""
    def __init__(self,anim_list:list,loop:bool=False,stuns:bool=False):
        self.first = Node(anim_list[0])
        self.curr = self.first
        self.len = len(anim_list)
        self.loop = loop
        self.stuns = stuns
        self.anim_list = anim_list # for indexing only
        assert self.len > 0, "Received empty list."
        for i in range(1,len(anim_list)):
            self.curr.next = Node(anim_list[i])
            self.curr = self.curr.next
        self.curr = self.first # Start on frame 1
    
    def get(self, i:int = 0):
        return self.anim_list[i]

    def next(self):
        """Loops back to the first if self.loop. Otherwise,
        it does nothing once finished, only returning data
        from the last node each time."""
        if self.curr.next is not None:
            self.curr = self.curr.next
        elif self.loop:
            self.curr = self.first
        return self.curr.data
    def reset(self):
        self.curr = self.first

class Node():
    """A single pointer node."""
    def __init__(self,data=None):
        self.data = data
        self.next = None


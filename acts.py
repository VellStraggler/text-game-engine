from linked import Linked
from statics import deconstruct_path

class Acts():
    def __init__(self):
        self.acts = []
        self.acted_obj_chars = set()
        # This is used to find which objects are
        # never used and can be removed as objects.
    def new(self,func,name="default",type="interact", item_char="",
        arg=None,map="default",act_on_self=False,locked = False, loc_arg = []):
        if map != "default":
            map = deconstruct_path(map)
        if isinstance(arg,list): # List of strings should be a Linked list.
            all_strs = True
            for i in arg:
                if not isinstance(i,str):
                    all_strs = False
            if all_strs:
                arg = Linked(arg)
        new_act = self.Act(func,name,type,item_char,arg,map,act_on_self,locked,loc_arg)
        self.acts.append(new_act)

        self.acted_obj_chars.add(item_char)
        self.acted_obj_chars.add(item_char)

    class Act():
        def __init__(self,func,name="default",type="interact",
        item_char="",arg=None,map="",act_on_self=False,locked=False,loc_arg = []):
            self.func = func
            self.name = name
            self.type = type # location, item, survive, die, interact
            self.item_char = item_char # The char of the object that was interacted with.
            self.act_on_self= act_on_self              
            self.arg = arg # could be the new skin,
            self.map = map
            self.locked = locked
            self.loc_arg = loc_arg

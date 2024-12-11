import sys
import os

# Add the parent folder of "textengine.py" to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from textengine import Game,Linked,DEFAULT_COLOR
from statics import color_by_number

g = Game()
g.set_map_path("under/m/menu")
g.set_sprite_path("under/sprites")
g.get_texts("under/text")
g.set_theme('under/a/menu')
g.camera_follow = ["x","y"]
wood = 52
wall = 235
robe = 239

g.new_object("title","Z",color=232,geom="background")
g.new_object("cursor","X",move="wasd",yspeed=50,xspeed=5)
g.new_object("start","Y",geom="all",color=236)
g.new_object("quit","Q",geom="all",color=244)

g.new_action(name="quit game",type="touch",item_char="Q",
    func=g.act_sound,arg="under/a/move_cursor2")
g.new_action(g.act_quit,"quit game","touch","Q")
g.new_action(g.act_sound,"start game","touch","Y",arg="under/a/move_cursor2.wav")
g.new_action(g.act_change_theme,"start game","touch","Y","under/a/theme.wav")
g.new_action(g.act_change_map,"start game","touch","Y","under/m/map1.txt",map="under/m/menu.txt")

g.new_object("grimm","A",geom="line",move="wasd",xspeed=50, yspeed=20,animate="sneaky")

doors_locked = ["door-locked","door-open"]
doors =     ["door-closed","door-open"]
door_geom = ["line","skeleton"]
windows=    ["window-closed","window-open"]
clock =     Linked(["clock-l","clock","clock-r","clock"],True)
lights =    Linked([color_by_number(58),DEFAULT_COLOR])
grimm_open =Linked(["grimm-w-open1","grimm-w-open2","grimm-w-open3","grimm-w"],False,True)

box_anim =  Linked(["box","box-f1","box-f2","box-f3","box-f4","box-f5","box-f6"],True)
g.new_object("box","\"",geom="line",color=wood,animate=box_anim)

g.new_object("couch","C",color=wood)
g.objs.sprites["couch"] = g.objs.get_flipped_sprite(g.objs.sprites["couch"])
g.new_object("door-closed","d",geom="line",color=wood)
g.new_object("door-locked","D",geom="line",color=wood)
g.new_object("wall-side","w",color=wall)
g.new_object("wall","f",color=wall,geom="skeleton")
g.new_object("wall-back","b",color=wall)
g.new_object("wall-block","J",color=wall)
g.new_object("father","u",geom="line",color=robe)
g.new_object("fence","x",geom="line")
g.new_object("fence-side","z")
g.new_object("piano","p",geom="line")
g.new_object("plant","K",geom="line")
g.new_object("carpet","G",geom="background",color=53)
g.new_object("carpet-side","H",geom="background",color=53)
g.new_object("light","P",geom="line",color=58)
g.new_object("key","k",geom="line")
g.new_object("bedside","t",geom="line",color=wood)
g.new_object("bed","U",geom="all")
g.new_object("bed-large","e",geom="all",color=wood)
g.new_object("bookshelf","B",geom="line")
g.new_object("curtain","W",geom="skeleton")
g.new_object("window","v",geom="background")
g.new_object("window-closed","h",geom="all")
g.new_object("clock","c",geom="line",color=wood,animate=clock)
g.new_object("stairs-up","S",geom="background")
g.new_object("stairs-down","s",geom="background")
g.new_object("table","T",geom="line",color=wood)
g.new_object("flower","^",geom=None)
g.new_object("grass","&",geom=None,color=28)
g.new_object("bush","n",geom="line")
g.new_object("tree","O",geom="skeleton",color=wood)
g.new_object("shingles","#",geom="background")
g.new_object("v-roof","R",geom="line")
g.new_object("outer-wall","r",geom="line")
g.new_object("diagon-wall","a",geom="background")
g.new_object("mirror",">",geom="background")
g.mirrors.new_type("mirror",True,-1,False,False,False,1)
g.mirrors.new_type("water",False,17,True,False,True)
g.mirrors.new("outside","water",30,31,80,40,0,-1)
g.mirrors.new("bedroom","mirror",41,6,47,14,0,5)

g.new_object("cloud","{",geom="line",move="leftright",xspeed=1,color=248)
g.new_object("moon","m",geom="background")
g.mirrors.new("sleepy","water",0,28,180,37,0,-1)
g.new_object("grassyfloor","}",geom=None,color=34)
g.new_object("star","*",geom="background")

def open_door(obj,arg):
    g.act_sound(obj,arg[0])
    g.act_change_sprite(obj,arg[1])
    g.act_change_geom(obj,arg[2])
door_arg = ["under/a/door_close.wav",Linked(doors),Linked(door_geom),grimm_open]
g.new_action(item_char="d",func=open_door,arg=door_arg)
g.new_action(g.act_animate,item_char="d",act_on_self=True,arg=grimm_open)
g.new_action(g.act_sound,item_char="D",arg="under/a/door_close.wav")
g.new_action(g.act_message,"not sleepy","interact","U",7)
g.new_action(g.act_message,"unlocked","interact","D",3)
g.new_action(g.act_change_sprite,"unlock_door","interact","D",doors,locked=True)
g.new_action(g.act_change_geom,"unlock_door","interact","D",door_geom,locked=True)
g.new_action(g.act_animate,"unlock_door","interact","D",act_on_self=True,arg=grimm_open,locked=True)
g.new_action(item_char="P",func=g.act_sound,arg="under/a/bink_sound.wav")
g.new_action(g.act_change_color,"light-switch",item_char="P",arg=lights)
g.new_action(g.act_animate,item_char="P",act_on_self=True,arg=grimm_open)
g.new_action(g.act_change_sprite,"open-curtain",item_char="h",arg=windows)
g.new_action(g.act_animate,item_char="h",act_on_self=True,arg=grimm_open)
g.new_action(item_char="h",func=g.act_sound,arg="under/a/bink_sound.wav")

g.new_action(g.act_change_map,"","location","A",[25,17,"under/m/map2.txt"],loc_arg=[228,13],map="under/m/map1.txt")
g.new_action(g.act_sound,"","location","A","under/a/3steps_away.wav",loc_arg=[228,13],map="under/m/map1.txt")
g.new_action(g.act_message,"","location","A",5,loc_arg=[228,14],map="under/m/map1.txt")

g.new_action(g.act_change_map,"","location","A",[228,16,"under/m/map1.txt"],loc_arg=[25,14],map="under/m/map2.txt")
g.new_action(g.act_sound,"","location","A","under/a/3steps_away.wav",loc_arg=[25,14],map="under/m/map2.txt")
g.new_action(g.act_message,"","location","A",6,loc_arg=[25,15],map="under/m/map2.txt")

g.new_action(g.act_change_map,"","location","A",[40,35,"under/m/bedroom.txt"],loc_arg=[62,15],map="under/m/map2.txt")
g.new_action(g.act_change_map,"","location","A",[62,17,"under/m/map2.txt"],loc_arg=[40,36],map="under/m/bedroom.txt")

def go_outside(obj,arg):
    g.act_change_map(obj,arg)
    g.set_default_color(color_by_number(64))
g.new_action(go_outside,"","location","A",[48,33,"under/m/outside.txt"],loc_arg=[-1,78],map="under/m/map1.txt")
g.new_action(g.act_change_map,"","location","A",[79,77,"under/m/map1.txt"],loc_arg=[48,31],map="under/m/outside.txt")

g.new_action(g.act_message,"play_piano","interact","p",1)
g.new_action(g.act_sound,"play_piano",item_char="p",arg="under/a/piano.wav")

def get_key(obj,arg=None):
    g.act_unlock(obj,"unlock_door")
    g.act_lock(obj,"unlocked")
    g.act_message(obj,2)
    g.act_kill(obj)
    g.act_sound(obj,"under/a/key.wav")
g.new_action(item_char="k",func=get_key)

g.run_game(debug=True)
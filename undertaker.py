from textengine import Game,Linked,color_by_num,DEFAULT_COLOR

g = Game()
g.set_map_path("under/m/menu")
g.set_sprite_path("under/sprites")
g.get_texts("under/text")
g.set_theme('under/a/menu')
g.camera_follow = ["x","y"]
wood = 52
wall = 235
robe = 239

g.objs.new("title","Z",color=232,geom="background")
g.objs.new("cursor","X",move="wasd",yspeed=500,xspeed=10)
g.objs.new("start","Y",geom="all",color=236)
g.objs.new("quit","Q",geom="all",color=244)

g.acts.new(name="quit game",type="touch",item_char="Q",
    func=g.act_sound,arg="under/a/move_cursor2")
g.acts.new(g.act_quit,"quit game","touch","Q")
g.acts.new(g.act_sound,"start game","touch","Y",arg="under/a/move_cursor2.wav")
g.acts.new(g.act_change_theme,"start game","touch","Y","under/a/theme.wav")
g.acts.new(g.act_change_map,"start game","touch","Y","under/m/map1.txt",map="under/m/menu.txt")

g.objs.new("grimm","A",geom="line",move="wasd",xspeed=50, yspeed=20,animate="sneaky")

doors_locked = ["door-locked","door-open"]
doors =     ["door-closed","door-open"]
door_geom = ["line","skeleton"]
windows=    ["window-closed","window-open"]
clock = Linked(["clock-l","clock","clock-r","clock"],True)
lights =    Linked([color_by_num(58),DEFAULT_COLOR])
grimm_open =Linked(["grimm-w-open1","grimm-w-open2","grimm-w-open3","grimm-w"],False,True)

g.objs.new("couch","C",color=wood)
g.objs.sprites["couch"] = g.objs.get_flipped_sprite(g.objs.sprites["couch"])
g.objs.new("door-closed","d",geom="line",color=wood)
g.objs.new("door-locked","D",geom="line",color=wood)
g.objs.new("wall-side","w",color=wall)
g.objs.new("wall","f",color=wall,geom="skeleton")
g.objs.new("wall-back","b",color=wall)
g.objs.new("wall-block","J",color=wall)
g.objs.new("father","u",geom="line",color=robe)
g.objs.new("fence","x",geom="line")
g.objs.new("fence-side","z")
g.objs.new("piano","p",geom="line")
g.objs.new("plant","K",geom="line")
g.objs.new("carpet","G",geom="background",color=53)
g.objs.new("carpet-side","H",geom="background",color=53)
g.objs.new("light","P",geom="line",color=58)
g.objs.new("key","k",geom="line")
g.objs.new("bedside","t",geom="line",color=wood)
g.objs.new("bed","U",geom="all")
g.objs.new("bed-large","e",geom="all",color=wood)
g.objs.new("bookshelf","B",geom="line")
g.objs.new("curtain","W",geom="skeleton")
g.objs.new("window","v",geom="background")
g.objs.new("window-closed","h",geom="all")
g.objs.new("clock","c",geom="line",color=wood,animate=clock)
g.objs.new("stairs-up","S",geom="background")
g.objs.new("stairs-down","s",geom="background")
g.objs.new("table","T",geom="line",color=wood)
g.objs.new("flower","^",geom=None)
g.objs.new("grass","&",geom=None,color=28)
g.objs.new("bush","n",geom="line")
g.objs.new("tree","O",geom="skeleton",color=wood)
g.objs.new("shingles","#",geom="background")
g.objs.new("v-roof","R",geom="line")
g.objs.new("outer-wall","r",geom="line")
g.objs.new("diagon-wall","a",geom="background")
g.objs.new("mirror",">",geom="background")
g.mirs.new_type("mirror",True,-1,False,False,False,1)
g.mirs.new_type("water",False,17,True,False,True)
g.mirs.new("outside","water",30,30,60,40,0,-1)
g.mirs.new("bedroom","mirror",41,6,47,14,0,5)

g.objs.new("cloud","{",geom="line",move="leftright",xspeed=1,color=248)
g.objs.new("moon","m",geom="background")
g.mirs.new("sleepy","water",0,28,180,37,0,-1)
g.objs.new("grassyfloor","}",geom=None,color=34)
g.objs.new("star","*",geom="background")



def open_door(obj,arg):
    g.act_sound(obj,arg[0])
    g.act_change_sprite(obj,arg[1])
    g.act_change_geom(obj,arg[2])
door_arg = ["under/a/door_close.wav",Linked(doors),Linked(door_geom),grimm_open]
g.acts.new(item_char="d",func=open_door,arg=door_arg)
g.acts.new(g.act_animate,item_char="d",act_on_self=True,arg=grimm_open)
g.acts.new(g.act_sound,item_char="D",arg="under/a/door_close.wav")
g.acts.new(g.act_message,"not sleepy","interact","U",7)
g.acts.new(g.act_message,"unlocked","interact","D",3)
g.acts.new(g.act_change_sprite,"unlock_door","interact","D",doors,locked=True)
g.acts.new(g.act_change_geom,"unlock_door","interact","D",door_geom,locked=True)
g.acts.new(g.act_animate,"unlock_door","interact","D",act_on_self=True,arg=grimm_open,locked=True)
g.acts.new(item_char="P",func=g.act_sound,arg="under/a/bink_sound.wav")
g.acts.new(g.act_change_color,"light-switch",item_char="P",arg=lights)
g.acts.new(g.act_animate,item_char="P",act_on_self=True,arg=grimm_open)
g.acts.new(g.act_change_sprite,"open-curtain",item_char="h",arg=windows)
g.acts.new(g.act_animate,item_char="h",act_on_self=True,arg=grimm_open)
g.acts.new(item_char="h",func=g.act_sound,arg="under/a/bink_sound.wav")

g.acts.new(g.act_change_map,"","location","A",[25,17,"under/m/map2.txt"],loc_arg=[228,13],map="under/m/map1.txt")
g.acts.new(g.act_sound,"","location","A","under/a/3steps_away.wav",loc_arg=[228,13],map="under/m/map1.txt")
g.acts.new(g.act_message,"","location","A",5,loc_arg=[228,14],map="under/m/map1.txt")

g.acts.new(g.act_change_map,"","location","A",[228,16,"under/m/map1.txt"],loc_arg=[25,14],map="under/m/map2.txt")
g.acts.new(g.act_sound,"","location","A","under/a/3steps_away.wav",loc_arg=[25,14],map="under/m/map2.txt")
g.acts.new(g.act_message,"","location","A",6,loc_arg=[25,15],map="under/m/map2.txt")

g.acts.new(g.act_change_map,"","location","A",[40,35,"under/m/bedroom.txt"],loc_arg=[62,15],map="under/m/map2.txt")
g.acts.new(g.act_change_map,"","location","A",[62,17,"under/m/map2.txt"],loc_arg=[40,36],map="under/m/bedroom.txt")

def go_outside(obj,arg):
    g.act_change_map(obj,arg)
    g.set_default_color(color_by_num(64))
g.acts.new(go_outside,"","location","A",[48,33,"under/m/house.txt"],loc_arg=[-1,78],map="under/m/map1.txt")
g.acts.new(g.act_change_map,"","location","A",[79,77,"under/m/map1.txt"],loc_arg=[48,31],map="under/m/house.txt")

g.acts.new(g.act_message,"play_piano","interact","p",1)
g.acts.new(g.act_sound,"play_piano",item_char="p",arg="under/a/piano.wav")

def get_key(obj,arg=None):
    g.act_unlock(obj,"unlock_door")
    g.act_lock(obj,"unlocked")
    g.act_message(obj,2)
    g.act_kill(obj)
    g.act_sound(obj,"under/a/key.wav")
g.acts.new(item_char="k",func=get_key)

g.run_game(debug=True)
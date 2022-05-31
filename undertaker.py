import textengine as tx
import os
from time import sleep
os.system("")

g = tx.Game()
g.set_map_path("under/m/menu.txt")
g.set_sprite_path("under/sprites.txt")
g.get_texts("under/text.txt")
g.set_theme('under/a/menu.wav')
g.camera_follow = ["x","y"]
wood = 52
wall = 235
robe = 239

g.objs.new("title","Z",color=232,geom="background")
g.objs.new("cursor","X",move="wasd",yspeed=500,xspeed=1)
g.objs.new("start","Y",geom="all",color=236)
g.objs.new("help","V",geom="all",color=240)
g.objs.new("quit","Q",geom="all",color=244)

g.acts.new("","touch","X","sound",["V","under/a/move_cursor2.wav"])
g.acts.new("quit game","touch","X","sound",["Q","under/a/move_cursor2.wav"])
g.acts.new("quit game","touch","X","quit",["Q"])
g.acts.new("start game","touch","X","sound",["Y","under/a/move_cursor2.wav"])
g.acts.new("start game","touch","X","change_theme",["Y","under/a/theme.wav"])
g.acts.new("start game","touch","X","change_map",["Y","under/m/menu.txt","under/m/map1.txt"])

g.objs.new("grimm","A",geom="line",move="wasd",xspeed=50, yspeed=20,animate="sneaky")

g.objs.new("couch","C",color=wood)
g.objs.sprites["couch"] = g.objs.get_flipped_sprite(g.objs.sprites["couch"])
g.objs.new("face","L")
g.objs.new("face","q",geom="skeleton")
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
g.objs.new("clock","c",geom="line",color=wood)
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

doors =     {"door-closed":"door-open","door-open":"door-closed","door-locked":"door-open"}
door_geom = {"skeleton":"line","line":"skeleton"}
windows=    {"window-closed":"window-open","window-open":"window-closed"}
lights =    {tx.color_by_num(58):tx.DEFAULT_COLOR,tx.DEFAULT_COLOR:tx.color_by_num(58)}

g.acts.new(char="d",effect="sound",arg="under/a/door_close.wav")
g.acts.new(char="d",effect="change_sprite",arg=doors)
g.acts.new(char="d",effect="change_geometry",arg=door_geom)
g.acts.new(char="D",effect="sound",arg="under/a/door_close.wav")
g.acts.new("","interact","U","message",[7])
g.acts.new("unlocked","interact","D","message",[3])
g.acts.new("unlock_door","interact","D","change_sprite",doors,True)
g.acts.new("unlock_door","interact","D","change_geometry",door_geom,True)
g.acts.new(char="P",effect="sound",arg="under/a/bink_sound.wav")
g.acts.new("light-switch",char="P",effect="change_color",arg=lights)
g.acts.new("open-curtain",char="h",effect="change_sprite",arg=windows)
g.acts.new(char="h",effect="sound",arg="under/a/bink_sound.wav")

g.acts.new("","location","g","change_map",[228,13,25,17,"under/m/map1.txt","under/m/map2.txt"])
g.acts.new("","location","g","sound",[228,13,"under/m/map1.txt","under/a/3steps_away.wav"])
g.acts.new("","location","g","message",[228,14,"under/m/map1.txt",5])

g.acts.new("","location","g","change_map",[25,14,228,16,"under/m/map2.txt","under/m/map1.txt"])
g.acts.new("","location","g","sound",[25,14,"under/m/map2.txt","under/a/3steps_away.wav"])
g.acts.new("","location","g","message",[25,15,"under/m/map2.txt",6])

g.acts.new("","location","g","change_map",[62,15,40,35,"under/m/map2.txt","under/m/bedroom.txt"])
g.acts.new("","location","g","change_map",[40,36,62,17,"under/m/bedroom.txt","under/m/map2.txt"])

g.acts.new("","location","g","change_map",[79,78,48,33,"under/m/map1.txt","under/m/outside.txt"])

g.acts.new("","location","g","change_map",[48,31,79,77,"under/m/outside.txt","under/m/map1.txt"])

g.acts.new("play_piano","interact","p","message",[1])
g.acts.new("play_piano",char="p",effect="sound",arg="under/a/piano.wav")
g.acts.new(char="k",effect="unlock",arg="unlock_door")
g.acts.new(char="k",effect="lock",arg="unlocked")
g.acts.new(char="k",effect="message",arg=[2])
g.acts.new(char="k",effect="kill")
g.acts.new(char="k",effect="sound",arg="under/a/key.wav")

g.run_game(debug=True)
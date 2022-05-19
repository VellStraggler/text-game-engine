import textengine as tx
import os
from time import sleep
os.system("")

g = tx.Game()
g.set_map_path("under/menu.txt")
g.set_sprite_path("under/sprites.txt")
g.get_texts("under/text.txt")
g.set_theme('under/menu.wav')
g.camera_follow = ["x","y"]
wood = 52
wall = 235
robe = 239

g.objs.new("title","Z",color=232)
g.objs.new("cursor","X",move="wasd",yspeed=30,xspeed=30)
g.objs.new("start","Y",geom="all",color=236)
g.objs.new("help","V",geom="all",color=240)
g.objs.new("quit","Q",geom="all",color=244)
g.objs.new("invis-wall","A",geom="all")

g.acts.new("","touch","X","sound",["V","under/move_cursor2.wav"])
g.acts.new("quit game","touch","X","sound",["Q","under/move_cursor2.wav"])
g.acts.new("quit game","touch","X","quit",["Q"])
g.acts.new("start game","touch","X","sound",["Y","under/move_cursor2.wav"])
g.acts.new("start game","touch","X","change_theme",["Y","under/theme.wav"])
g.acts.new("start game","touch","X","change_map",["Y","under/menu.txt","under/map1.txt"])

g.objs.new("grimm","g",geom="line",move="wasd",xspeed=50, yspeed=20,animate="sneaky",color=robe)

g.objs.new("face","L")
g.objs.new("face","q",geom="skeleton")
g.objs.new("door-closed","d",geom="line",color=wood)
g.objs.new("door-locked","D",geom="line",color=wood)
g.objs.new("wall-side","w",color=wall)
g.objs.new("wall","f",color=wall,geom="skeleton")
g.objs.new("wall-back","b",color=wall)
g.objs.new("wall-block","J",color=wall)
g.objs.new("father","u",geom="line",color=robe)
g.objs.new("jack",'t',geom="line")
g.objs.new("fence","x",geom="line")
g.objs.new("fence-side","z")
g.objs.new("piano","p",geom="line",color=wood)
g.objs.new("piano-sheet","@",geom="skeleton",color=7)
g.objs.new("couch","C",color=wood)
g.objs.new("carpet","G",geom="background")
g.objs.new("light","P",geom="line",color=58)
g.objs.new("key","k",geom="line")
g.objs.new("bedside","t",geom="line",color=wood)
g.objs.new("bed","U",geom="all",color=wood)
g.objs.new("bookshelf","B",geom="line",color=wood)
g.objs.new("curtain","W",geom="skeleton",color=wall+5)
g.objs.new("window","v",geom="background",color=192)
g.objs.new("stairs","S",geom="background")
g.objs.new("table","T",geom="line",color=wood)
g.objs.new("flower","^",geom="background",color=226)
g.objs.new("grass","&",geom="background",color=28)
g.objs.new("bush","n",geom="line",color=28)
g.objs.new("tree","O",geom="line",color=wood)

doors =     {"door-closed":"door-open","door-open":"door-closed","door-locked":"door-open"}
door_geom = {"skeleton":"line","line":"skeleton"}
plants =    {"plant":"plant1","plant1":"plant"}
lights =    {tx.color_by_num(58):tx.DEFAULT_COLOR,tx.DEFAULT_COLOR:tx.color_by_num(58)}

g.acts.new(char="d",effect="sound",arg="under/door_close.wav")
g.acts.new(char="d",effect="change_sprite",arg=doors)
g.acts.new(char="d",effect="change_geometry",arg=door_geom)
g.acts.new(char="D",effect="sound",arg="under/door_close.wav")
g.acts.new("unlock_door","interact","D","change_sprite",doors,True)
g.acts.new("unlocked","interact","D","message",[3])
g.acts.new("unlock_door","interact","D","change_geometry",door_geom,True)
g.acts.new(char="P",effect="sound",arg="under/bink_sound.wav")
g.acts.new("light-switch",char="P",effect="change_color",arg=lights)
g.acts.new("","location","g","change_map",[235,15,235,45,"under/map1.txt","under/upstairs.txt"])
g.acts.new("","location","g","change_map",[235,47,235,18,"under/upstairs.txt","under/map1.txt"])
g.acts.new("","location","g","change_map",[79,78,48,33,"under/map1.txt","under/outside.txt"])
g.acts.new("","location","g","change_map",[48,32,79,77,"under/outside.txt","under/map1.txt"])
g.acts.new("play_piano","interact","p","message",[1])
g.acts.new("play_piano",char="p",effect="sound",arg="under/piano.wav")
g.acts.new(char="k",effect="unlock",arg="unlock_door")
g.acts.new(char="k",effect="lock",arg="unlocked")
g.acts.new(char="k",effect="kill")
g.acts.new(char="k",effect="sound",arg="under/key.wav")

g.run_game(debug=True)
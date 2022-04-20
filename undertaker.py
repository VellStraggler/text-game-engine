import textengine as tx

g = tx.Game()
g.curr_map.set_path("under/menu.txt")
#g.get_texts("under/text.txt")
g.objs.get_sprites("under/sprites.txt")
g.camera_follow = ["x","y"]
g.add_theme('under/menu.wav')
wood = 52
wall = 235
robe = 239

g.objs.new("title","Z",color=232)
g.objs.new("cursor","X",move="wasd",yspeed=30,xspeed=30)
g.objs.new("start","Y",geom="all",color=236)
g.objs.new("help","V",geom="all",color=240)
g.objs.new("quit","Q",geom="all",color=244)

g.acts.new("","touch","X","sound",["V","under/move_cursor2.wav"])
g.acts.new("quit game","touch","X","sound",["Q","under/move_cursor2.wav"])
g.acts.new("quit game","touch","X","quit",["Q"])
g.acts.new("start game","touch","X","sound",["Y","under/move_cursor2.wav"])
g.acts.new("start game","touch","X","switch_theme",["Y","under/theme.wav"])
g.acts.new("start game","touch","X","switch_map",["Y","under/map1.txt"])

player = g.objs.Obj("grimm","g",geom="line",move="wasd",
    xspeed=100, yspeed=20,animate="sneaky",color=robe)
g.objs.append_obj(player)
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
g.objs.new("piano-key","@",geom="skeleton",color=7)
g.objs.new("couch","C",color=wood)
g.objs.new("carpet","G",geom=None)
g.objs.new("plant","P",geom="line",color=58)
g.objs.new("key","k",geom=None)
g.objs.new("bedside","t",geom="line",color=wood)
g.objs.new("bookshelf","B",geom="line",color=wood)
g.objs.new("curtain","W",geom="skeleton",color=wall+5)
g.objs.new("window","v",color=192)
g.objs.new("stair-flat","s",geom=None)
g.objs.new("stair-wall","S",geom=None)
g.objs.new("table","T",geom="line",color=wood)

doors =     {"door-closed":"door-open","door-open":"door-closed","door-locked":"door-open"}
door_geom = {"skeleton":"line","line":"skeleton"}
plants = {"plant":"plant1","plant1":"plant"}

g.acts.new("message","touch","X","message",["B",1])
g.acts.new(char="d",effect="sound",arg="under/door_close.wav")
g.acts.new(char="d",effect="switch_sprite",arg=doors)
g.acts.new(char="d",effect="switch_geometry",arg=door_geom)
g.acts.new(char="D",effect="sound",arg="under/door_close.wav")
g.acts.new("unlock_door","interact","D","switch_sprite",doors,True)
g.acts.new("unlock_door","interact","D","switch_geometry",door_geom)
g.acts.new(char="P",effect="sound",arg="under/bink_sound.wav")
g.acts.new(char="P",effect="switch_sprite",arg=plants)
g.acts.new("","location","g","switch_map",[235,15,"under/map1.txt"])
g.acts.new(char="p",effect="sound",arg="under/piano.wav")
g.acts.new(char="k",effect="unlock",arg="unlock_door")
g.acts.new(char="k",effect="sound",arg="under/bink_sound.wav")
g.acts.new(char="k",effect="kill")

g.run_game(debug=False)
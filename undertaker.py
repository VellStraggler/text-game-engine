import textengine as tx

g = tx.Game()
g.curr_map.set_path("under/menu.txt")
g.curr_map.set_overlay("under/overlay.txt")
g.objs.get_sprites("under/sprites.txt")
g.objs.get_texts("under/text.txt")
g.camera_follow = ["x","y"]
g.folder = "under/"
g.default_color = tx.get_color_number(54)
g.add_theme('menu.wav')

g.objs.new("title","Z")
g.objs.new("cursor","X",move="wasd",geom="all",yspeed=30,xspeed=30)
g.objs.new("start","Y",geom="all")
g.objs.new("help","V",geom="all")
g.objs.new("quit","Q",geom="all")

g.acts.new("","touch","X","sound",["V","move_cursor2.wav"])
g.acts.new("quit game","touch","X","sound",["Q","move_cursor2.wav"])
g.acts.new("quit game","touch","X","quit",["Q"])
g.acts.new("start game","touch","X","sound",["Y","move_cursor2.wav"])
g.acts.new("start game","touch","X","switch_theme",["Y","theme.wav"])
g.acts.new("start game","touch","X","switch_map",["Y","under/map1.txt"])

player = g.objs.Obj("grimm","g",geom="line",move="wasd",
    xspeed=100, yspeed=20,animate="sneaky")
g.objs.append_obj(player)
g.objs.new("face","L")
g.objs.new("face","q",geom="skeleton")
g.objs.new("door-closed","d",geom="skeleton")
g.objs.new("door-locked","D",geom="skeleton")
g.objs.new("wall-side","w")
g.objs.new("wall","f")
g.objs.new("wall-back","b")
g.objs.new("father","u",geom="line")
g.objs.new("jack",'t',geom="line")
g.objs.new("fence","x",geom="line")
g.objs.new("fence-side","z")
g.objs.new("piano","p",geom="line")
g.objs.new("couch","C",geom="complex")
g.objs.new("carpet","G",geom=None)
g.objs.new("plant","P",geom="line")
g.objs.new("key","k",geom=None)
g.objs.new("bedside","t",geom="line")
g.objs.new("bookshelf","B",geom="line")
g.objs.new("curtain-window","W")
g.objs.new("stair-flat","s",geom=None)
g.objs.new("stair-wall","S",geom=None)
g.objs.new("table","T",geom="line")

doors = {"door-closed":"door-open","door-open":"door-closed","door-locked":"door-open"}
plants = {"plant":"plant1","plant1":"plant"}

g.acts.new(char="d",effect="sound",arg="door_close.wav")
g.acts.new(char="d",effect="switch_sprite",arg=doors)
g.acts.new(char="D",effect="sound",arg="door_close.wav")
g.acts.new("unlock_door","interact","D","switch_sprite",doors,True)
g.acts.new(char="P",effect="sound",arg="bink_sound.wav")
g.acts.new(char="P",effect="switch_sprite",arg=plants)
g.acts.new("","location","g","switch_map",[235,15,"under/map1.txt"])
g.acts.new(char="p",effect="sound",arg="piano.wav")
g.acts.new(char="k",effect="unlock",arg="unlock_door")
g.acts.new(char="k",effect="sound",arg="bink_sound.wav")
g.acts.new(char="k",effect="kill")

g.run_game()
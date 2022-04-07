import textengine as tx

g = tx.Game()
g.curr_map.set_path("under/map1.txt")
g.curr_map.set_overlay("under/under_overlay.txt")
g.objs.get_sprites("under/under_sprites.txt")
g.objs.get_texts("under/under_text.txt")
g.camera_follow = ["x","y"]
g.add_theme('under/theme.wav')
g.folder = "under/"

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

g.acts.new(char="d",effect="switch_sprite",arg=doors)
g.acts.new(char="d",effect="sound",arg="door_close.wav")
g.acts.new("unlock_door","interact","D","switch_sprite",doors,True)
g.acts.new(char="D",effect="sound",arg="door_close.wav")
g.acts.new(char="P",effect="switch_sprite",arg=plants)
g.acts.new(char="P",effect="sound",arg="bink_sound.wav")
g.acts.new("","location","g","switch_map",[235,15,"under/map1_copy.txt"])
g.acts.new(char="p",effect="sound",arg="piano.wav")
g.acts.new(char="k",effect="unlock",arg="unlock_door")
g.acts.new(char="k",effect="sound",arg="bink_sound.wav")
g.acts.new(char="k",effect="kill")

g.run_game()#
import textengine as tx

g = tx.Game()
g.map.set_path("under/under_house_map.txt")
g.map.set_overlay("under/under_overlay.txt")
g.objs.get_sprites("under/under_sprites.txt")
g.objs.get_texts("under/under_text.txt")
g.camera_follow = ["x","y"]
#g.add_theme('under/theme.wav')
g.folder = "under/"

player = g.objs.Obj("grimm","g",geom="line",move="wasd",
    xspeed=100, yspeed=20,animate="sneaky")
g.objs.append_obj(player)
g.objs.new("face","L")
g.objs.new("door1","h",geom="skeleton")
g.objs.new("face","q",geom="skeleton")
g.objs.new("wall","f")
g.objs.new("wall-side","s")
g.objs.new("wall-back","b")
g.objs.new("father","u",geom="line")
g.objs.new("tree",'t',geom="line")
g.objs.new("fence","x",geom="line")
g.objs.new("fence-side","z")
g.objs.new("piano","p",geom="line")
g.objs.new("couch","C",geom="complex")
g.objs.new("carpet","G",geom=None)
g.objs.new("plant","P",geom="line")
g.objs.new("door3","H",geom="skeleton")
g.objs.new("key","k",geom="line")

doors = {"door2":"door1","door1":"door2","door3":"door2"}
plants = {"plant":"plant1","plant1":"plant"}
g.acts.new(char="h",effect="switch_sprite",arg=doors)
g.acts.new(char="h",effect="sound",arg="door_close.wav")
g.acts.new(char="P",effect="switch_sprite",arg=plants)
g.acts.new(char="P",effect="sound",arg="bink_sound.wav")
g.acts.new("","location","g","quit",[110,35])
g.acts.new(char="p",effect="sound",arg="piano.wav")
g.acts.new("unlock_door","interact","H","switch_sprite",doors,True)
g.acts.new(char="H",effect="sound",arg="door_close.wav")
g.acts.new(char="k",effect="unlock",arg="unlock_door")
g.acts.new(char="k",effect="sound",arg="bink_sound.wav")
g.acts.new(char="k",effect="kill")

g.run_game()#
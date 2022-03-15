import textengine as tx

g = tx.Game()
g.map.set_path("undertaker/under_house_map.txt")
g.objs.get_sprites("undertaker/under_sprites.txt")
g.camera_follow = ["x","y"]
g.theme = ''#song.wav'


g.objs.new("door-open","d",geom="line")
g.objs.new("door","h",geom="complex")
g.objs.new("face","q")
g.objs.new("wall","f")
g.objs.new("wall-side","s")
g.objs.new("wall-back","b")
g.objs.new("father","u",geom="line")
g.objs.new("tree",'t',geom="line")
g.objs.new("fence","x",geom="line")
g.objs.new("fence-side","z")
g.objs.new("piano","p",geom="line")
g.objs.new("grimm-d","g",move="wasd",geom="line",xspeed=2,
    yspeed=1)

g.run_game()
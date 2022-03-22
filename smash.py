import textengine as tx
g = tx.Game()
g.map.set_path("smash/smash_map1.txt")
g.objs.get_sprites("smash/smash_sprites.txt")
g.camera_follow = ['x','y']

g.objs.new("link","q",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("samus","w",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("donkey","e",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("ness","r",move="wasd",grav=True,xspeed=30,yspeed=2)
g.objs.new("yoshi","t",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("pikachu","p",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("fox","f",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("jiggly","j",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("kirby","k",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("link-old","b",geom="line",move="leftright",grav=True,xspeed=29)
g.objs.new("floor","a")

g.run_game()
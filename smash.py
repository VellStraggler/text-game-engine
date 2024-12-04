import textengine as tx
g = tx.Game()
g.set_map_path("smash/smash_map1.txt")
g.set_sprite_path("smash/smash_sprites.txt")
g.camera_follow = ['x','y']

g.objs.new("link","q",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("samus","w",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("donkey","e",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("ness","r",move="wasd",grav=True,xspeed=100,yspeed=30,max_jump=10,
animate = "flip")
g.objs.new("yoshi","t",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("pikachu","p",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("fox","f",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("jiggly","j",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("kirby","k",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("link-old","b",geom="line",move="none",grav=True,xspeed=29,
animate = "flip")
g.objs.new("floor","a")

g.run_game()
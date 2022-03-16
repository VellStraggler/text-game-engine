import textengine as tx
g = tx.Game()
g.map.set_path("smash/smash_map1.txt")
g.objs.get_sprites("smash/smash_sprites.txt")
g.camera_follow = ['x','y']

g.objs.new("link","q",move="leftright",grav_tick=1)
g.objs.new("samus","w",move="leftright",grav_tick=1)
g.objs.new("donkey","e",move="leftright",grav_tick=1)
g.objs.new("ness","r",move="wasd",grav_tick=1,yspeed=4)
g.objs.new("yoshi","t",move="leftright",grav_tick=1)
g.objs.new("pikachu","p",move="leftright",grav_tick=1)
g.objs.new("fox","f",move="leftright",grav_tick=1)
g.objs.new("jiggly","j",move="leftright",grav_tick=1)
g.objs.new("kirby","k",move="leftright",grav_tick=1)
g.objs.new("link-old","b",move="leftright",grav_tick=1)
g.objs.new("floor","a")

g.run_game()
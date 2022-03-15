import textengine as tx
g = tx.Game()
g.map.set_path("smash/smash_map1.txt")
g.objs.get_sprites("smash/smash_sprites.txt")
g.camera_follow = ['x','y']

g.objs.new("link","q",[0,0],"wasd","line",1,2,grav_tick=4)
g.objs.new("samus","w",move="leftright")
g.objs.new("donkey","e",move="leftright")
g.objs.new("ness","r",move="leftright")
g.objs.new("yoshi","t",move="leftright")
g.objs.new("pikachu","p",move="leftright")
g.objs.new("fox","f",move="leftright")
g.objs.new("jiggly","j",move="leftright")
g.objs.new("kirby","k",move="leftright")
g.objs.new("link-old","b",move="leftright")
g.objs.new("floor","a")

g.run_game()
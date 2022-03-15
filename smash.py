import textengine as tx
g = tx.Game()
g.map.set_path("smash/smash_map1.txt")
g.objs.get_sprites("smash/smash_sprites.txt")
g.camera_follow = ['x','y']

g.objs.new("link","q",[0,0],"wasd","line",1,2,grav_tick=4)
g.objs.new("samus","w")
g.objs.new("donkey","e")
g.objs.new("ness","r")
g.objs.new("yoshi","t")
g.objs.new("pikachu","p")
g.objs.new("fox","f")
g.objs.new("jiggly","j")
g.objs.new("kirby","k")
g.objs.new("link-old","b",geom=None)
g.objs.new("floor","a")

g.run_game()
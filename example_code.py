import textengine as tx

g = tx.Game()
g.set_map_path('example/example_map.txt')
g.set_sprite_path('example/spritesheet.txt')

g.objs.new('playerframe1','p',move = "wasd",geom = "line",xspeed=10,yspeed=5)
g.objs.new('tree','t',geom = "line")
g.objs.new('cottage','c',geom = "line")
g.objs.new('wall','w',geom = "all")
g.objs.new('castle','f',geom = "all")

g.run_game()
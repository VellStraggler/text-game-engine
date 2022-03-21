import textengine as tx

g = tx.Game()
g.map.set_path('example/example_map.txt')
g.objs.get_sprites('example/spritesheet.txt')

g.objs.new('playerframe1','p',move = "wasd",geom = "line")
g.objs.new('tree','t',geom = "line")
g.objs.new('cottage','c',geom = "line")
g.objs.new('wall','w',geom = "all")
g.objs.new('castle','f',geom = "all")

g.run_game()
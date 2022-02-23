import textengine as tx

g = tx.Game()
g.map.set_path('mario_map.txt')
g.objs.get_sprites('mario_sprites.txt')

g.objs.new('mario','m',movement = "user",health=1,gravity="down")
g.objs.new('goomba','g',movement = "leftright")
g.objs.new('block','b')
g.objs.new('block2','v')
g.objs.new('pipe','p')
g.objs.new('flag','f')

g.run_map()
import textengine as tx

g = tx.Game()
g.map.set_path('mario_map.txt')
g.sprites.get_sprites('mario_sprites.txt')

g.sprites.new('mario','m',movement = True,geometry = "all")
g.sprites.new('goomba','g',geometry = "all")
g.sprites.new('block','b',geometry = "all")
g.sprites.new('block2','v',geometry = "all")
g.sprites.new('pipe','p',geometry = "all")
g.sprites.new('flag','f',geometry = "all")

g.follow_sprite('mario')
g.run_map()
import textengine as tx

g = tx.GameObject()
g.map.path = 'mario_map.txt'
g.sprites.path = 'mario_sprites.txt'
g.map.translate()
g.sprites.get_sprites()

g.sprites.new('mario','m',movement = True,geometry = "all",)
g.sprites.new('goomba','g',geometry = "all")
g.sprites.new('block','b',geometry = "all")
g.sprites.new('block2','v',geometry = "all")
g.sprites.new('pipe','p',geometry = "all")
g.sprites.new('flag','f',geometry = "all")

g.run_map()
import textengine as tx

g = tx.GameObject()
g.map.path = 'example/example_map.txt'
g.sprites.path = 'example/spritesheet.txt'
g.map.translate()
g.sprites.get_sprites()

g.sprites.new('playerframe1','p',movement = True,geometry = "all")
g.sprites.new('tree','t',geometry = "line")
g.sprites.new('cottage','c',geometry = "line")
g.sprites.new('wall','w',geometry = "all")
g.sprites.new('castle','f',geometry = "all")

g.run_map()
import textengine as tx
import time

g = tx.GameObject()
g.map.path = 'example_map.txt'
g.map.translate()
g.sprites.path = 'spritesheet1.txt'
g.sprites.get_sprites()
points = 0
timeofday = 4

g.sprites.new('playerframe1','p',movement = True,geometry = "all")
g.sprites.new('tree','t')
g.sprites.new('cottage','c')
g.sprites.new('wall','w')

g.run_map()
import textengine as tx

g = tx.GameObject()
g.map.path = 'example_map.txt'
g.map.translate()
g.sprites.path = 'spritesheet1.txt'
points = 0
timeofday = 4

player = g.sprites.add('giant-head','p',[3,4])
player.movement = True
tree = g.sprites.add('tree','t',[7,6])
cottage = g.sprites.add('cottage','c')
brick = g.sprites.add('wall','w')

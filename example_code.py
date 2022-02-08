import textengine as tx

g = tx.GameObject()
g.map.path = 'example_map.txt'
g.map.translate()
g.sprites.path = 'spritesheet1.txt'
g.sprites.get_sprites()
points = 0
timeofday = 4

player = g.sprites.Sprite('giant-head','p',[3,4])
player.movement = True
tree = g.sprites.Sprite('tree','t',[7,6])
cottage = g.sprites.Sprite('cottage','c')
brick = g.sprites.Sprite('wall','w')

g.run_map()

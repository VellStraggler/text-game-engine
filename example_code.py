import textengine as tx

g = tx.GameObject()
g.map.path = 'example_map.txt'
g.map.translate()
g.sprites.path = 'spritesheet1.txt'
points = 0
timeofday = 4

player = tx.Sprite('giant-head','p',[3,4])
player.movement = True
g.sprites.add(player)
tree = tx.Sprite('tree','t',[7,6])
g.sprites.add(tree)
cottage = tx.Sprite('cottage','c')
g.sprites.add(cottage)
brick = tx.Sprite('wall','w')
g.sprites.add(brick)

g.run_map()

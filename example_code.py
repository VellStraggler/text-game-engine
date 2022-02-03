import textengine as tx

game = tx.GameObject()
map = game.Map('example_map.txt')
sprites = game.Sprites('spritesheet1.txt')
points = 0
timeofday = 4


#Sprites
player = Sprite('giant-head')
player.on_map = 'p'
player.xy = 3,4
player.movement = True
tree = sprite('tree')
tree.on_map = 't'
tree.xy = 7,6

cottage = sprite('cottage')
cottage.on_map = 'c'
brick = sprite('wall')
brick.on_map = 'w'



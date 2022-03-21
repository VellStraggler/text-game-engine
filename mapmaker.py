import textengine as tx
g = tx.Game()
map_path = input("Please enter the map path: ")
sprite_path = input("Please enter the sprite path: ")
g.map.set_path(map_path)
g.objs.get_sprites(sprite_path)
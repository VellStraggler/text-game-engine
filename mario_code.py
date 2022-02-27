import textengine as tx

g = tx.Game()
g.map.set_path('mario_map.txt')
g.objs.get_sprites('mario_sprites.txt')

g.objs.new('mario','m',move = "wasd",hp=1,grav=True,
    xspeed =3,yspeed = 3,enemy_chars=['g','f'],geom="all")
g.objs.new('goomba','g',geom="all",move = "leftright",
    dmg=1)
g.objs.new('block','b')
g.objs.new('block2','v')
g.objs.new('pipe','p')
g.objs.new('flag','f')

g.run_map()
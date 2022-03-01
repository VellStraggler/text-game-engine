import textengine as tx

input()
def main():
    g = tx.Game()
    g.map.set_path('mario_map.txt')
    g.objs.get_sprites('mario_sprites.txt')

    g.objs.new('mario','m',move = "wasd",grav=True,
        xspeed =3,yspeed = 3,enemy_chars=['g','f'],geom="all",
        dmg_dirs=['down'])
    g.objs.new('goomba','g',geom="all",move = "leftright",
        dmg_dirs=['left','right','down'],enemy_chars=['m'])
    g.objs.new('block','b')
    g.objs.new('block2','v')
    g.objs.new('pipe','p')
    g.objs.new('flag','f',dmg_dirs=['left'])

    g.run_map()

while True:
    main()